import re
import json
from pathlib import Path


class PositionParser:

    def __init__(self):

        self.positions=[]

    def parse(self,text):

        axis=0

        for line in text.splitlines():

            a=re.search(r"Axis\s*#(\d+)",line)

            if a:

                axis=int(a.group(1))

            m=re.match(r"(\d+)\s+0:END.*?([\d\.]+)\s+([\d\.]+)",line)

            if m:

                self.positions.append({

                    "axis":axis,

                    "position_no":int(m.group(1)),

                    "position":float(m.group(2)),

                    "speed":float(m.group(3))

                })

        return self.positions

    def save(self):

        Path("database").mkdir(exist_ok=True)

        with open("database/positions.json","w") as f:

            json.dump(self.positions,f,indent=4)