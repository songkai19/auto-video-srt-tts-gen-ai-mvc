import pysrt
import requests


api_url = "https://rhxrowgrri.execute-api.ap-southeast-1.amazonaws.com/dev/lambda-translate/translate"
# method = "POST"
headers = {
    "Content-Type": "application/json"
}


def line_tt(transcript_line):
    refinedSegment = f"{transcript_line.text.strip().replace('-->', '->')}"
    srt_text = {"text": refinedSegment}

    response = requests.post(
        api_url, headers=headers, json=srt_text)

    response.raise_for_status()  # Raise an exception for bad status codes

    new_sub_item = pysrt.SubRipItem(
        transcript_line.index, transcript_line.start, transcript_line.end, response.text)

    return new_sub_item
