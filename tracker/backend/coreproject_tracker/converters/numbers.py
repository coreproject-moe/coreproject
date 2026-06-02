_all_ = ["convert_str_int_to_float"]


def convert_str_int_to_float(num: str | int | None) -> float | None:
    return float(num) if num else None
