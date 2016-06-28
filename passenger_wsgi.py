import os
import sys

sys.path.append(os.getcwd())
from app import app as application
from client import start_client

start_client(in_background=True)