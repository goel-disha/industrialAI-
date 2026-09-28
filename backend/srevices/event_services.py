from backend.machine.event_engine import event_engine


def get_events(limit=20):

    return {
        "events": event_engine.get_events(limit)
    }


def clear_events():

    event_engine.clear()

    return {
        "status": "success",
        "message": "Event history cleared"
    }