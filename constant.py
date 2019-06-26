from enum import IntEnum, unique


def unique_mask(enumeration):
    for name, value in enumeration.__members__.items():
        if value ^ (value & (- value)) > 0:
            raise ValueError(f"Non-binary mask found in {enumeration}: "
                             f"{name} -> {value}")
    unique(enumeration)


@unique_mask
class UserPermission(IntEnum):
    SITE_MANAGER = 1 << 0
