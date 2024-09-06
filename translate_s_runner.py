from typing import Iterator
import time
from tqdm import tqdm

from translate_worker import line_tt


def run(transcript: Iterator[dict], language):
    print(f"Start translating the subtitles.")
    result_list = []
    start = time.time()

    len_subs = len(transcript)

    for subtitle in tqdm(transcript, total=len_subs,
                         desc="Subtitle Translation Progress"):
        # 前一行字幕内容
        bw_index = subtitle.index - 2
        bw_data = ""
        if bw_index >= 0:
            bw_data = transcript[bw_index].text

        # 下一行字幕内容
        fw_index = subtitle.index
        fw_data = ""
        if fw_index < len_subs:
            fw_data = transcript[fw_index].text

        result_list.append(line_tt(subtitle, bw_data, fw_data, language))

    print(f"Time taken = {time.time() - start:.10f}")

    return result_list
