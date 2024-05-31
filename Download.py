
import threading
import time
from tkinter import *
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
from pytube import YouTube, Stream
import os
from moviepy.editor import AudioFileClip
import notifypy
import functools

# Used to Fix Unsupported Platform error in win 11 | Fix By https://github.com/TransparentLC
notifypy.Notify._selected_notification_system = functools.partial(notifypy.Notify._selected_notification_system, override_windows_version_detection=True)

root_folder = os.path.dirname(os.path.abspath(__file__))


class Download:
    def __init__(self, url="") -> None:
        WIDTH = 700
        HEIGHT = 500
        PATH = f"{os.environ.get('USERPROFILE')}\\Downloads\\Youtube2Mp3\\"

        if(not os.path.exists(PATH)):    
            os.makedirs(PATH)
        os.chdir(PATH)


        self.url = url
        self.thread = None
        self.download_window = ttk.Toplevel()
        self.download_window.minsize(WIDTH, HEIGHT)
        
        self.download_window.title("Download")
        self.download_window.geometry(f"{WIDTH}x{HEIGHT}")

        self.msg_label = ttk.Label(self.download_window, text="", padding=4)
        self.msg_label.place(relx=0.1, rely=0.8, relwidth=0.8)
        
        self.download_meter = ttk.Meter(self.download_window, textright=" %",metertype="semi", metersize=180, amountused=0, bootstyle="danger")
        self.download_meter.place(relx=0.1, rely=0.3, relwidth=0.8)

        self.restart = ttk.Button(self.download_window, text="Restart", style="success",command=self.download)

        


    def set_download_meter(self, stream:Stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        pct_completed = int((bytes_downloaded / total_size) * 100)
        for i in range(self.download_meter.amountusedvar.get(), pct_completed+1):
            self.download_meter.configure(amountused=i)
        self.download_meter.configure(amountused=pct_completed)

    def set_download_meter_complete(self , stream:Stream, file_handle):
        for i in range(self.download_meter.amountusedvar.get(), 101):
            self.download_meter.configure(amountused=i)
        self.download_meter.configure(amountused=100)

        self.msg_label.configure(text=f"Download Completed : {stream.title}\nConverting to MP3...")

        # start = time.time()
        audio = AudioFileClip(file_handle)
        audio.write_audiofile(f"{file_handle[:-4]}.mp3", verbose=False, logger=None,ffmpeg_params=["-qscale:a", "4"])
        audio.close()

        # print(f"Conversion Time : {time.time() - start}")

        os.remove(file_handle)
        self.msg_label.configure(text=f"Download Completed : {stream.title}\nConversion Completed")
        self.notify("Download Completed ", f"{stream.title} Conversion Completed")
        
        # Destroy Download Window
        time.sleep(3)
        self.download_window.destroy()

    def download(self):
        
        self.download_meter.configure(amountused=0)
        self.restart.pack_forget()

        try:
            yt = YouTube(self.url, on_progress_callback=self.set_download_meter, on_complete_callback=self.set_download_meter_complete)
            self.msg_label.configure(text=f"Downloading : {yt.title}")
            yt.streams.get_audio_only().download()
        except Exception as e:
            self.download_meter.configure(amountused=0)
            e = str(e)

            if "regex" in e:
                e="Invalid URL"
            elif "urlopen" in e:
                e="Check Internet Connection or Firewall"
            elif "age rest" in e:
                e = "Age restricted video . Cannot Download"
            
            self.msg_label.configure(text=e)
            self.notify("Download Error", e)
            self.restart.pack(pady=10)

        finally:
            return

        
    def notify(self, title: str, message: str):
        """
        Sends a notification using the notif-py engine.

        Args:
            title: str: the title of the notification
            message: str: the message of the notification
        Note:
            Cross-Platform: could be used on any OS.
        """
        notification = notifypy.Notify(enable_logging=False) # I like enabling logging :)
        notification.application_name = "Youtube2Mp3"
        notification.title = title
        notification.message = message
        
        notification.urgency = "low"   # 'low', 'normal' or 'critical'
        # notification.audio = "path/to/audio.wav" 
        # notification.icon = "path/to/icon.png"


        notification.send(block=False)  # block=False spawns a separate thread inorder not to block the main app thread

    
