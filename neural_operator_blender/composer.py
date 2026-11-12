"""Blender interface for composing and exporting neural operators."""
import json
from pathlib import Path
import re
import shlex
import bpy
from bpy.props import StringProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
from . import caffe_nodes, caffe_export, graph

EXAMPLES = Path(__file__).parent / 'examples'

def active_tree(context):
    tree = getattr(context.space_data, 'edit_tree', None)
    if tree is None or tree.bl_idname != 'CaffeNodeTree':
        raise ValueError('Open a Neural Operator Composer node tree first')
    return tree

def show_tree(context, tree):
    space = context.space_data
    space.tree_type = 'CaffeNodeTree'
    space.pin = True
    space.node_tree = tree

def export_caffe(tree, directory):
    summary = graph.validate(tree)
    solvers = [n for n in tree.nodes if n.bl_idname == 'SolverNodeType']
    if len(solvers) != 1:
        raise ValueError('Add exactly one Solver node before exporting')
    solver = solvers[0]
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', solver.solvername) or solver.solvername in {'.', '..'}:
        raise ValueError('Solver name must use letters, digits, underscores, dots or hyphens')
    if solver.lr_policy == 'multistep':
        raise ValueError('The multistep learning-rate policy is not supported; choose another policy')
    directory = Path(directory).resolve()
    original_path = solver.config_path
    data_nodes = [n for n in tree.nodes if n.bl_idname == 'DataNodeType']
    phases = [n.include_in for n in data_nodes]
    weight_nodes = [n for n in tree.nodes if getattr(n, 'use_custom_weight', False)]
    weight_paths = [n.custom_weight for n in weight_nodes]
    try:
        solver.config_path = str(directory) + '/'
        for node in weight_nodes:
            path = Path(node.custom_weight)
            if not path.is_absolute() and not node.custom_weight.startswith('//'):
                path = EXAMPLES / path
            else:
                path = Path(bpy.path.abspath(node.custom_weight))
            if not path.is_file():
                raise ValueError('Missing custom operator weights: ' + node.name)
            node.custom_weight = str(path)
        nodes = graph.topological(tree) + solvers
        files = caffe_export.generate(nodes)
        headers = []
        excluded = {'DataNodeType', 'SMLossNodeType', 'SCELossNodeType', 'EULossNodeType', 'AccuracyNodeType', 'HDF5OutputNodeType', 'SolverNodeType', 'NodeFrame', 'NodeReroute'}
        deployment = [node for node in nodes if node.bl_idname not in excluded and node.include_in != 'TRAIN']
        available = {socket.output_name for node in data_nodes for socket in node.outputs}
        used_data = set()
        for node in deployment:
            for socket in node.inputs:
                source = socket.links[0].from_socket
                if source.output_name not in available:
                    raise ValueError('Deployment input depends on an excluded training/evaluation node: ' + node.name)
                if source.node in data_nodes:
                    used_data.add(source.output_name)
            available.update(socket.output_name for socket in node.outputs)
        for node in data_nodes:
            for index, socket in enumerate(node.outputs):
                if index == 0 or socket.output_name in used_data:
                    headers.append(f'input: {caffe_export.proto_string(socket.output_name)}\ninput_shape {{ dim: 1 dim: {node.input_channels} dim: {node.input_height} dim: {node.input_width} }}\n')
        name = solver.solvername
        files[name + '_deploy.prototxt'] = ''.join(headers) + files[name + '_deploy.prototxt']
        executable = str(Path(bpy.path.abspath(solver.caffe_exec)) / 'caffe')
        command = [executable, 'train', '--solver=' + str(directory / (name + '_solver.prototxt'))]
        if solver.solver_mode == 'GPU':
            command.append('--gpu=' + (solver.gpus or '0'))
        files['train_' + name + '.sh'] = '#!/usr/bin/env sh\nexec ' + shlex.join(command) + '\n'
    finally:
        solver.config_path = original_path
        for node, phase in zip(data_nodes, phases):
            node.include_in = phase
        for node, path in zip(weight_nodes, weight_paths):
            node.custom_weight = path
    directory.mkdir(parents=True, exist_ok=True)
    for filename, content in files.items():
        (directory / filename).write_text(content)
    return summary

class NOC_OT_new(bpy.types.Operator):
    bl_idname = 'noc.new'
    bl_label = 'New Neural Graph'
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        tree = bpy.data.node_groups.new('Neural Operator', 'CaffeNodeTree')
        tree.use_fake_user = True
        show_tree(context, tree)
        return {'FINISHED'}

