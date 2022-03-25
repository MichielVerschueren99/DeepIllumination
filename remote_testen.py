import os
import random
from math import floor
import threading
from fabric import *
import time
import zipfile
import shutil

dataset_name = "primitive_room_2"

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
             "waver", "zwalm"]
# behalve yvoir
input_remote_dir = "/home/r0705259/Thesis/scenefiles"
output_remote_dir = "/home/r0705259/Thesis/trainingdata"
pbrt_remote_dir = "/home/r0705259/Thesis/PBRTmod/build"

max_batch_size = 8000

class ConnectionThread(threading.Thread):
    def __init__(self, hostname, job_list):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.job_list = job_list
        self.done = False

    def run(self):

        print("starting " + self.hostname + "...")

        try:
            # open connectie
            c = Connection('r0705259@' + self.hostname + '.cs.kotnet.kuleuven.be',
                           connect_kwargs={"key_filename": key, "password": password, "banner_timeout": 60000},
                           gateway=Connection('r0705259@st.cs.kuleuven.be',
                                              connect_kwargs={"key_filename": key, "password": password}))

            run_command = "cd " + pbrt_remote_dir + "; "
            for current_job in self.job_list:
                run_command += "./pbrt " + input_remote_dir + "/" + current_job + ".pbrt --quiet; "
                run_command += "mv " + current_job + ".exr " + output_remote_dir + "/" + current_job + ".exr; "
            c.run(run_command)

            # sluit connectie
            c.close()
        except:
            print("{} failed, assigned renders were: {}".format(self.hostname, self.job_list))

        print("exiting " + self.hostname + "...")


