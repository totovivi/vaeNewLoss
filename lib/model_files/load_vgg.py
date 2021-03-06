import cPickle as pickle
import theano.tensor as T

from lasagne.layers import InputLayer, DenseLayer, NonlinearityLayer
from lasagne.layers.dnn import Conv2DDNNLayer as ConvLayer
from lasagne.layers import Pool2DLayer as PoolLayer
from lasagne.nonlinearities import softmax
import lasagne

import numpy as np

import theano

def vgg_network(x, mb_size, image_width):
    def normalize(x):
        return (x.transpose(0,3,1,2)[:,::-1,:,:] - np.array([104, 117, 123]).reshape((1,3,1,1)).astype('float32'))

    obj = pickle.load(open('model_files/vgg19_normalized.pkl'))

    params = obj['param values']

    xn = normalize(x)

    net = {}
    net['input'] = InputLayer((mb_size, 3, image_width, image_width))
    net['conv1_1'] = ConvLayer(net['input'], 64, 3, pad=1)
    net['conv1_2'] = ConvLayer(net['conv1_1'], 64, 3, pad=1)
    net['pool1'] = PoolLayer(net['conv1_2'], 2, mode='average_exc_pad')
    net['conv2_1'] = ConvLayer(net['pool1'], 128, 3, pad=1)
    net['conv2_2'] = ConvLayer(net['conv2_1'], 128, 3, pad=1)
    net['pool2'] = PoolLayer(net['conv2_2'], 2, mode='average_exc_pad')
    net['conv3_1'] = ConvLayer(net['pool2'], 256, 3, pad=1)
    net['conv3_2'] = ConvLayer(net['conv3_1'], 256, 3, pad=1)
    net['conv3_3'] = ConvLayer(net['conv3_2'], 256, 3, pad=1)
    net['conv3_4'] = ConvLayer(net['conv3_3'], 256, 3, pad=1)
    net['pool3'] = PoolLayer(net['conv3_4'], 2, mode='average_exc_pad')
    net['conv4_1'] = ConvLayer(net['pool3'], 512, 3, pad=1)
    net['conv4_2'] = ConvLayer(net['conv4_1'], 512, 3, pad=1)
    net['conv4_3'] = ConvLayer(net['conv4_2'], 512, 3, pad=1)
    net['conv4_4'] = ConvLayer(net['conv4_3'], 512, 3, pad=1)
    net['pool4'] = PoolLayer(net['conv4_4'], 2, mode='average_exc_pad')
    net['conv5_1'] = ConvLayer(net['pool4'], 512, 3, pad=1)
    net['conv5_2'] = ConvLayer(net['conv5_1'], 512, 3, pad=1)
    net['conv5_3'] = ConvLayer(net['conv5_2'], 512, 3, pad=1)
    net['conv5_4'] = ConvLayer(net['conv5_3'], 512, 3, pad=1)
    net['pool5'] = PoolLayer(net['conv5_4'], 2, mode='average_exc_pad')

    #average_exc_pad

    lasagne.layers.set_all_param_values(net['pool5'], params)

    output = lasagne.layers.get_output(net['pool5'], xn)

    vgg_params = lasagne.layers.get_all_params(net['pool5'], trainable=True)

    return {'params' : vgg_params, 'output' : output}

'''
Assumes that x is of the shape: 

    (minibatch, channels, rows, columns)

With raw RGB (no normalization).  

'''

