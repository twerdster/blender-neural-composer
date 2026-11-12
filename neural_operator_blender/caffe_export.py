"""Modernized Caffe-GUI-Tool implementation; see NOTICE and LICENSES/Unlicense.txt."""
__author__ = 'gip'
bl_info = {'name': 'Create Caffe solution', 'category': 'Object'}
import bpy
import json
import random
import time
import os
tab = '    '
tab2 = tab + tab
tab3 = tab2 + tab

def proto_string(value):
    return json.dumps(str(value), ensure_ascii=False)

def getFillerString(filler, name):
    fillerString = tab3 + 'type: %s\n' % proto_string(filler.type)
    if filler.type == 'constant':
        fillerString += tab3 + 'value: %.9g\n' % filler.value
    elif filler.type == 'xavier' or filler.type == 'msra':
        fillerString += tab3 + 'variance_norm: %s\n' % filler.variance_norm
    elif filler.type == 'gaussian':
        fillerString += tab3 + 'mean: %.9g\n' % filler.mean
        fillerString += tab3 + 'std: %.9g\n' % filler.std
        if filler.is_sparse:
            fillerString += tab3 + 'sparse: %i\n' % filler.sparse
    elif filler.type == 'uniform':
        fillerString += tab3 + 'min: %.9g\n' % filler.min
        fillerString += tab3 + 'max: %.9g\n' % filler.max
    string = '        %s {\n%s\n        }\n' % (name, fillerString)
    return string

def conv_template(node):
    if node.square_padding:
        padding_string = tab2 + 'pad: %i\n' % node.pad
    else:
        padding_string = tab2 + 'pad_h: %i\n' % node.pad_h
        padding_string += tab2 + 'pad_w: %i\n' % node.pad_w
    if node.square_kernel:
        kernel_string = tab2 + 'kernel_size: %i\n' % node.kernel_size
    else:
        kernel_string = tab2 + 'kernel_h: %i\n' % node.kernel_h
        kernel_string += tab2 + 'kernel_w: %i\n' % node.kernel_w
    if node.square_stride:
        stride_string = tab2 + 'stride: %i\n' % node.stride
    else:
        stride_string = tab2 + 'stride_h: %i\n' % node.stride_h
        stride_string += tab2 + 'stride_w: %i\n' % node.stride_w
    weight_filler_string = ''
    bias_filler_string = ''
    if not node.use_custom_weight:
        weight_filler_string = getFillerString(node.weight_filler, 'weight_filler')
        bias_filler_string = getFillerString(node.bias_filler, 'bias_filler')
    string = '    convolution_param {\n        num_output: %i\n        bias_term: %i\n        group: %i\n%s\n%s\n%s\n%s\n%s\n    }\n' % (node.num_output, node.bias_term, node.group, padding_string, kernel_string, stride_string, weight_filler_string, bias_filler_string)
    return string

def data_param_template(node, source, batch_size):
    string = '    data_param {\n        source: %s\n        backend: %s\n        batch_size: %i\n        rand_skip: %i\n    }\n' % (proto_string(source), node.db_type, batch_size, node.rand_skip)
    return string

def image_data_param_template(node, source, batch_size):
    string = '    image_data_param {\n        source: %s\n        batch_size: %i\n        rand_skip: %i\n        shuffle: %i\n        new_height: %i\n        new_width: %i\n        is_color: %i\n    }\n' % (proto_string(source), batch_size, node.rand_skip, node.shuffle, node.new_height, node.new_width, node.is_color)
    return string

def transform_param_template(node):
    mean_file_string = ''
    if node.use_mean_file:
        mean_file_string = tab2 + 'mean_file: %s\n' % proto_string(node.mean_file)
    string = '    transform_param {\n        scale: %.9g\n        mirror: %i\n%s\n    }\n' % (node.scale, node.mirror, mean_file_string)
    return string

