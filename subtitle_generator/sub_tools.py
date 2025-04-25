# subtitle_generator/sub_tools.py

import os
import pysrt
import logging
import ffmpeg
import subprocess

class SubTools:
    """
    A class to manage subtitle-related operations such as checking,
    formatting, realigning, and removing subtitles.
    """

    @staticmethod
    def has_external_subtitles(file_path, output_extension=".srt"):
        """
        Checks if an external subtitle file exists for the given video.

        Args:
            file_path (str): Path to the video file.
            output_extension (str): Subtitle file extension (default is .srt).

        Returns:
            bool: True if an external subtitle file exists, False otherwise.
        """
        srt_path = os.path.splitext(file_path)[0] + output_extension
        exists = os.path.exists(srt_path)
        logging.info(f"Checking for external subtitles: {'Found' if exists else 'Not found'}")
        logging.debug(f"Subtitle path checked: {srt_path}")
        return exists

    @staticmethod
    def has_embedded_subtitles(file_path):
        """
        Uses ffmpeg to check if a video file has embedded subtitles.

        Args:
            file_path (str): Path to the video file.

        Returns:
            bool: True if the video contains embedded subtitles, False otherwise.
        """
        logging.info(f"Checking for embedded subtitles in {file_path}")
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-select_streams', 's:s', '-show_entries', 
                 'stream=index', '-of', 'csv=p=0', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            has_embedded = bool(result.stdout.strip())
            logging.info(f"Embedded subtitles {'found' if has_embedded else 'not found'} in {file_path}")
            return has_embedded
        except Exception as e:
            logging.error(f"Error checking embedded subtitles: {e}")
            logging.debug(f"Detailed error: {str(e)}", exc_info=True)
            return False

    @staticmethod
    def remove_subtitle_formatting(srt_path):
        """
        Removes formatting and styles from an external subtitle file.

        Args:
            srt_path (str): Path to the .srt subtitle file.

        Returns:
            None: The formatted .srt file is saved.
        """
        logging.info(f"Removing subtitle formatting from {srt_path}")
        try:
            subs = pysrt.open(srt_path)
            original_count = len(subs)
            for sub in subs:
                sub.text = sub.text.replace('<i>', '').replace('</i>', '') \
                                   .replace('<b>', '').replace('</b>', '') \
                                   .replace('<font', '').split('>')[-1] \
                                   .replace('</font>', '')
            subs.save(srt_path)
            logging.info(f"Subtitle formatting removed. Processed {original_count} subtitles.")
        except Exception as e:
            logging.error(f"Error removing subtitle formatting: {e}")
            logging.debug(f"Detailed error: {str(e)}", exc_info=True)

    @staticmethod
    def check_subtitle_alignment(video_path, srt_path):
        """
        Checks if the subtitles are properly aligned with the video timecodes.

        Args:
            video_path (str): Path to the video file.
            srt_path (str): Path to the subtitle file (.srt).

        Returns:
            bool: True if subtitles are aligned, False otherwise.
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_duration = float(probe['format']['duration'])

            subs = pysrt.open(srt_path)
            first_sub_time = subs[0].start.to_time().total_seconds()
            last_sub_time = subs[-1].end.to_time().total_seconds()

            # Check if subtitle timecodes fit within the video duration
            if first_sub_time < 0 or last_sub_time > video_duration:
                return False
            return True
        except Exception as e:
            logging.error(f"Error checking subtitle alignment: {e}")
            return False

    @staticmethod
    def realign_subtitles(video_path, srt_path, threshold_seconds=2):
        """
        Attempts to realign subtitles by shifting them if they are misaligned.

        Args:
            video_path (str): Path to the video file.
            srt_path (str): Path to the subtitle file.
            threshold_seconds (int): The maximum time shift allowed for realignment.

        Returns:
            bool: True if realignment was successful, False otherwise.
        """
        try:
            subs = pysrt.open(srt_path)
            first_sub_start = subs[0].start.to_time()

            # Shift subtitles if they are off by more than the threshold
            if abs(first_sub_start.total_seconds()) > threshold_seconds:
                for sub in subs:
                    sub.shift(seconds=-first_sub_start.total_seconds())
                subs.save(srt_path)
                return True
            return False
        except Exception as e:
            logging.error(f"Error realigning subtitles: {e}")
            return False

    @staticmethod
    def delete_subtitles(srt_path):
        """
        Deletes the subtitle file if realignment or other operations fail.

        Args:
            srt_path (str): Path to the subtitle file to delete.

        Returns:
            None: The subtitle file is deleted if it exists.
        """
        try:
            if os.path.exists(srt_path):
                os.remove(srt_path)
                logging.info(f"Deleted subtitle file: {srt_path}")
            else:
                logging.warning(f"Subtitle file not found: {srt_path}")
        except Exception as e:
            logging.error(f"Error deleting subtitle file: {e}")


# Class to handle subtitle verification for broken or misaligned subtitles
class SubtitleVerifier:
    """
    A class to handle verification and correction of broken or misaligned subtitles.
    """

    @staticmethod
    def is_subtitle_broken(srt_path):
        """
        Checks if the subtitle file is broken by analyzing durations and overlaps.

        Args:
            srt_path (str): Path to the subtitle file.

        Returns:
            bool: True if the subtitle is broken, False otherwise.
        """
        try:
            subs = pysrt.open(srt_path)
            for sub in subs:
                if sub.duration.seconds > 10 * 60:  # Arbitrary check: no subtitle should last 10+ minutes
                    return True
            return False
        except Exception as e:
            logging.warning(f"Error reading or checking subtitle file: {e}")
            return True
