from enum import Enum
from backend.machine.servo_engine import servo
from backend.machine.production_engine import production
from backend.machine.event_engine import event_engine


class MotionState(Enum):

    READY = "READY"

    WAITING = "WAITING"

    BOX_DETECTED = "BOX_DETECTED"

    CONVEYOR_STOPPED = "CONVEYOR_STOPPED"

    POSITIONING = "POSITIONING"

    TAPPING = "TAPPING"

    RETURN_HOME = "RETURN_HOME"

    COMPLETE = "COMPLETE"

    ERROR = "ERROR"


class MotionController:

    def __init__(self):

        self.state = MotionState.READY

        ####################################################

        # PLC Inputs (Motion -> PLC)

        self.ready = True

        self.busy = False

        self.error = False

        self.start_complete = False

        self.position_complete = False

        ####################################################

        # PLC Outputs (PLC -> Motion)

        self.plc_ready = False

        self.servo_on = False

        self.position_start = False

        self.axis_stop = False

        self.forward_jog = False

        self.reverse_jog = False

        self.status = False

        ####################################################

        self.target_position = 200000

    ###########################################################

    def update(self):

        if self.state == MotionState.READY:

           self.ready = True
           self.busy = False

           self.state = MotionState.WAITING

           return

        #######################################################

        if self.state == MotionState.WAITING:

            self.start_cycle()

            return

        #######################################################

        if self.state == MotionState.BOX_DETECTED:

            self.state = MotionState.CONVEYOR_STOPPED

            event_engine.log("BOX DETECTED")

            return

        #######################################################

        if self.state == MotionState.CONVEYOR_STOPPED:

            self.position_start = True

            self.busy = True

            self.start_complete = True

            servo.move_down()

            self.state = MotionState.POSITIONING

            event_engine.log("POSITION START")

            return

        #######################################################

        if self.state == MotionState.POSITIONING:

            servo.update()

            if servo.at_bottom():

                self.busy = False

                self.position_complete = True

                self.state = MotionState.TAPPING

                event_engine.log("POSITION COMPLETE")

            return

        #######################################################

        if self.state == MotionState.TAPPING:

            self.state = MotionState.RETURN_HOME

            servo.move_up()

            event_engine.log("AUTO TAPPING")

            return

        #######################################################

        if self.state == MotionState.RETURN_HOME:

            servo.update()

            if servo.at_home():

                production.cycle_finished()

                self.state = MotionState.COMPLETE

                event_engine.log("HOME POSITION")

            return

        #######################################################

        if self.state == MotionState.COMPLETE:

           self.busy = False

           self.ready = True

           self.position_complete = False

           self.start_complete = False

           self.position_start = False

           self.state = MotionState.WAITING

           return

    ###########################################################

    def start_cycle(self):

        if self.state == MotionState.WAITING:

            production.cycle_started()

            self.state = MotionState.BOX_DETECTED

    ###########################################################

    def emergency_stop(self):

        self.axis_stop = True

        self.busy = False

        self.error = True

        self.state = MotionState.ERROR

        event_engine.log("EMERGENCY")

    ###########################################################

    def reset(self):

        self.axis_stop = False

        self.error = False

        self.busy = False

        self.ready = True

        self.state = MotionState.WAITING

    ###########################################################

    def dashboard(self):

        return {

            "state": self.state.name,

            "ready": self.ready,

            "busy": self.busy,

            "error": self.error,

            "servo_on": self.servo_on,

            "position": servo.position,

            "speed": servo.speed,

            "boxes_today": production.boxes_today,

            "cycle_time": production.average_cycle_time,

            "efficiency": production.efficiency()

        }
    
    ###########################################################

    def read_tag(self, tag):

        from backend.machine.plc_memory import plc

        return plc.read(tag)
  

motion = MotionController()
