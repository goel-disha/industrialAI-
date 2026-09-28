from backend.repositries.engineering_repository import (
    get_programs,
    get_statements,
    get_network,
    get_timers,
    get_servo_constants,
    search_engineering
)


##############################################################
# Complete Engineering Data
##############################################################

def engineering():

    return {

        "programs": get_programs(),

        "statements": get_statements(),

        "network": get_network(),

        "timers": get_timers(),

        "servo_constants": get_servo_constants()

    }


##############################################################
# Programs
##############################################################

def programs():

    return get_programs()


##############################################################
# Statements
##############################################################

def statements():

    return get_statements()


##############################################################
# Network
##############################################################

def network():

    return get_network()


##############################################################
# Timers
##############################################################

def timers():

    return get_timers()


##############################################################
# Servo Constants
##############################################################

def servo_constants():

    return get_servo_constants()


##############################################################
# Engineering Search
##############################################################

def engineering_search(keyword):

    return search_engineering(keyword)