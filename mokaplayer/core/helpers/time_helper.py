def seconds_to_string(duration):
    """Convert a time in seconds to a mm:ss string
    """
    if duration is None:
        return '00:00'

    minutes = int(duration // 60)
    seconds = int(duration % 60)

    return '{:02d}:{:02d}'.format(minutes, seconds)
