"""Streaming compressed snapshots in authenticated, bounded Git LFS objects."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import shutil

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MAGIC = b'STUDY-GIT-1\x00'


def derive(password, salt):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=600000).derive(password.encode('utf-8'))


def open_store(root, password, create=False, maximum_bytes=8 * 1024**3):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    path = root / 'key.json'
    if path.exists():
        config = json.loads(path.read_text())
        key = derive(password, bytes.fromhex(config['salt']))
        try:
            check = AESGCM(key).decrypt(bytes.fromhex(config['nonce']), base64.b64decode(config['check']), MAGIC)
        except Exception as error:
            raise ValueError('Incorrect transfer password or damaged key metadata.') from error
        if check != MAGIC:
            raise ValueError('Invalid transfer key metadata.')
    else:
        if not create:
            raise ValueError('Transfer key metadata is missing.')
        salt = os.urandom(16)
        key = derive(password, salt)
        nonce = os.urandom(12)
        config = {'version': 1, 'salt': salt.hex(), 'nonce': nonce.hex(), 'check': base64.b64encode(AESGCM(key).encrypt(nonce, MAGIC, MAGIC)).decode('ascii')}
        path.write_text(json.dumps(config, indent=2) + '\n')
    return Store(root, key, maximum_bytes)


class Store:
    def __init__(self, root, key, maximum_bytes):
        self.root, self.key = Path(root), key
        self.objects = self.root / 'objects'
        self.objects.mkdir(exist_ok=True)
        self.maximum_bytes = maximum_bytes
        self.new_bytes = 0

    def path(self, digest):
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Invalid encrypted object identity.')
        return self.objects / (digest + '.blob')

    def put(self, plain):
        digest = hashlib.sha256(plain).hexdigest()
        path = self.path(digest)
        if path.exists():
            record = {'digest': digest, 'bytes': len(plain), 'cipher_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            if self.get(record) != plain:
                raise ValueError('Existing encrypted object does not match its identity.')
            return record
        # Reserve both the snapshot and its later local Git LFS object copy.
        size = len(plain) + len(MAGIC) + 12 + 16
        if self.new_bytes + size > self.maximum_bytes or shutil.disk_usage(self.root).free < self.new_bytes + size * 2 + 512 * 1024**2:
            raise ValueError('Insufficient reserved disk space or configured snapshot capacity. Source data remains intact.')
        nonce = os.urandom(12)
        payload = MAGIC + nonce + AESGCM(self.key).encrypt(nonce, plain, digest.encode('ascii'))
        path.write_bytes(payload)
        self.new_bytes += len(payload)
        return {'digest': digest, 'bytes': len(plain), 'cipher_sha256': hashlib.sha256(payload).hexdigest()}

    def get(self, record):
        path = self.path(record['digest'])
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != record['cipher_sha256'] or not payload.startswith(MAGIC):
            raise ValueError('Encrypted object is missing, corrupted or still a Git LFS pointer.')
        try:
            plain = AESGCM(self.key).decrypt(payload[len(MAGIC):len(MAGIC)+12], payload[len(MAGIC)+12:], record['digest'].encode('ascii'))
        except Exception as error:
            raise ValueError('Encrypted object authentication failed.') from error
        if len(plain) != record['bytes'] or hashlib.sha256(plain).hexdigest() != record['digest']:
            raise ValueError('Decrypted object content mismatch.')
        return plain

    def verify(self, records):
        for record in records:
            self.get(record)


class Writer(io.RawIOBase):
    def __init__(self, store, chunk_bytes=32 * 1024**2):
        self.store, self.chunk_bytes = store, chunk_bytes
        self.buffer = bytearray()
        self.records = []
        self.position = 0

    def writable(self):
        return True

    def tell(self):
        return self.position

    def write(self, value):
        self.position += len(value)
        self.buffer.extend(value)
        while len(self.buffer) >= self.chunk_bytes:
            self.records.append(self.store.put(bytes(self.buffer[:self.chunk_bytes])))
            del self.buffer[:self.chunk_bytes]
        return len(value)

    def finish(self):
        if self.buffer:
            self.records.append(self.store.put(bytes(self.buffer)))
            self.buffer.clear()
        return self.records


class Reader(io.RawIOBase):
    def __init__(self, store, records):
        self.store, self.records = store, iter(records)
        self.buffer = b''

    def readable(self):
        return True

    def __iter__(self):
        while True:
            data = self.read(1024**2)
            if not data:
                return
            yield data

    def read(self, size=-1):
        if size < 0:
            values = [self.buffer]
            self.buffer = b''
            values.extend(self.store.get(record) for record in self.records)
            return b''.join(values)
        while len(self.buffer) < size:
            try:
                self.buffer += self.store.get(next(self.records))
            except StopIteration:
                break
        value, self.buffer = self.buffer[:size], self.buffer[size:]
        return value
