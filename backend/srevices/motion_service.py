from backend.repositries.motion_repositry import(

    get_motion,
    search_motion
)

def motion():

    return get_motion()

def search(keyword):
    return search_motion(keyword)