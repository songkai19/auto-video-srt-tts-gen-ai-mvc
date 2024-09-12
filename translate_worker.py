import pysrt
from openai import AzureOpenAI


client = AzureOpenAI(
    azure_endpoint="https://openai-translation.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2023-03-15-preview",
    api_key="d5069013ce5942f4b8f7500a96f91793",
    api_version="2023-03-15-preview"
)


def line_tt(transcript_line, bw_data: str, fw_data: str, language: str):
    refinedSegment = f"{transcript_line.text.strip().replace('-->', '->')}"

    if language == "":
        language == "Chinese(Simplified)"

    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant who can translate text content about sport training and electronic speech."},
            {"role": "system", "content": "You refer to the given context to improve the quality of tranlation."},
            {"role": "user", "content": f"Translate the following text into {language}: \n Gonna switch it up a little bit today, show you guys a little bit what a workout looks"},
            {"role": "user", "content": "Above sentence is within the following context, do consider it for your translation: \n Yo, what's going on guys? \n Gonna switch it up a little bit today, show you guys a little bit what a workout looks \n like here."},
            {"role": "assistant", "content": "今天要稍微改变一下，给你们展示一下在这里训练的样子"},
            {"role": "user", "content": f"Translate the following text into {language}: \n {refinedSegment} "},
            {"role": "user", "content": f"Above sentence is within the following context, do consider it for your translation: \n {bw_data} \n {refinedSegment} \n {fw_data} "},
            {"role": "user", "content": f"Make the translation as short as possible."},
            {"role": "user", "content": f"Remove the duplicated translation appeared in the context. Only keep the translation for the current sentence."}
        ],
        temperature=0.5
    )

    result = response.choices[0].message.content

    new_sub_item = pysrt.SubRipItem(
        transcript_line.index, transcript_line.start, transcript_line.end, result)
    
    return new_sub_item
