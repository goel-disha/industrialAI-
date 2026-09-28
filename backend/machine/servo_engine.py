from backend.machine.plc_memory import plc
from backend.database import get_connection

import time
import math


# ==============================================================
# ENGINEERING / RUNTIME PARAMETERS
# ==============================================================

def get_axis_parameters(axis_no):
    """
    Read the actual runtime parameters stored in the engineering DB.

    axis_runtime contains:
        target_position
        command_speed
        acceleration
        deceleration
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            target_position,
            command_speed,
            acceleration,
            deceleration
        FROM axis_runtime
        WHERE axis = ?
        """,
        (axis_no,)
    )

    row = cursor.fetchone()

    conn.close()

    if not row:
        return {
            "target_position": 0.0,
            "command_speed": 0.0,
            "acceleration": 1000.0,
            "deceleration": 1000.0
        }

    return {
        "target_position": float(row["target_position"] or 0),
        "command_speed": float(row["command_speed"] or 0),
        "acceleration": float(row["acceleration"] or 1000),
        "deceleration": float(row["deceleration"] or 1000)
    }


# ==============================================================
# SERVO AXIS
# ==============================================================

class ServoAxis:

    def __init__(
        self,
        name,
        axis_no,
        position_register,
        feedback_register,
        complete_bit,
        ready_bit,
        error_register=None,
        speed_register=None
    ):

        self.name = name
        self.axis_no = axis_no

        # PLC / Motion CPU registers
        self.position_register = position_register
        self.feedback_register = feedback_register
        self.complete_bit = complete_bit
        self.ready_bit = ready_bit

        self.error_register = error_register
        self.speed_register = speed_register

        # ------------------------------------------------------
        # Motion state
        # ------------------------------------------------------

        self.target = 0.0
        self.position = 0.0

        self.speed = 0.0
        self.command_speed = 0.0

        self.acceleration = 1000.0
        self.deceleration = 1000.0

        self.actual_speed = 0.0

        self.busy = False
        self.complete = True
        self.ready = True
        self.error = False

        self.direction = 0
        self.position_error = 0.0
        self.distance_remaining = 0.0

        # ------------------------------------------------------
        # Motion diagnostics
        # ------------------------------------------------------

        self.motion_start_position = 0.0
        self.motion_start_time = None

        self.last_update_time = time.monotonic()

        self.current_command = "IDLE"

        self.target_changed = False

        self.move_count = 0

    # ==========================================================
    # ENGINEERING PARAMETERS
    # ==========================================================

    def load_parameters(self):

        params = get_axis_parameters(self.axis_no)

        self.command_speed = params["command_speed"]
        self.acceleration = params["acceleration"]
        self.deceleration = params["deceleration"]

        return params

    # ==========================================================
    # LOAD TARGET
    # ==========================================================

    def load_target(self, target, command_name="POSITION"):

        target = float(target)

        # Detect a new command
        if target != self.target:

            self.motion_start_position = self.position
            self.motion_start_time = time.monotonic()

            self.target_changed = True

            self.move_count += 1

        else:

            self.target_changed = False

        self.target = target

        self.position_error = self.target - self.position
        self.distance_remaining = abs(self.position_error)

        # ------------------------------------------------------
        # Target reached
        # ------------------------------------------------------

        if abs(self.position - self.target) < 0.001:

            self.position = self.target

            self.actual_speed = 0.0
            self.speed = 0.0

            self.busy = False
            self.complete = True
            self.ready = True

            self.direction = 0

            self.current_command = command_name

        # ------------------------------------------------------
        # Target not reached
        # ------------------------------------------------------

        else:

            self.busy = True
            self.complete = False
            self.ready = False

            self.current_command = command_name

    # ==========================================================
    # HOLD
    # ==========================================================

    def hold(self):

        self.busy = False

        self.actual_speed = 0.0
        self.speed = 0.0

        self.direction = 0

        self.position_error = self.target - self.position
        self.distance_remaining = abs(self.position_error)

        if abs(self.position - self.target) < 0.001:

            self.position = self.target

            self.complete = True
            self.ready = True

        else:

            self.complete = False
            self.ready = True

        self.current_command = "HOLD"

    # ==========================================================
    # STOP
    # ==========================================================

    def stop(self):

        self.actual_speed = 0.0
        self.speed = 0.0

        self.busy = False
        self.complete = False
        self.ready = True

        self.direction = 0

        self.position_error = self.target - self.position
        self.distance_remaining = abs(self.position_error)

        self.current_command = "STOP"

    # ==========================================================
    # MOTION UPDATE
    # ==========================================================

    def move(self, dt=None):

        now = time.monotonic()

        if dt is None:

            dt = now - self.last_update_time

        self.last_update_time = now

        # Prevent abnormal time jumps
        dt = max(0.001, min(dt, 0.2))

        # ------------------------------------------------------
        # No movement required
        # ------------------------------------------------------

        error = self.target - self.position

        self.position_error = error
        self.distance_remaining = abs(error)

        if abs(error) < 0.001:

            self.position = self.target

            self.actual_speed = 0.0
            self.speed = 0.0

            self.busy = False
            self.complete = True
            self.ready = True

            self.direction = 0

            return

        command_speed_mm_min = max(0.0, self.command_speed)

        acceleration_ms = max(1.0, self.acceleration)
        deceleration_ms = max(1.0, self.deceleration)

        # mm/min -> micrometres/sec
        max_speed = (
            command_speed_mm_min
            * 1000.0
            / 60.0
        )

        acceleration = (
            max_speed
            / (acceleration_ms / 1000.0)
        )

        deceleration = (
            max_speed
            / (deceleration_ms / 1000.0)
        )

        # ------------------------------------------------------
        # Direction
        # ------------------------------------------------------

        direction = 1 if error > 0 else -1

        self.direction = direction

        # ------------------------------------------------------
        # Distance required to stop
        #
        # v² = 2as
        # ------------------------------------------------------

        stopping_distance = 0.0

        if deceleration > 0:

            stopping_distance = (
                self.actual_speed ** 2
            ) / (
                2.0 * deceleration
            )

        # ------------------------------------------------------
        # Accelerate or decelerate
        # ------------------------------------------------------

        if self.distance_remaining <= stopping_distance:

            # Deceleration phase
            self.actual_speed = max(
                0.0,
                self.actual_speed
                - deceleration * dt
            )

        else:

            # Acceleration phase
            self.actual_speed = min(
                max_speed,
                self.actual_speed
                + acceleration * dt
            )

        # ------------------------------------------------------
        # Position update
        # ------------------------------------------------------

        movement = self.actual_speed * dt

        movement = min(
            movement,
            self.distance_remaining
        )

        self.position += direction * movement

        # ------------------------------------------------------
        # Final target correction
        # ------------------------------------------------------

        if (
            abs(self.target - self.position)
            <= max(0.001, movement)
            and self.actual_speed <= max_speed
        ):

            if abs(self.target - self.position) < 0.001:

                self.position = self.target

        # ------------------------------------------------------
        # Update telemetry
        # ------------------------------------------------------

        self.position_error = (
            self.target - self.position
        )

        self.distance_remaining = abs(
            self.position_error
        )

        self.speed = self.actual_speed

        # ------------------------------------------------------
        # Check completion
        # ------------------------------------------------------

        if abs(self.position_error) < 0.001:

            self.position = self.target

            self.actual_speed = 0.0
            self.speed = 0.0

            self.busy = False
            self.complete = True
            self.ready = True

            self.direction = 0

            if self.motion_start_time is not None:

                self.current_command = "COMPLETE"

        else:

            self.busy = True
            self.complete = False
            self.ready = False

    # ==========================================================
    # TELEMETRY
    # ==========================================================

    def telemetry(self):

        motion_time = 0.0

        if self.motion_start_time is not None:

            motion_time = (
                time.monotonic()
                - self.motion_start_time
            )

        return {

            "name": self.name,

            "axis": self.axis_no,

            "position": round(
                self.position,
                3
            ),

            "target": round(
                self.target,
                3
            ),

            "position_error": round(
                self.position_error,
                3
            ),

            "distance_remaining": round(
                self.distance_remaining,
                3
            ),

            "speed": round(
                self.speed,
                3
            ),

            "command_speed": round(
                self.command_speed,
                3
            ),

            "acceleration": round(
                self.acceleration,
                3
            ),

            "deceleration": round(
                self.deceleration,
                3
            ),

            "direction": self.direction,

            "busy": self.busy,

            "complete": self.complete,

            "ready": self.ready,

            "error": self.error,

            "current_command": self.current_command,

            "motion_time": round(
                motion_time,
                3
            ),

            "move_count": self.move_count,

            "position_register":
                self.position_register,

            "feedback_register":
                self.feedback_register,

            "complete_bit":
                self.complete_bit,

            "ready_bit":
                self.ready_bit,

            "error_register":
                self.error_register,

            "speed_register":
                self.speed_register
        }


