import imageio
import numpy as np
import OpenEXR as exr
import Imath
import torch
import util

_np_to_exr = {
    np.float16: Imath.PixelType.HALF,
    np.float32: Imath.PixelType.FLOAT,
    np.uint32: Imath.PixelType.UINT,
}


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
    # img = np.where(img < 0.0, 0.0, np.where(img > 1.0, 1, img))

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


def write_exr(filename, values):
    """Writes the values in a multi-channel ndarray into an EXR file.
  Args:
    filename: The filename of the output file
    values: A numpy ndarray with shape [height, width, channels]
    channel_names: A list of strings with length = channels
  Raises:
    TypeError: If the numpy array has an unsupported type.
    ValueError: If the length of the array and the length of the channel names
      list do not match.
  """
    channel_names = ['R', 'G', 'B']

    if values.shape[-1] != len(channel_names):
        raise ValueError(
            'Number of channels in values does not match channel names (%d, %d)' %
            (values.shape[-1], len(channel_names)))
    header = exr.Header(values.shape[1], values.shape[0])
    try:
        exr_channel_type = Imath.PixelType(Imath.PixelType.HALF)
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


lijst = []

# lijst.append(readEXR("C:\\Users\\Michi\\Documents\\school\\0.exr"))
# lijst.append(readEXR("C:\\Users\\Michi\\Documents\\school\\1.exr"))

lijst.append(torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]))
lijst.append(torch.tensor([[0.0, -2.0, 334.0], [4, 25.0, 63.0]]))

som = torch.stack(lijst)
mean = torch.mean(som)
std = torch.std(som)

som.add_(-mean).mul_(1.0 / std)
A_mean = torch.full((3, 10, 10), 1.0)
B_mean = torch.full((3, 10, 10), 3.0)
C = torch.cat((A_mean, B_mean))


D2 = C[-4:]

tt = [1, 2, 3]

t = [x / 2 for x in tt]

# albedo1 = torch.full((3, 256, 256), 1.0)
# util.save_image(albedo1, "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\nm_test\\train\\albedo\\0.exr")
# albedo2 = torch.full((3, 256, 256), 3.0)
# util.save_image(albedo2, "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\nm_test\\train\\albedo\\1.exr")
# direct1 = torch.full((3, 256, 256), 10.0)
# util.save_image(direct1, "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\nm_test\\train\\direct\\0.exr")
# direct2 = torch.full((3, 256, 256), 14.0)
# util.save_image(direct2, "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\nm_test\\train\\direct\\1.exr")
# normal1 = torch.full((3, 256, 256), 19.0)
# util.save_image(normal1, "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\nm_test\\train\\normal\\0.exr")
# normal2 = torch.full((3, 256, 256), 25.0)
# util.save_image(normal2, "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\nm_test\\train\\normal\\1.exr")
# depth1 = torch.full((3, 256, 256), 28.0)
# util.save_image(depth1, "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\nm_test\\train\\depth\\0.exr")
# depth2 = torch.full((3, 256, 256), 36.0)
# util.save_image(depth2, "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\nm_test\\train\\depth\\1.exr")
# gt1 = torch.full((3, 256, 256), 37.0)
# util.save_image(gt1, "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\nm_test\\train\\gt\\0.exr")
# gt2 = torch.full((3, 256, 256), 47.0)
# util.save_image(gt2, "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\nm_test\\train\\gt\\1.exr")
print("test")
