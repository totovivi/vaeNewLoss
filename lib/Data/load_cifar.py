import glob
from PIL import Image
import numpy as np

import cPickle

class CifarData:

    def __init__(self, config, segment):

        assert segment in ["train", "test"]

        if segment == "train":
            batches = ["data_batch_1", "data_batch_2", "data_batch_3", "data_batch_4", "data_batch_5"]
        elif segment == "test":
            batches = ["test_batch"]

        self.lastIndex = 0

        xl = []

        for batch in batches: 
            dataFile = open(config['cifar_location'] + batch, "rb")

            obj = cPickle.load(dataFile)

            dataFile.close()

            print "batch", obj.keys()
            xl += [obj["data"].reshape((10000, 3, 32, 32)).transpose(0,2,3,1).astype('float32')]
        
        self.images = np.concatenate(xl)

        self.numExamples = self.images.shape[0]

        self.mb_size = config['mb_size']
        self.image_width = config['image_width']

    def normalize(self, x):
        return (x / 127.5) - 1.0

    def denormalize(self, x):
        return (x + 1.0) * 127.5

    def getBatch(self):
        
        index = self.lastIndex
        self.lastIndex = index + self.mb_size


        if index + self.mb_size >= self.numExamples:
            index = 0
            self.lastIndex = 0

        x = self.images[index : index + self.mb_size]

        return {'x' : x}

if __name__ == "__main__":

    config = {}
    
    config["cifar_location"] = "/u/lambalex/data/cifar/cifar-10-batches-py/"
    config['mb_size'] = 128
    config['image_width'] = 32

    cd = CifarData(config, segment = "train")


