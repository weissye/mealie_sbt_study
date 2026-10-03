"""Keep encrypted payloads and the Git LFS cache on the selected storage disk."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess

from blob_store import MAGIC


def configure(central, transfer, storage_root):
    central, transfer = Path(central), Path(transfer)
    storage_root = Path(storage_root)
    if not storage_root.is_absolute():
        raise ValueError('StorageRoot must be an absolute path.')
    storage_root.mkdir(parents=True, exist_ok=True)
    key_id = hashlib.sha256((transfer / 'key.json').read_bytes()).hexdigest()[:24]
    scope = storage_root / central.name / key_id
    chunks = scope / 'chunks'
    media = scope / 'lfs'
    chunks.mkdir(parents=True, exist_ok=True)
    media.mkdir(parents=True, exist_ok=True)
    # Refuse to hide existing local ciphertext copies or completed snapshots.
    # Existing pointers are small and can safely stay in the source worktree.
    for path in (transfer / 'objects').glob('*.blob'):
        with path.open('rb') as source:
            if source.read(len(MAGIC)) == MAGIC:
                raise ValueError('Local encrypted payloads still exist on the source disk. Do not delete completed snapshots; review storage migration first.')
    env = subprocess.run(['git', '-C', str(central), 'lfs', 'env'], capture_output=True, text=True, check=True).stdout
    previous = next((line.split('=', 1)[1] for line in env.splitlines() if line.startswith('LocalMediaDir=')), None)
    if not previous:
        raise ValueError('Git LFS did not report its current storage directory.')
    # Old committed LFS objects remain available after the local config changes.
    # Copy to the selected disk; do not prune or delete the old cache.
    old_media = Path(previous)
    new_media = media / 'objects'
    new_media.mkdir(exist_ok=True)
    if old_media.resolve() != new_media.resolve() and old_media.exists():
        for directory, _, files in os.walk(old_media):
            for name in files:
                if len(name) != 64 or any(c not in '0123456789abcdef' for c in name):
                    continue
                old = Path(directory) / name
                target = new_media / old.relative_to(old_media)
                if hashlib.sha256(old.read_bytes()).hexdigest() != name:
                    raise ValueError('Old local Git LFS object failed its checksum.')
                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(old, target)
                if hashlib.sha256(target.read_bytes()).hexdigest() != name:
                    raise ValueError('Selected Git LFS storage failed its checksum.')
    subprocess.run(['git', '-C', str(central), 'config', '--local', 'lfs.storage', str(media)], check=True)
    return chunks


def write_pointer(worktree_path, ciphertext_path, cipher_digest):
    """Only publish a small LFS pointer after the ciphertext has been verified."""
    worktree_path, ciphertext_path = Path(worktree_path), Path(ciphertext_path)
    if worktree_path.exists():
        with worktree_path.open('rb') as source:
            if source.read(len(MAGIC)) == MAGIC:
                raise ValueError('Refusing to replace a source ciphertext file with a pointer.')
    size = ciphertext_path.stat().st_size
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    worktree_path.write_text('version https://git-lfs.github.com/spec/v1\n'
                             'oid sha256:' + cipher_digest + '\nsize ' + str(size) + '\n', encoding='ascii')
