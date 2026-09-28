from backend.machine.plc_memory import plc


class ProductionEngine:

    def __init__(self):

        self.total_cycles = 0
        self.completed_cycles = 0
        self.rejected_cycles = 0

        self.current_cycle = 0
        self.cycle_running = False
        self.cycle_complete = False

        self.previous_state = "IDLE"

    # ==========================================================
    # Start Cycle
    # ==========================================================

    def start_cycle(self):

        if not self.cycle_running:

            self.cycle_running = True
            self.cycle_complete = False

            self.current_cycle += 1
            self.total_cycles += 1

    # ==========================================================
    # Complete Cycle
    # ==========================================================

    def complete_cycle(self):

        if self.cycle_running:

            self.cycle_running = False
            self.cycle_complete = True

            self.completed_cycles += 1

    # ==========================================================
    # Reject Cycle
    # ==========================================================

    def reject_cycle(self):

        if self.cycle_running:

            self.cycle_running = False
            self.cycle_complete = True

            self.rejected_cycles += 1

    # ==========================================================
    # Update
    # ==========================================================

    def update(self, machine_state):

        # New cycle started
        if (
            machine_state != "IDLE"
            and self.previous_state == "IDLE"
        ):
            self.start_cycle()

        # Cycle completed
        elif (
            machine_state == "IDLE"
            and self.previous_state != "IDLE"
            and self.cycle_running
        ):
            self.complete_cycle()

        self.previous_state = machine_state

    # ==========================================================
    # Reset
    # ==========================================================

    def reset(self):

        self.total_cycles = 0
        self.completed_cycles = 0
        self.rejected_cycles = 0

        self.current_cycle = 0
        self.cycle_running = False
        self.cycle_complete = False

        self.previous_state = "IDLE"

    # ==========================================================
    # Dashboard Data
    # ==========================================================

    def get_status(self):

        return {
            "total_cycles": self.total_cycles,
            "completed_cycles": self.completed_cycles,
            "rejected_cycles": self.rejected_cycles,
            "current_cycle": self.current_cycle,
            "cycle_running": self.cycle_running,
            "cycle_complete": self.cycle_complete,
        }


production = ProductionEngine()