from backend.repositries.position_repositry import(

    get_positions,
    search_position
)

def position():

    return get_positions()

def search(keyword):
    return search_position(keyword)