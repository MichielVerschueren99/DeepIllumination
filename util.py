import numpy as np
#from scipy.misc import imread, imresize, imsave
import imageio
import torch
import re
import sys

def load_image(filepath):
    image = imageio.imread(filepath)
    if len(image.shape) < 3:
        image = np.expand_dims(image, axis=2)
        image = np.repeat(image, 3, axis=2)
    image = np.transpose(image, (2, 0, 1))
    image = torch.from_numpy(image)
    min = image.min()
    max = image.max()
    image = torch.FloatTensor(image.size()).copy_(image)
    image.add_(-min).mul_(1.0 / (max - min))
    image = image.mul_(2).add_(-1)
    return image

def load_depth(filepath):
    image = read_pfm('C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\initialtest\\train\\depth\\cornell-box.pfm')
    if len(image.shape) < 3:
        image = np.expand_dims(image, axis=2)
        image = np.repeat(image, 3, axis=2)
    if image.shape[2] == 4:
        image = np.resize(image, (256, 256, 3))
    image = np.transpose(image, (2, 0, 1))
    image = torch.from_numpy(image)
    min = image.min()
    max = image.max()
    image = torch.FloatTensor(image.size()).copy_(image)
    image.add_(-min).mul_(1.0 / (max - min))
    image = image.mul_(2).add_(-1)
    return image

def save_image(image, filename):
    image = image.add_(1).div_(2)
    image = image.numpy()
    image *= 255.0
    image = image.clip(0, 255)
    image = np.transpose(image, (1, 2, 0))
    image = image.astype(np.uint8)
    imageio.imsave(filename, image)
    print ("Image saved as {}".format(filename))

def is_image(filename):
    return any(filename.endswith(extension) for extension in [".png", ".jpg"])


def read_pfm(file):
    file = open(file, 'rb')

    color = None
    width = None
    height = None
    scale = None
    endian = None

    header = file.readline().rstrip()
    if header.decode('ascii') == 'PF':
        color = True
    elif header.decode('ascii') == 'Pf':
        color = False
    else:
        raise Exception('Not a PFM file.')

    dim_match = re.search(r'(\d+)\s(\d+)', file.readline().decode('ascii'))
    if dim_match:
        width, height = map(int, dim_match.groups())
    else:
        raise Exception('Malformed PFM header.')

    scale = float(file.readline().rstrip())
    if scale < 0:  # little-endian
        endian = '<'
        scale = -scale
    else:
        endian = '>'  # big-endian

    data = np.fromfile(file, endian + 'f')
    shape = (height, width, 3) if color else (height, width)
    return np.reshape(data, shape)
