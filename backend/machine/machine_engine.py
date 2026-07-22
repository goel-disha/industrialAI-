from datetime import datetime

from backend.machine.motion_controller import motion
from backend.machine.event_engine import event_engine
from backend.machine.production_engine import production
from backend.machine.servo_engine import servo


class MachineEngine:

    def __init__(self):

        self.previous_state = ""

    #########################################################

    def update(self):

        """
        One machine scan cycle
        """

        motion.update()

        state = motion.state.name

        if state != self.previous_state:

            event_engine.log(state)

            self.previous_state = state

    #########################################################

    def value(self, tag):

        """
        Read simulated PLC memory
        """

        return motion.read_tag(tag)

    #########################################################

    def dashboard(self):

        return {

            "machine": "AUTO TAPPING",

            "state": motion.state.name,

            "ready": motion.ready,

            "busy": motion.busy,

            "error": motion.error,

            "servo_on": motion.servo_on,

            "boxes_today": production.boxes_today,

            "good_boxes": production.good_boxes,

            "rejected_boxes": production.rejected_boxes,

            "current_cycle": production.current_cycle,

            "cycle_time": production.average_cycle_time,

            "efficiency": production.efficiency(),

            "axis_position": servo.position,

            "axis_speed": servo.speed,

            "updated_at": datetime.now().strftime("%H:%M:%S")

        }


engine = MachineEngine()