# ==============================================================
# SERVO AXES
# ==============================================================

axis1 = ServoAxis(
    name="Axis-1",
    axis_no=1,
    position_register="D1100",
    feedback_register="U0/G800",
    complete_bit="L610",
    ready_bit="L700",
    error_register="D940",
    speed_register="D900"
)

axis2 = ServoAxis(
    name="Axis-2",
    axis_no=2,
    position_register="D1110",
    feedback_register="U0/G900",
    complete_bit="L611",
    ready_bit="L701",
    error_register="D942",
    speed_register="D910"
)

axis3 = ServoAxis(
    name="Axis-3",
    axis_no=3,
    position_register="D1120",
    feedback_register="U0/G1000",
    complete_bit="L612",
    ready_bit="L702",
    error_register="D944",
    speed_register="D920"
)


# ==============================================================
# SERVO ENGINE
# ==============================================================

class ServoEngine:

    def __init__(self):

        # ------------------------------------------------------
        # Model Position Registers
        #
        # Each model occupies 10 registers.
        # ------------------------------------------------------

        self.model_positions = {

            1: {
                "axis1": {
                    "pos1": "D300",
                    "pos2": "D306"
                },
                "axis2": {
                    "pos1": "D500",
                    "pos2": "D506"
                },
                "axis3": {
                    "pos1": "D700",
                    "pos2": "D706"
                }
            },

            2: {
                "axis1": {
                    "pos1": "D310",
                    "pos2": "D316"
                },
                "axis2": {
                    "pos1": "D510",
                    "pos2": "D516"
                },
                "axis3": {
                    "pos1": "D710",
                    "pos2": "D716"
                }
            },

            3: {
                "axis1": {
                    "pos1": "D320",
                    "pos2": "D326"
                },
                "axis2": {
                    "pos1": "D520",
                    "pos2": "D526"
                },
                "axis3": {
                    "pos1": "D720",
                    "pos2": "D726"
                }
            },

            4: {
                "axis1": {
                    "pos1": "D330",
                    "pos2": "D336"
                },
                "axis2": {
                    "pos1": "D530",
                    "pos2": "D536"
                },
                "axis3": {
                    "pos1": "D730",
                    "pos2": "D736"
                }
            },

            5: {
                "axis1": {
                    "pos1": "D340",
                    "pos2": "D346"
                },
                "axis2": {
                    "pos1": "D540",
                    "pos2": "D546"
                },
                "axis3": {
                    "pos1": "D740",
                    "pos2": "D746"
                }
            },

            6: {
                "axis1": {
                    "pos1": "D350",
                    "pos2": "D356"
                },
                "axis2": {
                    "pos1": "D550",
                    "pos2": "D556"
                },
                "axis3": {
                    "pos1": "D750",
                    "pos2": "D756"
                }
            },

            7: {
                "axis1": {
                    "pos1": "D360",
                    "pos2": "D366"
                },
                "axis2": {
                    "pos1": "D560",
                    "pos2": "D566"
                },
                "axis3": {
                    "pos1": "D760",
                    "pos2": "D766"
                }
            },

            8: {
                "axis1": {
                    "pos1": "D370",
                    "pos2": "D376"
                },
                "axis2": {
                    "pos1": "D570",
                    "pos2": "D576"
                },
                "axis3": {
                    "pos1": "D770",
                    "pos2": "D776"
                }
            },

            9: {
                "axis1": {
                    "pos1": "D380",
                    "pos2": "D386"
                },
                "axis2": {
                    "pos1": "D580",
                    "pos2": "D586"
                },
                "axis3": {
                    "pos1": "D780",
                    "pos2": "D786"
                }
            },

            10: {
                "axis1": {
                    "pos1": "D390",
                    "pos2": "D396"
                },
                "axis2": {
                    "pos1": "D590",
                    "pos2": "D596"
                },
                "axis3": {
                    "pos1": "D790",
                    "pos2": "D796"
                }
            },

            11: {
                "axis1": {
                    "pos1": "D400",
                    "pos2": "D406"
                },
                "axis2": {
                    "pos1": "D600",
                    "pos2": "D606"
                },
                "axis3": {
                    "pos1": "D800",
                    "pos2": "D806"
                }
            },

            12: {
                "axis1": {
                    "pos1": "D410",
                    "pos2": "D416"
                },
                "axis2": {
                    "pos1": "D610",
                    "pos2": "D616"
                },
                "axis3": {
                    "pos1": "D810",
                    "pos2": "D816"
                }
            }
        }

        # ------------------------------------------------------
        # Scan timing
        # ------------------------------------------------------

        self.last_update_time = time.monotonic()

        # ------------------------------------------------------
        # Runtime telemetry
        # ------------------------------------------------------

        self.scan_count = 0

        self.last_model = 1

    # ==========================================================
    # MODEL SELECTION
    # ==========================================================

    def selected_model(self):

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

                self.last_model = model

                return model

        return self.last_model

    # ==========================================================
    # READ POSITION
    # ==========================================================

    def read_position(
        self,
        model,
        axis,
        position
    ):

        if model not in self.model_positions:

            model = 1

        register = self.model_positions[
            model
        ][axis][position]

        return int(
            plc.read(register) or 0
        )

    # ==========================================================
    # LOAD ENGINEERING PARAMETERS
    # ==========================================================

    def update_parameters(self):

        axis1.load_parameters()
        axis2.load_parameters()
        axis3.load_parameters()

    # ==========================================================
    # AXIS 1 COMMAND
    # ==========================================================

    def update_axis1(self, model):

        # ------------------------------------------------------
        # Return Home
        # ------------------------------------------------------

        if int(plc.read("L1020") or 0):

            axis1.load_target(
                0,
                "HOME"
            )

        # ------------------------------------------------------
        # Servo 1 Position 1
        # ------------------------------------------------------

        elif int(plc.read("L502") or 0):

            target = self.read_position(
                model,
                "axis1",
                "pos1"
            )

            axis1.load_target(
                target,
                "POSITION_1"
            )

        # ------------------------------------------------------
        # No command
        # ------------------------------------------------------

        else:

            axis1.hold()

    # ==========================================================
    # AXIS 2 COMMAND
    # ==========================================================

    def update_axis2(self, model):

        # ------------------------------------------------------
        # Return Home
        # ------------------------------------------------------

        if int(plc.read("L1020") or 0):

            axis2.load_target(
                0,
                "HOME"
            )

        # ------------------------------------------------------
        # Position 2
        # ------------------------------------------------------

        elif int(plc.read("L504") or 0):

            target = self.read_position(
                model,
                "axis2",
                "pos2"
            )

            axis2.load_target(
                target,
                "POSITION_2"
            )

        # ------------------------------------------------------
        # Position 1
        # ------------------------------------------------------

        elif int(plc.read("L516") or 0):

            target = self.read_position(
                model,
                "axis2",
                "pos1"
            )

            axis2.load_target(
                target,
                "POSITION_1"
            )

        # ------------------------------------------------------
        # No command
        # ------------------------------------------------------

        else:

            axis2.hold()

    # ==========================================================
    # AXIS 3 COMMAND
    # ==========================================================

    def update_axis3(self, model):

        # ------------------------------------------------------
        # Return Home
        # ------------------------------------------------------

        if int(plc.read("L1020") or 0):

            axis3.load_target(
                0,
                "HOME"
            )

        # ------------------------------------------------------
        # Position 2
        # ------------------------------------------------------

        elif int(plc.read("L506") or 0):

            target = self.read_position(
                model,
                "axis3",
                "pos2"
            )

            axis3.load_target(
                target,
                "POSITION_2"
            )

        # ------------------------------------------------------
        # Position 1
        # ------------------------------------------------------

        elif int(plc.read("L518") or 0):

            target = self.read_position(
                model,
                "axis3",
                "pos1"
            )

            axis3.load_target(
                target,
                "POSITION_1"
            )

        # ------------------------------------------------------
        # No command
        # ------------------------------------------------------

        else:

            axis3.hold()

    # ==========================================================
    # UPDATE FEEDBACK
    # ==========================================================

    def update_feedback(self):

        # ------------------------------------------------------
        # Current positions
        # ------------------------------------------------------

        plc.write(
            axis1.position_register,
            round(axis1.position)
        )

        plc.write(
            axis2.position_register,
            round(axis2.position)
        )

        plc.write(
            axis3.position_register,
            round(axis3.position)
        )

        # ------------------------------------------------------
        # Motion CPU feedback
        # ------------------------------------------------------

        plc.write(
            axis1.feedback_register,
            round(axis1.position)
        )

        plc.write(
            axis2.feedback_register,
            round(axis2.position)
        )

        plc.write(
            axis3.feedback_register,
            round(axis3.position)
        )

        # ------------------------------------------------------
        # Actual speed registers
        # ------------------------------------------------------

        if axis1.speed_register:

            plc.write(
                axis1.speed_register,
                round(axis1.speed)
            )

        if axis2.speed_register:

            plc.write(
                axis2.speed_register,
                round(axis2.speed)
            )

        if axis3.speed_register:

            plc.write(
                axis3.speed_register,
                round(axis3.speed)
            )

        # ------------------------------------------------------
        # Error registers
        # ------------------------------------------------------

        if axis1.error_register:

            plc.write(
                axis1.error_register,
                int(axis1.error)
            )

        if axis2.error_register:

            plc.write(
                axis2.error_register,
                int(axis2.error)
            )

        if axis3.error_register:

            plc.write(
                axis3.error_register,
                int(axis3.error)
            )

    # ==========================================================
    # POSITION COMPLETE BITS
    # ==========================================================

    def update_complete_bits(self):

        plc.write(
            axis1.complete_bit,
            int(axis1.complete)
        )

        plc.write(
            axis2.complete_bit,
            int(axis2.complete)
        )

        plc.write(
            axis3.complete_bit,
            int(axis3.complete)
        )

    # ==========================================================
    # READY / BUSY STATUS
    # ==========================================================

    def update_ready_bits(self):

        axis1.ready = not axis1.busy
        axis2.ready = not axis2.busy
        axis3.ready = not axis3.busy

        plc.write(
            axis1.ready_bit,
            int(axis1.ready)
        )

        plc.write(
            axis2.ready_bit,
            int(axis2.ready)
        )

        plc.write(
            axis3.ready_bit,
            int(axis3.ready)
        )

        # ------------------------------------------------------
        # Global servo status
        # ------------------------------------------------------

        servo_busy = (
            axis1.busy
            or axis2.busy
            or axis3.busy
        )

        servo_ready = (
            axis1.ready
            and axis2.ready
            and axis3.ready
        )

        servo_error = (
            axis1.error
            or axis2.error
            or axis3.error
        )

        plc.write(
            "L712",
            int(servo_busy)
        )

        plc.write(
            "L710",
            int(servo_ready)
        )

        plc.write(
            "L714",
            int(servo_error)
        )

        plc.write(
            "L718",
            int(
                axis1.complete
                or axis2.complete
                or axis3.complete
            )
        )

    # ==========================================================
    # ORIGIN COMPLETE
    # ==========================================================

    def update_origin_complete(self):

        origin_complete = (

            abs(axis1.position) < 0.001

            and

            abs(axis2.position) < 0.001

            and

            abs(axis3.position) < 0.001
        )

        plc.write(
            "L704",
            int(origin_complete)
        )

        plc.write(
            "L720",
            int(origin_complete)
        )

    # ==========================================================
    # AXIS TELEMETRY
    # ==========================================================

    def telemetry(self):

        return {

            "axis1": axis1.telemetry(),

            "axis2": axis2.telemetry(),

            "axis3": axis3.telemetry(),

            "model": self.last_model,

            "scan_count": self.scan_count
        }

    # ==========================================================
    # SERVO UPDATE
    # ==========================================================

    def update(self):

        now = time.monotonic()

        dt = (
            now
            - self.last_update_time
        )

        self.last_update_time = now

        # Keep simulator stable
        dt = max(
            0.001,
            min(dt, 0.2)
        )

        self.scan_count += 1

        # ------------------------------------------------------
        # Current model
        # ------------------------------------------------------

        model = self.selected_model()

        # ------------------------------------------------------
        # Read actual engineering parameters
        # ------------------------------------------------------

        self.update_parameters()

        # ------------------------------------------------------
        # Generate commands
        # ------------------------------------------------------

        self.update_axis1(model)

        self.update_axis2(model)

        self.update_axis3(model)

        # ------------------------------------------------------
        # Execute motion
        # ------------------------------------------------------

        axis1.move(dt)

        axis2.move(dt)

        axis3.move(dt)

        # ------------------------------------------------------
        # Write live PLC feedback
        # ------------------------------------------------------

        self.update_feedback()

        # ------------------------------------------------------
        # Status bits
        # ------------------------------------------------------

        self.update_complete_bits()

        self.update_ready_bits()

        self.update_origin_complete()


# ==============================================================
# SERVO ENGINE INSTANCE
# ==============================================================

servo = ServoEngine()