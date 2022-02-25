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

lock = threading.Lock()

lock.acquire()
lock.acquire()
print("t")