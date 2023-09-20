# -*- coding: utf-8 -*-
"""
Created on Sat Sep 9 01:46:03 2023

@author: Lenovo
"""

import PySimpleGUI as sg
from video_to_audio import (
    convert_video_audio,
    split_into_chuncks,
    merged_audio_video,
    plot_wav_file,
)
from S_T_T import recognize_audio
from dablaje import translate
from T_T_S import text_to_speech
import os
from clean import clean
from concurrent.futures import ThreadPoolExecutor

# Graphical user interface
sg.ChangeLookAndFeel('Dark')  
layout = [
    [sg.Text('Caption Any Video!', size=(30, 1), font=("Helvetica", 25))],  
    [sg.Text('What language would you like to switch to:')],
    [sg.Text('Choose the language')],
    [sg.Combo(['French'], size=(30, 3), default_value='French', key='languages')],
    
    [sg.Text("Do you want to change the volume of video")],
    [sg.Slider(range=(1, 3), default_value=1, orientation='h', size=(10, 20), key='volume')],

    [sg.Text('Choose A Video', size=(35, 1))],
    [
        sg.Text('Your Folder', size=(15, 1), auto_size_text=False, justification='right'),
        sg.InputText(), sg.FileBrowse(file_types=(("Video File", ("*.mp4", "*.avi")),),key='file')
    ],
    [sg.Output(size=(100, 10))],
    [sg.ProgressBar(max_value=100, orientation='h', size=(20, 20), key='progressbar')],
    [sg.Button("Transform", size=(8, 1), font=(14)), sg.Button("Exit", size=(8, 1), font=(14))]
]
window = sg.Window('Audio Translator', layout, resizable=True, icon='data/icon.ico')

# Function to process a single audio chunk
def process_audio_chunk(wav_file):
    file_path = os.path.join("audio_chunks", wav_file)
    
    # recognize audio
    recognized_text = recognize_audio(file_path)

    # Translate it
    motarjam = translate(recognized_text)
    
    text_to_speech(motarjam, "translated_chuncks/" + wav_file)
    window.refresh()

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    
    if event == 'Transform':
        if values["file"] == "":
            sg.popup("You didn't specify the file!", keep_on_top=True)
            continue
            
        # Extract the audio from video and change the video if needed    
        audio, video_clip = convert_video_audio(values["file"], values["volume"])
        window['progressbar'].update(20)
        
        # Plot the Amplitude to detect wanted threshold value (default=36)
        silence_threshold = plot_wav_file(audio)
        silence_dic = split_into_chuncks(audio, silence_threshold)
        window['progressbar'].update(40)

        directory = "audio_chunks"
        
        # List all files in the directory
        wav_files = [file for file in os.listdir(directory) if file.endswith(".wav")]
        wav_files = sorted(wav_files, key=lambda x: int(x.split("_")[1].split(".")[0]))
        
        with ThreadPoolExecutor() as executor:
            executor.map(process_audio_chunk, wav_files)
            
        window['progressbar'].update(80)
        merged_audio_video(video_clip, silence_dic)
            
        clean()
        window['progressbar'].update(100)
        sg.popup("Audio converted successfully!", keep_on_top=True)

# Close the window when the loop exits
window.close()
