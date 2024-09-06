import pysrt
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://openai-translation.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2023-03-15-preview",
    api_key="d5069013ce5942f4b8f7500a96f91793",
    api_version="2023-03-15-preview"
)


def line_tt(transcript_line):
    refinedSegment = f"{transcript_line.text.strip().replace('-->', '->')}"

    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant that translates English to Simple Chinese. The text content to be translated is about electronic knowledges."},
            {"role": "user", "content": f"Translate the text content: \n {refinedSegment}"}
        ]
    )

    # print(response.choices[0].message.content)

    new_sub_item = pysrt.SubRipItem(
        transcript_line.index, transcript_line.start, transcript_line.end, response.choices[0].message.content)

    return new_sub_item
