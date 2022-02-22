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


c = Connection('r0705259@zwalm.cs.kotnet.kuleuven.be',
                   connect_kwargs={"key_filename": key, "password": password},
                   gateway=Connection('r0705259@st.cs.kuleuven.be',
                                      connect_kwargs={"key_filename": key, "password": password}))
    c.put("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\scene.pbrt", "/home/r0705259")
    with c.cd("/home/r0705259/Thesis/pbrt-v3/build"):
        c.run("./pbrt /home/r0705259/scene.pbrt")
    c.get("/home/r0705259/Thesis/pbrt-v3/build/cornell-box.png")
    c.close()