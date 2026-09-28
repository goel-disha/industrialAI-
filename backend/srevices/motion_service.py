from backend.repositries.motion_repositry import (
    get_runtime,
    get_parameters,
    get_registers,
    get_register,
    get_axis_registers
)


##############################################################
# Complete Motion Module
##############################################################

def motion():

    return {

        "axis_runtime": get_runtime(),

        "parameters": get_parameters(),

        "registers": get_registers()

    }


##############################################################
# Axis Runtime
##############################################################

def runtime():

    return get_runtime()


##############################################################
# Motion Parameters
##############################################################

def parameters():

    return get_parameters()


##############################################################
# Motion Registers
##############################################################

def registers():

    return get_registers()


##############################################################
# Single Motion Register
##############################################################

def register(address):

    return get_register(address)


##############################################################
# Registers of One Axis
##############################################################

def axis_registers(axis):

    return get_axis_registers(axis)