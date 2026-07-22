from backend.machine.plc_memory import plc


class ServoEngine:

    def __init__(self):

        self.home_position = 0
        self.bottom_position = 200000

        self.position = self.home_position
        self.target = self.home_position

        self.speed = 5000

    ###################################################

    def move_down(self):

        self.target = self.bottom_position

    ###################################################

    def move_up(self):

        self.target = self.home_position

    ###################################################

    def update(self):
      
      if self.position < self.target:
        self.position = min(
            self.position + self.speed,
            self.target
        )

      elif self.position > self.target:
        self.position = max(
            self.position - self.speed,
            self.target
        )

      plc.write("D100", self.position)


    ###################################################

    def at_bottom(self):

        return self.position >= self.bottom_position

    ###################################################

    def at_home(self):

        return self.position <= self.home_position
    
    def status(self):
        return {
        "position": self.position,
        "target": self.target,
        "home": self.at_home(),
        "bottom": self.at_bottom(),
        "moving": self.position != self.target
    }


servo = ServoEngine()