import sys
import os

parent_dir = os.path.dirname(os.path.dirname(__file__))

if parent_dir not in sys.path:
    sys.path.append(parent_dir)