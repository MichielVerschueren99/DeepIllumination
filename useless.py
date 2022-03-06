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

global_job_list = ['train_direct_0', 'train_direct_1', 'train_direct_2', 'train_gt_0', 'train_gt_1', 'train_gt_2']
camera_position = u.generate_random_list(-0.9, 0.9, 3)
camera_position[1] = 1.2

print(camera_position)