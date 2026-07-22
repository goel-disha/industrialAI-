import re
import json
from pathlib import Path


class ProgramParser:

    def __init__(self):

        self.programs=[]

    def parse(self,text):

        for line in text.splitlines():

            m=re.match(r"(AUTO|HOME|MAIN|SERVO|MANUAL|OUTPUT)",line.strip())

            if m:

                self.programs.append(m.group(1))

        return self.programs

    def save(self):

        Path("database").mkdir(exist_ok=True)

        with open("database/programs.json","w") as f:

            json.dump(self.programs,f,indent=4)