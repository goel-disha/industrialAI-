from datetime import datetime


class ProductionEngine:

    def __init__(self):

        self.boxes_today = 0

        self.good_boxes = 0

        self.rejected_boxes = 0

        self.current_cycle = 0

        self.total_cycle_time = 0.0

        self.average_cycle_time = 0.0

        self.machine_start = datetime.now()

        self.last_cycle_start = datetime.now()

        self.machine_running = True

    ########################################################

    def cycle_started(self):

        self.last_cycle_start = datetime.now()

    ########################################################

    def cycle_finished(self):

        self.current_cycle += 1

        self.boxes_today += 1

        self.good_boxes += 1

        cycle = (

            datetime.now() -

            self.last_cycle_start

        ).total_seconds()

        self.total_cycle_time += cycle

        self.average_cycle_time = (

            self.total_cycle_time /

            self.current_cycle

        )

    ########################################################

    def reject_box(self):

        self.rejected_boxes += 1

    ########################################################

    def uptime(self):

        return (

            datetime.now() -

            self.machine_start

        ).total_seconds()

    ########################################################

    def efficiency(self):

        total = self.good_boxes + self.rejected_boxes

        if total == 0:

            return 100

        return round(

            (self.good_boxes / total) * 100,

            2

        )

    ########################################################

    def summary(self):

        return {

            "boxes_today": self.boxes_today,

            "good_boxes": self.good_boxes,

            "rejected_boxes": self.rejected_boxes,

            "current_cycle": self.current_cycle,

            "average_cycle_time": round(

                self.average_cycle_time,

                2

            ),

            "uptime": round(

                self.uptime(),

                1

            ),

            "efficiency": self.efficiency()

        }


production = ProductionEngine()