def vgg_network_pair(x1, x2, params, config):    

    def normalize(x):
        return x.transpose(0,3,1,2)[:,::-1,:,:] - np.array([104, 117, 123]).reshape((1,3,1,1)).astype('float32')

    x1n = normalize(x1)
    x2n = normalize(x2)

    net = {}
    net['input'] = InputLayer((config['mb_size'], 3, config['image_width'], config['image_width']))
    net['conv1_1'] = ConvLayer(net['input'], 64, 3, pad=1)
    net['conv1_2'] = ConvLayer(net['conv1_1'], 64, 3, pad=1)
    net['pool1'] = PoolLayer(net['conv1_2'], 2, mode='average_exc_pad')
    net['conv2_1'] = ConvLayer(net['pool1'], 128, 3, pad=1)
    net['conv2_2'] = ConvLayer(net['conv2_1'], 128, 3, pad=1)
    net['pool2'] = PoolLayer(net['conv2_2'], 2, mode='average_exc_pad')
    net['conv3_1'] = ConvLayer(net['pool2'], 256, 3, pad=1)
    net['conv3_2'] = ConvLayer(net['conv3_1'], 256, 3, pad=1)
    net['conv3_3'] = ConvLayer(net['conv3_2'], 256, 3, pad=1)
    net['conv3_4'] = ConvLayer(net['conv3_3'], 256, 3, pad=1)
    net['pool3'] = PoolLayer(net['conv3_4'], 2, mode='average_exc_pad')
    net['conv4_1'] = ConvLayer(net['pool3'], 512, 3, pad=1)
    net['conv4_2'] = ConvLayer(net['conv4_1'], 512, 3, pad=1)
    net['conv4_3'] = ConvLayer(net['conv4_2'], 512, 3, pad=1)
    net['conv4_4'] = ConvLayer(net['conv4_3'], 512, 3, pad=1)
    net['pool4'] = PoolLayer(net['conv4_4'], 2, mode='average_exc_pad')
    net['conv5_1'] = ConvLayer(net['pool4'], 512, 3, pad=1)
    net['conv5_2'] = ConvLayer(net['conv5_1'], 512, 3, pad=1)
    net['conv5_3'] = ConvLayer(net['conv5_2'], 512, 3, pad=1)
    net['conv5_4'] = ConvLayer(net['conv5_3'], 512, 3, pad=1)
    net['pool5'] = PoolLayer(net['conv5_4'], 2, mode='average_exc_pad')

    lasagne.layers.set_all_param_values(net['pool5'], params)

    outputs1 = {}
    outputs2 = {}

    for key in net: 
        outputs1[key] = lasagne.layers.get_output(net[key], x1n)
        outputs2[key] = lasagne.layers.get_output(net[key], x2n)

    return outputs1, outputs2

def multiplier(key, image_width, t):
    k2s = {}
    k2s['conv1_1'] = (64, image_width)
    k2s['conv1_2'] = (64, image_width)
    k2s['pool1'] = (64, image_width / 2)
    k2s['conv2_1'] = (128, image_width / 2)
    k2s['conv2_2'] = (128, image_width / 2)
    k2s['pool2'] = (128, image_width / 4)
    k2s['conv3_1'] = (256, image_width / 4)
    k2s['conv3_2'] = (256, image_width / 4)
    k2s['conv3_3'] = (256, image_width / 4)
    k2s['conv3_4'] = (256, image_width / 4)
    k2s['pool3'] = (512, image_width / 8)
    k2s['conv4_1'] = (512, image_width / 8)
    k2s['conv4_2'] = (512, image_width / 8)
    k2s['conv4_3'] = (512, image_width / 8)
    k2s['conv4_4'] = (512, image_width / 8)
    k2s['pool4'] = (512, image_width / 16)
    k2s['conv5_1'] = (512, image_width / 16)
    k2s['conv5_2'] = (512, image_width / 16)
    k2s['conv5_3'] = (512, image_width / 16)
    k2s['conv5_4'] = (512, image_width / 16)
    k2s['pool5'] = (512, image_width / 32)

    #number of filters
    N = k2s[key][0]
    #number of filter positions
    M = k2s[key][1]

    if t == "style":
        mult = 100.0 / (4.0 * M**4 * N**2)
    elif t == "content":
        mult = 10000.0 / (M)

    print "Key multiplier", key, t, mult

    return mult


def gram_matrix(x, mb_size):

    #gram = (x.dimshuffle(0, 'x', 1, 2, 3) * x.dimshuffle(0, 1, 'x', 2, 3)).sum(axis=[3, 4])
    #return gram.flatten(ndim=2)


    def one_step(x_example):
        x_example = x_example.reshape((1, x.shape[1], x.shape[2] * x.shape[3]))
        return T.tensordot(x_example, x_example, axes = ([2], [2]))

    results, _ = theano.scan(fn=one_step, outputs_info=None,non_sequences=[],sequences=[x], n_steps = mb_size)

    #x is (128, 3, 32, 32).  

    #x = x.flatten(3)
    #g = T.tensordot(x, x, axes=([2], [2]))

    return results