def hdf5_data_template(node, source, batch_size):
    string = '    hdf5_data_param {\n        source: %s\n        batch_size: %i\n        shuffle: %i\n    }\n' % (proto_string(source), batch_size, node.shuffle)
    return string

def pool_template(node):
    string = '    pooling_param {\n        pool: %s\n        kernel_size: %i\n        stride: %i\n    }\n' % (node.mode, node.kernel_size, node.stride)
    return string

def padding_template(node):
    string = '    padding_param {\n        pad_method: %s\n        pad_l: %i\n        pad_r: %i\n        pad_t: %i\n        pad_b: %i\n        pad_value: %.9g\n    }\n' % (node.mode, node.padl, node.padr, node.padt, node.padb, node.padval)
    return string

def mvntemplate(name, bottom, normalize_variance, across_channels, eps):
    string = 'layer {\n        name: %s\n        type: "MVN"\n        bottom: %s\n        top: %s\n        mvn_param  {\n        normalize_variance: %s\n        across_channels: %s\n        eps: %.9g\n        }\n        }\n' % (proto_string(name), proto_string(bottom), proto_string(name), normalize_variance, across_channels, eps)
    return string

def FC_template(node):
    weight_filler_string = getFillerString(node.weight_filler, 'weight_filler')
    bias_filler_string = getFillerString(node.bias_filler, 'bias_filler')
    string = '    inner_product_param {\n        num_output: %i\n        bias_term: %i\n%s\n%s\n        axis: %i\n    }\n' % (node.num_output, node.bias_term, weight_filler_string, bias_filler_string, node.axis)
    return string

def PReLU_template(node):
    filler_string = getFillerString(node.filler, 'filler')
    string = '    prelu_param {\n        channel_shared: %i\n%s\n    }\n' % (node.channel_shared, filler_string)
    return string

def Concattemplate(node):
    string = '    concat_param {\n        axis: %i\n    }\n    ' % node.axis
    return string

def argmaxtemplate(node):
    string = '    argmax_param {\n        out_max_val: %i\n        top_k: %i\n    }\n' % (node.OutMaxVal, node.TopK)
    return string

def hdf5outputtemplate(node):
    string = '    hdf5_output_param {\n        file_name: %s\n    }\n' % proto_string(node.filename)
    return string

def logtemplate(node):
    string = '    log_param {\n        scale: %.9g\n        shift: %.9g\n        base: %.9g\n    }\n' % (node.scale, node.shift, node.base)
    return string

def powertemplate(node):
    string = '    power_param {\n        power: %.9g\n        scale: %.9g\n        shift: %.9g\n    }\n' % (node.power, node.scale, node.shift)
    return string

def reductiontemplate(node):
    string = '    reduction_param {\n        operation: %s\n        axis: %i\n        coeff: %.9g\n    }\n' % (node.operation, node.axis, node.coeff)
    return string

def slicetemplate(node):
    slice_points_string = '\n'.join(map(lambda x: tab2 + 'slice_point: %i' % x.slice_point, node.slice_points))
    string = '    slice_param {\n        axis: %i\n%s\n    }\n' % (node.axis, slice_points_string)
    return string

