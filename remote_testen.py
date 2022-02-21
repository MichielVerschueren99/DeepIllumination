import os
import random
import subprocess
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
from termcolor import cprint
import util as u
import threading
from fabric import *

key = "C:\\Users\\Michi\\.ssh\\id_rsa"
password = open("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\wachtwoord.txt", 'r').read().rstrip()
hostnames = ["aalst", "aarlen", "alken", "ans", "antwerpen", "asse", "aubel", "balen", "bergen", "bevekom", "beveren",
             "bierbeek", "binche", "borgworm", "brugge", "charleroi", "chimay", "damme", "diest", "dinant", "doornik",
             "dour", "durbuy", "eeklo", "eupen", "fleurus", "geel", "genk", "gent", "gouvy", "haacht", "halle", "ham",
             "hamme", "hasselt", "hastiere", "heers", "heist", "herent", "hoei", "hove", "ieper", "kaprijke", "komen",
             "laarne", "lanaken", "libin", "libramont", "lier", "lint", "lommel", "luik", "maaseik", "malle",
             "mechelen", "moeskroen", "musson", "namen", "nijvel", "ohey", "olen", "ottignies", "overpelt", "perwez",
             "pittem", "riemst", "rixensart", "roeselare", "ronse", "schoten", "spa", "stavelot", "temse", "terhulpen",
             "tienen", "torhout", "tremelo", "turnhout", "veurne", "vielsalm", "vilvoorde", "voeren", "waterloo", "waver",
             "yvoir", "zwalm"]

class ConnectionThread(threading.Thread):
    def __init__(self, hostname, samplename):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.samplename = samplename

    def run(self):
        print("Starting " + self.hostname)
        c = Connection('r0705259@' + self.hostname + '.cs.kotnet.kuleuven.be',
                       connect_kwargs={"key_filename": key, "password": password, "banner_timeout": 60000},
                       gateway=Connection('r0705259@st.cs.kuleuven.be',
                                          connect_kwargs={"key_filename": key, "password": password}))
        with c.cd("/home/r0705259/Thesis/pbrt-v3/build"):
            c.run("./pbrt /home/r0705259/Thesis/scenefiles/gt/" + self.samplename + ".pbrt --outfile /home/r0705259/Thesis/trainingdata/")
        c.close()
        print("Exiting " + self.hostname)


for i in range(0, 86):
    ConnectionThread(hostnames[i], str(i)).start()

print("Exiting Main Thread")

# c = Connection('r0705259@dinant.cs.kotnet.kuleuven.be',
#                connect_kwargs={"key_filename": key, "password": password},
#                gateway=Connection('r0705259@st.cs.kuleuven.be',
#                                   connect_kwargs={"key_filename": key, "password": password}))
# c.put("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\scene.pbrt", "/home/r0705259")
# with c.cd("/home/r0705259/Thesis/pbrt-v3/build"):
#     c.run("./pbrt /home/r0705259/scene.pbrt")
# c.get("/home/r0705259/Thesis/pbrt-v3/build/cornell-box.png")
# c.close()

# c1 = Connection('r0705259@dinant.cs.kotnet.kuleuven.be',
#                 connect_kwargs={"key_filename": key, "password": password},
#                 gateway=Connection('r0705259@st.cs.kuleuven.be',
#                                    connect_kwargs={"key_filename": key, "password": password}))
#
# c2 = Connection('r0705259@aalst.cs.kotnet.kuleuven.be',
#                 connect_kwargs={"key_filename": key, "password": password},
#                 gateway=Connection('r0705259@st.cs.kuleuven.be',
#                                    connect_kwargs={"key_filename": key, "password": password}))
