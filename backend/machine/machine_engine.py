import threading
import time
from datetime import datetime, timezone

from backend.machine.auto_engine import auto
from backend.machine.servo_engine import servo
from backend.machine.production_engine import production
from backend.machine.plc_memory import plc


class MachineEngine:

    def __init__(self):

        # ==========================================================
        # Machine State
        # ==========================================================

        self.state = "IDLE"
        self.current_model = 1
        self.running = False

        # ==========================================================
        # Scan / Telemetry
        # ==========================================================

        self.scan_count = 0

        self.telemetry_history = []
        self.max_history = 6000

        self.lock = threading.Lock()

        # ==========================================================
        # Cycle Tracking
        # ==========================================================

        self.cycle_number = 0

        self.cycle_running = False
        self.cycle_complete = False

        self.cycle_start_time = None
        self.cycle_end_time = None

        self.current_cycle_duration = 0
        self.last_cycle_duration = 0

        self.previous_state = "IDLE"

        # ==========================================================
        # Automatic Continuous Cycle
        # ==========================================================

        # When enabled, the digital twin automatically starts a new
        # production cycle whenever the previous cycle has completed.
        self.auto_cycle_enabled = True
        self.auto_cycle_delay = 1.0       # seconds between cycles
        self.last_cycle_end_time = None

        # ==========================================================
        # Sequence History
        # ==========================================================

        self.sequence_history = []
        self.max_sequence_history = 1000

        self.last_sequence_state = "IDLE"

        # ==========================================================
        # Engine Timing
        # ==========================================================

        self.start_time = time.time()

        # ==========================================================
        # Background Machine Loop
        # ==========================================================

        self.thread = threading.Thread(
            target=self.machine_loop,
            daemon=True
        )

        self.thread.start()

    # ==============================================================
    # MACHINE LOOP
    # ==============================================================

    def machine_loop(self):

        while True:

            try:

                self.update()

            except Exception as e:

                print(
                    f"[MachineEngine] Error in machine loop: {e}"
                )

            time.sleep(0.01)

    # ==============================================================
    # UPDATE
    # ==============================================================

    def update(self):

        # ----------------------------------------------------------
        # 0. Automatic continuous cycle controller
        # ----------------------------------------------------------

        self.auto_cycle_controller()

        # ----------------------------------------------------------
        # 1. Automatic sequence
        # ----------------------------------------------------------

        auto.scan()

        # ----------------------------------------------------------
        # 2. Servo simulation
        # ----------------------------------------------------------

        servo.update()

        # ----------------------------------------------------------
        # 3. Production tracking
        # ----------------------------------------------------------

        production.update(
            getattr(auto, "state", "IDLE")
        )

        # ----------------------------------------------------------
        # 4. Update machine state
        # ----------------------------------------------------------

        self.update_state()

        # ----------------------------------------------------------
        # 5. Update cycle information
        # ----------------------------------------------------------

        self.update_cycle()

        # ----------------------------------------------------------
        # 6. Record sequence transitions
        # ----------------------------------------------------------

        self.update_sequence_history()

        # ----------------------------------------------------------
        # 7. Store live telemetry
        # ----------------------------------------------------------

        self.store_telemetry()

        # ----------------------------------------------------------
        # 8. Increment scan counter
        # ----------------------------------------------------------

        self.scan_count += 1

    # ==============================================================
    # AUTOMATIC CONTINUOUS CYCLE
    # ==============================================================

    def auto_cycle_controller(self):

        # Keep telemetry/scanning alive even when the machine is IDLE.
        # When automatic cycling is enabled, start the next cycle
        # automatically after a short delay.

        if not self.auto_cycle_enabled:
            return

        # Never automatically restart while emergency stop or
        # air-pressure fault is active.
        try:
            if int(plc.read("M90") or 0):
                return

            if int(plc.read("M91") or 0):
                return
        except Exception:
            return

        current_state = getattr(auto, "state", "IDLE")

        # If the machine is currently running, do nothing.
        if current_state != "IDLE":
            return

        now = time.time()

        # First startup:
        # wait a short moment so the backend can initialize and
        # begin collecting telemetry before the first cycle.
        if self.cycle_number == 0:
            if now - self.start_time < self.auto_cycle_delay:
                return
        else:
            # After a completed cycle, wait before starting the next.
            if self.last_cycle_end_time is None:
                return

            if now - self.last_cycle_end_time < self.auto_cycle_delay:
                return

        # Make sure AUTO mode is enabled.
        plc.write("M500", 1)

        # Start the automatic machine cycle using the same PLC
        # start signals as the normal /control/start endpoint.
        plc.write("M500", 1)
        plc.write("X21", 1)
        plc.write("L540", 0)
        plc.write("L541", 0)

        plc.write("X20", 1)
        plc.write("L501", 1)

    # ==============================================================
    # MACHINE STATE
    # ==============================================================

    def update_state(self):

        state = getattr(
            auto,
            "state",
            "IDLE"
        )

        model = getattr(
            auto,
            "current_model",
            getattr(auto, "model", 1)
        )

        self.state = state
        self.current_model = model

        self.running = (
            state != "IDLE"
        )

    # ==============================================================
    # CYCLE TRACKING
    # ==============================================================

    def update_cycle(self):

        current_state = self.state

        # ----------------------------------------------------------
        # New cycle
        # IDLE -> ACTIVE
        # ----------------------------------------------------------

        if (
            self.previous_state == "IDLE"
            and current_state != "IDLE"
        ):

            self.cycle_number += 1

            self.cycle_running = True
            self.cycle_complete = False

            self.cycle_start_time = time.time()
            self.cycle_end_time = None

            self.current_cycle_duration = 0

        # ----------------------------------------------------------
        # Cycle currently running
        # ----------------------------------------------------------

        if self.cycle_running:

            if self.cycle_start_time is not None:

                self.current_cycle_duration = round(
                    time.time()
                    - self.cycle_start_time,
                    3
                )

        # ----------------------------------------------------------
        # Cycle completed
        # ACTIVE -> IDLE
        # ----------------------------------------------------------

        if (
            self.previous_state != "IDLE"
            and current_state == "IDLE"
            and self.cycle_running
        ):

            self.cycle_running = False
            self.cycle_complete = True

            self.cycle_end_time = time.time()
            self.last_cycle_end_time = self.cycle_end_time

            if self.cycle_start_time is not None:

                self.last_cycle_duration = round(
                    self.cycle_end_time
                    - self.cycle_start_time,
                    3
                )

                self.current_cycle_duration = (
                    self.last_cycle_duration
                )

        self.previous_state = current_state

    # ==============================================================
    # AUTOMATIC CYCLE CONTROL
    # ==============================================================

    def set_auto_cycle(self, enabled=True):

        self.auto_cycle_enabled = bool(enabled)

        return {
            "status": "success",
            "auto_cycle_enabled": self.auto_cycle_enabled,
            "cycle_delay": self.auto_cycle_delay
        }

    # ==============================================================
    # SEQUENCE HISTORY
    # ==============================================================

    def update_sequence_history(self):

        current_state = self.state

        if current_state != self.last_sequence_state:

            entry = {
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),

                "scan": self.scan_count,

                "from_state": self.last_sequence_state,

                "to_state": current_state,

                "model": self.current_model,

                "cycle_number": self.cycle_number
            }

            with self.lock:

                self.sequence_history.append(
                    entry
                )

                if len(self.sequence_history) > self.max_sequence_history:

                    self.sequence_history = (
                        self.sequence_history[
                            -self.max_sequence_history:
                        ]
                    )

            self.last_sequence_state = current_state

    # ==============================================================
    # TELEMETRY
    # ==============================================================

    def store_telemetry(self):

        try:

            servo_data = servo.telemetry()

        except Exception:

            servo_data = {}

        axis1_data = servo_data.get(
            "axis1",
            {}
        )

        axis2_data = servo_data.get(
            "axis2",
            {}
        )

        axis3_data = servo_data.get(
            "axis3",
            {}
        )

        snapshot = {

            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "scan": self.scan_count,

            "state": self.state,

            "model": self.current_model,

            "cycle": {
                "number": self.cycle_number,

                "running": self.cycle_running,

                "complete": self.cycle_complete,

                "duration": self.current_cycle_duration
            },

            "sequence": self.state,

            "axis1": {
                "position": axis1_data.get(
                    "position",
                    0
                ),

                "target": axis1_data.get(
                    "target",
                    0
                ),

                "speed": axis1_data.get(
                    "speed",
                    0
                ),

                "command_speed": axis1_data.get(
                    "command_speed",
                    0
                ),

                "actual_speed": axis1_data.get(
                    "actual_speed",
                    axis1_data.get("speed", 0)
                ),

                "error": axis1_data.get(
                    "error",
                    False
                ),

                "busy": axis1_data.get(
                    "busy",
                    False
                ),

                "complete": axis1_data.get(
                    "complete",
                    False
                )
            },

            "axis2": {
                "position": axis2_data.get(
                    "position",
                    0
                ),

                "target": axis2_data.get(
                    "target",
                    0
                ),

                "speed": axis2_data.get(
                    "speed",
                    0
                ),

                "command_speed": axis2_data.get(
                    "command_speed",
                    0
                ),

                "actual_speed": axis2_data.get(
                    "actual_speed",
                    axis2_data.get("speed", 0)
                ),

                "error": axis2_data.get(
                    "error",
                    False
                ),

                "busy": axis2_data.get(
                    "busy",
                    False
                ),

                "complete": axis2_data.get(
                    "complete",
                    False
                )
            },

            "axis3": {
                "position": axis3_data.get(
                    "position",
                    0
                ),

                "target": axis3_data.get(
                    "target",
                    0
                ),

                "speed": axis3_data.get(
                    "speed",
                    0
                ),

                "command_speed": axis3_data.get(
                    "command_speed",
                    0
                ),

                "actual_speed": axis3_data.get(
                    "actual_speed",
                    axis3_data.get("speed", 0)
                ),

                "error": axis3_data.get(
                    "error",
                    False
                ),

                "busy": axis3_data.get(
                    "busy",
                    False
                ),

                "complete": axis3_data.get(
                    "complete",
                    False
                )
            }
        }

        with self.lock:

            self.telemetry_history.append(
                snapshot
            )

            if len(self.telemetry_history) > self.max_history:

                self.telemetry_history = (
                    self.telemetry_history[
                        -self.max_history:
                    ]
                )

    # ==============================================================
    # GET TELEMETRY HISTORY
    # ==============================================================

    def get_history(self, limit=100):

        with self.lock:

            return self.telemetry_history[
                -limit:
            ]

    # ==============================================================
    # GET TELEMETRY SINCE
    # ==============================================================

    def get_history_since(self, seconds=60):

        cutoff = (
            datetime.now(
                timezone.utc
            ).timestamp()
            - seconds
        )

        result = []

        with self.lock:

            for item in self.telemetry_history:

                try:

                    timestamp = datetime.fromisoformat(
                        item["timestamp"]
                    ).timestamp()

                    if timestamp >= cutoff:

                        result.append(item)

                except Exception:

                    continue

        return result

    # ==============================================================
    # GET LATEST TELEMETRY
    # ==============================================================

    def get_latest(self):

        with self.lock:

            if not self.telemetry_history:

                return {}

            return self.telemetry_history[-1]

    # ==============================================================
    # GET CYCLE INFORMATION
    # ==============================================================

    def get_cycle_info(self):

        current_duration = (
            self.current_cycle_duration
        )

        if (
            self.cycle_running
            and self.cycle_start_time is not None
        ):

            current_duration = round(
                time.time()
                - self.cycle_start_time,
                3
            )

        return {

            "cycle_number": self.cycle_number,

            "running": self.cycle_running,

            "start_time": self.cycle_start_time,

            "end_time": self.cycle_end_time,

            "current_duration": current_duration,

            "last_cycle_duration": (
                self.last_cycle_duration
            )
        }

    # ==============================================================
    # GET SEQUENCE HISTORY
    # ==============================================================

    def get_sequence_history(self, limit=100):

        with self.lock:

            return self.sequence_history[
                -limit:
            ]


# ==============================================================
# GLOBAL MACHINE ENGINE
# ==============================================================

engine = MachineEngine()