import os
import random
import subprocess
from math import floor

from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
from termcolor import cprint
import util as u
import threading
from fabric import *
import time

import shutil


for i in range(0, 500):
    shutil.copyfile("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\test3.pfm", "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\primitive_room_no_normal\\val\\normal\\" + str(i) + ".pfm")
