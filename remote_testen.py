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
             "dour", "durbuy", "eeklo", "eupen", "fleurus", "genk", "gent", "gouvy", "haacht", "halle", "ham",
             "hamme", "hasselt", "hastiere", "heers", "heist", "herent", "hoei", "hove", "ieper", "kaprijke", "komen",
             "laarne", "lanaken", "libin", "libramont", "lier", "lint", "lommel", "luik", "maaseik", "malle",
             "mechelen", "moeskroen", "musson", "namen", "nijvel", "ohey", "olen", "ottignies", "overpelt", "perwez",
             "pittem", "riemst", "rixensart", "roeselare", "ronse", "schoten", "spa", "stavelot", "temse", "terhulpen",
             "tienen", "torhout", "tremelo", "turnhout", "veurne", "vielsalm", "vilvoorde", "voeren", "waterloo",
             "waver", "yvoir"]  # behalve zwalm
                                # geel is down
input_remote_dir = "/home/r0705259/Thesis/scenefiles"
output_remote_dir = "/home/r0705259/Thesis/trainingdata"
pbrt_remote_dir = "/home/r0705259/Thesis/PBRTmod/build"

class ConnectionThread(threading.Thread):
    def __init__(self, hostname, job_list):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.job_list = job_list

    def run(self):

        print("Starting " + self.hostname)

        #open connectie
        c = Connection('r0705259@' + self.hostname + '.cs.kotnet.kuleuven.be',
                       connect_kwargs={"key_filename": key, "password": password, "banner_timeout": 60000},
                       gateway=Connection('r0705259@st.cs.kuleuven.be',
                                          connect_kwargs={"key_filename": key, "password": password}))

        #draai pbrt
        run_command = "./pbrt "
        for current_job in self.job_list:
            run_command += input_remote_dir + "/" + current_job + ".pbrt "
        run_command += " --quiet"
        with c.cd(pbrt_remote_dir):
            c.run(run_command)

        # run_command = "cd" + pbrt_remote_dir + "; "
        # for current_job in self.job_list:
        #     run_command += "./pbrt " + input_remote_dir + "/" + current_job + ".pbrt --quiet "
        # c.run(run_command)

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
    global_job_list = []
    for local_path in all_file_paths:
        global_job_list.append(local_path.replace(".pbrt", "").replace(root + "\\", "").replace("\\", "_"))
    random.shuffle(global_job_list)

    # maak lijst die taken sorteerd per buffer
    buffers = []
    for job in global_job_list:
        buffer = job[job.index('_') + 1:job.rindex('_')]
        if buffer not in buffers:
            buffers.append(buffer)
    global_job_list_per_buffer = []
    for buffer in buffers:
        global_job_list_per_buffer.append(list(filter(lambda k: buffer in k, global_job_list)))

    # check dat we voor alle buffers evenveel samples hebben
    for i in global_job_list_per_buffer:
        assert (len(i) == len(global_job_list_per_buffer[0]))

    # zwalm voor download en upload
    up_down_c = Connection('r0705259@' + 'zwalm.cs.kotnet.kuleuven.be',
                           connect_kwargs={"key_filename": key, "password": password, "banner_timeout": 60000},
                           gateway=Connection('r0705259@st.cs.kuleuven.be',
                                              connect_kwargs={"key_filename": key, "password": password}))

    # bepaal verdeling van taken over hosts
    amount_of_samples = len(global_job_list_per_buffer[0])
    amount_of_hosts = len(hostnames)
    if amount_of_samples < amount_of_hosts:
        samples_per_host = 0  # zonder remainder samples
    else:
        samples_per_host = floor(amount_of_samples / amount_of_hosts)
    remainder = amount_of_samples % amount_of_hosts

    #verwijder inhoud van scenefiles en trainingdata directories
    up_down_c.run("rm -rf /home/r0705259/Thesis/trainingdata && mkdir /home/r0705259/Thesis/trainingdata")
    up_down_c.run("rm -rf /home/r0705259/Thesis/scenefiles && mkdir /home/r0705259/Thesis/scenefiles")

    # upload .pbrt files
    progress_counter = 0
    for j in global_job_list:
        input_local_path = 'C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\' + dataset_name + "\\" + j + ".pbrt"
        up_down_c.put(input_local_path, input_remote_dir)
        progress_counter += 1
        print("{}/{} scenefiles uploaded".format(progress_counter, len(global_job_list)))

    # start rendering threads
    last_job_id_for_this_host = -1
    for i in range(0, amount_of_hosts):
        first_job_id_for_this_host = last_job_id_for_this_host + 1
        if i < remainder:
            last_job_id_for_this_host = first_job_id_for_this_host + samples_per_host
        else:
            last_job_id_for_this_host = first_job_id_for_this_host + samples_per_host - 1

        jobs_for_this_host = []
        for b_list in global_job_list_per_buffer:
            if last_job_id_for_this_host == first_job_id_for_this_host:
                jobs_for_this_host.append(b_list[first_job_id_for_this_host])
            else:
                jobs_for_this_host += b_list[first_job_id_for_this_host:last_job_id_for_this_host + 1]
        random.shuffle(jobs_for_this_host)
        if jobs_for_this_host:
            ConnectionThread(hostnames[i], jobs_for_this_host).start()
        time.sleep(0.2)

    # download renders en verwijder remote kopie
    progress_counter = 0
    while progress_counter < len(global_job_list):
        time.sleep(5)
        with up_down_c.cd("/home/r0705259/Thesis/trainingdata"):
            finished_renders = up_down_c.run("ls", hide='out').stdout.splitlines()
        for render in finished_renders:
            output_local_dir = 'C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\' + dataset_name + "\\" + render.replace(
                "_", "\\")
            up_down_c.get(output_remote_dir + "/" + render, output_local_dir)
            progress_counter += 1
            with up_down_c.cd("/home/r0705259/Thesis/trainingdata"):
                up_down_c.run("rm " + render)

            print("{}/{} renders completed".format(progress_counter, len(global_job_list)))


    # verwijder inhoud van scenefiles en trainingdata directories
    up_down_c.run("rm -rf /home/r0705259/Thesis/trainingdata && mkdir /home/r0705259/Thesis/trainingdata")
    up_down_c.run("rm -rf /home/r0705259/Thesis/scenefiles && mkdir /home/r0705259/Thesis/scenefiles")

    #sluit connectie
    up_down_c.close()
    print("Exiting Main (zwalm)")

