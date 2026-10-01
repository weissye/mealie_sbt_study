"""Stopped-container filesystem and mounted-data snapshots for study migration."""
import copy
import gzip
import json
import subprocess
import tempfile
from pathlib import Path

from blob_store import Reader, Writer
from file_snapshots import IterReader, snapshot_tar, tar_catalog, within


def client():
    import docker
    endpoint = json.loads(subprocess.check_output(['docker', 'context', 'inspect', '--format', '{{json .Endpoints.docker.Host}}'], text=True))
    return docker.DockerClient(base_url=endpoint, version='auto', timeout=600)


def inspect_selected(api, plan):
    result = []
    for declared in plan['containers']:
        item = api.inspect_container(declared['Name'])
        if item['Name'].lstrip('/') != declared['Name']:
            raise ValueError('Unexpected Docker container identity.')
        host = item['HostConfig']
        if host.get('AutoRemove') or host.get('Privileged') or host.get('Devices') or host.get('DeviceRequests') or host.get('VolumesFrom') or host.get('Links') or str(host.get('NetworkMode', '')).startswith('container:'):
            raise ValueError('Unsupported Docker host configuration requires review: ' + declared['Name'])
        expected = {(m['Type'], m['Destination']) for m in declared['Mounts']}
        actual = {(m['Type'], m['Destination']) for m in item['Mounts']}
        if expected != actual:
            raise ValueError('Docker mount topology changed; update the transfer inventory: ' + declared['Name'])
        for declared_mount in declared['Mounts']:
            actual_mount = next(m for m in item['Mounts'] if m['Destination'] == declared_mount['Destination'])
            if (declared_mount['Type'] == 'volume' and actual_mount.get('Name') != declared_mount.get('Name')) or (declared_mount['Type'] == 'bind' and actual_mount['Source'] != declared_mount['Source']) or bool(actual_mount.get('RW')) != bool(declared_mount.get('Writable')):
                raise ValueError('Docker mount source or access mode changed; refresh the inventory.')
        for mount in item['Mounts']:
            if mount['Type'] not in ('bind', 'volume'):
                raise ValueError('Unsupported Docker mount type.')
            if mount['Type'] == 'bind' and mount.get('RW') and not any(within(mount['Source'], root) for root in plan['projects']):
                raise ValueError('Writable Docker bind mount is outside the selected projects.')
            if mount['Type'] == 'volume':
                volume = api.inspect_volume(mount['Name'])
                if volume['Driver'] != 'local' or volume.get('Options'):
                    raise ValueError('Nonstandard Docker volume requires review.')
        for network in item['NetworkSettings']['Networks'].values():
            if network.get('IPAMConfig'):
                raise ValueError('Static network addresses require a separate migration plan.')
        item['_name'] = declared['Name']
        item['_was_running'] = bool(item['State']['Running'])
        result.append(item)
    names = {item['Id'] for item in result}
    mounted_volumes = {m['Name'] for item in result for m in item['Mounts'] if m['Type'] == 'volume'}
    bind_sources = {m['Source'] for item in result for m in item['Mounts'] if m['Type'] == 'bind' and m.get('RW')}
    for summary in api.containers(all=True):
        other = api.inspect_container(summary['Id'])
        if other['Id'] in names:
            continue
        if '.study-backup-' in other['Name'] and not other['State']['Running']:
            continue
        if any((m['Type'] == 'volume' and m.get('Name') in mounted_volumes) or (m['Type'] == 'bind' and m['Source'] in bind_sources) for m in other['Mounts']):
            raise ValueError('A container outside the plan shares snapshot data. No containers were stopped.')
    return result


def helper(api, image, mount, writable=False):
    source = mount['Name'] if mount['Type'] == 'volume' else mount['Source']
    result = api.create_container(image=image, entrypoint=['/bin/true'], command=[],
        host_config=api.create_host_config(binds={source: {'bind': '/transfer', 'mode': 'rw' if writable else 'ro'}}))
    return result['Id']


def capture_mount(api, image, mount, store, chunk_bytes):
    container = helper(api, image, mount)
    try:
        stream, _ = api.get_archive(container, '/transfer/.', chunk_size=1024**2)
        return snapshot_tar(stream, store, chunk_bytes)
    finally:
        api.remove_container(container, v=True)


def verify_mount(api, image, mount, expected):
    container = helper(api, image, mount)
    try:
        stream, _ = api.get_archive(container, '/transfer/.', chunk_size=1024**2)
        if tar_catalog(IterReader(stream)) != expected:
            raise ValueError('Docker mounted data failed its independent content/ownership verification.')
    finally:
        api.remove_container(container, v=True)


