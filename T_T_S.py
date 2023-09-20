from gtts import gTTS

def text_to_speech(text,name):
    tts = gTTS(text, lang='fr')
    tts.save(name)

# I'm tring to train my own model for text to speech so it take some time but for now
# I use an api from google