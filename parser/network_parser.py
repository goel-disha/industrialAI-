import json
from pathlib import Path


class NetworkParser:

    def __init__(self):

        self.lines=[]

    def parse(self,text):

        for line in text.splitlines():

            if len(line.strip())>2:

                self.lines.append(line.strip())

        return self.lines

    def save(self):

        Path("database").mkdir(exist_ok=True)

        with open("database/network.json","w") as f:

            json.dump(self.lines,f,indent=4)