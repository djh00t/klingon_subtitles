# subtitle_generator/srt_generator.py

import pysrt


def seconds_to_subriptime(seconds):
    """
    Convert seconds into SubRipTime format, which is used in SRT subtitle files.

    Args:
        seconds (float): Time in seconds.

    Returns:
        SubRipTime: Time in SubRip (SRT) format.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return pysrt.SubRipTime(hours=hours, minutes=minutes, seconds=secs, milliseconds=milliseconds)


def generate_srt(segments):
    """
    Generate an SRT (SubRip Subtitle) file from transcription segments.

    Args:
        segments (list): A list of dictionaries where each dictionary represents a subtitle segment 
                         with 'start', 'end', and 'text' keys.

    Returns:
        SubRipFile: A PySRT SubRipFile object containing the generated subtitles.
    """
    subs = pysrt.SubRipFile()
    for idx, segment in enumerate(segments, start=1):
        start_seconds = segment.get('start', 0)
        end_seconds = segment.get('end', 0)
        text = segment.get('text', '').strip().replace('\n', ' ')

        # Convert start and end times from seconds to SubRipTime format
        start = seconds_to_subriptime(start_seconds)
        end = seconds_to_subriptime(end_seconds)

        # Create a new subtitle item and append it to the SRT file
        sub = pysrt.SubRipItem(index=idx, start=start, end=end, text=text)
        subs.append(sub)

    return subs
