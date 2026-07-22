from backend.repositries.device_repositries import search_device
from backend.repositries.program_repositry import search_program
from backend.repositries.motion_repositry import search_motion
from backend.repositries.position_repositry import search_position
from backend.repositries.timer_repositry import search_timer
from backend.repositries.statement_repositry import search_statement
from backend.repositries.network_repositry import search_network

def search(keyword):

    return {

        "devices": search_device(keyword),

        "motion": search_motion(keyword),

        "positions": search_position(keyword),

        "timers": search_timer(keyword),

        "programs": search_program(keyword),

        "statements": search_statement(keyword),

        "network": search_network(keyword)

    }