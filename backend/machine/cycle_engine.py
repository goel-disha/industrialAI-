from backend.machine.plc_memory import plc
from backend.machine.safety_engine import safety
from backend.machine.auto_engine import auto


class CycleEngine:

    def update(self):

        if (

            plc.read("X20")
            and safety.safe()
            and auto.auto()

        ):

            plc.write("L501", 1)

        if plc.read("X21"):

            plc.write("L501", 0)

    ############################

    def running(self):

        return plc.read("L501")


cycle = CycleEngine()