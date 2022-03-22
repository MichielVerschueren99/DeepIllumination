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
    # min = img.min() + 0.0
    # max = img.max() + 0.0
    # img = torch.FloatTensor(img.size()).copy_(img)
    # img.add_(-min).mul_(1.0 / (max - min))
    # img = img.mul_(2).add_(-1)

    return img


lijst = []

#lijst.append(readEXR("C:\\Users\\Michi\\Documents\\school\\0.exr"))
#lijst.append(readEXR("C:\\Users\\Michi\\Documents\\school\\1.exr"))

lijst.append(torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]))
lijst.append(torch.tensor([[0.0, -2.0, 334.0], [4, 25.0, 63.0]]))

som = torch.stack(lijst)
mean = torch.mean(som)
std = torch.std(som)

som.add_(-mean).mul_(1.0 / std)
A_mean = torch.full((3, 256, 256), 1.0)
B_mean = torch.full((3, 256, 256), 3.0)
C = torch.cat((A_mean, B_mean))

D = torch.sub(B_mean, A_mean)
print("test")
