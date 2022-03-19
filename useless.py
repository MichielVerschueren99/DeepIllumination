import imageio
import numpy as np
import OpenEXR as exr
import Imath
import torch

import util

def readEXR(filename):

    image_file = exr.InputFile(filename)
    header = image_file.header()

    dw = header['dataWindow']
    i_size = (dw.max.y - dw.min.y + 1, dw.max.x - dw.min.x + 1)

    channelData = dict()

    # convert all channels in the image to numpy arrays
    for c in header['channels']:
        C = image_file.channel(c, Imath.PixelType(Imath.PixelType.FLOAT))
        C = np.frombuffer(C, dtype=np.float32)
        C = np.reshape(C, i_size)

        channelData[c] = C

    colorChannels = ['R', 'G', 'B', 'A'] if 'A' in header['channels'] else ['R', 'G', 'B']
    img = np.concatenate([channelData[c][..., np.newaxis] for c in colorChannels], axis=2)

    # sanitize image to be in range [0, 1]
    #img = np.where(img < 0.0, 0.0, np.where(img > 1.0, 1, img))

    assert 'A' not in header['channels']
    assert 'Z' not in header['channels']

    img = np.transpose(img, (2, 0, 1))
    img = torch.from_numpy(img)
    min = img.min() + 0.0
    max = img.max() + 0.0
    img = torch.FloatTensor(img.size()).copy_(img)
    img.add_(-min).mul_(1.0 / (max - min))
    img = img.mul_(2).add_(-1)

    return img


test = readEXR("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\train_gt_1070.exr")
#test2 = readEXR("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\test_depth_23.exr")
image = util.load_image("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\train_gt_1070.pfm", "pfm")
#image2 = util.load_image("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\test_depth_23.pfm", "pfm")
#base = util.load_image("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\7.png")
print("test")
