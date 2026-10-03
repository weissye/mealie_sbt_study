"""Git-backed compressed/encrypted handoff of two study trees and Docker state."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

from blob_store import Reader, Writer, Store, open_store
from file_snapshots import restore_files, snapshot_files, within, checked_target
from docker_state import client, inspect_selected, snapshot_docker, put_mount, capture_mount, recreate_container
from root_mapping import relocate_plan, relocate_snapshot
from external_storage import configure as configure_external_storage, write_pointer


def git(root, *arguments, allow_empty=False):
    process = subprocess.run(['git', '-C', str(root)] + list(arguments), capture_output=True, text=True, encoding='utf-8', errors='replace')
    if process.returncode and not allow_empty:
        raise ValueError('Git command failed: ' + ' '.join(arguments[:2]) + '\n' + process.stderr[-2000:])
    return process.stdout.strip()


def priority(item):
    image = str(item['Config']['Image']).lower()
    return 0 if 'postgres' in image else 1 if ('redis' in image or 'valkey' in image) else 2


def restart(api, items):
    failures = []
    for item in sorted(items, key=priority):
        if item['_was_running']:
            try:
                api.start(item['Id'])
            except Exception:
                failures.append(item['_name'])
    if failures:
        raise ValueError('Source services require manual restart: ' + ', '.join(failures))


def all_chunks(manifest):
    for project in manifest['files']:
        yield from project['snapshot']['chunks']
    yield from manifest['docker']['images']
    for mount in manifest['docker']['mounts']:
        yield from mount['snapshot']['chunks']


def setup_tracking(root):
    root = Path(root)
    name = root.name
    if git(root, 'branch', '--show-current') != 'main':
        raise ValueError('Study transfer currently requires the main branch.')
    remote = git(root, 'remote', 'get-url', 'origin')
    if remote not in ('https://github.com/weissye/' + name + '.git', 'git@github.com:weissye/' + name + '.git'):
        raise ValueError('Unexpected repository remote; no upload was attempted.')
    git(root, 'lfs', 'install', '--local')
    attributes = root / '.gitattributes'
    line = '.study-transfer/objects/*.blob filter=lfs diff=lfs merge=lfs -text'
    content = attributes.read_text(encoding='utf-8-sig') if attributes.exists() else ''
    if line not in content:
        attributes.write_text(content.rstrip() + '\n' + line + '\n', encoding='utf-8')
    ignore = root / '.gitignore'
    content = ignore.read_text(encoding='utf-8-sig') if ignore.exists() else ''
    if '.study-transfer/local/' not in content:
        ignore.write_text(content.rstrip() + '\n.study-transfer/local/\n', encoding='utf-8')
    tool = root / '.study-transfer/tool'
    tool.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve().parent
    for filename in ['study_transfer.py', 'blob_store.py', 'file_snapshots.py', 'docker_state.py', 'root_mapping.py', 'external_storage.py', 'Invoke-Study-Git-Transfer.ps1', 'requirements.txt', 'README.md', 'transfer-plan.json']:
        if (source / filename).resolve() != (tool / filename).resolve():
            shutil.copy2(source / filename, tool / filename)
    # Commit already-tracked source edits and the migration tool. Ignored and
    # untracked project files are preserved only in the encrypted snapshot.
    git(root, 'add', '-u')
    git(root, 'add', '-f', '--', '.gitattributes', '.gitignore', '.study-transfer/tool')
    if git(root, 'diff', '--cached', '--name-only'):
        git(root, 'commit', '-m', 'Prepare reproducible Git study handoff')


def validate_no_nested_bind_data(items):
    binds = sorted({m['Source'] for item in items for m in item['Mounts'] if m['Type'] == 'bind' and m.get('RW')})
    for index, left in enumerate(binds):
        for right in binds[index+1:]:
            if within(left, right) or within(right, left):
                raise ValueError('Overlapping writable bind roots require a separate plan.')
    return binds


def export(plan, password, push=False, storage_root=None):
    for root in plan['projects']:
        if not (Path(root) / '.git').is_dir():
            raise ValueError('Each study must already be a local Git repository.')
    engine = client()
    api = engine.api
    selected = inspect_selected(api, plan)
    binds = validate_no_nested_bind_data(selected)
    for root in plan['projects']:
        setup_tracking(root)
    central = Path(plan['central_project'])
    transfer = central / '.study-transfer'
    store = open_store(transfer, password, create=True, maximum_bytes=int(plan['maximum_new_gib'] * 1024**3))
    if storage_root:
        storage_root = Path(storage_root).resolve()
        if any(within(storage_root, root) for root in plan['projects']):
            raise ValueError('StorageRoot must be outside the source study trees.')
        store.objects = configure_external_storage(central, transfer, storage_root)
        store.source_disk = central
    lfs_environment = git(central, 'lfs', 'env')
    media_directory = next((line.split('=', 1)[1] for line in lfs_environment.splitlines() if line.startswith('LocalMediaDir=')), None)
    if not media_directory:
        raise ValueError('Git LFS did not report its local object directory. No containers were stopped.')
    store.enable_single_copy_lfs(media_directory)
    available = shutil.disk_usage(store.objects).free
    requested_cap = 64 * 1024**3 if storage_root else int(plan['maximum_new_gib'] * 1024**3)
    cap = min(requested_cap, max(0, available - 1024**3))
    store.maximum_bytes = cap
    print('Single-copy encrypted Git LFS storage enabled. Existing partial objects were authenticated and retained.', flush=True)
    print('Encrypted payload storage: ' + str(store.objects), flush=True)
    print('New-object capacity: %.3f GiB; current storage free space: %.3f GiB.' % (cap / 1024**3, available / 1024**3), flush=True)
    if storage_root and shutil.disk_usage(central).free < 2 * 1024**3:
        raise ValueError('Keep at least 2 GiB free on the source disk for Git metadata and Docker activity.')
    heads = {root: git(root, 'rev-parse', 'HEAD') for root in plan['projects']}
    manifest = {'version': 1, 'created_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'source_heads': heads, 'files': [], 'excluded_dependencies': ['.git', '.study-transfer', 'node_modules', '.venv', 'venv', '__pycache__', '.pytest_cache'],
                'tools': {}, 'docker': None}
    stopped = []
    print('Temporarily stopping the 15 explicitly selected study containers for a consistent snapshot.', flush=True)
    try:
        for item in sorted(selected, key=priority, reverse=True):
            if item['_was_running']:
                stopped.append(item)
                api.stop(item['Id'], timeout=60)
                if api.inspect_container(item['Id'])['State']['Running']:
                    raise ValueError('A study container did not stop.')
        for root in plan['projects']:
            print('Compressing and encrypting study tree: ' + Path(root).name, flush=True)
            manifest['files'].append({'root': root, 'snapshot': snapshot_files(root, store, binds, plan['chunk_bytes'])})
        manifest['docker'] = snapshot_docker(api, plan, selected, store)
    finally:
        restart(api, stopped)
    descriptor = Writer(store, plan['chunk_bytes'])
    descriptor.write(gzip.compress(json.dumps(manifest, separators=(',', ':')).encode('utf-8'), mtime=0))
    manifest_chunks = descriptor.finish()
    records = list(all_chunks(manifest)) + manifest_chunks
    store.verify(records)
    # The public manifest reveals no environment values, project contents or credentials.
    public = {'version': 1, 'created_utc': manifest['created_utc'], 'source_heads': heads,
              'manifest_chunks': manifest_chunks, 'objects': sorted({item['digest'] for item in records}),
              'project_file_count': sum(len(item['snapshot']['files']) for item in manifest['files']),
              'container_count': len(selected), 'snapshot_encrypted_gib': round(sum(store.path(d).stat().st_size for d in {r['digest'] for r in records}) / 1024**3, 3), 'new_encrypted_gib': round(store.new_bytes / 1024**3, 3),
              'source_restart_completed': True, 'home_restore_accepted': False}
    (transfer / 'manifest.json').write_text(json.dumps(public, indent=2) + '\n')
    git(central, 'add', '-f', '--', '.study-transfer/key.json', '.study-transfer/manifest.json')
    for record in records:
        if storage_root:
            write_pointer(transfer / 'objects' / (record['digest'] + '.blob'), store.path(record['digest']), record['cipher_sha256'])
        git(central, 'add', '-f', '--', '.study-transfer/objects/' + record['digest'] + '.blob')
    git(central, 'lfs', 'fsck')
    git(central, 'commit', '-m', 'Save encrypted study and stopped-server handoff')
    if push:
        for root in plan['projects']:
            print('Uploading Git and LFS objects: ' + Path(root).name, flush=True)
            git(root, 'push', 'origin', 'main')
    public['status'] = 'SOURCE_EXPORT_AND_PUSH_COMPLETE' if push else 'SOURCE_EXPORT_COMMITTED_NOT_PUSHED'
    return public


def preserve_file(path, backup):
    path, backup = Path(path), Path(backup)
    if path.exists():
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(backup))


def file_matches(path, record):
    path = Path(path)
    if not path.is_file() or path.stat().st_size != record['bytes']:
        return False
    digest = hashlib.sha256()
    with path.open('rb') as source:
        while True:
            data = source.read(1024**2)
            if not data:
                break
            digest.update(data)
    return digest.hexdigest() == record['sha256']


def clear_volume(api, image, mount):
    source = mount['Name']
    result = api.create_container(image=image, entrypoint=['/bin/sh'], command=['-c', 'find /transfer -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +'],
        host_config=api.create_host_config(binds={source: {'bind': '/transfer', 'mode': 'rw'}}))
    identifier = result['Id']
    try:
        api.start(identifier)
        if api.wait(identifier, timeout=600)['StatusCode'] != 0:
            raise ValueError('Could not clear a backed-up target volume.')
    finally:
        api.remove_container(identifier, v=True)


def import_state(plan, password, pull=False):
    central = Path(plan['central_project'])
    if pull:
        for root in plan['projects']:
            git(root, 'pull', '--ff-only')
        git(central, 'lfs', 'pull')
    transfer = central / '.study-transfer'
    public = json.loads((transfer / 'manifest.json').read_text())
    store = open_store(transfer, password)
    with Reader(store, public['manifest_chunks']) as source:
        manifest = json.loads(gzip.decompress(source.read()))
    if manifest['source_heads'] != public['source_heads']:
        raise ValueError('Authenticated snapshot and public code references differ.')
    manifest = relocate_snapshot(manifest, plan)
    for root, head in manifest['source_heads'].items():
        if root not in plan['projects']:
            raise ValueError('Snapshot project root is outside the migration plan.')
        # Snapshot/tool-only commits after the saved head are permitted.
        if git(root, 'diff', head, 'HEAD', '--', '.', ':(exclude).study-transfer'):
            raise ValueError('Destination code differs from the saved snapshot. No state was restored.')
        if git(root, 'diff', '--name-only') or git(root, 'diff', '--cached', '--name-only'):
            raise ValueError('Destination has local tracked edits. Preserve them before restoring.')
    if set(item['root'] for item in manifest['files']) != set(plan['projects']):
        raise ValueError('Snapshot does not contain both expected project trees.')
    records = list(all_chunks(manifest)) + public['manifest_chunks']
    store.verify(records)
    unchanged = {item['root']: {record['path'] for record in item['snapshot']['files'] if file_matches(checked_target(item['root'], record['path']), record)} for item in manifest['files']}
    required = sum(record['bytes'] for item in manifest['files'] for record in item['snapshot']['files'] if record['path'] not in unchanged[item['root']])
    required += sum(record.get('bytes', 0) for asset in manifest['docker']['mounts'] for record in asset['snapshot']['catalog'])
    required += manifest['docker'].get('image_tar_bytes', 0)
    if shutil.disk_usage(central).free < required + 1024**3:
        raise ValueError('Destination needs free space for staged project restoration plus Docker data.')
    run = time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    local = transfer / 'local' / run
    staging = local / 'staged'
    staging.mkdir(parents=True)
    file_count = 0
    # Decrypt, stage and independently verify every project byte before any live data changes.
    for item in manifest['files']:
        destination = staging / Path(item['root']).name
        file_count += restore_files(item['snapshot'], store, destination, unchanged[item['root']])
    engine = client()
    api = engine.api
    docker = manifest['docker']
    # Image load is non-destructive to the existing containers and their data.
    with Reader(store, docker['images']) as source:
        for update in api.load_image(source):
            event = json.loads(update) if isinstance(update, (str, bytes)) else update
            if isinstance(event, dict) and event.get('error'):
                raise ValueError('Docker image import failed.')
    for item in docker['containers']:
        if api.inspect_image(item['_committed_image'])['Id'] != item['_committed_image']:
            raise ValueError('A saved container image was not loaded.')
    existing = []
    for item in docker['containers']:
        matches = api.containers(all=True, filters={'name': '^/' + item['_name'] + '$'})
        if matches:
            before = api.inspect_container(matches[0]['Id'])
            before['_name'] = item['_name']
            before['_was_running'] = bool(before['State']['Running'])
            existing.append(before)
    # Reject incompatible networks and nonstandard target volumes before stopping anything.
    for name in docker['networks']:
        matches = [n for n in api.networks(names=[name]) if n['Name'] == name]
        if matches and (matches[0]['Driver'] != 'bridge' or matches[0].get('Internal') or matches[0].get('Ingress')):
            raise ValueError('Existing network has an incompatible configuration.')
    for asset in docker['mounts']:
        mount = asset['mount']
        if mount['Type'] == 'bind':
            if not any(within(mount['Source'], root) for root in plan['projects']):
                raise ValueError('Destination bind is outside the selected projects.')
            checked_target(Path(mount['Source']).parent, Path(mount['Source']).name)
        else:
            volumes = [v for v in (api.volumes(filters={'name': mount['Name']})['Volumes'] or []) if v['Name'] == mount['Name']]
            if volumes and (volumes[0]['Driver'] != 'local' or volumes[0].get('Options')):
                raise ValueError('Nonstandard destination volume requires review.')
    selected_ids = {item['Id'] for item in existing}
    wanted_volumes = {asset['mount']['Name'] for asset in docker['mounts'] if asset['mount']['Type'] == 'volume'}
    wanted_binds = {asset['mount']['Source'] for asset in docker['mounts'] if asset['mount']['Type'] == 'bind'}
    for summary in api.containers(all=True):
        item = api.inspect_container(summary['Id'])
        if item['Id'] in selected_ids:
            continue
        if '.study-backup-' in item['Name'] and not item['State']['Running']:
            continue
        if any((m['Type'] == 'volume' and m.get('Name') in wanted_volumes) or (m['Type'] == 'bind' and m['Source'] in wanted_binds) for m in item['Mounts']):
            raise ValueError('An unselected destination container shares restore data.')
    cutover = False
    journal = local / 'restore-status.json'
    journal.write_text(json.dumps({'status': 'BACKING_UP_DESTINATION', 'backup_directory': str(local)}, indent=2))
    try:
        for item in sorted(existing, key=priority, reverse=True):
            if item['_was_running']:
                api.stop(item['Id'], timeout=60)
        backup_records = []
        backup_root = local / 'before-store'
        backup_root.mkdir()
        shutil.copy2(transfer / 'key.json', backup_root / 'key.json')
        backup_store = Store(backup_root, store.key, store.maximum_bytes)
        # Existing volume contents are captured and authenticated before clearing.
        for asset in docker['mounts']:
            mount = asset['mount']
            if mount['Type'] == 'volume':
                volumes = [v for v in (api.volumes(filters={'name': mount['Name']})['Volumes'] or []) if v['Name'] == mount['Name']]
                if volumes:
                    backup_records.append({'mount': mount, 'snapshot': capture_mount(api, docker['helper_image'], mount, backup_store, plan['chunk_bytes'])})
                else:
                    api.create_volume(name=mount['Name'])
        backup_writer = Writer(backup_store, plan['chunk_bytes'])
        backup_writer.write(gzip.compress(json.dumps({'containers': existing, 'mounts': backup_records}, separators=(',', ':')).encode(), mtime=0))
        backup_chunks = backup_writer.finish()
        backup_store.verify(backup_chunks + [chunk for asset in backup_records for chunk in asset['snapshot']['chunks']])
        (local / 'destination-before.json').write_text(json.dumps({'manifest_chunks': backup_chunks}, indent=2))
        cutover = True
        journal.write_text(json.dumps({'status': 'CUTOVER_STARTED', 'backup_directory': str(local)}, indent=2))
        for item in existing:
            api.rename(item['Id'], item['_name'] + '.study-backup-' + run)
            for name in item['NetworkSettings']['Networks']:
                if name not in ('bridge', 'host', 'none'):
                    api.disconnect_container_from_network(item['Id'], name, force=True)
        for name, network in docker['networks'].items():
            matches = [n for n in api.networks(names=[name]) if n['Name'] == name]
            if matches:
                if matches[0]['Driver'] != 'bridge':
                    raise ValueError('Existing network has an incompatible driver.')
            else:
                api.create_network(name, driver='bridge', labels=network.get('Labels') or {})
        for item in manifest['files']:
            root = Path(item['root'])
            stage = staging / root.name
            for record in item['snapshot']['files']:
                relative = Path(record['path'])
                target = checked_target(root, record['path'])
                if record['path'] in unchanged[item['root']]:
                    if not file_matches(target, record):
                        raise ValueError('A previously unchanged destination file changed during restore.')
                    if 'mtime_ns' in record:
                        os.utime(target, ns=(record['mtime_ns'], record['mtime_ns']))
                    continue
                preserve_file(target, local / 'files-before' / root.name / relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(stage / relative), str(target))
        for asset in docker['mounts']:
            mount = asset['mount']
            if mount['Type'] == 'bind':
                source = Path(mount['Source'])
                preserve_file(source, local / 'binds-before' / hashlib.sha256(str(source).encode()).hexdigest()[:16])
                source.mkdir(parents=True, exist_ok=True)
            else:
                clear_volume(api, docker['helper_image'], mount)
            put_mount(api, docker['helper_image'], mount, store, asset['snapshot'])
        created = []
        for item in docker['containers']:
            identifier = recreate_container(api, item)
            created.append(dict(item, Id=identifier))
        restart(api, created)
        running = {item['_name']: bool(api.inspect_container(item['Id'])['State']['Running']) for item in created}
        if any(running[item['_name']] != item['_was_running'] for item in created):
            raise ValueError('Restored container running/stopped state does not match the saved state.')
    except Exception as error:
        journal.write_text(json.dumps({'status': 'RESTORE_NOT_ACCEPTED', 'cutover_started': cutover, 'backup_directory': str(local)}, indent=2))
        if not cutover:
            restart(api, existing)
        raise ValueError('Restore stopped. Original data backups: ' + str(local) + '. Do not blindly repeat Import; inspect restore-status.json first.') from error
    journal.write_text(json.dumps({'status': 'DATA_RESTORE_COMPLETE', 'backup_directory': str(local)}, indent=2))
    return {'status': 'HOME_FILES_AND_DOCKER_BYTES_RESTORED', 'project_files_verified': file_count,
            'containers_restored': len(created), 'mounted_data_verified': len(docker['mounts']),
            'backup_directory': str(local), 'application_api_acceptance': False,
            'host_root_mapping': manifest['host_root_mapping'],
            'active_test_processes_resumed': False, 'running': running}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['export', 'import'])
    parser.add_argument('--plan', type=Path, default=Path(__file__).with_name('transfer-plan.json'))
    parser.add_argument('--push', action='store_true')
    parser.add_argument('--pull', action='store_true')
    parser.add_argument('--root', help='Absolute parent directory containing both study repositories.')
    parser.add_argument('--storage-root', type=Path, help='External payload and Git LFS storage directory for export.')
    args = parser.parse_args()
    password = os.environ.get('STUDY_TRANSFER_PASSWORD', '')
    if len(password) < 12:
        raise ValueError('Use a transfer password of at least 12 characters.')
    try:
        plan = relocate_plan(json.loads(args.plan.read_text(encoding='utf-8-sig')), args.root)
        if args.mode == 'import' and args.storage_root:
            raise ValueError('StorageRoot currently applies to export only.')
        result = export(plan, password, args.push, args.storage_root) if args.mode == 'export' else import_state(plan, password, args.pull)
        print(json.dumps(result, indent=2), flush=True)
        return 0
    except Exception as error:
        # Full Docker responses can contain configured credentials. Do not echo them.
        if isinstance(error, ValueError):
            print('TRANSFER_NOT_ACCEPTED: ' + str(error), file=sys.stderr)
        else:
            print('TRANSFER_NOT_ACCEPTED: ' + type(error).__name__ + '. Inspect local state before retrying.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
