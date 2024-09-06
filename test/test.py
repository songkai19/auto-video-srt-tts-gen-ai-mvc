import os
import ffmpeg
# import tempfile
import whisper
from typing import Iterator, TextIO
import pysrt
import time
from typing import Iterator
from tqdm import tqdm
from translate_worker_aoai import line_tt


def filename(path):
    return os.path.splitext(os.path.basename(path))[0]


def format_timestamp(seconds: float, always_include_hours: bool = False):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def write_srt(transcript: Iterator[dict], file: TextIO):
    for i, segment in enumerate(transcript, start=1):
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True)} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True)}\n"
            f"{segment['text'].strip().replace('-->', '->')}\n",
            file=file,
            flush=True,
        )


def run(transcript: Iterator[dict]):
    print(f"Start translating the subtitles.")
    result_list = []
    start = time.time()

    len_subs = len(transcript)

    for subtitle in tqdm(transcript, total=len_subs,
                         desc="Subtitle Translation Progress", colour="black"):

        result_list.append(line_tt(subtitle))

    print(f"Time taken = {time.time() - start:.10f}")

    return result_list


# temp_dir = tempfile.gettempdir()
path = "[Elite] Upper Body Baseball Training  Overtime Athletes.mp4"
output_dir = ".\output"

print(f"Extracting audio from {filename(path)}...")
audio_output_path = os.path.join(output_dir, f"{filename(path)}.wav")

ffmpeg.input(path).output(
    audio_output_path,
    acodec="pcm_s16le", ac=1, ar="16k"
).run(quiet=True, overwrite_output=True)

print(f"Extracted audio file: {audio_output_path}")

model = whisper.load_model("base")

# # load audio and pad/trim it to fit 30 seconds
# audio = whisper.load_audio(audio_output_path)
# audio = whisper.pad_or_trim(audio)

# # make log-Mel spectrogram and move to the same device as the model
# mel = whisper.log_mel_spectrogram(audio).to(model.device)

# # detect the spoken language
# _, probs = model.detect_language(mel)
# print(f"Detected language: {max(probs, key=probs.get)}")

# # decode the audio
# options = whisper.DecodingOptions(fp16 = False)
# result = whisper.decode(model, mel, options)

# # print the recognized text
# print(result.text)


srt_path = os.path.join(output_dir, f"{filename(path)}.srt")

print(f"Generating subtitles for {filename(path)}... This might take a while.")

result = model.transcribe(audio_output_path)
print("Subtitles generated.")
# print(result["text"])
# print(result["segments"])

with open(srt_path, "w", encoding="utf-8") as srt:
    write_srt(result["segments"], file=srt)
print("SRT file wrote to output folder.")

# srt_path_translated = os.path.join(
#     output_dir, f"{filename(srt_path)}_translated.srt")
# subs = pysrt.open(srt_path)

# result_translated = run(subs)
# new_subs = pysrt.SubRipFile(result_translated)
# new_subs.save(srt_path_translated)
