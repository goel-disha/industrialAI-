from backend.repositries.program_repositry import(

    get_programs,
    search_program
)

def programs():

    return get_programs()

def search(keyword):

    return search_program(keyword)