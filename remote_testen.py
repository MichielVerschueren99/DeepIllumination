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
input_remote_dir = "/home/r0705259/Thesis/scenefiles"
output_remote_dir = "/home/r0705259/Thesis/trainingdata"
pbrt_remote_dir = "/home/r0705259/Thesis/pbrt-v3/build"

class ConnectionThread(threading.Thread):
    def __init__(self, hostname):
        threading.Thread.__init__(self)
        self.hostname = hostname

    def run(self):

        print("Starting " + self.hostname)

        #open connectie
        c = Connection('r0705259@' + self.hostname + '.cs.kotnet.kuleuven.be',
                       connect_kwargs={"key_filename": key, "password": password, "banner_timeout": 60000},
                       gateway=Connection('r0705259@st.cs.kuleuven.be',
                                          connect_kwargs={"key_filename": key, "password": password}))

        # vind job, draai pbrt en verwijder .pbrt file
        while True:
            unfinished_job_list_lock.acquire()

            if not unfinished_job_list:
                break

            job = unfinished_job_list[0]

            #job_available = c.run("(ls " + input_remote_dir + "/" + job + ".pbrt >> /dev/null 2>&1 && echo yes) || echo no", hide='out').stdout

            if job in c.run("ls " + input_remote_dir, hide='out').stdout:
                print("ja")
                unfinished_job_list.remove(job)
                unfinished_job_list_lock.release()
                with c.cd(pbrt_remote_dir):
                    c.run("./pbrt " + input_remote_dir + "/" + job + ".pbrt --quiet --outfile " + output_remote_dir + "/" + job + ".png")
                with c.cd(input_remote_dir):
                    c.run("rm " + job + ".pbrt")
            else:
                print("nee")
                unfinished_job_list_lock.release()

        #sluit connectie
        c.close()
        print("Exiting " + self.hostname)


if __name__ == "__main__":

    print("Starting Main (zwalm)")

    # zoek alle .pbrt files
    root = 'C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\' + dataset_name
    all_file_paths = []
    for r, d, f in os.walk(root):
        for file in f:
            all_file_paths.append(os.path.join(r, file))

    # maak id voor alle taken
    job_list = []
    for local_path in all_file_paths:
        job_list.append(local_path.replace(".pbrt", "").replace(root + "\\", "").replace("\\", "_"))
    random.shuffle(job_list)

    # zwalm voor download en upload
    up_down_c = Connection('r0705259@' + 'zwalm.cs.kotnet.kuleuven.be',
                           connect_kwargs={"key_filename": key, "password": password, "banner_timeout": 60000},
                           gateway=Connection('r0705259@st.cs.kuleuven.be',
                                              connect_kwargs={"key_filename": key, "password": password}))

    # bepaal verdeling van taken over hosts
    amount_of_renders = len(job_list)
    amount_of_hosts = len(hostnames)

    #verwijder inhoud van scenefiles en trainingdata directories
    up_down_c.run("rm -rf /home/r0705259/Thesis/trainingdata && mkdir /home/r0705259/Thesis/trainingdata")
    up_down_c.run("rm -rf /home/r0705259/Thesis/scenefiles && mkdir /home/r0705259/Thesis/scenefiles")

    # start rendering threads
    unfinished_job_list = job_list.copy()
    unfinished_job_list_lock = threading.Lock()
    for i in range(0, amount_of_hosts):
        ConnectionThread(hostnames[i]).start()
        time.sleep(0.1)

    # upload .pbrt files
    progress_counter = 0
    for j in job_list:
        input_local_path = 'C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\' + dataset_name + "\\" + j + ".pbrt"
        up_down_c.put(input_local_path, input_remote_dir)
        progress_counter += 1
        print("{}/{} scenefiles uploaded".format(progress_counter, amount_of_renders))

    # download renders en verwijder remote kopie
    progress_counter = 0
    while progress_counter < amount_of_renders:
        with up_down_c.cd("/home/r0705259/Thesis/trainingdata"):
            finished_renders = up_down_c.run("ls", hide='out').stdout.splitlines()
        for render in finished_renders:
            output_local_dir = 'C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\' + dataset_name + "\\" + render.replace(
                "_", "\\") + ".png"
            up_down_c.get(output_remote_dir + "/" + render, output_local_dir)
            progress_counter += 1
            with up_down_c.cd("/home/r0705259/Thesis/trainingdata"):
                up_down_c.run("rm " + render)

            print("{}/{} renders completed".format(progress_counter, amount_of_renders))

    #sluit connectie
    up_down_c.close()
    print("Exiting Main (zwalm)")

