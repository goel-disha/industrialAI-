import re
import json
from pathlib import Path


class TimerParser:

    def __init__(self):

        self.timers=[]

    def parse(self,text):

        for line in text.splitlines():

            m=re.search(r"(T\d+)\s+([DK]\d+)",line)

            if m:

                self.timers.append({

                    "timer":m.group(1),

                    "preset":m.group(2)

                })

        return self.timers

    def save(self):

        Path("database").mkdir(exist_ok=True)

        with open("database/timers.json","w") as f:

            json.dump(self.timers,f,indent=4)