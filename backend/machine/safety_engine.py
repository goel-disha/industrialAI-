from backend.machine.plc_memory import plc


class SafetyEngine:

    def __init__(self):

        self.machine_ready = False

    ##############################################################
    # Emergency Stop
    ##############################################################

    def emergency(self):

        emergency = int(plc.read("M90") or 0)

        if emergency:

            plc.write("L501", 0)
            plc.write("L502", 0)
            plc.write("L1031", 0)
            plc.write("L1032", 0)

            return False

        return True

    ##############################################################
    # Air Pressure
    ##############################################################

    def air_pressure(self):

        pressure_fault = int(plc.read("M91") or 0)

        if pressure_fault:

            plc.write("L501", 0)

            return False

        return True

    ##############################################################
    # Servo Ready
    ##############################################################

    def servo_ready(self):

        ready = int(plc.read("M500") or 0)

        return ready == 1

    ##############################################################
    # Home Complete
    ##############################################################

    def home_complete(self):

        return (

            int(plc.read("L610") or 0)

            and

            int(plc.read("L611") or 0)

            and

            int(plc.read("L612") or 0)

        )

    ##############################################################
    # Complete Safety Scan
    ##############################################################

    def scan(self):

        self.machine_ready = (

            self.emergency()

            and

            self.air_pressure()

            and

            self.servo_ready()

        )

        plc.write("M1000", int(self.machine_ready))

        return self.machine_ready


safety = SafetyEngine()