def solver_template(node):
    net_path = node.config_path + '%s_train_test.prototxt' % node.solvername
    lr_string = ''
    if node.lr_policy == 'step':
        lr_string += 'gamma: %.9g\n' % node.gamma
        lr_string += 'stepsize: %i\n' % node.stepsize
    elif node.lr_policy == 'exp':
        lr_string += 'gamma: %.9g\n' % node.gamma
    elif node.lr_policy == 'inv':
        lr_string += 'gamma: %.9g\n' % node.gamma
        lr_string += 'power: %.9g\n' % node.power
    elif node.lr_policy == 'multistep':
        raise ValueError('The multistep learning-rate policy is not supported; choose another policy')
    elif node.lr_policy == 'poly':
        lr_string += 'power: %.9g\n' % node.power
    elif node.lr_policy == 'sigmoid':
        lr_string += 'gamma: %.9g\n' % node.gamma
        lr_string += 'stepsize: %i\n' % node.stepsize
    random_seed_string = ''
    if node.use_random_seed:
        random_seed_string = 'random_seed: %i' % node.random_seed
    delta_string = ''
    if node.solver_type == 'ADAGRAD':
        delta_string = 'delta: %.9g' % node.delta
    string = 'net: %s\ntest_iter: %i\ntest_interval: %i\ntest_compute_loss: %i\ntest_initialization: %i\nbase_lr: %.9g\ndisplay: %i\naverage_loss: %i\nmax_iter: %i\niter_size: %i\nlr_policy: %s\n%s\nmomentum: %.9g\nweight_decay: %.9g\nregularization_type: %s\nsnapshot: %i\nsnapshot_prefix: %s\nsnapshot_diff: %i\nsolver_mode: %s\n%s\nsolver_type: %s\n%s\ndebug_info: %i\nsnapshot_after_train: %i\n' % (proto_string(bpy.path.abspath(net_path)), node.test_iter, node.test_interval, node.test_compute_loss, node.test_initialization, node.base_lr, node.display, node.average_loss, node.max_iter, node.iter_size, proto_string(node.lr_policy), lr_string, node.momentum, node.weight_decay, proto_string(node.regularization_type), node.snapshot, proto_string(bpy.path.abspath(node.snapshot_prefix)), node.snapshot_diff, node.solver_mode, random_seed_string, node.solver_type, delta_string, node.debug_info, node.snapshot_after_train)
    return '\n'.join(filter(lambda x: x.strip(), string.splitlines())) + '\n'

def deploytemplate(batch, channels, size, datain):
    deploystring = 'name: "Autogen"\ninput: %s\ninput_dim: %i\ninput_dim: %i\ninput_dim: %i\ninput_dim: %i\n' % (proto_string(datain), batch, channels, size, size)
    return deploystring

def scripttemplate(caffepath, configpath, solvername, gpus, solver):
    gpustring = ''
    usedcount = 0
    extrastring = ''
    if solver == 'GPU' and gpus:
        extrastring = '--gpu=%s' % gpus
    solverstring = configpath + '%s_solver.prototxt' % solvername
    caffestring = caffepath + 'caffe'
    string = "#!/usr/bin/env sh \n '%s' train --solver='%s' %s" % (caffestring, solverstring, extrastring)
    return string

def loss_weight_template(loss_weight):
    return tab + 'loss_weight: %.9g' % loss_weight

def param_template(param):
    string = tab + 'param {\n'
    if param.name.strip():
        string += tab2 + 'name: %s\n' % proto_string(param.name)
    string += tab2 + 'lr_mult: %.9g\n' % param.lr_mult
    string += tab2 + 'decay_mult: %.9g\n' % param.decay_mult
    string += tab + '}'
    return string

def get_params(node):
    params = []
    if node.extra_params:
        params.append(param_template(node.weight_params))
        if not hasattr(node, 'bias_term') or node.bias_term:
            params.append(param_template(node.bias_params))
    return params

def get_include_in(node):
    if node.include_in == 'BOTH':
        return ''
    string = '    include {\n        phase: %s\n    }\n' % node.include_in
    return string

def layer_template(node, tops, bottoms, special_params):
    tops_string = '\n'.join(map(lambda x: tab + 'top: %s' % proto_string(x), tops))
    bottoms_string = '\n'.join(map(lambda x: tab + 'bottom: %s' % proto_string(x), bottoms))
    params_string = '\n'.join(get_params(node))
    special_params_string = '\n'.join(special_params)
    include_in_string = get_include_in(node)
    custom_weight_string = ''
    if node.use_custom_weight:
        with open(node.custom_weight) as f:
            custom_weight_string = f.read()
        custom_weight_string = '\n'.join((tab + r for r in custom_weight_string.split('\n')))
    string = 'layer {\n    name: %s\n    type: %s\n%s\n%s\n%s\n%s\n%s\n%s\n}\n' % (proto_string(node.name), proto_string(node.mode.strip(chr(34)) if node.bl_idname == 'AcNodeType' else node.n_type), tops_string, bottoms_string, params_string, special_params_string, include_in_string, custom_weight_string)
    return '\n'.join(filter(lambda x: x.strip(), string.splitlines())) + '\n'

