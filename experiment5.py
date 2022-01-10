import os
import random
import subprocess
from termcolor import cprint
import util as u
import shutil

#EXPERIMENT 5: roterende buddha animatie zonder directe belichting map

def experiment5():


    source = "D:\\Thesis\\DeepIllumination\\dataset\\experiment5\\niks.png"

    name = 0

    while name < 45:
        shutil.copyfile(source, "dataset\\experiment5\\test\\direct\\{}.png".format(name))
        name += 1

    name = 0

    while name < 350:
        shutil.copyfile(source, "dataset\\experiment5\\train\\direct\\{}.png".format(name))
        name += 1

    name = 0

    while name < 150:
        shutil.copyfile(source, "dataset\\experiment5\\val\\direct\\{}.png".format(name))
        name += 1



experiment5()
