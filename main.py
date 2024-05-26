import time
from tkinter import *
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
from pytube import YouTube
import threading, os
from moviepy.editor import AudioFileClip

WIDTH = 700
HEIGHT = 500
PROGRESS_DELAY = 0.000001
PATH = f"{os.environ.get('USERPROFILE')}\\Downloads\\Youtube2Mp3\\"

if(not os.path.exists(PATH)):    
    os.makedirs(PATH)
os.chdir(PATH)

def set_download_meter(stream, chunk, bytes_remaining):
    
    
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    pct_completed = int((bytes_downloaded / total_size) * 100)
    download_meter.configure(amountused=pct_completed)

def set_download_meter_complete(stream, file_handle):
    download_meter.configure(amountused=100)

    msg_label.configure(text=f"Download Completed : {stream.title}\nConverting to MP3...")

    audio = AudioFileClip(file_handle)
    audio.write_audiofile(f"{file_handle[:-4]}.mp3", verbose=False, logger=None)
    audio.close()
    os.remove(file_handle)
    msg_label.configure(text=f"Download Completed : {stream.title}\nConversion Completed")

def download():
    url = url_entry.get()
    download_meter.configure(amountused=0)
    download_button.configure(state="disabled")

    try:
        yt = YouTube(url, on_progress_callback=set_download_meter, on_complete_callback=set_download_meter_complete)
        msg_label.configure(text=f"Downloading : {yt.title}")
        yt.streams.get_audio_only().download()
    except Exception as e:
        download_meter.configure(amountused=0)
        
        if "regex" in str(e):
            msg_label.configure(text="Error : Invalid URL")
        else:
            msg_label.configure(text=f"Error : {str(e)}")

    finally:
        download_button.configure(state="normal")
    # Download the video
    # Convert the video to MP3
    # Save the MP3 file

def worker():
    thread = threading.Thread(target=download)
    thread.start()


root = ttk.Window(themename="darkly")

root.title("Youtube2MP3")
root.geometry(f"{WIDTH}x{HEIGHT}")

"https://youtu.be/xEALTVLxrDw?list=RDxEALTVLxrDw"
"https://youtu.be/WcIcVapfqXw?list=RDxEALTVLxrDw"
"https://youtu.be/ruohUTTo8Kw" # 12 min
"https://youtu.be/pAMiPgT1m4E" #45 min

msg_label = ttk.Label(root, text="", padding=4)
url_label = ttk.Label(root, text="URL", padding=4)
url_entry = ttk.Entry(root)
download_meter = ttk.Meter(root, textright=" %",metertype="semi", metersize=180, amountused=20, interactive=True, bootstyle="danger")
download_button = ttk.Button(root, text="Download", style="success", padding=4,command=worker)

url_label.place(relx=0.02, rely=0.1, relwidth=0.2)
url_entry.place(relx=0.1, rely=0.1, relwidth=0.8)
download_meter.place(relx=0.1, rely=0.3, relwidth=0.8)
download_button.place(relx=0.35, rely=0.8, relwidth=0.3)
msg_label.place(relx=0.1, rely=0.9, relwidth=0.8)

root.mainloop()