def compute_style_penalty(o1, o2, keys, mb_size, image_width):
    ls = 0.0


    sequences = []
    keyMap = {}
    index = 0

    shapeMap = {}

    shapeMap['conv1_1'] = (64, 96, 96)
    shapeMap['conv2_1'] = (128, 48, 48)
    shapeMap['conv3_1'] = (256, 24, 24)
    shapeMap['conv4_1'] = (512, 12, 12)

    for key in keys:
        sequences += [o1[key]]
        sequences += [o2[key]]

        keyMap[(1, key)] = index
        keyMap[(2, key)] = index + 1

        index += 2


    def gram(args, keyUse, sx, ex, sy, ey):

        x1 = args[keyMap[(1, keyUse)]]
        x2 = args[keyMap[(2, keyUse)]]

        shape_raw = shapeMap[keyUse]
        print "keyUse", keyUse, shape_raw
        shape = (1, shape_raw[0], ex - sx, ey - sy)

        x1 = x1[:,sx:ex,sy:ey]
        x2 = x2[:,sx:ex,sy:ey]

        x1 = x1.reshape((1, shape[1], shape[2] * shape[3]))
        gram1 = T.tensordot(x1, x1, axes = ([2], [2]))

        x2 = x2.reshape((1, shape[1], shape[2] * shape[3]))
        gram2 = T.tensordot(x2, x2, axes = ([2], [2]))

        #100000
        return T.sum(10.0 * T.sqr(gram1 - gram2)) * multiplier(key, image_width, "style")


    def one_step(*args):

        style_loss = 0.0

        for key in keys:

            style_loss += gram(args, key, 0, 120, 0, 120)

        return style_loss

    results, _ = theano.scan(fn=one_step, outputs_info=None,non_sequences=[],sequences=sequences, n_steps = mb_size)

    return results.sum()

class NetDist:

    def __init__(self, x1, x2, config):
        self.config = config

        obj = pickle.load(open(config['vgg19_file']))

        params = obj['param values']

        o1,o2 = vgg_network_pair(x1, x2, params, config)

        self.o1 = o1
        self.o2 = o2

    def get_dist_style(self):

        style_keys = self.config['style_keys']

        dist_style = 0.0

        dist_style += compute_style_penalty(self.o1, self.o2, style_keys, self.config['mb_size'], self.config['image_width'])

        return dist_style, dist_style, dist_style

    def get_dist_content(self):

        shapeMap = {}
        shapeMap['conv1_1'] = (1, 64, 1, 1)
        shapeMap['conv1_2'] = (1, 64, 1, 1)
        shapeMap['conv2_1'] = (1, 128, 1, 1)
        shapeMap['conv2_2'] = (1, 128, 1, 1)
        shapeMap['conv3_1'] = (1, 256, 1, 1)
        shapeMap['conv3_2'] = (1, 256, 1, 1)
        shapeMap['conv3_3'] = (1, 256, 1, 1)
        shapeMap['conv3_4'] = (1, 256, 1, 1)

        dist_content = {}

        content_keys = self.config['content_keys']


        for key in content_keys:

            h1 = self.o1[key]
            h2 = self.o2[key]


            dist_content[key] = T.sum(T.sqr(h1 - h2))

        return dist_content, []


if __name__ == "__main__":


    obj = pickle.load(open('/u/lambalex/trained_models/vgg-19/vgg19_normalized.pkl'))

    p = obj['param values']

    for e in p:
        print e.shape

    import numpy.random as rng
    srng = theano.tensor.shared_randomstreams.RandomStreams(rng.randint(999999))
    x = srng.normal(size=(1, 32, 32, 3))

    import time

    config = {}

    config['mb_size'] = 1
    config['image_width'] = 32
    config['vgg19_file'] = '/u/lambalex/trained_models/vgg-19/vgg19_normalized.pkl'

    t0 = time.time()
    f = theano.function(inputs = [], outputs = get_dist(x, x, config)[0])
    print time.time() - t0, "time to compile"

    #x = np.random.uniform(size = (config['mb_size'], 32, 32, 3)).astype('float32')

    t0 = time.time()
    res = f()
    print res

