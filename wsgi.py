# wsgi.py
import sys
import os

path = '/home/tonusername/cedar-o-backend'
if path not in sys.path:
    sys.path.append(path)

from app import app as application