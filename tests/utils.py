import os
from roundabout.config import Config

def testdata(filename):
    return os.path.join(os.path.dirname(__file__), "data", filename)
