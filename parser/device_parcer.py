import re
import json
from pathlib import Path


class DeviceParser:

    def __init__(self):

        self.devices = []

    def parse(self, text: str):

        pattern = re.compile(
            r"\b([MDXYLTSCR]\d+)\s+([A-Za-z0-9_./#() -]+)"
        )

        for match in pattern.finditer(text):

            tag = match.group(1)

            comment = match.group(2).strip()

            device_types = {
                        "X": "Input",
                        "Y": "Output",
                        "M": "Internal Relay",
                        "L": "Latch Relay",
                        "D": "Data Register",
                        "T": "Timer",
                        "C": "Counter",
                        "S": "Step Relay",
                        "R": "File Register"
                        }

            self.devices.append(
                {
                    "tag": tag,
                    "type": device_types.get(tag[0], "Unknown"),
                    "address": int(tag[1:]),
                    "comment": comment
                }
            )

        return self.devices

    def save_json(self, filename="database/device_tags.json"):

        Path("database").mkdir(exist_ok=True)

        with open(filename, "w", encoding="utf8") as f:

            json.dump(self.devices, f, indent=4)

        print("Saved", len(self.devices), "devices")