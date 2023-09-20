# -*- coding: utf-8 -*-
"""
Created on Sat Sep  2 00:46:03 2023

@author: Lenovo
"""

from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment, silence
from pydub.silence import split_on_silence
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg

def convert_video_audio(video_path, volume):
    """
    

    Parameters
    ----------
    video_path : str
        The path of the video file you need to convert it.
    volume : float
        The value of the volume you need to change. Default = 1 "Not change the audio".

    Returns
    -------
    audio : TYPE
        DESCRIPTION.
    video_clip : TYPE
        DESCRIPTION.

    """
    # Load the video file
    video_clip = VideoFileClip(video_path)
    
    # Extract the audio
    audio_clip = video_clip.audio
    
    # Change the volume
    audio_clip.volumex(volume)
    
    # Save the extracted audio to a file
    audio_clip.write_audiofile("output_audio.wav", verbose=False, logger=None)
    
    # Load the audio file
    audio = AudioSegment.from_wav("output_audio.wav") 
    
    # Close the video and audio clips
    audio_clip.close()
    
    print("Audio Extracted Successfully!")
    return audio, video_clip
    
def plot_wav_file(audio):
    """
    

    Parameters
    ----------
    audio : pydub.audio_segment.AudioSegment
        The audio file you want to plot to see the threshold value.

    Returns
    -------
    threshold
        int number of the threshold value.

    """

    audio_data = np.array(audio.get_array_of_samples())

    # Calculate the time axis for the signal
    duration = len(audio_data) / audio.frame_rate
    time = np.linspace(0, duration, len(audio_data))

    # Convert audio data to dBFS
    audio_data_dBFS = 20 * np.log10(np.abs(audio_data) / (2 ** 15))  # Assuming 16-bit audio

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(time, audio_data_dBFS)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude (dBFS)')
    ax.set_title('Audio Signal in dBFS')
    ax.grid(True)

    # Create the PySimpleGUI layout
    layout = [
        [sg.Canvas(key="-CANVAS-")],
        [sg.Button("Zoom In"), sg.Button("Zoom Out")],
        [sg.Text("", key="-INFO-"),[sg.Text("Set the silence threshold (adjust this based on your audio characteristics):")],
        [sg.InputText("-36", key="-THRESHOLD-")],
        [sg.Button("Submit")]]  # Display cursor information
    ]
    
    window = sg.Window("Silence Threshold:", layout, finalize=True, disable_close=True, keep_on_top=True)

    canvas_elem = window["-CANVAS-"]
    canvas = FigureCanvasTkAgg(fig, master=canvas_elem.Widget)
    canvas.get_tk_widget().pack(fill="both", expand=True)
    canvas.draw()

    x_limit = ax.get_xlim()
    y_limit = ax.get_ylim()

    def on_motion(event):
        if event.inaxes is not None:
            x, y = event.xdata, event.ydata
            if x is not None and y is not None:
                window["-INFO-"].update(value=f"Time: {x:.2f} s\nAmplitude: {y:.2f} dBFS")

    fig.canvas.mpl_connect('motion_notify_event', on_motion)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Exit":
            break
        
        elif event == "Zoom In":
            x_limit = ax.get_xlim()
            y_limit = ax.get_ylim()
            ax.set_xlim(x_limit[0] * 0.9, x_limit[1] * 0.9)
            ax.set_ylim(y_limit[0], y_limit[1])
            canvas.draw()
        elif event == "Zoom Out":
            x_limit = ax.get_xlim()
            y_limit = ax.get_ylim()
            ax.set_xlim(x_limit[0] * 1.1, x_limit[1] * 1.1)
            ax.set_ylim(y_limit[0], y_limit[1])
            canvas.draw()
        elif event == "Submit":
            try:
                threshold = int(values["-THRESHOLD-"])
                window.close()
                return threshold
            except:
                window.close()
                return -36

    
def split_into_chuncks(audio, silence_threshold):
    """
    

    Parameters
    ----------
    audio : pydub.audio_segment.AudioSegment
        The audio file.
    silence_threshold : int
        Silence Threshold determines the level of background noise or 
        quietness in an audio signal that is considered as "silence".

    Returns
    -------
    silent_time : dict
        the start and the end of each silent intervals.

    """

    # Split audio at silent intervals
    audio_chunks = split_on_silence(
        audio,
        min_silence_len=500,  # Minimum silence length in milliseconds
        silence_thresh=silence_threshold,
        keep_silence=500  # Keep a bit of silence at the beginning and end of each chunk
    )
    
    # Initialize a variable to keep track of the accumulated duration
    accumulated_duration = 0
    # Extract and save each interval as a separate WAV file
    for i, chunk in enumerate(audio_chunks):
        start_time_ms = accumulated_duration  # Start time in milliseconds
        end_time_ms = accumulated_duration + len(chunk)  # End time in milliseconds
        chunk.export(f"audio_chunks/chunk_{i}.wav", format="wav")
        # Print start and end times in seconds for audio chunks
        start_time_sec = start_time_ms / 1000
        end_time_sec = end_time_ms / 1000
    
        # Update the accumulated duration
        accumulated_duration += len(chunk)
        
    silent_time = {}
    # Display timing for silence segments
    silence_segments = silence.detect_silence(audio, silence_thresh=silence_threshold,min_silence_len = 500)
    for i, (start, end) in enumerate(silence_segments):
        start_time_sec = start / 1000
        end_time_sec = end / 1000
        silent_time[start_time_sec] = end_time_sec
    return silent_time


def merged_audio_video(video_clip, silence_dic):
    """
    

    Parameters
    ----------
    video_path : TYPE
        This function Merge the translated chuncks files.
        Then Merge the new audio with the original file

    Returns
    -------
    output_video_with_new_audio.

    """

    chunk_file_paths = [file for file in os.listdir("translated_chuncks/") if file.endswith(".wav")]
    chunk_file_paths = sorted(chunk_file_paths, key=lambda x: int(x.split("_")[1].split(".")[0]))

    # Load the audio chunks into AudioSegment objects
    audio_chunks = [AudioSegment.from_file("translated_chuncks\\"+chunk) for chunk in chunk_file_paths]

    # Initialize an empty result AudioSegment
    merged_audio = AudioSegment.empty()
    
    # Iterate through both silence intervals and audio chunks
    for (start, end), chunk in zip(silence_dic.items(), audio_chunks):
        silence_duration = ((end - start) * 1000)  # Convert to milliseconds
        silence = AudioSegment.silent(duration=silence_duration)
        
        # Add silence to merged_audio
        merged_audio += silence
    
        # Add the chunk
        merged_audio += chunk
    
    # Export the final merged audio
    merged_audio.export("merged_audio.wav", format="wav")

    # Remove the existing audio
    video_clip = video_clip.set_audio(None)
    
    # Load the new audio clip
    new_audio = AudioFileClip("merged_audio.wav")
    
    # Set the new audio for the video clip
    video_clip = video_clip.set_audio(new_audio)
    
    # Write the final video with the new audio
    video_clip.write_videofile("output_video_with_new_audio.mp4", codec="libx264", audio_codec="aac", verbose=False, logger=None)

