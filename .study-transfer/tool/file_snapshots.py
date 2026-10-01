"""Project byte snapshots with no full-size plaintext intermediate copy."""
import gzip
import hashlib
import io
import os
from pathlib import Path, PurePosixPath
import tarfile

from blob_store import Reader, Writer

EXCLUDED = {'.git', '.study-transfer', 'node_modules', '.venv', 'venv', '__pycache__', '.pytest_cache'}


def within(path, root):
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except ValueError:
        return False


def snapshot_files(root, store, excluded_roots=(), chunk_bytes=32 * 1024**2):
    root = Path(root)
    writer = Writer(store, chunk_bytes)
    catalog = []
    with gzip.GzipFile(fileobj=writer, mode='wb', mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w|', format=tarfile.PAX_FORMAT) as archive:
            for directory, directories, files in os.walk(root):
                directories[:] = sorted(name for name in directories if name not in EXCLUDED and not any(within(Path(directory)/name, excluded) for excluded in excluded_roots))
                for name in directories:
                    candidate = Path(directory) / name
                    if candidate.is_symlink() or getattr(os.path, 'isjunction', lambda p: False)(candidate):
                        raise ValueError('Directory links require separate review: ' + str(candidate))
                for name in sorted(files):
                    path = Path(directory) / name
                    if any(within(path, excluded) for excluded in excluded_roots):
                        continue
                    if path.is_symlink() or getattr(os.path, 'isjunction', lambda p: False)(path):
                        raise ValueError('External filesystem links require separate review: ' + str(path))
                    stat = path.stat()
                    digest = hashlib.sha256()
                    class HashReader:
                        def __init__(self, source):
                            self.source = source
                        def read(self, size):
                            data = self.source.read(size)
                            digest.update(data)
                            return data
                    relative = path.relative_to(root).as_posix()
                    info = archive.gettarinfo(str(path), arcname=relative)
                    if not info.isfile():
                        raise ValueError('Unsupported project file: ' + relative)
                    with path.open('rb') as source:
                        archive.addfile(info, HashReader(source))
                    after = path.stat()
                    if stat.st_size != after.st_size or stat.st_mtime_ns != after.st_mtime_ns:
                        raise ValueError('A project file changed during export. Finish the active run first: ' + relative)
                    catalog.append({'path': relative, 'bytes': stat.st_size, 'sha256': digest.hexdigest(), 'mtime_ns': stat.st_mtime_ns})
    return {'chunks': writer.finish(), 'files': catalog, 'total_bytes': sum(item['bytes'] for item in catalog)}


def checked_target(root, relative):
    parts = PurePosixPath(relative)
    if not relative or parts.is_absolute() or '\\' in relative or ':' in relative or '..' in parts.parts:
        raise ValueError('Unsafe snapshot member path.')
    path = Path(root).joinpath(*parts.parts)
    for candidate in [path] + list(path.parents):
        if candidate == Path(root).parent:
            break
        if candidate.is_symlink() or getattr(os.path, 'isjunction', lambda p: False)(candidate):
            raise ValueError('Restore destination contains a filesystem link.')
    if not within(path, root):
        raise ValueError('Snapshot member escapes the restore directory.')
    return path


def restore_files(snapshot, store, target, skip_paths=()):
    target = Path(target)
    expected = {item['path']: item for item in snapshot['files']}
    if len(expected) != len(snapshot['files']):
        raise ValueError('Duplicate project catalog entries.')
    observed = set()
    with gzip.GzipFile(fileobj=Reader(store, snapshot['chunks']), mode='rb') as compressed:
        with tarfile.open(fileobj=compressed, mode='r|') as archive:
            for member in archive:
                if not member.isfile() or member.name not in expected or member.name in observed:
                    raise ValueError('Unexpected or unsupported project snapshot member.')
                path = checked_target(target, member.name)
                digest = hashlib.sha256()
                size = 0
                skipped = member.name in skip_paths
                if not skipped:
                    path.parent.mkdir(parents=True, exist_ok=True)
                destination = io.BytesIO() if skipped else path.open('xb')
                with archive.extractfile(member) as source, destination:
                    while True:
                        data = source.read(1024**2)
                        if not data:
                            break
                        if not skipped:
                            destination.write(data)
                        digest.update(data)
                        size += len(data)
                wanted = expected[member.name]
                if size != wanted['bytes'] or digest.hexdigest() != wanted['sha256']:
                    raise ValueError('Restored project file failed its byte verification.')
                if not skipped and 'mtime_ns' in wanted:
                    os.utime(path, ns=(wanted['mtime_ns'], wanted['mtime_ns']))
                observed.add(member.name)
    if observed != set(expected):
        raise ValueError('Incomplete project snapshot.')
    return len(observed)


class IterReader(io.RawIOBase):
    def __init__(self, iterator, sink=None):
        self.iterator = iter(iterator)
        self.buffer = b''
        self.sink = sink
    def readable(self):
        return True
    def read(self, size=-1):
        if size < 0:
            pieces = [self.buffer]
            self.buffer = b''
            for piece in self.iterator:
                if self.sink:
                    self.sink.write(piece)
                pieces.append(piece)
            return b''.join(pieces)
        while len(self.buffer) < size:
            try:
                piece = next(self.iterator)
            except StopIteration:
                break
            if self.sink:
                self.sink.write(piece)
            self.buffer += piece
        value, self.buffer = self.buffer[:size], self.buffer[size:]
        return value


def tar_catalog(reader):
    catalog = []
    with tarfile.open(fileobj=reader, mode='r|') as archive:
        for member in archive:
            name = member.name.removeprefix('./').rstrip('/') or '.'
            record = {'path': name, 'type': member.type.decode('ascii'), 'uid': member.uid, 'gid': member.gid, 'mode': member.mode, 'link': member.linkname}
            if member.isfile():
                digest = hashlib.sha256()
                with archive.extractfile(member) as source:
                    while True:
                        data = source.read(1024**2)
                        if not data:
                            break
                        digest.update(data)
                record.update(bytes=member.size, sha256=digest.hexdigest())
            catalog.append(record)
    # Consume archive padding and remaining stream data for a complete captured tar.
    while reader.read(1024**2):
        pass
    return sorted(catalog, key=lambda value: value['path'])


def snapshot_tar(iterator, store, chunk_bytes):
    writer = Writer(store, chunk_bytes)
    with gzip.GzipFile(fileobj=writer, mode='wb', mtime=0) as compressed:
        catalog = tar_catalog(IterReader(iterator, compressed))
    return {'chunks': writer.finish(), 'catalog': catalog}
