import time

from backend.repositries.device_repositries import get_all_devices

from backend.srevices.live_service import update

from backend.machine.machine_engine import engine


def run():

    print("Simulator Started...")

    while True:

     engine.update()

     devices = get_all_devices()

     for device in devices:

        value = engine.value(device["tag"])

        update(device["tag"], value)

     time.sleep(1)


if __name__ == "__main__":

    run()