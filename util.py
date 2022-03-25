import os
import random

import numpy as np
# from scipy.misc import imread, imresize, imsave
import imageio
import torch
import re
import sys
import OpenEXR as exr
import Imath

def load_image(filename):

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

    assert 'A' not in header['channels']
    assert 'Z' not in header['channels']

    img = np.transpose(img, (2, 0, 1))
    img = torch.from_numpy(img)

    return img


def save_image(values, filename):

    values = values.numpy()
    values = np.transpose(values, (1, 2, 0))

    channel_names = ['R', 'G', 'B']

    if values.shape[-1] != len(channel_names):
        raise ValueError(
            'Number of channels in values does not match channel names (%d, %d)' %
            (values.shape[-1], len(channel_names)))
    header = exr.Header(values.shape[1], values.shape[0])
    try:
        exr_channel_type = Imath.PixelType(Imath.PixelType.FLOAT)
    except KeyError:
        raise TypeError('Unsupported numpy type: %s' % str(values.dtype))
    header['channels'] = {
        n: Imath.Channel(exr_channel_type) for n in channel_names
    }
    channel_data = [values[..., i] for i in range(values.shape[-1])]
    img = exr.OutputFile(filename, header)
    img.writePixels(
        dict((n, d.tobytes()) for n, d in zip(channel_names, channel_data)))
    img.close()
    print("Image saved as {}".format(filename))


def is_image(filename):
    return any(filename.endswith(extension) for extension in [".png", ".jpg", ".exr"])


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


def get_mean_and_std(dataloader):
    num_batches = 0
    sums = [0, 0, 0, 0, 0]
    squared_sums = [0, 0, 0, 0, 0]
    for (i, images) in enumerate(dataloader):
        (albedo_cpu, direct_cpu, normal_cpu, depth_cpu, gt_cpu) = (images[0], images[1], images[2], images[3], images[4])
        sums[0] += torch.mean(albedo_cpu)
        sums[1] += torch.mean(direct_cpu)
        sums[2] += torch.mean(normal_cpu)
        sums[3] += torch.mean(depth_cpu)
        sums[4] += torch.mean(gt_cpu)
        squared_sums[0] += torch.mean(albedo_cpu ** 2)
        squared_sums[1] += torch.mean(direct_cpu ** 2)
        squared_sums[2] += torch.mean(normal_cpu ** 2)
        squared_sums[3] += torch.mean(depth_cpu ** 2)
        squared_sums[4] += torch.mean(gt_cpu ** 2)
        num_batches += 1

    means = [x / num_batches for x in sums]
    stds = []
    for i in range(0, len(squared_sums)):
        stds.append((squared_sums[i] / num_batches - means[i] ** 2) ** 0.5)

    return means, stds


def makePBRT(integrator, sampler, filter, film, camera, world):
    return """Integrator {}
Sampler {}
PixelFilter {}
Film {}
{}
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

def indirectIlluminationIntegrator(maxdepth=65):
    return "\"indirectlighting\" \"integer maxdepth\" [ {} ]".format(maxdepth)


def sobolSampler(samples=64):
    return "\"sobol\" \"integer pixelsamples\" [ {} ]".format(samples)

def stratifiedSampler(xsamples=8, ysamples=8):
    return "\"stratified\" \"integer xsamples\" [ {} ] \"integer ysamples\" [ {} ]".format(xsamples, ysamples)


def triangleFilter(xwidth=1, ywidth=1):
    return "\"triangle\" \"float xwidth\" [ {} ] \"float ywidth\" [ {} ]".format(xwidth, ywidth)


def imageFilm(filename, xresolution=256, yresolution=256):
    return "\"image\" \"integer xresolution\" [ {} ] \"integer yresolution\" [ {} ] \"string filename\" [ \"{}\" ]".format(
        xresolution, yresolution, filename)


def perspectiveCamera(fov=19.5):
    return "Camera \"perspective\" \"float fov\" [ {} ]".format(fov)

def lookAtPerspectiveCamera(position, look_at_point, up, fov=19.5):
    return """LookAt {} {} {}
       {} {} {}
       {} {} {}
Camera \"perspective\" \"float fov\" [ {} ]""".format(position[0], position[1], position[2], look_at_point[0], look_at_point[1], look_at_point[2], up[0], up[1], up[2], fov)


def cornellBoxLight():
    return """AttributeBegin
		AreaLightSource \"diffuse\" \"rgb L\" [ 17.000000 12.000000 4.000000 ] 
		NamedMaterial \"Light\" 
		Shape \"trianglemesh" \"integer indices\" [ 0 1 2 0 2 3 ] \"point P\" [ -0.24 0.6 -0.22 0.23 0.6 -0.22 0.23 0.6 0.16 -0.24 0.6 0.16 ] \"normal N\" [ -8.74228e-008 -1 1.86006e-007 -8.74228e-008 -1 1.86006e-007 -8.74228e-008 -1 1.86006e-007 -8.74228e-008 -1 1.86006e-007 ] \"float uv\" [ 0 0 1 0 1 1 0 1 ] 
	AttributeEnd"""