def LRNtemplate(node):
    string = '    lrn_param {\n        local_size: %i\n        alpha: %.9g\n        beta: %.9g\n        norm_region: %s\n    }\n    ' % (node.size, node.alpha, node.beta, node.mode)
    return string

def eltwise_template(node):
    stable_prod_grad_string = ''
    coeffs_string = ''
    if node.operation == 'PROD':
        stable_prod_grad_string = tab2 + 'stable_prod_grad: %i' % node.stable_prod_grad
    elif node.operation == 'SUM':
        coeffs_string = '\n'.join(map(lambda x: tab2 + 'coeff: %.9g' % x.coeff, node.coeffs))
    string = '    eltwise_param {\n        operation: %s\n%s\n%s\n    }\n' % (node.operation, coeffs_string, stable_prod_grad_string)
    return string

def Relutemplate(node):
    string = '    relu_param {\n        negative_slope: %.9g\n    }\n    ' % node.negative_slope
    return string

def dropouttemplate(node):
    string = '    dropout_param {\n        dropout_ratio: %.9g\n    }\n    ' % node.dropout_ratio
    return string

class Vertex:
    pass

def reorder(graph):
    res_string = []
    res_dstring = []
    while len(graph) > 0:
        curr = min(graph, key=lambda x: len(x.bottoms))
        if len(curr.bottoms) != 0:
            raise ValueError('Unresolved Caffe graph dependencies')
        res_string.append(curr.string)
        res_dstring.append(curr.dstring)
        for item in graph:
            for top in curr.tops:
                try:
                    item.bottoms.remove(top)
                except:
                    pass
        graph.remove(curr)
    return (res_string, res_dstring)

