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
print(global_job_list[4:4])
