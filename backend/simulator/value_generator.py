from backend.machine.motion_controller import motion

def generate(tag):
    return motion.read_tag(tag)