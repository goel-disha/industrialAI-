from datetime import datetime
from backend.repositries.live_repositry import update_live

class PLCMemory:

    def __init__(self):

        self.bits = {}
        self.words = {}

    ##############################

    def read(self, tag):

        if tag.startswith(("X", "Y", "M", "L")):
            return self.bits.get(tag, 0)

        return self.words.get(tag, 0)

    ##############################

    def write(self, tag, value):

     if tag.startswith(("X", "Y", "M", "L")):

        old = self.bits.get(tag)

        if old != int(value):

            self.bits[tag] = int(value)

            update_live(
                tag,
                int(value),
                datetime.now().isoformat()
            )

     else:

        old = self.words.get(tag)

        if old != value:

            self.words[tag] = value

            update_live(
                tag,
                value,
                datetime.now().isoformat()
            )
    ##############################

    def all(self):

        return {

            "bits": self.bits,

            "words": self.words

        }


plc = PLCMemory()