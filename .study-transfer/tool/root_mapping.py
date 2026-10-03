"""Map authenticated study snapshots to a different host project root."""
import copy
from pathlib import PurePosixPath, PureWindowsPath
import re


def host_path(value):
    text = str(value)
    return PureWindowsPath(text) if re.match(r'^[A-Za-z]:[\\/]', text) or text.startswith('\\\\') else PurePosixPath(text)


def project_name(value):
    return host_path(value).name


def relocate_path(value, mapping, required=False):
    path = host_path(value)
    for source, destination in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        source_path = host_path(source)
        if type(path) is not type(source_path):
            continue
        try:
            relative = path.relative_to(source_path)
        except ValueError:
            continue
        if '..' in relative.parts:
            raise ValueError('Snapshot host path contains traversal components.')
        return str(host_path(destination).joinpath(*relative.parts))
    if required:
        raise ValueError('Writable snapshot bind is outside the authenticated project roots.')
    return value


def relocate_mount(mount, mapping, inventory=False):
    if mount['Type'] == 'bind':
        writable = bool(mount.get('Writable')) if inventory else bool(mount.get('RW'))
        mount['Source'] = relocate_path(mount['Source'], mapping, required=writable)


def relocate_labels(labels, mapping):
    for key in ('com.docker.compose.project.working_dir', 'com.docker.compose.project.config_files'):
        if key in labels:
            labels[key] = ','.join(relocate_path(value, mapping) for value in labels[key].split(','))


def relocate_plan(plan, root):
    if not root:
        return plan
    destination = host_path(root)
    if not destination.is_absolute() or '..' in destination.parts:
        raise ValueError('Destination project root must be an absolute path without traversal.')
    mapping = {source: str(destination / project_name(source)) for source in plan['projects']}
    if len(set(mapping.values())) != len(mapping):
        raise ValueError('Project names collide under the requested root.')
    result = copy.deepcopy(plan)
    result['projects'] = list(mapping.values())
    result['central_project'] = mapping[plan['central_project']]
    for container in result.get('containers', []):
        for mount in container['Mounts']:
            relocate_mount(mount, mapping, inventory=True)
        for field in ('ComposeWorkingDirectory', 'ComposeConfigurationFiles'):
            if container.get(field):
                container[field] = ','.join(relocate_path(value, mapping) for value in container[field].split(','))
        if container.get('CandidateProjectRoots'):
            container['CandidateProjectRoots'] = [relocate_path(value, mapping) for value in container['CandidateProjectRoots']]
    return result


def relocate_snapshot(manifest, plan):
    """Return a runtime copy after the caller authenticates the original manifest."""
    sources = list(manifest['source_heads'])
    files = [item['root'] for item in manifest['files']]
    if len(set(files)) != len(files) or set(sources) != set(files):
        raise ValueError('Authenticated snapshot project roots are inconsistent.')
    targets = {project_name(path): path for path in plan['projects']}
    names = [project_name(source) for source in sources]
    if len(targets) != len(plan['projects']) or len(set(names)) != len(names) or set(names) != set(targets):
        raise ValueError('Snapshot does not contain exactly the expected project names.')
    mapping = {source: targets[project_name(source)] for source in sources}
    result = copy.deepcopy(manifest)
    result['source_heads'] = {mapping[source]: head for source, head in manifest['source_heads'].items()}
    for item in result['files']:
        item['root'] = mapping[item['root']]
    docker = result['docker']
    visited_mounts = set()
    def move_mount(mount):
        if id(mount) not in visited_mounts:
            relocate_mount(mount, mapping)
            visited_mounts.add(id(mount))
    for asset in docker['mounts']:
        move_mount(asset['mount'])
    for container in docker['containers']:
        for mount in container['Mounts']:
            move_mount(mount)
        relocate_labels(container['Config'].get('Labels') or {}, mapping)
    result['host_root_mapping'] = mapping
    return result
