from datetime import datetime


class EventEngine:

    def __init__(self):

        self.events = []

        self.last_state = "IDLE"
        self.last_axis1_complete = True
        self.last_axis2_complete = True
        self.last_axis3_complete = True

    # ==========================================================
    # Add Event
    # ==========================================================

    def add(self, event_type, message, severity="INFO"):

        event = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": event_type,
            "message": message,
            "severity": severity
        }

        self.events.insert(0, event)

        # Keep only latest 100 events
        self.events = self.events[:100]

    # ==========================================================
    # Monitor Machine
    # ==========================================================

    def update(self, state, axis1_complete,
               axis2_complete, axis3_complete):

        # ------------------------------------------------------
        # Machine state changed
        # ------------------------------------------------------

        if state != self.last_state:

            self.add(
                "MACHINE",
                f"Machine state changed: "
                f"{self.last_state} -> {state}"
            )

            self.last_state = state

        # ------------------------------------------------------
        # Axis 1 complete
        # ------------------------------------------------------

        if axis1_complete and not self.last_axis1_complete:

            self.add(
                "SERVO",
                "Axis 1 movement completed"
            )

        # ------------------------------------------------------
        # Axis 2 complete
        # ------------------------------------------------------

        if axis2_complete and not self.last_axis2_complete:

            self.add(
                "SERVO",
                "Axis 2 movement completed"
            )

        # ------------------------------------------------------
        # Axis 3 complete
        # ------------------------------------------------------

        if axis3_complete and not self.last_axis3_complete:

            self.add(
                "SERVO",
                "Axis 3 movement completed"
            )

        self.last_axis1_complete = axis1_complete
        self.last_axis2_complete = axis2_complete
        self.last_axis3_complete = axis3_complete

    # ==========================================================
    # Get Events
    # ==========================================================

    def get_events(self, limit=20):

        return self.events[:limit]

    # ==========================================================
    # Clear Events
    # ==========================================================

    def clear(self):

        self.events.clear()

        self.last_state = "IDLE"

        self.last_axis1_complete = True
        self.last_axis2_complete = True
        self.last_axis3_complete = True


event_engine = EventEngine()