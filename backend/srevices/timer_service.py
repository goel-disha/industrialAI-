from backend.repositries.timer_repositry import(
    get_timers,
    search_timer
)

def timer():

    return get_timers()

def search(keyword):

    return search_timer(keyword)