"""Portable, data-only neural graph interchange and validation."""
import json
from pathlib import Path
import bpy

SCHEMA = 'neural-operator-composer/v1'

def property_names(value):
    result = set()
    for cls in type(value).__mro__:
        result.update(getattr(cls, '__annotations__', {}))
    return sorted(result)

def properties(value):
    result = {}
    for key in property_names(value):
        field = getattr(value, key)
        if isinstance(field, bpy.types.PropertyGroup):
            result[key] = properties(field)
        elif key in value.bl_rna.properties and value.bl_rna.properties[key].type == 'COLLECTION':
            result[key] = [properties(item) for item in field]
        elif isinstance(field, (str, int, float, bool)):
            result[key] = field
    return result

def set_properties(value, fields):
    allowed = set(property_names(value))
    items = sorted(fields.items(), key=lambda item: (item[0] not in {'input_amount', 'output_amount', 'num_of_slices'}, item[0]))
    for key, field in items:
        if key not in allowed:
            raise ValueError(f'Unknown property: {key}')
        target = getattr(value, key)
        if isinstance(field, dict):
            set_properties(target, field)
        elif isinstance(field, list):
            target.clear()
            for item in field:
                set_properties(target.add(), item)
        else:
            setattr(value, key, field)

def to_dict(tree):
    nodes = []
    for node in tree.nodes:
        nodes.append({
            'id': node.name, 'type': node.bl_idname, 'label': node.label,
            'location': list(node.location), 'width': node.width,
            'hide': node.hide, 'color': list(node.color),
            'use_custom_color': node.use_custom_color,
            'parent': node.parent.name if node.parent else None,
            'properties': properties(node),
            'outputs': [getattr(s, 'output_name', '') for s in node.outputs],
        })
    links = [
        {'from': link.from_node.name, 'output': list(link.from_node.outputs).index(link.from_socket),
         'to': link.to_node.name, 'input': list(link.to_node.inputs).index(link.to_socket)}
        for link in tree.links
    ]
    return {'schema': SCHEMA, 'name': tree.name, 'nodes': nodes, 'links': links}

def from_dict(document, name=None):
    if document.get('schema') != SCHEMA:
        raise ValueError('Unsupported neural graph schema')
    if len(document.get('nodes', [])) > 10000 or len(document.get('links', [])) > 50000:
        raise ValueError('Graph exceeds import size limit')
    from .caffe_nodes import CLASSES
    types = {cls.bl_idname for cls in CLASSES if issubclass(cls, bpy.types.Node)} | {'NodeFrame', 'NodeReroute'}
    identifiers = [n['id'] for n in document['nodes']]
    if any(not isinstance(identifier, str) or not identifier for identifier in identifiers):
        raise ValueError('Node identifiers must be nonempty strings')
    if len(set(identifiers)) != len(identifiers):
        raise ValueError('Duplicate node identifiers')
    if any(n['type'] not in types for n in document['nodes']):
        raise ValueError('Unknown neural node type')
    identifier_set = set(identifiers)
    destinations = set()
    for link in document['links']:
        if link.get('from') not in identifier_set or link.get('to') not in identifier_set:
            raise ValueError('Link refers to a missing node')
        if any(type(link.get(key)) is not int or link[key] < 0 for key in ('output', 'input')):
            raise ValueError('Socket indices must be nonnegative integers')
        destination = (link['to'], link['input'])
        if destination in destinations:
            raise ValueError('Multiple links target the same input socket')
        destinations.add(destination)
    tree = bpy.data.node_groups.new(name or document['name'], 'CaffeNodeTree')
    tree.use_fake_user = True
    try:
        nodes = {}
        for record in document['nodes']:
            node = tree.nodes.new(record['type'])
            node.name = record['id']
            node.label = record.get('label', '')
            set_properties(node, record.get('properties', {}))
            node.width = record.get('width', 180)
            node.hide = record.get('hide', False)
            node.color = record.get('color', (0.3, 0.3, 0.3))
            node.use_custom_color = record.get('use_custom_color', False)
            output_names = record.get('outputs', [])
            if not isinstance(output_names, list) or len(output_names) != len(node.outputs) or any(not isinstance(text, str) for text in output_names):
                raise ValueError('Output names must match the node socket count: ' + node.name)
            for socket, text in zip(node.outputs, output_names):
                if hasattr(socket, 'output_name'):
                    socket.output_name = text
            nodes[record['id']] = node
        for record in document['nodes']:
            node = nodes[record['id']]
            if record.get('parent'):
                node.parent = nodes[record['parent']]
            node.location = record['location']
        for link in document['links']:
            nodes_from, nodes_to = nodes[link['from']], nodes[link['to']]
            if link['output'] >= len(nodes_from.outputs) or link['input'] >= len(nodes_to.inputs):
                raise ValueError('Link socket index is out of range')
        for link in document['links']:
            nodes_from, nodes_to = nodes[link['from']], nodes[link['to']]
            tree.links.new(nodes_from.outputs[link['output']], nodes_to.inputs[link['input']])
        return tree
    except Exception:
        bpy.data.node_groups.remove(tree)
        raise

def save(tree, path):
    Path(path).write_text(json.dumps(to_dict(tree), indent=2, sort_keys=True) + '\n')

def load(path):
    return from_dict(json.loads(Path(path).read_text()))

def topological(tree):
    nodes = [n for n in tree.nodes if n.bl_idname not in {'NodeFrame', 'SolverNodeType'}]
    remaining = {n.name: n for n in nodes}
    done, ordered = set(), []
    while remaining:
        ready = sorted((n for n in remaining.values() if all(link.from_node.name in done for s in n.inputs for link in s.links)), key=lambda n:n.name)
        if not ready:
            raise ValueError('Cycle in neural graph: ' + ', '.join(sorted(remaining)[:5]))
        for node in ready:
            ordered.append(node)
            done.add(node.name)
            del remaining[node.name]
    return ordered

def validate(tree):
    ordered = topological(tree)
    blobs, errors = {}, []
    for node in ordered:
        if node.bl_idname == 'NodeReroute':
            errors.append('Replace reroutes with direct links before Caffe export: ' + node.name)
        for socket in node.outputs:
            name = getattr(socket, 'output_name', '')
            if not name or any(c in name for c in '\n\r"\\'):
                errors.append('Set a valid output blob name: ' + node.name)
            elif name in blobs:
                errors.append('Duplicate output blob: ' + name)
            blobs[name] = node.name
        for socket in node.inputs:
            if not socket.is_linked:
                errors.append('Unconnected input: ' + node.name + '/' + socket.name)
        if any(c in node.name for c in '\n\r"\\'):
            errors.append('Invalid Caffe layer name: ' + node.name)
    if errors:
        raise ValueError('\n'.join(errors[:15]))
    return {'nodes': len(ordered), 'links': len(tree.links), 'blobs': len(blobs)}
