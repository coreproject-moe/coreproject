from coreproject_tracker.enums import EVENT_NAMES

_EVENT_ID_MAP = {
    0: EVENT_NAMES.UPDATE,
    1: EVENT_NAMES.COMPLETE,
    2: EVENT_NAMES.START,
    3: EVENT_NAMES.STOP,
    4: EVENT_NAMES.PAUSE,
}

_EVENT_NAME_MAP = {
    "update": EVENT_NAMES.UPDATE,
    "completed": EVENT_NAMES.COMPLETE,
    "started": EVENT_NAMES.START,
    "stopped": EVENT_NAMES.STOP,
    "paused": EVENT_NAMES.PAUSE,
}


def convert_event_id_to_event_enum(event_id: int) -> EVENT_NAMES:
    event = _EVENT_ID_MAP.get(event_id)
    if event is None:
        raise ValueError("`event_id` is not supported")
    return event


def convert_event_name_to_event_enum(event_name: str | None) -> EVENT_NAMES:
    if event_name is None:
        raise ValueError("`event_name` is None")
    event = _EVENT_NAME_MAP.get(event_name.lower())
    if event is None:
        raise ValueError("`event_name` not supported")
    return event
