from backend.machine.plc_memory import plc


class SafetyEngine:

    def update(self):

        # Emergency PB

        if plc.read("X22"):

            plc.write("M90", 1)

        # Air Pressure Low

        if plc.read("X3D"):

            plc.write("M91", 1)

        # Reset PB

        if plc.read("X23"):

            plc.write("M90", 0)

            plc.write("M91", 0)

    #########################

    def safe(self):

        return (

            plc.read("M90") == 0 and
            plc.read("M91") == 0

        )


safety = SafetyEngine()