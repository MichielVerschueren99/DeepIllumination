
import shutil


for i in range(0, 500):
    shutil.copyfile("D:\\Thesis\\niks.exr", "D:\\Thesis\\DeepIllumination\\dataset\\primitive_room_2_no_depth_no_normal\\val\\normal\\" + str(i) + ".exr")
