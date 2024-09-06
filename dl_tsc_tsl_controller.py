from pytubefix import YouTube, request, exceptions
import os
import whisper
from utils import filename, write_srt
import pysrt
import tempfile
import ffmpeg
from translate_s_runner import run
import datetime


DOMAIN_NAME = "www.youtube.com/watch?v="
DOWNLOAD_PATH = ".\downloaded"
OUTPUT_PATH = ".\output"


class StepOneController:
    def __init__(self, view):
        self.view = view

    def handle_progress(self, stream, chunk, bytes_remaining):
        chunkSize = len(chunk)
        total_size = stream.filesize

        if (chunkSize >= total_size):
            self.view.update_pb_progress(100.0)
        else:
            bytes_downloaded = total_size - bytes_remaining
            download_percentage = (bytes_downloaded / total_size) * 100
            self.view.update_pb_progress(download_percentage)

    def handle_complete(self, stream, downloaded_file_path):
        self.view.update_lbl_msg(f"✓ Video Downloaded!")
        self.view.update_tsc_lbl_msg(downloaded_file_path)
        self.view.update_btn_state("normal")

    def download(self, vid):
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)

        if len(vid) > 0 and DOMAIN_NAME in vid:
            self.view.update_btn_state("disabled")

            self.view.update_pb_progress(0.0)

            try:
                yt_obj = YouTube(vid)
            except exceptions.VideoUnavailable:
                self.view.update_lbl_msg(
                    f'Video {vid} is unavaialable, skipping.')
            else:
                print(f'Downloading video: {vid}')
                yt_obj.register_on_progress_callback(self.handle_progress)
                yt_obj.register_on_complete_callback(self.handle_complete)

                filters = yt_obj.streams.filter(
                    progressive=True, file_extension='mp4')

                # download the highest quality video
                filters.get_highest_resolution().download(
                    output_path=DOWNLOAD_PATH, skip_existing=False)
        else:
            self.view.update_lbl_msg("URL is not valid.")

    def get_audio(self, path):
        temp_dir = tempfile.gettempdir()

        self.view.update_tsc_lbl_msg(f"Extracting audio file...")
        output_path = os.path.join(temp_dir, f"{filename(path)}.wav")

        ffmpeg.input(path).output(
            output_path,
            acodec="pcm_s16le", ac=1, ar="16k"
        ).run(quiet=True, overwrite_output=True)

        audio_paths = {}
        audio_paths[path] = output_path

        return audio_paths

    def tsc(self, downloaded_path):
        audio = self.get_audio(downloaded_path)
        self.view.update_tsc_lbl_msg("Audio file extracted...")

        os.makedirs(OUTPUT_PATH, exist_ok=True)
        model = whisper.load_model("medium")

        path = list(audio.keys())[0]
        audio_path = audio[path]
        srt_path = os.path.join(OUTPUT_PATH, f"{filename(path)}.srt")

        self.view.update_tsc_lbl_msg(f"Generating subtitles...")
        result = model.transcribe(audio_path)

        with open(srt_path, "w", encoding="utf-8") as srt:
            write_srt(result["segments"], file=srt)

        self.view.update_tsc_lbl_msg("✓ SRT file wrote to output folder.")
        self.view.update_tsl_lbl_msg(srt_path)

    def tsl(self, srt_path):
        srt_path_translated = os.path.join(
            OUTPUT_PATH, f"{filename(srt_path)}_t.srt")

        subs = pysrt.open(srt_path)

        tsl_lang = "Chinese(Simplified)"
        if len(tsl_lang) > 0:
            self.view.update_tsl_lbl_msg("Translating subtitles...")
            result_translated = run(subs, tsl_lang)
            new_subs = pysrt.SubRipFile(result_translated)
            new_subs.save(srt_path_translated)
            self.view.update_tsl_lbl_msg(
                "✓ Translated subtitle wrote to output folder.")

    def atc(self, v_path):
        sub_file_path = os.path.join(OUTPUT_PATH, f"{filename(v_path)}_t.srt")
        print(f"{v_path} /n")
        print(sub_file_path)
        dt_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        out_path = os.path.join(
            OUTPUT_PATH, f"{filename(v_path)}_{dt_str}.mp4")

        self.view.update_lbl_s_path(
            f"Adding subtitles to {filename(v_path)}...")

        video = ffmpeg.input(v_path)
        audio = video.audio

        # v4+ (ASS) Style Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
        ffmpeg.concat(
            video.filter('subtitles', sub_file_path, force_style="Fontname=KaiTi,Fontsize=20,OutlineColour=&H40000000,BorderStyle=3,MarginV=2"), audio, v=1, a=1
        ).output(out_path).run(quiet=False, overwrite_output=True)

        self.view.update_lbl_s_path(
            f"Subtitle attached to {filename(v_path)}_{dt_str}.mp4")

    def dl_tsc(self, vid):
        self.view.update_btn_state("disabled")
        self.download(vid)
        self.view.update_btn_state("disabled")
        self.tsc(self.view.get_tsc_lbl_msg())
        self.view.update_btn_state("normal")

    def dl_tsc_tsl(self, vid):
        self.view.update_btn_state("disabled")
        self.download(vid)
        self.view.update_btn_state("disabled")
        self.tsc(self.view.get_tsc_lbl_msg())
        self.tsl(self.view.get_tsl_lbl_msg())
        self.view.update_btn_state("normal")
