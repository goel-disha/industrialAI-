from backend.database import get_connection


class PLCMemory:

    def __init__(self):

        self.memory = {}

        # Addresses that actually exist in servo_devices
        self.database_addresses = set()

        # ----------------------------------------------------------
        # Load database-backed PLC devices
        # ----------------------------------------------------------

        self.load()

        # ----------------------------------------------------------
        # Load runtime PLC addresses
        # ----------------------------------------------------------

        self.load_runtime_addresses()

        # ----------------------------------------------------------
        # Load engineering position registers
        # ----------------------------------------------------------

        self.load_engineering_registers()

        # ----------------------------------------------------------
        # Default model
        # ----------------------------------------------------------

        self.initialize_default_model()

    # ==========================================================
    # LOAD ENGINEERING / SERVO DATABASE
    # ==========================================================

    def load(self):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                address,
                current_value
            FROM servo_devices
        """)

        rows = cursor.fetchall()

        conn.close()

        self.memory.clear()
        self.database_addresses.clear()

        for row in rows:

            address = row["address"]
            value = row["current_value"]

            self.memory[address] = str(value)

            self.database_addresses.add(address)

    # ==========================================================
    # LOAD RUNTIME PLC ADDRESSES
    # ==========================================================

    def load_runtime_addresses(self):

        runtime_addresses = {

            # --------------------------------------------------
            # Safety / Mode
            # --------------------------------------------------

            "M90": "0",          # Emergency
            "M91": "0",          # Air fault
            "M500": "0",         # Auto mode
            "M100": "0",         # Manual mode

            # --------------------------------------------------
            # Physical Inputs
            # --------------------------------------------------

            "X20": "0",          # Cycle Start
            "X21": "1",          # Cycle Stop NC -> NORMAL = 1
            "X22": "0",          # Emergency input
            "X23": "0",          # Reset
            "X24": "0",          # Auto / Manual
            "X25": "0",          # Home
            "X30": "0",          # Part Entry

            "X33": "0",          # Center Forward Limit
            "X34": "1",          # Center Reverse/Home Limit

            # --------------------------------------------------
            # Physical Outputs
            # --------------------------------------------------

            "Y46": "0",          # Center Forward
            "Y47": "0",          # Center Reverse

            # --------------------------------------------------
            # Auto Sequence
            # --------------------------------------------------

            "L501": "0",         # AUTO_CYCLE START

            "L502": "0",         # AUTO_SERVO_1 RUN

            "L504": "0",         # AUTO_SERVO_2 POSITION 2
            "L506": "0",         # AUTO_SERVO_3 POSITION 2

            "L508": "0",         # Center Forward
            "L509": "0",         # Center Forward Complete

            "L510": "0",         # Center Reverse
            "L511": "0",         # Center Reverse Complete

            "L516": "0",         # Servo 2 Position 1
            "L518": "0",         # Servo 3 Position 1

            "L1020": "0",        # Return Home

            # --------------------------------------------------
            # Servo Completion
            # --------------------------------------------------

            "L610": "0",         # Axis 1 complete
            "L611": "0",         # Axis 2 complete
            "L612": "0",         # Axis 3 complete

            # --------------------------------------------------
            # Servo Status
            # --------------------------------------------------

            "L700": "0",         # Axis 1 selected / ready
            "L701": "0",         # Axis 2 selected / ready
            "L702": "0",         # Axis 3 selected / ready
            "L704": "0",         # Servo origin

            "L710": "0",         # Servo ready
            "L712": "0",         # Servo busy
            "L714": "0",         # Servo error
            "L718": "0",         # Position reached
            "L720": "0",         # Origin

            # --------------------------------------------------
            # Model Selection
            # --------------------------------------------------

            "L800": "0",         # Model 1
            "L802": "0",         # Model 2
            "L804": "0",         # Model 3
            "L806": "0",         # Model 4
            "L808": "0",         # Model 5
            "L810": "0",         # Model 6
            "L812": "0",         # Model 7
            "L814": "0",         # Model 8
            "L816": "0",         # Model 9
            "L818": "0",         # Model 10
            "L820": "0",         # Model 11
            "L822": "0",         # Model 12

            # Selected model register
            "D1800": "0",

            # --------------------------------------------------
            # Timer
            # --------------------------------------------------

            "T100": "0"
        }

        for address, value in runtime_addresses.items():

            # Database value always takes priority.
            # Runtime addresses are only added if they
            # don't already exist in servo_devices.

            if address not in self.memory:

                self.memory[address] = value

    # ==========================================================
    # INITIALIZE DEFAULT MODEL
    # ==========================================================

    def initialize_default_model(self):

        model_bits = [
            "L800",
            "L802",
            "L804",
            "L806",
            "L808",
            "L810",
            "L812",
            "L814",
            "L816",
            "L818",
            "L820",
            "L822"
        ]

        # Check whether a model is already selected

        model_selected = any(
            int(self.memory.get(bit, 0) or 0)
            for bit in model_bits
        )

        # If no model is selected,
        # default to Model 1.

        if not model_selected:

            for bit in model_bits:

                self.memory[bit] = "0"

            self.memory["L800"] = "1"
            self.memory["D1800"] = "1"

    # ==========================================================
    # LOAD ENGINEERING POSITION REGISTERS
    # ==========================================================

    def load_engineering_registers(self):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                axis,
                target_position
            FROM axis_runtime
        """)

        rows = cursor.fetchall()

        conn.close()

        for row in rows:

            axis = int(row["axis"])
            target = int(row["target_position"] or 0)

            # --------------------------------------------------
            # Current engineering target
            # Model 1 Position 1
            # --------------------------------------------------

            if axis == 1:

                self.memory["D300"] = str(target)

            elif axis == 2:

                self.memory["D500"] = str(target)

            elif axis == 3:

                self.memory["D700"] = str(target)

    # ==========================================================
    # READ DEVICE
    # ==========================================================

    def read(self, address):

        return self.memory.get(address)

    # ==========================================================
    # WRITE DEVICE
    # ==========================================================

    def write(self, address, value):

        # Do not silently create arbitrary PLC addresses.

        if address not in self.memory:

            return False

        self.memory[address] = str(value)

        return True

    # ==========================================================
    # TOGGLE BIT
    # ==========================================================

    def toggle(self, address):

        value = int(
            self.read(address) or 0
        )

        if value:

            self.write(address, 0)

        else:

            self.write(address, 1)

    # ==========================================================
    # SAVE DATABASE-BACKED VALUES
    # ==========================================================

    def save(self):

        conn = get_connection()
        cursor = conn.cursor()

        # Only save addresses that actually came from
        # servo_devices.

        for address in self.database_addresses:

            if address not in self.memory:

                continue

            value = self.memory[address]

            cursor.execute("""
                UPDATE servo_devices
                SET current_value=?
                WHERE address=?
            """, (value, address))

        conn.commit()
        conn.close()

    # ==========================================================
    # RESET PLC
    # ==========================================================

    def reset(self):

        # ------------------------------------------------------
        # Reset database-backed registers
        # ------------------------------------------------------

        for address in self.database_addresses:

            if address not in self.memory:

                continue

            if address.startswith(
                ("X", "Y", "M", "L", "T")
            ):

                self.memory[address] = "0"

            elif address.startswith("SM"):

                self.memory[address] = "1"

            else:

                self.memory[address] = "0"

        # ------------------------------------------------------
        # Reset runtime machine state
        # ------------------------------------------------------

        self.reset_runtime()

        # ------------------------------------------------------
        # Save only database-backed values
        # ------------------------------------------------------

        self.save()

    # ==========================================================
    # RESET RUNTIME MACHINE STATE
    # ==========================================================

    def reset_runtime(self):

        # ------------------------------------------------------
        # Safety
        # ------------------------------------------------------

        self.memory["M90"] = "0"
        self.memory["M91"] = "0"

        # Keep current Auto / Manual mode unchanged.
        # M500 is intentionally NOT reset.

        # ------------------------------------------------------
        # Inputs
        # ------------------------------------------------------

        self.memory["X20"] = "0"

        # X21 is NC:
        # 1 = normal
        # 0 = stop pressed

        self.memory["X21"] = "1"

        self.memory["X22"] = "0"
        self.memory["X23"] = "0"
        self.memory["X24"] = "0"
        self.memory["X25"] = "0"
        self.memory["X30"] = "0"

        # Centering cylinder starts at reverse/home limit.

        self.memory["X33"] = "0"
        self.memory["X34"] = "1"

        # ------------------------------------------------------
        # Outputs
        # ------------------------------------------------------

        self.memory["Y46"] = "0"
        self.memory["Y47"] = "0"

        # ------------------------------------------------------
        # Auto sequence
        # ------------------------------------------------------

        for address in (
            "L501",
            "L502",
            "L504",
            "L506",
            "L508",
            "L509",
            "L510",
            "L511",
            "L516",
            "L518",
            "L1020"
        ):

            self.memory[address] = "0"

        # ------------------------------------------------------
        # Servo completion
        # ------------------------------------------------------

        self.memory["L610"] = "0"
        self.memory["L611"] = "0"
        self.memory["L612"] = "0"

        # ------------------------------------------------------
        # Servo status
        # ------------------------------------------------------

        self.memory["L700"] = "0"
        self.memory["L701"] = "0"
        self.memory["L702"] = "0"
        self.memory["L704"] = "0"

        self.memory["L710"] = "0"
        self.memory["L712"] = "0"
        self.memory["L714"] = "0"
        self.memory["L718"] = "0"
        self.memory["L720"] = "0"

        # ------------------------------------------------------
        # Timer
        # ------------------------------------------------------

        self.memory["T100"] = "0"

        # ------------------------------------------------------
        # Preserve / restore selected model
        # ------------------------------------------------------

        model_bits = [
            "L800",
            "L802",
            "L804",
            "L806",
            "L808",
            "L810",
            "L812",
            "L814",
            "L816",
            "L818",
            "L820",
            "L822"
        ]

        selected_model = 0

        for index, bit in enumerate(model_bits, start=1):

            if int(
                self.memory.get(bit, 0) or 0
            ):

                selected_model = index
                break

        # If somehow no model exists,
        # restore Model 1.

        if selected_model == 0:

            selected_model = 1

            for bit in model_bits:

                self.memory[bit] = "0"

            self.memory["L800"] = "1"

        self.memory["D1800"] = str(
            selected_model
        )

    # ==========================================================
    # SNAPSHOT
    # ==========================================================

    def snapshot(self):

        return dict(self.memory)


# ==============================================================
# GLOBAL PLC INSTANCE
# ==============================================================

plc = PLCMemory()