from backend.machine.plc_memory import plc


class AutoEngine:

    def __init__(self):

        self.state = "IDLE"
        self.model = 1

        self.center_timer = 0
        self.center_travel = 0

    # ==========================================================
    # MODEL SELECTION
    # ==========================================================

    def read_model(self):

        model_bits = {
            1: "L800",
            2: "L802",
            3: "L804",
            4: "L806",
            5: "L808",
            6: "L810",
            7: "L812",
            8: "L814",
            9: "L816",
            10: "L818",
            11: "L820",
            12: "L822"
        }

        for model, bit in model_bits.items():

            if int(plc.read(bit) or 0):

                self.model = model

                return model

        return self.model

    # ==========================================================
    # SAFETY
    # ==========================================================

    def safety_ok(self):

        emergency = int(plc.read("M90") or 0)
        air_fault = int(plc.read("M91") or 0)
        auto_mode = int(plc.read("M500") or 0)

        return (
            emergency == 0
            and air_fault == 0
            and auto_mode == 1
        )

    # ==========================================================
    # RESET COMMANDS
    # ==========================================================

    def reset_sequence(self):

        for bit in [
            "L502",
            "L504",
            "L506",
            "L508",
            "L510",
            "L516",
            "L518",
            "L1020"
        ]:

            plc.write(bit, 0)

        plc.write("Y46", 0)
        plc.write("Y47", 0)

        self.center_timer = 0
        self.center_travel = 0

    # ==========================================================
    # START CYCLE
    # ==========================================================

    def start_cycle(self):

        if not self.safety_ok():
            return

        self.read_model()

        plc.write("L501", 1)

        self.state = "SERVO1"

    # ==========================================================
    # STOP CYCLE
    # ==========================================================

    def stop_cycle(self):

        plc.write("L501", 0)

        self.reset_sequence()

        self.state = "IDLE"

    # ==========================================================
    # SERVO 1
    #
    # L502 -> Axis 1 Position 1
    # ==========================================================

    def servo1(self):

        plc.write("L502", 1)

        current_position = int(
            plc.read("D1100") or 0
        )

        target_position = int(
            plc.read(
                f"D{300 + ((self.model - 1) * 10)}"
            ) or 0
        )

        if current_position == target_position:

            plc.write("L502", 0)

            self.state = "SERVO2_3_POS2"

    # ==========================================================
    # SERVO 2 + SERVO 3 POSITION 2
    #
    # L504 -> Axis 2 Position 2
    # L506 -> Axis 3 Position 2
    # ==========================================================

    def servo2_3_pos2(self):

        plc.write("L504", 1)
        plc.write("L506", 1)

        axis2_position = int(
            plc.read("D1110") or 0
        )

        axis3_position = int(
            plc.read("D1120") or 0
        )

        offset = (self.model - 1) * 10

        axis2_target = int(
            plc.read(f"D{506 + offset}") or 0
        )

        axis3_target = int(
            plc.read(f"D{706 + offset}") or 0
        )

        axis2_done = (
            axis2_position == axis2_target
        )

        axis3_done = (
            axis3_position == axis3_target
        )

        if axis2_done and axis3_done:

            plc.write("L504", 0)
            plc.write("L506", 0)

            self.center_timer = 0
            self.center_travel = 0

            self.state = "CENTER_FORWARD"

    # ==========================================================
    # CENTERING FORWARD
    # ==========================================================

    def center_forward(self):

        plc.write("L508", 1)

        plc.write("Y46", 1)
        plc.write("Y47", 0)

        self.center_travel += 1

        # Simulated forward travel
        if self.center_travel >= 5:

            plc.write("X33", 1)
            plc.write("X34", 0)

        preset = int(
            plc.read("D80") or 20
        )

        if preset <= 0:
            preset = 20

        self.center_timer += 1

        if self.center_timer >= preset:

            plc.write("L508", 0)
            plc.write("Y46", 0)

            plc.write("L509", 1)

            self.center_timer = 0
            self.center_travel = 0

            self.state = "CENTER_REVERSE"

    # ==========================================================
    # CENTERING REVERSE
    # ==========================================================

    def center_reverse(self):

        plc.write("L510", 1)

        plc.write("Y47", 1)
        plc.write("Y46", 0)

        self.center_travel += 1

        # Simulated reverse travel
        if self.center_travel >= 5:

            plc.write("X34", 1)
            plc.write("X33", 0)

        if int(plc.read("X34") or 0):

            plc.write("L510", 0)
            plc.write("Y47", 0)

            plc.write("L511", 1)

            self.center_travel = 0

            self.state = "SERVO2_3_POS1"

    # ==========================================================
    # SERVO 2 + SERVO 3 POSITION 1
    #
    # L516 -> Axis 2 Position 1
    # L518 -> Axis 3 Position 1
    # ==========================================================

    def servo2_3_pos1(self):

        plc.write("L516", 1)
        plc.write("L518", 1)

        axis2_position = int(
            plc.read("D1110") or 0
        )

        axis3_position = int(
            plc.read("D1120") or 0
        )

        offset = (self.model - 1) * 10

        axis2_target = int(
            plc.read(f"D{500 + offset}") or 0
        )

        axis3_target = int(
            plc.read(f"D{700 + offset}") or 0
        )

        axis2_done = (
            axis2_position == axis2_target
        )

        axis3_done = (
            axis3_position == axis3_target
        )

        if axis2_done and axis3_done:

            plc.write("L516", 0)
            plc.write("L518", 0)

            self.state = "RETURN_HOME"

    # ==========================================================
    # RETURN HOME
    #
    # L1020 -> Home command
    # ==========================================================

    def return_home(self):

        plc.write("L1020", 1)

        axis1_home = (
            int(plc.read("D1100") or 0) == 0
        )

        axis2_home = (
            int(plc.read("D1110") or 0) == 0
        )

        axis3_home = (
            int(plc.read("D1120") or 0) == 0
        )

        if axis1_home and axis2_home and axis3_home:

            plc.write("L1020", 0)

            plc.write("L501", 0)
            plc.write("L509", 0)
            plc.write("L511", 0)

            self.center_timer = 0
            self.center_travel = 0

            self.state = "IDLE"

    # ==========================================================
    # MAIN AUTO SCAN
    # ==========================================================

    def scan(self):

        # ------------------------------------------------------
        # SAFETY
        # ------------------------------------------------------

        if not self.safety_ok():

            if self.state != "IDLE":

                self.stop_cycle()

            return

        # ------------------------------------------------------
        # STOP
        # ------------------------------------------------------

        if int(plc.read("L540") or 0):

            self.stop_cycle()

            return

        # ------------------------------------------------------
        # RESET
        # ------------------------------------------------------

        if int(plc.read("L541") or 0):

            self.stop_cycle()

            return

        # ------------------------------------------------------
        # START
        # ------------------------------------------------------

        if self.state == "IDLE":

            if int(plc.read("L501") or 0):

                self.read_model()

                self.state = "SERVO1"

            else:

                return

        # ------------------------------------------------------
        # STATE MACHINE
        # ------------------------------------------------------

        if self.state == "SERVO1":

            self.servo1()

        elif self.state == "SERVO2_3_POS2":

            self.servo2_3_pos2()

        elif self.state == "CENTER_FORWARD":

            self.center_forward()

        elif self.state == "CENTER_REVERSE":

            self.center_reverse()

        elif self.state == "SERVO2_3_POS1":

            self.servo2_3_pos1()

        elif self.state == "RETURN_HOME":

            self.return_home()


# ==========================================================
# GLOBAL INSTANCE
# ==========================================================

auto = AutoEngine()