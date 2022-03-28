import imageio
import numpy as np
import OpenEXR as exr
import Imath
import torch
import util




A_mean = torch.full((3, 10, 10), 1.0)
B_mean = torch.full((3, 10, 10), 3.0)
C = torch.cat((A_mean, B_mean))


D2 = C[-4:]

tt = [1, 2, 3]

t = [x / 2 for x in tt]

direct = util.load_image("D:\\Thesis\\DeepIllumination\\dataset\\primitive_room_2\\test\\direct\\0.exr")
indirect = util.load_image("D:\\Thesis\\DeepIllumination\\dataset\\primitive_room_2\\test\\indirect\\0.exr")

full = torch.add(direct, indirect)

util.save_image(full, "D:\\Thesis\\test.exr")

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
