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

dataset_name = "sphere_in_cornell"

key = "C:\\Users\\Michi\\.ssh\\id_rsa"
password = open("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\wachtwoord.txt", 'r').read().rstrip()
hostnames = ["aalst", "aarlen", "alken", "ans", "antwerpen", "asse", "aubel", "balen", "bergen", "bevekom", "beveren",
             "bierbeek", "binche", "borgworm", "brugge", "charleroi", "chimay", "damme", "diest", "dinant", "doornik",
             "dour", "durbuy", "eeklo", "eupen", "fleurus", "geel", "genk", "gent", "gouvy", "haacht", "halle", "ham",
             "hamme", "hasselt", "hastiere", "heers", "heist", "herent", "hoei", "hove", "ieper", "kaprijke", "komen",
             "laarne", "lanaken", "libin", "libramont", "lier", "lint", "lommel", "luik", "maaseik", "malle",
             "mechelen", "moeskroen", "musson", "namen", "nijvel", "ohey", "olen", "ottignies", "overpelt", "perwez",
             "pittem", "riemst", "rixensart", "roeselare", "ronse", "schoten", "spa", "stavelot", "temse", "terhulpen",
             "tienen", "torhout", "tremelo", "turnhout", "veurne", "vielsalm", "vilvoorde", "voeren", "waterloo",
             "waver", "yvoir"]  # behalve zwalm


def upload():

    #upload pbrt files
    root = 'C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\' + dataset_name
    all_file_paths = []
    for r, d, f in os.walk(root):
        for file in f:
            all_file_paths.append(os.path.join(r, file))

    c = Connection('r0705259@zwalm.cs.kotnet.kuleuven.be',
                   connect_kwargs={"key_filename": key, "password": password},
                   gateway=Connection('r0705259@st.cs.kuleuven.be',
                                      connect_kwargs={"key_filename": key, "password": password}))
    for path in all_file_paths:
        c.put(path, "/home/r0705259/Thesis/" + dataset_name + path.replace(root, "").replace("\\", "/"))
    c.close()


    # maak id voor alle taken
    global_job_list = []
    for path in all_file_paths:
        global_job_list.append(path.replace(".pbrt", "").replace(root, "").replace("\\", "_"))




def main():


    # bepaal verdeling van taken over hosts
    amount_of_renders = len(global_job_list)
    amount_of_hosts = len(hostnames)
    if amount_of_renders < amount_of_hosts:
        renders_per_host = 1
    else:
        renders_per_host = floor(amount_of_renders / amount_of_hosts)
    remainder = amount_of_renders % amount_of_hosts

    # start rendering threads
    last_job_for_this_host = -1
    for i in range(0, amount_of_hosts):
        first_job_for_this_host = last_job_for_this_host + 1
        if i < remainder:
            last_job_for_this_host = first_job_for_this_host + renders_per_host
        else:
            last_job_for_this_host = first_job_for_this_host + renders_per_host - 1
        ConnectionThread(hostnames[i], global_job_list[first_job_for_this_host:last_job_for_this_host + 1]).start()
        time.sleep(0.05)

    print("Exiting Main Thread")


class ConnectionThread(threading.Thread):
    def __init__(self, hostname, job_list):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.job_list = job_list

    def run(self):
        print("Starting " + self.hostname)
        c = Connection('r0705259@' + self.hostname + '.cs.kotnet.kuleuven.be',
                       connect_kwargs={"key_filename": key, "password": password, "banner_timeout": 60000},
                       gateway=Connection('r0705259@st.cs.kuleuven.be',
                                          connect_kwargs={"key_filename": key, "password": password}))
        for job in self.job_list:
            with c.cd("/home/r0705259/Thesis/pbrt-v3/build"):
                c.run("./pbrt /home/r0705259/Thesis/scenefiles/" + dataset_name + job.replace("_", "/")
                      + ".pbrt --quiet --outfile /home/r0705259/Thesis/trainingdata" + job.replace("_", "/") + ".png")
        c.close()
        print("Exiting " + self.hostname)


upload()

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
