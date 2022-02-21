import os
import random
import subprocess
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
from termcolor import cprint
import util as u
from fabric import Connection


key = "C:\\Users\\Michi\\.ssh\\id_rsa"
password = open("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\wachtwoord.txt", 'r').read().rstrip()


# c = Connection('r0705259@dinant.cs.kotnet.kuleuven.be',
#                connect_kwargs={"key_filename" : key, "password" : password},
#                gateway=Connection('r0705259@st.cs.kuleuven.be',
#                                   connect_kwargs={"key_filename" : key, "password" : password}))\
#     .run('ls', hide=True)
# print(c)

c = Connection('r0705259@dinant.cs.kotnet.kuleuven.be',
               connect_kwargs={"key_filename": key, "password": password},
               gateway=Connection('r0705259@st.cs.kuleuven.be',
                                  connect_kwargs={"key_filename": key, "password": password}))
c.put("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\scene.pbrt", "/home/r0705259")
with c.cd("/home/r0705259/Thesis/pbrt-v3/build"):
    c.run("./pbrt /home/r0705259/scene.pbrt")
c.get("/home/r0705259/Thesis/pbrt-v3/build/cornell-box.png")
c.close()