def cornellBoxWorld(attribute):
    return """
MakeNamedMaterial "LeftWall" "string type" [ "matte" ] "rgb Kd" [ 0.630000 0.065000 0.050000 ] 
MakeNamedMaterial "RightWall" "string type" [ "matte" ] "rgb Kd" [ 0.140000 0.450000 0.091000 ] 
MakeNamedMaterial "Floor" "string type" [ "matte" ] "rgb Kd" [ 0.725000 0.710000 0.680000 ] 
MakeNamedMaterial "Ceiling" "string type" [ "matte" ] "rgb Kd" [ 0.725000 0.710000 0.680000 ] 
MakeNamedMaterial "BackWall" "string type" [ "matte" ] "rgb Kd" [ 0.725000 0.710000 0.680000 ] 
MakeNamedMaterial "Item" "string type" [ "matte" ] "rgb Kd" [ 0.60000 0.60000 0.60000 ] 
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

#4 muren, random kleuren voor de 2 muren
def emptyPrimitiveRoom(back_rgb, right_rgb, front_rgb, left_rgb):
    return """MakeNamedMaterial "LeftWall" "string type" [ "matte" ] "rgb Kd" [ {} {} {} ] 
	MakeNamedMaterial "RightWall" "string type" [ "matte" ] "rgb Kd" [ {} {} {} ] 
	MakeNamedMaterial "Floor" "string type" [ "matte" ] "rgb Kd" [ 0.725000 0.710000 0.680000 ] 
	MakeNamedMaterial "Ceiling" "string type" [ "matte" ] "rgb Kd" [ 0.725000 0.710000 0.680000 ] 
	MakeNamedMaterial "BackWall" "string type" [ "matte" ] "rgb Kd" [ {} {} {} ] 
	MakeNamedMaterial "FrontWall" "string type" [ "matte" ] "rgb Kd" [ {} {} {} ] 
	MakeNamedMaterial "Light" "string type" [ "matte" ] "rgb Kd" [ 0.000000 0.000000 0.000000 ] 
	NamedMaterial "Floor" 
	Shape "trianglemesh" "integer indices" [ 0 1 2 0 2 3 ] "point P" [ -1 0 -1 -1 0 1 1 0 1 1 0 -1 ] "normal N" [ 0 1 0 0 1 0 0 1 0 0 1 0 ] "float uv" [ 0 0 1 0 1 1 0 1 ] 
	NamedMaterial "Ceiling" 
	Shape "trianglemesh" "integer indices" [ 0 1 2 0 2 3 ] "point P" [ 1 2 1 -1 2 1 -1 2 -1 1 2 -1 ] "normal N" [ 0 -1 0 0 -1 0 0 -1 0 0 -1 0 ] "float uv" [ 0 0 1 0 1 1 0 1 ] 
	NamedMaterial "BackWall" 
	Shape "trianglemesh" "integer indices" [ 0 1 2 0 2 3 ] "point P" [ -1 0 -1 -1 2 -1 1 2 -1 1 0 -1 ] "normal N" [ 0 0 -1 0 0 -1 0 0 -1 0 0 -1 ] "float uv" [ 0 0 1 0 1 1 0 1 ]
	NamedMaterial "FrontWall" 
	Shape "trianglemesh" "integer indices" [ 0 1 2 0 2 3 ] "point P" [ -1 0 1 -1 2 1 1 2 1 1 0 1 ] "normal N" [ 0 0 1 0 0 1 0 0 1 0 0 1 ] "float uv" [ 0 0 1 0 1 1 0 1 ]
	NamedMaterial "RightWall" 
	Shape "trianglemesh" "integer indices" [ 0 1 2 0 2 3 ] "point P" [ 1 0 -1 1 2 -1 1 2 1 1 0 1 ] "normal N" [ 1 0 0 1 0 0 1 0 0 1 0 0 ] "float uv" [ 0 0 1 0 1 1 0 1 ] 
	NamedMaterial "LeftWall" 
	Shape "trianglemesh" "integer indices" [ 0 1 2 0 2 3 ] "point P" [ -1 0 1 -1 2 1 -1 2 -1 -1 0 -1 ] "normal N" [ -1 0 0 -1 0 0 -1 0 0 -1 0 0 ] "float uv" [ 0 0 1 0 1 1 0 1 ] """ \
        .format(left_rgb[0], left_rgb[1], left_rgb[2], right_rgb[0], right_rgb[1], right_rgb[2], back_rgb[0], back_rgb[1], back_rgb[2], front_rgb[0], front_rgb[1], front_rgb[2])


def put_render_in_location(path):
    if os.path.exists(path):
        os.remove(path)
    if path.endswith(".png"):
        os.rename(os.path.abspath("render.png"), path)
    else:
        os.rename(os.path.abspath("render.pfm"), path)


def generate_random_list(min, max, length):
    random_list = []
    for i in range(0, length):
        x = (random.random() * (max - min)) + min
        random_list.append(x)
    return random_list

def generate_random_xz_locations(min, max, distance, length):
    random_list = []
    for i in range(0, length):
        new_point = [(random.random() * (max - min)) + min, (random.random() * (max - min)) + min]
        while too_close_to_other_point(random_list, new_point, distance):
            new_point = [(random.random() * (max - min)) + min, (random.random() * (max - min)) + min]
        random_list.append(new_point)
    return random_list

def too_close_to_other_point(list, new_point, distance):
    for point in list:
        if (((point[0] - new_point[0]) ** 2) + ((point[1] - new_point[1]) ** 2))**0.5 < distance:
            return True
    return False


