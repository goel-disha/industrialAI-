import re
import json
from pathlib import Path


class MotionParser:

    def __init__(self):
        self.motion = {}

    def parse(self, text):

        current_axis = None

        for line in text.splitlines():

            axis = re.search(r"Axis\s*#(\d+)", line)

            if axis:
                current_axis = f"Axis_{axis.group(1)}"

                if current_axis not in self.motion:
                    self.motion[current_axis] = {}

            if current_axis is None:
                continue

            p = re.match(r"(Pr\.\d+:[^0-9]+)(.+)", line)

            if p:

                key = p.group(1).strip()

                value = p.group(2).strip()

                self.motion[current_axis][key] = value

        return self.motion

    def save(self):

        Path("database").mkdir(exist_ok=True)

        with open("database/motion.json","w",encoding="utf8") as f:

            json.dump(self.motion,f,indent=4)