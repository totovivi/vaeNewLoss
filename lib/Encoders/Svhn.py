from Layers.ConvolutionalLayer import ConvPoolLayer
from Layers.HiddenLayer import HiddenLayer

def svhn_encoder(x,numHidden):
    c1 = ConvPoolLayer(input=x.dimshuffle(0, 3, 1, 2), in_channels = 3, out_channels = 128, kernel_len = 5, in_rows = 32, in_columns = 32, batch_size = 100,
                                        convstride=2, padsize=2,
                                        poolsize=1, poolstride=0,
                                        bias_init=0.0, name = "c1", paramMap = None)

    c2 = ConvPoolLayer(input=c1.output, in_channels = 128, out_channels = 256, kernel_len = 5, in_rows = 17, in_columns = 17, batch_size = 100,
                                        convstride=2, padsize=2,
                                        poolsize=1, poolstride=0,
                                        bias_init=0.0, name = "c2", paramMap = None
                                        )

    c3 = ConvPoolLayer(input=c2.output, in_channels = 256, out_channels = 1024, kernel_len = 5, in_rows = 10, in_columns = 10, batch_size = 100,
                                        convstride=2, padsize=2,
                                        poolsize=1, poolstride=0,
                                        bias_init=0.0, name = "c3", paramMap = None)

    h1 = HiddenLayer(c6.output.dimshuffle(0, 2, 3, 1).flatten(2), num_in = 16384, num_out = numHidden, initialization = 'xavier', name = "h1", activation = "relu")

    h2 = HiddenLayer(h1.output, num_in = numHidden, num_out = numHidden, initialization = 'xavier', name = "h2", activation = "relu")

    layers = {'c1' : c1, 'c2' : c2, 'c3' : c3, 'h1' : h1, 'h2' : h2}

    return {'layers' : layers, 'output' : h1.output + h2.output}

