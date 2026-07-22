from backend.repositries.network_repositry import(

    get_network,
    search_network
)

def network():

    return get_network()

def search(keyword):
    return search_network(keyword)