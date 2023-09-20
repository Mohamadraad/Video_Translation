import os

def clean():
    """
    This Function will clean all the files created by this project

    Returns
    -------
    None.

    """
    try:
        
        audio_chunks_dir = "audio_chunks"
        translated_chunks_dir = "translated_chuncks"
        
        audio_files = os.listdir(audio_chunks_dir)
        translated_files = os.listdir(translated_chunks_dir)
        
        # Delete all files in the audio_chunks directory
        for file in audio_files:
            file_path = os.path.join(audio_chunks_dir, file)
            os.remove(file_path)
        
        # Delete all files in the translated_chuncks directory
        for file in translated_files:
            file_path = os.path.join(translated_chunks_dir, file)
            os.remove(file_path)
        os.remove("merged_audio.wav")
        os.remove("output_audio.wav")
    except:
        pass

clean()