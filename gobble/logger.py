import simplejson as json
import _pickle as pickle

class Logger:

    def __init__(self):
        with open("log.json") as f:
            self.log = json.load(f)
