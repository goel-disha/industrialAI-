from backend.machine.plc_memory import plc


class DeviceService:

    # ==========================================================
    # Read one device
    # ==========================================================

    def read(self, address):

        value = plc.read(address)

        if value is None:
            return None

        try:
            return int(value)

        except (ValueError, TypeError):
            return value

    # ==========================================================
    # Read multiple devices
    # ==========================================================

    def read_many(self, addresses):

        result = {}

        for address in addresses:

            result[address] = self.read(address)

        return result

    # ==========================================================
    # ALL DEVICES
    # ==========================================================

    def devices(self):

        result = []

        for address, value in plc.memory.items():

            try:
                numeric_value = int(value)
            except (ValueError, TypeError):
                numeric_value = value

            result.append({
                "address": address,
                "value": numeric_value,
                "active": (
                    numeric_value != 0
                    if isinstance(numeric_value, int)
                    else False
                )
            })

        result.sort(
            key=lambda item: item["address"]
        )

        return {
            "count": len(result),
            "devices": result
        }

    # ==========================================================
    # Servo Runtime Status
    #
    # Uses YOUR existing servo registers.
    # ==========================================================

    def servo_status(self):

        return {

            "axis1": {
                "position": self.read("D1100"),
                "complete": self.read("L610"),
                "ready": self.read("L700")
            },

            "axis2": {
                "position": self.read("D1110"),
                "complete": self.read("L611"),
                "ready": self.read("L701")
            },

            "axis3": {
                "position": self.read("D1120"),
                "complete": self.read("L612"),
                "ready": self.read("L702")
            }
        }

    # ==========================================================
    # Model Position Registers
    #
    # IMPORTANT:
    # These are the registers already used by your
    # current ServoEngine.
    # ==========================================================

    def model_positions(self, model):

        if model < 1 or model > 12:

            return {
                "status": "error",
                "message": "Model must be between 1 and 12"
            }

        offset = (model - 1) * 10

        registers = {

            "axis1": {
                "pos1": f"D{300 + offset}",
                "pos2": f"D{306 + offset}"
            },

            "axis2": {
                "pos1": f"D{500 + offset}",
                "pos2": f"D{506 + offset}"
            },

            "axis3": {
                "pos1": f"D{700 + offset}",
                "pos2": f"D{706 + offset}"
            }
        }

        return {

            "model": model,

            "registers": registers,

            "positions": {

                "axis1": {
                    "pos1": self.read(
                        registers["axis1"]["pos1"]
                    ),
                    "pos2": self.read(
                        registers["axis1"]["pos2"]
                    )
                },

                "axis2": {
                    "pos1": self.read(
                        registers["axis2"]["pos1"]
                    ),
                    "pos2": self.read(
                        registers["axis2"]["pos2"]
                    )
                },

                "axis3": {
                    "pos1": self.read(
                        registers["axis3"]["pos1"]
                    ),
                    "pos2": self.read(
                        registers["axis3"]["pos2"]
                    )
                }
            }
        }

    # ==========================================================
    # Complete Machine Snapshot
    # ==========================================================

    def snapshot(self, model=1):

        return {

            "model": model,

            "servo": self.servo_status(),

            "positions": self.model_positions(
                model
            )
        }


# ==========================================================
# GLOBAL SERVICE
# ==========================================================

device_service = DeviceService()