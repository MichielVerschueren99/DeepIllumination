import shutil


def overwrite(buffername):
    for i in range(0, 30):
        shutil.copyfile("D:\\Thesis\\niks.exr", "D:\\Thesis\\DeepIllumination\\dataset\\primitive_room_ff_no_" + buffername + "\\test\\" + buffername + "\\" + str(i) + ".exr")

    for i in range(0, 500):
        shutil.copyfile("D:\\Thesis\\niks.exr", "D:\\Thesis\\DeepIllumination\\dataset\\primitive_room_ff_no_" + buffername + "\\val\\" + buffername + "\\" + str(i) + ".exr")

    for i in range(0, 2000):
        shutil.copyfile("D:\\Thesis\\niks.exr", "D:\\Thesis\\DeepIllumination\\dataset\\primitive_room_ff_no_" + buffername + "\\train\\" + buffername + "\\" + str(i) + ".exr")


overwrite("albedo")
overwrite("depth")
overwrite("direct")
overwrite("normal")