import re
import json
from pathlib import Path


class StatementParser:

    def __init__(self):

        self.steps=[]

    def parse(self,text):

        for line in text.splitlines():

            m=re.match(r"(\d+)(.+)",line)

            if m:

                self.steps.append({

                    "step":int(m.group(1)),

                    "statement":m.group(2).strip()

                })

        return self.steps

    def save(self):

        Path("database").mkdir(exist_ok=True)

        with open("database/statements.json","w") as f:

            json.dump(self.steps,f,indent=4)