from gtts import gTTS
from gtts.tokenizer.symbols import SUB_PAIRS
import os
import re

def replace_at_start_of_sentence(text):
    sub_pairs = []
    with open('sub_pairs.txt', 'r') as file:
        for line in file:
            old, new = line.strip().split(',')
            sub_pairs.append((old, new))
    
    for old, new in sub_pairs:
        pattern = r'(?<!\S)' + re.escape(old)
        text = re.sub(pattern, new, text)
    return text

# Text to be converted to speech
text = "saribanong"
text = replace_at_start_of_sentence(text)

# Create a gTTS object
tts = gTTS(text=text.lower(), lang='id', )

# Save the audio file
tts.save("output.mp3")

# Play the audio file (optional)
os.system("start output.mp3")  # For Windows
