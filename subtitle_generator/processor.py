# subtitle_generator/processor.py

import os
import subprocess
import logging
from moviepy.editor import VideoFileClip
from transformers import pipeline
from pyannote.audio import Pipeline as DiarizationPipeline
from subtitle_generator.srt_generator import generate_srt
from subtitle_generator.sub_tools import SubTools, SubtitleVerifier
from subtitle_generator.utils import get_device

class Processor:
    """
    Class to handle the processing of video files for subtitle generation,
    including transcription, speaker detection, and subtitle realignment.
    """

    def __init__(self, config):
        """
        Initialize the processor with configuration and sub-tools.

        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.sub_tools = SubTools()
        self.model_cache = {}
        self.device = get_device()
        logging.info("Processor initialized with configuration")
        logging.debug(f"Processor configuration: {config}")

    def get_transcription_pipeline(self, model_name):
        """
        Load the Hugging Face ASR model pipeline.

        Args:
            model_name (str): The name of the Hugging Face ASR model.

        Returns:
            Pipeline: Hugging Face model pipeline for automatic speech recognition.
        """
        if model_name not in self.model_cache:
            logging.info(f"Loading Hugging Face model: {model_name}")
            logging.debug(f"Device for model: {self.device}")
            token = os.getenv('HUGGINGFACE_TOKEN')
            if token:
                self.model_cache[model_name] = pipeline(
                    "automatic-speech-recognition", 
                    model=model_name, 
                    use_auth_token=token, 
                    device=0 if self.device != "cpu" else -1,
                    language='en'
                ),
                language='en'
            else:
                self.model_cache[model_name] = pipeline(
                    "automatic-speech-recognition", 
                    model=model_name, 
                    device=0 if self.device != "cpu" else -1
                )
        return self.model_cache[model_name]

    def extract_audio(self, file_path, temp_audio_path=None):
        """
        Extract the audio track from the video file and save it alongside the video.

        Args:
            file_path (str): Path to the video file.
            temp_audio_path (str): Optional path to store the temporary extracted audio.

        Returns:
            str: Path to the extracted audio file, or None on failure.
        """
        if not os.path.exists(file_path):
            logging.error(f"File does not exist: {file_path}")
            return None

        base_name = os.path.splitext(file_path)[0]
        temp_audio_path = temp_audio_path or f"{base_name}_temp_audio.wav"
        
        logging.info(f"Extracting audio from {file_path} to {temp_audio_path}")
        if not os.path.exists(file_path):
            logging.error(f"File does not exist: {file_path}")
            return None

        try:
            if file_path.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                video = VideoFileClip(file_path)
                video.audio.write_audiofile(temp_audio_path, codec='pcm_s16le')
                video.close()
            elif file_path.lower().endswith(('.mp3', '.wav', '.aac', '.flac')):
                # If it's already an audio file, just copy it
                subprocess.run(['cp', file_path, temp_audio_path], check=True)
            else:
                logging.warning(f"Unsupported file type: {file_path}")
                return None
            return temp_audio_path
        except Exception as e:
            logging.error(f"Error extracting audio: {e}")
            return None

    def get_speaker_diarization_pipeline(self):
        """
        Load the speaker diarization model pipeline from pyannote.

        Returns:
            Pipeline: Pyannote speaker diarization pipeline.
        """
        return DiarizationPipeline.from_pretrained("pyannote/speaker-diarization", device=self.device)

    def perform_speaker_diarization(self, temp_audio):
        """
        Perform speaker diarization on the given audio file.

        Args:
            temp_audio (str): Path to the temporary audio file.

        Returns:
            Iterable: Diarization results with speaker segments.
        """
        diarization_pipeline = self.get_speaker_diarization_pipeline()
        return diarization_pipeline(temp_audio)

    def process_file(self, file_path, output_extension=".srt"):
        """
        Process the video file to generate subtitles.

        Args:
            file_path (str): Path to the video file.
            output_extension (str): Extension for the output subtitle file.
        """
        logging.info(f"Starting processing of file: {file_path}")

        # Check if external subtitles already exist
        if self.sub_tools.has_external_subtitles(file_path, output_extension):
            logging.info(f"External subtitles already exist for {file_path}. Skipping processing.")
            return
        
        logging.info("Extracting audio from video file")
        temp_audio = self.extract_audio(file_path)
        if not temp_audio:
            logging.error(f"Failed to extract audio from {file_path}")
            return

        model_name = self.config.get('huggingface_model', 'openai/whisper-large')
        logging.info(f"Using ASR model: {model_name}")
        pipeline_asr = self.get_transcription_pipeline(model_name)

        try:
            logging.info("Starting transcription process")
            past_key_values = None  # Initialize past_key_values
            # Perform transcription
            logging.debug("Performing ASR transcription")
            transcription = pipeline_asr(temp_audio, chunk_length_s=30)
            logging.debug(f"Transcription completed. Text length: {len(transcription['text'])}")

            logging.info("Starting speaker diarization process")
            logging.debug("Performing speaker diarization")
            diarization = self.perform_speaker_diarization(temp_audio)

            logging.info("Processing diarization results")
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    'start': turn.start,
                    'end': turn.end,
                    'text': f"Speaker {speaker}: {transcription['text']}"  # Replace with relevant transcription text for the segment
                })
            logging.debug(f"Processed {len(segments)} diarization segments")

            # Generate and save SRT file
            logging.info("Generating SRT file")
            subs = generate_srt(segments)
            srt_path = os.path.splitext(file_path)[0] + output_extension
            subs.save(srt_path, encoding='utf-8')
            logging.info(f"SRT file generated with speaker detection: {srt_path}")
        except Exception as e:
            logging.error(f"Error during transcription or speaker diarization: {e}")
            logging.debug(f"Detailed error information: {str(e)}", exc_info=True)
            return
        finally:
            if os.path.exists(temp_audio):
                logging.debug(f"Removing temporary audio file: {temp_audio}")
                os.remove(temp_audio)


    def strip_embedded_subtitles(self, file_path):
        """
        Strip embedded subtitles from a video file using ffmpeg.

        Args:
            file_path (str): Path to the video file.

        Returns:
            str: Path to the video file without embedded subtitles.
        """
        try:
            output_file = os.path.splitext(file_path)[0] + '_nosubs' + os.path.splitext(file_path)[1]
            subprocess.run([
                'ffmpeg', '-i', file_path, '-map', '0:v', '-map', '0:a', 
                '-c', 'copy', '-c:s', 'none', output_file
            ], check=True)
            logging.info(f"Created video without subtitles: {output_file}")
            return output_file
        except Exception as e:
            logging.error(f"Error stripping subtitles: {e}")
            return None

    def realign_or_delete_broken_subtitles(self, file_path, output_extension=".srt"):
        """
        Realign or delete broken subtitles if they are not aligned with the video.

        Args:
            file_path (str): Path to the video file.
            output_extension (str): Extension of the subtitle file.
        """
        srt_path = os.path.splitext(file_path)[0] + output_extension
        if not self.sub_tools.check_subtitle_alignment(file_path, srt_path):
            logging.info(f"Subtitles are not aligned for {file_path}. Attempting to realign...")
            if not self.sub_tools.realign_subtitles(file_path, srt_path):
                logging.info(f"Failed to realign subtitles. Deleting...")
                self.sub_tools.delete_subtitles(srt_path)

    def handle_broken_subtitles(self, file_path, output_extension=".srt"):
        """
        Handle broken subtitles by deleting and regenerating them.

        Args:
            file_path (str): Path to the video file.
            output_extension (str): Extension for the subtitle file.
        """
        srt_path = os.path.splitext(file_path)[0] + output_extension
        if SubtitleVerifier.is_subtitle_broken(srt_path):
            logging.info(f"Broken subtitles detected for {file_path}. Deleting and regenerating...")
            os.remove(srt_path)
            self.process_file(file_path, output_extension)
