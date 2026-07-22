from backend.machine.plc_memory import plc


class AutoEngine:

    def update(self):

        if plc.read("X24"):

            plc.write("M500", 1)

        else:

            plc.write("M500", 0)

    ############################

    def auto(self):

        return plc.read("M500")


auto = AutoEngine()