class NOC_OT_import(bpy.types.Operator, ImportHelper):
    bl_idname = 'noc.import_graph'
    bl_label = 'Import Neural Graph'
    filename_ext = '.json'
    filter_glob: StringProperty(default='*.json', options={'HIDDEN'})
    def execute(self, context):
        try:
            show_tree(context, graph.load(self.filepath))
            return {'FINISHED'}
        except Exception as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}

class NOC_OT_export(bpy.types.Operator, ExportHelper):
    bl_idname = 'noc.export_graph'
    bl_label = 'Export Neural Graph JSON'
    filename_ext = '.json'
    filter_glob: StringProperty(default='*.json', options={'HIDDEN'})
    def execute(self, context):
        try:
            graph.save(active_tree(context), self.filepath)
            return {'FINISHED'}
        except Exception as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}

class NOC_OT_caffe(bpy.types.Operator):
    bl_idname = 'noc.export_caffe'
    bl_label = 'Export Caffe Solution'
    directory: StringProperty(subtype='DIR_PATH')
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    def execute(self, context):
        try:
            summary = export_caffe(active_tree(context), self.directory)
            self.report({'INFO'}, f"Exported {summary['nodes']} nodes")
            return {'FINISHED'}
        except Exception as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}

class NOC_OT_validate(bpy.types.Operator):
    bl_idname = 'noc.validate'
    bl_label = 'Validate Graph'
    def execute(self, context):
        try:
            summary = graph.validate(active_tree(context))
            self.report({'INFO'}, f"Valid graph: {summary['nodes']} nodes, {summary['links']} links")
            return {'FINISHED'}
        except Exception as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}

class NOC_OT_example(bpy.types.Operator):
    bl_idname = 'noc.example'
    bl_label = 'Load Patch-Beltrami Example'
    bl_options = {'REGISTER', 'UNDO'}
    example: EnumProperty(items=[('patch_beltrami_bw', 'Patch-Beltrami Grayscale', ''), ('patch_beltrami_rgb', 'Patch-Beltrami Color', ''), ('patch_beltrami_multifilter', 'Patch-Beltrami Five Stages', ''), ('operator_demo', 'Compact Operator Demo', '')])
    def execute(self, context):
        try:
            show_tree(context, graph.load(EXAMPLES / (self.example + '.json')))
            return {'FINISHED'}
        except Exception as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}

class NOC_MT_nodes(bpy.types.Menu):
    bl_idname = 'NOC_MT_nodes'
    bl_label = 'Neural Operators'
    def draw(self, context):
        for cls in caffe_nodes.CLASSES:
            if issubclass(cls, bpy.types.Node):
                op = self.layout.operator('node.add_node', text=cls.bl_label)
                op.type = cls.bl_idname
                op.use_transform = True

class NOC_PT_composer(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Composer'
    bl_label = 'Neural Operator Composer'
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CaffeNodeTree'
    def draw(self, context):
        layout = self.layout
        layout.operator('noc.new', icon='ADD')
        layout.operator('noc.import_graph', icon='IMPORT')
        layout.operator('noc.export_graph', icon='EXPORT')
        layout.separator()
        for key, title in [('operator_demo', 'Compact Operator Demo'), ('patch_beltrami_bw', 'Patch-Beltrami Grayscale'), ('patch_beltrami_rgb', 'Patch-Beltrami Color'), ('patch_beltrami_multifilter', 'Five-Stage Network')]:
            layout.operator('noc.example', text=title).example = key
        layout.separator()
        layout.operator('noc.validate', icon='CHECKMARK')
        layout.operator('noc.export_caffe', icon='FILE_TICK')
        tree = getattr(context.space_data, 'edit_tree', None)
        if tree:
            layout.label(text=f'{len(tree.nodes)} nodes / {len(tree.links)} links')
        layout.label(text='Caffe execution uses an external installation.')

def draw_add(self, context):
    if getattr(context.space_data, 'tree_type', None) == 'CaffeNodeTree':
        self.layout.menu('NOC_MT_nodes')

CLASSES = (NOC_OT_new, NOC_OT_import, NOC_OT_export, NOC_OT_caffe, NOC_OT_validate, NOC_OT_example, NOC_MT_nodes, NOC_PT_composer)

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.NODE_MT_add.append(draw_add)

def unregister():
    bpy.types.NODE_MT_add.remove(draw_add)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