def generate(nodes):
    graph = []
    for node in nodes:
        nname = node.name
        string = ''
        bottoms = []
        for input in node.inputs:
            if input.is_linked:
                bottom = input.links[0].from_socket.output_name
                bottoms.append(bottom)
        tops = [x.output_name for x in node.outputs]
        special_params = []
        is_deploy = True
        if node.bl_idname == 'DataNodeType':
            transform_param = transform_param_template(node)
            node.n_type = node.db_type
            if node.db_type in ('LMDB', 'LEVELDB'):
                train_params = [data_param_template(node, bpy.path.abspath(node.train_path), node.train_batch_size)]
                test_params = [data_param_template(node, bpy.path.abspath(node.test_path), node.test_batch_size)]
                node.n_type = 'Data'
                train_params.append(transform_param)
                test_params.append(transform_param)
            elif node.db_type == 'ImageData':
                train_params = [image_data_param_template(node, bpy.path.abspath(node.train_data), node.train_batch_size)]
                test_params = [image_data_param_template(node, bpy.path.abspath(node.test_data), node.test_batch_size)]
                train_params.append(transform_param)
                test_params.append(transform_param)
            elif node.db_type == 'HDF5Data':
                train_params = [hdf5_data_template(node, bpy.path.abspath(node.train_data), node.train_batch_size)]
                test_params = [hdf5_data_template(node, bpy.path.abspath(node.test_data), node.test_batch_size)]
            node.include_in = 'TRAIN'
            train_string = layer_template(node, tops, bottoms, train_params)
            node.include_in = 'TEST'
            test_string = layer_template(node, tops, bottoms, test_params)
            string = train_string + test_string
            dstring = ''
            is_deploy = False
        elif node.bl_idname == 'PoolNodeType':
            special_params.append(pool_template(node))
        elif node.bl_idname == 'PadNodeType':
            special_params.append(padding_template(node))
        elif node.bl_idname == 'ConvNodeType':
            special_params.append(conv_template(node))
        elif node.bl_idname == 'DeConvNodeType':
            special_params.append(conv_template(node))
        elif node.bl_idname == 'ExpNodeType':
            special_params.append('exp_param { base: %.9g scale: %.9g shift: %.9g }' % (node.base, node.scale, node.shift))
        elif node.bl_idname == 'MVNNodeType':
            special_params.append('mvn_param { normalize_variance: %s across_channels: %s eps: %.9g }' % (str(node.normalize_variance).lower(), str(node.across_channels).lower(), node.eps))
        elif node.bl_idname == 'FCNodeType':
            special_params.append(FC_template(node))
        elif node.bl_idname == 'FlattenNodeType':
            dstring = string
        elif node.bl_idname == 'AbsValNodeType':
            dstring = string
        elif node.bl_idname == 'SilenceNodeType':
            dstring = string
        elif node.bl_idname == 'LRNNodeType':
            special_params.append(LRNtemplate(node))
        elif node.bl_idname == 'AcNodeType':
            pass
        elif node.bl_idname == 'ReluNodeType':
            special_params.append(Relutemplate(node))
        elif node.bl_idname == 'PReluNodeType':
            special_params.append(PReLU_template(node))
            dstring = string
        elif node.bl_idname == 'DropoutNodeType':
            special_params.append(dropouttemplate(node))
        elif node.bl_idname == 'SMLossNodeType':
            special_params.append(loss_weight_template(node.w))
            dstring = ''
            is_deploy = False
        elif node.bl_idname == 'SCELossNodeType':
            special_params.append(loss_weight_template(node.w))
            dstring = ''
            is_deploy = False
        elif node.bl_idname == 'EULossNodeType':
            special_params.append(loss_weight_template(node.w))
            dstring = ''
            is_deploy = False
        elif node.bl_idname == 'ConcatNodeType':
            special_params.append(Concattemplate(node))
        elif node.bl_idname == 'AccuracyNodeType':
            dstring = ''
            is_deploy = False
        elif node.bl_idname == 'ArgMaxNodeType':
            special_params.append(argmaxtemplate(node))
            dstring = string
        elif node.bl_idname == 'HDF5OutputNodeType':
            special_params.append(hdf5outputtemplate(node))
            dstring = ''
            is_deploy = False
        elif node.bl_idname == 'LogNodeType':
            special_params.append(logtemplate(node))
            dstring = string
        elif node.bl_idname == 'PowerNodeType':
            special_params.append(powertemplate(node))
            dstring = string
        elif node.bl_idname == 'ReductionNodeType':
            special_params.append(reductiontemplate(node))
            dstring = string
        elif node.bl_idname == 'SliceNodeType':
            special_params.append(slicetemplate(node))
        elif node.bl_idname == 'EltwiseNodeType':
            special_params.append(eltwise_template(node))
        elif node.bl_idname == 'NodeReroute':
            string = ''
            dstring = ''
            is_deploy = False
        elif node.bl_idname == 'SolverNodeType':
            solverstring = solver_template(node)
            scriptstring = scripttemplate(bpy.path.abspath(node.caffe_exec), bpy.path.abspath(node.config_path), node.solvername, node.gpus, solver=node.solver_mode)
            configpath = node.config_path
            solvername = node.solvername
        elif string == 0:
            print(node.bl_idname)
        if node.bl_idname != 'SolverNodeType':
            if node.bl_idname != 'DataNodeType':
                string = layer_template(node, tops, bottoms, special_params)
                if is_deploy:
                    dstring = string
            v = Vertex()
            v.string = string
            v.dstring = dstring
            v.bottoms = bottoms
            v.tops = tops
            graph.append(v)
    strings, dstrings = reorder(graph)
    solution = ''.join(strings)
    dsolution = ''.join(dstrings)
    return {solvername + '_train_test.prototxt': solution, solvername + '_deploy.prototxt': dsolution, solvername + '_solver.prototxt': solverstring, 'train_' + solvername + '.sh': scriptstring}
