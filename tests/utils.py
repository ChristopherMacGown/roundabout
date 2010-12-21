import os
from roundabout.config import Config

def testdata(filename):
    return os.path.join(os.path.dirname(__file__), "data", filename)

def reset_config():
    # Reset config
    Config.__shared_state__.clear()
