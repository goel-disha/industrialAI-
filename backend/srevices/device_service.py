from backend.repositries.device_repositries import (
    get_all_devices,
    get_device,
    search_device
)


def devices():

    return get_all_devices()


def device(tag):

    return get_device(tag)


def search(keyword):

    return search_device(keyword)