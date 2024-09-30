import shortuuid


def generate_short_uuid():
    return shortuuid.ShortUUID().random(length=8)
