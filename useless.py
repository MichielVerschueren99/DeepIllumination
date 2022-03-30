import imageio
import numpy as np
import OpenEXR as exr
import Imath
import torch
import util

a = [1 , 2]
b = [3, 4]

c = a + b

z = torch.Tensor([[1, 2]])
y = torch.Tensor([[2, 5]])
lijst = [z, y]
x = torch.Tensor([[3, 8]])

bb = torch.cat(lijst + [x], 1)

print("test")
