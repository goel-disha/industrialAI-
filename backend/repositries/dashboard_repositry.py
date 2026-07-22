from backend.machine.machine_engine import engine
from backend.machine.production_engine import production
from backend.machine.servo_engine import servo
from backend.machine.event_engine import event_engine


def get_dashboard():

    return {

        "machine": engine.dashboard(),

        "production": {

            "boxes_today": production.boxes_today,

            "good_boxes": production.good_boxes,

            "rejected_boxes": production.rejected_boxes,

            "cycle_time": production.average_cycle_time,

            "efficiency": production.efficiency()

        },

        "servo": servo.status(),

        "events": event_engine.latest(10)

    }