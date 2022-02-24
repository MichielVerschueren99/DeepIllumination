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

key = "C:\\Users\\Michi\\.ssh\\id_rsa"
password = open("C:\\Users\\Michi\\Documents\\school\\Thesis-stuff\\wachtwoord.txt", 'r').read().rstrip()

# zwalm voor download en upload
up_down_c = Connection('r0705259@' + 'zwalm.cs.kotnet.kuleuven.be',
                       connect_kwargs={"key_filename": key, "password": password, "banner_timeout": 60000},
                       gateway=Connection('r0705259@st.cs.kuleuven.be',
                                          connect_kwargs={"key_filename": key, "password": password}))

job_available = up_down_c.run("(ls result.txt >> /dev/null 2>&1 && echo yes) || echo no", hide='out').stdout

if job_available == 'yes\n':
    print("joepie")

up_down_c.close()
