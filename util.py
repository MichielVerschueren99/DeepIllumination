import os

import numpy as np
#from scipy.misc import imread, imresize, imsave
import imageio
import torch
import re
import sys

#filepath is altijd van een png
def load_image(filepath, extension):
    if extension == "png":
        image = imageio.imread(filepath)
    else:
        size = len(filepath)
        actual_filepath = filepath[:size - 4] + ".pfm"
        image = read_pfm(actual_filepath)
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

def makePBRT(integrator, sampler, filter, film, camera, world):  # TODO wat doet die tranform hier?
    return """Integrator {}
Transform [ 1 -0 -0 -0 -0 1 -0 -0 -0 -0 -1 -0 -0 -1 6.8 1]
Sampler {}
PixelFilter {}
Film {}
Camera {}
WorldBegin
{}
WorldEnd""".format(integrator, sampler, filter, film, camera, world)


def pathTracingIntegrator(maxdepth=65):
    return "\"path\" \"integer maxdepth\" [ {} ]".format(maxdepth)


def normalIntegrator():
    return "\"normal\""


def depthIntegrator():
    return "\"depth\""

def albedoIntegrator():
    return "\"albedo\""


def directIlluminationIntegrator():
    return "\"directlighting\""


def sobolSampler(samples=64):
    return "\"sobol\" \"integer pixelsamples\" [ {} ]".format(samples)


def triangleFilter(xwidth=1, ywidth=1):
    return "\"triangle\" \"float xwidth\" [ {} ] \"float ywidth\" [ {} ]".format(xwidth, ywidth)


def imageFilm(filename, xresolution=256, yresolution=256):
    return "\"image\" \"integer xresolution\" [ {} ] \"integer yresolution\" [ {} ] \"string filename\" [ \"{}\" ]".format(
        xresolution, yresolution, filename)


def perspectiveCamera(fov=19.5):
    return "\"perspective\" \"float fov\" [ {} ]".format(fov)


def cornellBoxWorld(attribute):
    return """
MakeNamedMaterial "LeftWall" "string type" [ "matte" ] "rgb Kd" [ 0.630000 0.065000 0.050000 ] 
MakeNamedMaterial "RightWall" "string type" [ "matte" ] "rgb Kd" [ 0.140000 0.450000 0.091000 ] 
MakeNamedMaterial "Floor" "string type" [ "matte" ] "rgb Kd" [ 0.725000 0.710000 0.680000 ] 
MakeNamedMaterial "Ceiling" "string type" [ "matte" ] "rgb Kd" [ 0.725000 0.710000 0.680000 ] 
MakeNamedMaterial "BackWall" "string type" [ "matte" ] "rgb Kd" [ 0.725000 0.710000 0.680000 ] 
MakeNamedMaterial "Item" "string type" [ "matte" ] "rgb Kd" [ 0.725000 0.710000 0.680000 ] 
MakeNamedMaterial "Light" "string type" [ "matte" ] "rgb Kd" [ 0.000000 0.000000 0.000000 ] 
NamedMaterial "Floor" 
Shape "trianglemesh" "integer indices" [ 0 1 2 0 2 3 ] "point P" [ -1 1.74846e-007 -1 -1 1.74846e-007 1 1 -1.74846e-007 1 1 -1.74846e-007 -1 ] "normal N" [ 4.37114e-008 1 1.91069e-015 4.37114e-008 1 1.91069e-015 4.37114e-008 1 1.91069e-015 4.37114e-008 1 1.91069e-015 ] "float uv" [ 0 0 1 0 1 1 0 1 ] 
NamedMaterial "Ceiling" 
Shape "trianglemesh" "integer indices" [ 0 1 2 0 2 3 ] "point P" [ 1 2 1 -1 2 1 -1 2 -1 1 2 -1 ] "normal N" [ -8.74228e-008 -1 -4.37114e-008 -8.74228e-008 -1 -4.37114e-008 -8.74228e-008 -1 -4.37114e-008 -8.74228e-008 -1 -4.37114e-008 ] "float uv" [ 0 0 1 0 1 1 0 1 ] 
NamedMaterial "BackWall" 
Shape "trianglemesh" "integer indices" [ 0 1 2 0 2 3 ] "point P" [ -1 0 -1 -1 2 -1 1 2 -1 1 0 -1 ] "normal N" [ 8.74228e-008 -4.37114e-008 -1 8.74228e-008 -4.37114e-008 -1 8.74228e-008 -4.37114e-008 -1 8.74228e-008 -4.37114e-008 -1 ] "float uv" [ 0 0 1 0 1 1 0 1 ] 
NamedMaterial "RightWall" 
Shape "trianglemesh" "integer indices" [ 0 1 2 0 2 3 ] "point P" [ 1 0 -1 1 2 -1 1 2 1 1 0 1 ] "normal N" [ 1 -4.37114e-008 1.31134e-007 1 -4.37114e-008 1.31134e-007 1 -4.37114e-008 1.31134e-007 1 -4.37114e-008 1.31134e-007 ] "float uv" [ 0 0 1 0 1 1 0 1 ] 
NamedMaterial "LeftWall" 
Shape "trianglemesh" "integer indices" [ 0 1 2 0 2 3 ] "point P" [ -1 0 1 -1 2 1 -1 2 -1 -1 0 -1 ] "normal N" [ -1 -4.37114e-008 -4.37114e-008 -1 -4.37114e-008 -4.37114e-008 -1 -4.37114e-008 -4.37114e-008 -1 -4.37114e-008 -4.37114e-008 ] "float uv" [ 0 0 1 0 1 1 0 1 ] 

AttributeBegin
{}
AttributeEnd

AttributeBegin
    AreaLightSource "diffuse" "rgb L" [ 17.000000 12.000000 4.000000 ] 
    NamedMaterial "Light" 
    Shape "trianglemesh" "integer indices" [ 0 1 2 0 2 3 ] "point P" [ -0.24 1.98 -0.22 0.23 1.98 -0.22 0.23 1.98 0.16 -0.24 1.98 0.16 ] "normal N" [ -8.74228e-008 -1 1.86006e-007 -8.74228e-008 -1 1.86006e-007 -8.74228e-008 -1 1.86006e-007 -8.74228e-008 -1 1.86006e-007 ] "float uv" [ 0 0 1 0 1 1 0 1 ] 
AttributeEnd""".format(attribute)


def put_render_in_location(path):
    if os.path.exists(path):
        os.remove(path)
    if path.endswith(".png"):
        os.rename(os.path.abspath("render.png"), path)
    else:
        os.rename(os.path.abspath("render.pfm"), path)
