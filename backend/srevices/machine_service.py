from backend.machine.motion_controller import motion
from backend.machine.production_engine import production
from backend.machine.servo_engine import servo


def status():

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

        "average_cycle_time": production.average_cycle_time,

        "efficiency": production.efficiency(),

        "servo": servo.status()

    }