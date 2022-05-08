import math
import shutil
import os

dataset_name = "primitive_room_ffextra"
source_dataset_name = "primitive_room_ff"
new_buffers = ["normal2p0t0", "normal2p0t45", "normal2p90t45", "normal2p180t45", "normal2p270t45"]

phi_list = [0, 0, 90, 180, 270]
theta_list = [0, 45, 45, 45, 45]

def replace_text(file_name, original, replacement):
    f = open(file_name, 'r')
    filedata = f.read()
    f.close()
    newdata = filedata.replace(original, replacement)
    f = open(file_name, 'w')
    f.write(newdata)
    f.close()


if not os.path.exists("scenefiles"):
    os.mkdir("scenefiles")
if not os.path.exists(os.path.join("scenefiles", dataset_name)):
    os.mkdir(os.path.join("scenefiles", dataset_name))

for b in range(0, len(new_buffers)):

    buffer = new_buffers[b]
    phi = phi_list[b]
    theta = theta_list[b]

    if not os.path.exists(os.path.join("folders", buffer)):
        os.mkdir(os.path.join("folders", buffer))


    for data_type in ["test", "train", "val"]:

        amount = 0

        if data_type == "test":
            amount = 30
        if data_type == "train":
            amount = 2000
        if data_type == "val":
            amount = 500

        for i in range(0, amount):
            source = "scenefiles/{}/{}_albedo_{}.pbrt".format(source_dataset_name, data_type, str(i))
            new = "scenefiles/{}/{}_{}_{}.pbrt".format(dataset_name, data_type, buffer, str(i))
            shutil.copyfile(source, new)
            replace_text(new, 'Integrator "albedo"', 'Integrator "normal2" "float phi" [ {} ] "float theta" [ {} ]'.format(phi, theta))
            replace_text(new, '"string filename" [ "{}_albedo_{}.exr" ]'.format(data_type, str(i)), '"string filename" [ "{}_{}_{}.exr" ]'.format(data_type, buffer, str(i)))
    print("buffer done")