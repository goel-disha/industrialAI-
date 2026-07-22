from backend.repositries.device_repositries import get_all_devices
from backend.repositries.motion_repositry import get_motion
from backend.repositries.position_repositry import get_positions
from backend.repositries.program_repositry import get_programs
from backend.repositries.timer_repositry import get_timers
from backend.repositries.network_repositry import get_network


def explorer():

    return {

        "project": "AUTO_TAPPING",

        "folders":[

            {

                "name":"Devices",

                "count":len(get_all_devices())

            },

            {

                "name":"Programs",

                "count":len(get_programs())

            },

            {

                "name":"Motion",

                "count":len(get_motion())

            },

            {

                "name":"Positions",

                "count":len(get_positions())

            },

            {

                "name":"Timers",

                "count":len(get_timers())

            },

            {

                "name":"Network",

                "count":len(get_network())

            }

        ]

    }