if __name__ == "__main__":

    print("starting main (yvoir)...")

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
        global_job_list_per_buffer.append(list(filter(lambda k: buffer == k[k.index('_') + 1:k.rindex('_')], global_job_list)))

    # check dat we voor alle buffers evenveel samples hebben
    for i in global_job_list_per_buffer:
        assert (len(i) == len(global_job_list_per_buffer[0]))

    # maak lijst die bufferlijst sorteerd per batch
    global_job_list_per_batch_per_buffer = []
    total_samples = len(global_job_list_per_buffer[0])
    max_batch_samples = max_batch_size // len(global_job_list_per_buffer)
    lowerbound = 0
    upperbound = max_batch_samples - 1
    while True:
        if upperbound >= total_samples - 1:
            new_batch = []
            for i in global_job_list_per_buffer:
                new_batch.append(i[lowerbound:])
            global_job_list_per_batch_per_buffer.append(new_batch)
            break
        else:
            new_batch = []
            for i in global_job_list_per_buffer:
                new_batch.append(i[lowerbound:upperbound+1])
            global_job_list_per_batch_per_buffer.append(new_batch)
            lowerbound = upperbound + 1
            upperbound = upperbound + max_batch_samples

    # yvoir voor download en upload
    up_down_c = Connection('r0705259@' + 'yvoir.cs.kotnet.kuleuven.be',
                           connect_kwargs={"key_filename": key, "password": password, "banner_timeout": 60000},
                           gateway=Connection('r0705259@st.cs.kuleuven.be',
                                              connect_kwargs={"key_filename": key, "password": password}))

    # verwijder inhoud van scenefiles en trainingdata directories
    up_down_c.run("rm -r /home/r0705259/Thesis/trainingdata && mkdir /home/r0705259/Thesis/trainingdata")
    up_down_c.run("rm -r /home/r0705259/Thesis/scenefiles && mkdir /home/r0705259/Thesis/scenefiles")

    # upload .pbrt files
    print("zipping scenefiles...")
    shutil.make_archive("scenefiles", 'zip',
                        'C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\' + dataset_name)
    print("uploading scenefiles...")
    up_down_c.put("scenefiles.zip", input_remote_dir)
    os.remove("scenefiles.zip")
    with up_down_c.cd("/home/r0705259/Thesis/scenefiles"):
        up_down_c.run("unzip -q scenefiles.zip && rm scenefiles.zip")
    print("scenefiles uploaded")

    #verwerk elke batch om de beurt
    batch_counter = 0
    amount_done_old = 0
    total_batch_amount = len(global_job_list_per_batch_per_buffer)
    print("{} batches".format(total_batch_amount))
    for batch_job_list_per_buffer in global_job_list_per_batch_per_buffer:

        # bepaal verdeling van taken over hosts
        amount_of_samples = len(batch_job_list_per_buffer[0])
        amount_of_hosts = len(hostnames)
        if amount_of_samples < amount_of_hosts:
            samples_per_host = 0  # zonder remainder samples
        else:
            samples_per_host = floor(amount_of_samples / amount_of_hosts)
        remainder = amount_of_samples % amount_of_hosts

        # start rendering threads
        threads = []
        last_job_id_for_this_host = -1
        for i in range(0, amount_of_hosts):
            first_job_id_for_this_host = last_job_id_for_this_host + 1
            if i < remainder:
                last_job_id_for_this_host = first_job_id_for_this_host + samples_per_host
            else:
                last_job_id_for_this_host = first_job_id_for_this_host + samples_per_host - 1

            jobs_for_this_host = []
            for b_list in batch_job_list_per_buffer:
                if last_job_id_for_this_host == first_job_id_for_this_host:
                    jobs_for_this_host.append(b_list[first_job_id_for_this_host])
                else:
                    jobs_for_this_host += b_list[first_job_id_for_this_host:last_job_id_for_this_host + 1]
            random.shuffle(jobs_for_this_host)
            if jobs_for_this_host:
                t = ConnectionThread(hostnames[i], jobs_for_this_host)
                threads.append(t)
                t.start()
            time.sleep(0.2)

        #dit is gewoon om te kijken hoeveel er al klaar is
        while threads:
            with up_down_c.cd("/home/r0705259/Thesis/trainingdata"):
                amount_done = up_down_c.run("ls -1 | wc -l", hide='out').stdout
                amount_done = int(amount_done[:-1])
            print("{}/{} renders completed".format(amount_done_old + amount_done, len(global_job_list)))
            time.sleep(10)
            for t in threads:
                if not t.is_alive():
                    t.done = True
            threads = [t for t in threads if not t.done]


        #download en extract de batch
        with up_down_c.cd("/home/r0705259/Thesis"):
            print("downloading batch...")
            up_down_c.run("zip -9 -y -r -q /tmp/batch.zip trainingdata/", hide='out')
            up_down_c.get("/tmp/batch.zip", 'C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\')
            print("batch downloaded")
            up_down_c.run("rm -rf /tmp/batch.zip")
            up_down_c.run("rm -rf /home/r0705259/Thesis/trainingdata && mkdir /home/r0705259/Thesis/trainingdata")

        print("unzipping batch...")
        with zipfile.ZipFile("C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\batch.zip", 'r') as zip_ref:
            zip_ref.extractall("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\temp")  # TODO andere map?
        os.remove("C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\batch.zip")
        for render in os.listdir("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\temp\\trainingdata"):

            output_local_dir = 'C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\dataset\\' + dataset_name + "\\" + render.replace(
                "_", "\\")
            if os.path.exists(output_local_dir):
                os.remove(output_local_dir)
            os.rename("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\temp\\trainingdata\\" + render, output_local_dir)

        batch_counter += 1
        amount_done_old += len(global_job_list_per_buffer) * len(batch_job_list_per_buffer[0])
        print("batch {}/{} done".format(batch_counter, total_batch_amount))

    # verwijder inhoud van scenefiles directory
    up_down_c.run("rm -rf /home/r0705259/Thesis/scenefiles && mkdir /home/r0705259/Thesis/scenefiles")

    # sluit connectie
    up_down_c.close()


    print("exiting main (yvoir)...")
