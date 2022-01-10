import os
import random
import subprocess
from termcolor import cprint
import util as u
import shutil

#EXPERIMENT 3: roterende buddha animatie zonder depth map

def experiment3():


    source = "D:\\Thesis\\DeepIllumination\\dataset\\experiment3\\niks.pfm"

    name = 0

    while name < 45:
        shutil.copyfile(source, "dataset\\experiment3\\test\\depth\\{}.pfm".format(name))
        name += 1

    name = 0

    while name < 350:
        shutil.copyfile(source, "dataset\\experiment3\\train\\depth\\{}.pfm".format(name))
        name += 1

    name = 0

    while name < 150:
        shutil.copyfile(source, "dataset\\experiment3\\val\\depth\\{}.pfm".format(name))
        name += 1



experiment3()
