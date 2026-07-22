from datetime import datetime

from backend.repositries.live_repositry import (
    get_all_live,
    get_live,
    update_live
)


def live():

    return get_all_live()


def live_tag(tag):

    return get_live(tag)


def update(tag, value):

    timestamp = datetime.now().isoformat()

    update_live(tag, value, timestamp)