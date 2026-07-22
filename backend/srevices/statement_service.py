from backend.repositries.statement_repositry import(
    get_statements,
    search_statement
)

def statement():

    return get_statements()

def search(keyword):

     return search_statement(keyword)