def put_mount(api, image, mount, store, snapshot):
    container = helper(api, image, mount, writable=True)
    try:
        with gzip.GzipFile(fileobj=Reader(store, snapshot['chunks']), mode='rb') as source:
            if not api.put_archive(container, '/transfer', source):
                raise ValueError('Docker archive restore failed.')
    finally:
        api.remove_container(container, v=True)
    verify_mount(api, image, mount, snapshot['catalog'])


def snapshot_docker(api, plan, selected, store):
    image = api.inspect_image(plan['helper_image'])['Id']
    mounts = {}
    committed = []
    networks = {}
    for item in selected:
        for name in item['NetworkSettings']['Networks']:
            if name not in ('bridge', 'host', 'none') and name not in networks:
                network = api.inspect_network(name)
                if network['Driver'] != 'bridge' or network.get('Internal') or network.get('Ingress'):
                    raise ValueError('Unsupported Docker network requires review.')
                networks[name] = network
    try:
        for item in selected:
            # A stopped container commit preserves Keycloak data held in its writable layer.
            result = api.commit(item['Id'], pause=False)
            item['_committed_image'] = result['Id']
            committed.append(result['Id'])
            for mount in item['Mounts']:
                if mount['Type'] == 'bind' and not mount.get('RW'):
                    continue
                key = mount['Type'] + ':' + (mount['Name'] if mount['Type'] == 'volume' else mount['Source'])
                if key not in mounts:
                    print('Capturing mounted data: ' + mount['Destination'], flush=True)
                    mounts[key] = dict(mount=mount, snapshot=capture_mount(api, image, mount, store, plan['chunk_bytes']))
        writer = Writer(store, plan['chunk_bytes'])
        image_tar_bytes = 0
        # One save operation deduplicates shared base image layers in the tar archive.
        with tempfile.TemporaryFile() as errors:
            process = subprocess.Popen(['docker', 'image', 'save'] + committed + [image], stdout=subprocess.PIPE, stderr=errors)
            try:
                with gzip.GzipFile(fileobj=writer, mode='wb', mtime=0) as compressed:
                    while True:
                        data = process.stdout.read(1024**2)
                        if not data:
                            break
                        image_tar_bytes += len(data)
                        compressed.write(data)
                if process.wait() != 0:
                    raise ValueError('Docker image archive export failed.')
            finally:
                process.stdout.close()
                if process.poll() is None:
                    process.terminate()
                    process.wait()
        return {'containers': selected, 'mounts': list(mounts.values()), 'networks': networks,
                'images': writer.finish(), 'helper_image': image, 'image_tar_bytes': image_tar_bytes}
    finally:
        # Only disposable commit images made by this export are removed.
        for identifier in committed:
            try:
                api.remove_image(identifier, force=False, noprune=True)
            except Exception:
                print('Temporary export image retained; source data was preserved.', flush=True)


def recreate_container(api, item):
    config = copy.deepcopy(item['Config'])
    config['Image'] = item['_committed_image']
    host = copy.deepcopy(item['HostConfig'])
    host['Binds'] = None
    host['Mounts'] = [{'Type': mount['Type'], 'Source': mount['Name'] if mount['Type'] == 'volume' else mount['Source'],
                       'Target': mount['Destination'], 'ReadOnly': not mount.get('RW', False)} for mount in item['Mounts']]
    host['ContainerIDFile'] = ''
    host['ConsoleSize'] = [0, 0]
    config['HostConfig'] = host
    endpoints = {}
    for name, network in item['NetworkSettings']['Networks'].items():
        if name not in ('bridge', 'host', 'none'):
            aliases = [alias for alias in network.get('Aliases') or [] if alias not in (item['Id'], item['Id'][:12])]
            endpoints[name] = api.create_endpoint_config(aliases=aliases)
    if endpoints:
        first = next(iter(endpoints))
        config['NetworkingConfig'] = api.create_networking_config({first: endpoints[first]})
        config['HostConfig']['NetworkMode'] = first
    result = api.create_container_from_config(config, name=item['_name'])
    identifier = result['Id']
    for name in list(endpoints)[1:]:
        api.connect_container_to_network(identifier, name, aliases=endpoints[name].get('Aliases'))
    actual = api.inspect_container(identifier)
    if actual['Image'] != item['_committed_image']:
        raise ValueError('Restored container image identity mismatch.')
    return identifier
