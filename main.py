import sys
import threading
from tkinter import *
from ttkbootstrap.dialogs.dialogs import Messagebox
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
import os, time
from pytube import Playlist, Stream, YouTube
from concurrent.futures import ThreadPoolExecutor
from moviepy.editor import AudioFileClip
import notifypy, shutil

WIDTH = 700
HEIGHT = 200
root_folder = os.path.dirname(os.path.abspath(__file__))


videos = []
MAX_THREADS = 2

icon = ""
notification_audio = ""
PATH = ""

if sys.platform == "win32":
    icon = f"{root_folder}\\icons\\icon.ico"
    notification_audio = f"{root_folder}\\notifications\\notification.wav"
    PATH = f"{os.environ.get('USERPROFILE')}\\Downloads\\Youtube2Mp3\\"                                                                                                         
else:
    if shutil.which('aplay') is None:
        Messagebox.show_error("Install alsa-utils to play audio notifications in Linux", "Error")
    PATH = f"{os.environ.get('HOME')}/Downloads/Youtube2Mp3/"                                                                                                           
    notification_audio = f"{root_folder}/notifications/notification.wav"
    icon = f"{root_folder}/icons/icon.png"

if(not os.path.exists(PATH)):    
    os.makedirs(PATH)
os.chdir(PATH)


class DownloadWindow(ttk.Toplevel):
    def __init__(self,url='',notifications=False, popup=False, title="Download", iconphoto='', size=None, position=None, minsize=None, maxsize=None, resizable=None, transient=None, overrideredirect=False, windowtype=None, topmost=False, toolwindow=False, alpha=1, **kwargs):
        super().__init__(title, iconphoto, size, position, minsize, maxsize, resizable, transient, overrideredirect, windowtype, topmost, toolwindow, alpha, **kwargs)
        # self.geometry(f"{WIDTH}x{HEIGHT*3}")
        self.url = url
        self.notifications = notifications
        self.popup = popup

        if sys.platform == "win32":
            self.iconbitmap(icon)
        else:
            self.iconphoto(True, PhotoImage(file=icon))
        
        self.minsize(WIDTH, HEIGHT)
        
        self.geometry(f"{WIDTH}x{HEIGHT}")

        self.msg_label = ttk.Label(self, text="", padding=4)
        self.msg_label.place(relx=0.1, rely=0.8, relwidth=0.8)
        
        self.download_meter = ttk.Meter(self, textright=" %",metertype="semi", metersize=180, amountused=0, bootstyle="danger")
        self.download_meter.place(relx=0.1, rely=0.3, relwidth=0.8)

        self.restart = ttk.Button(self, text="Restart", style="success",command=self.download)

        self.withdraw()

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
        if self.notifications:
            self.notify("Download Completed ", f"{stream.title} Conversion Completed")
        
        # Destroy Download Window
        time.sleep(3)
        self.destroy()

    def download(self):
        
        if self.popup:
            self.deiconify()
        else:
            self.iconify()
        self.download_meter.configure(amountused=0)
        self.restart.pack_forget()

        try:
            yt = YouTube(self.url, on_progress_callback=self.set_download_meter, on_complete_callback=self.set_download_meter_complete)
            self.title(yt.title)
            
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
            if self.notifications:
                self.notify("Download Error", e)
            self.restart.pack(pady=10)
            # To Avoid Hide on Restart
            self.popup = True

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
            Linux: sudo apt-get install alsa-utils
        """
        notification = notifypy.Notify(enable_logging=False) # I like enabling logging :)
        notification.application_name = "Youtube2Mp3"
        notification.title = title
        notification.message = message
        
        notification.urgency = "low"   # 'low', 'normal' or 'critical'
        notification.audio = notification_audio
        notification.icon = icon[:-3]+"png"


        notification.send(block=False)  # block=False spawns a separate thread inorder not to block the main app thread


    

class App(ttk.Window):
    def __init__(self, title="Youtube2MP3", themename="darkly", iconphoto='', size=None, position=None, minsize=None, maxsize=None, resizable=None, hdpi=True, scaling=None, transient=None, overrideredirect=False, alpha=1):
        super().__init__(title, themename, iconphoto, size, position, minsize, maxsize, resizable, hdpi, scaling, transient, overrideredirect, alpha)

        # root = ttk.Window(themename="darkly")
        if sys.platform == "win32":
            self.iconbitmap(icon)
        else:
            self.iconphoto(True, PhotoImage(file=icon))
        self.title("Youtube2MP3")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.minsize(WIDTH, HEIGHT)
        
        self.url_label = ttk.Label(self, text="URL", padding=4)
        self.url_entry_string = ttk.StringVar()
        self.url_entry_string.set("")
        self.url_entry = ttk.Entry(self, textvariable=self.url_entry_string)

        self.is_playlist_var = ttk.IntVar()
        self.is_playlist_var.set(0)
        self.is_playlist = ttk.Checkbutton(self, text="Playlist", padding=4, variable=self.is_playlist_var)

        self.is_multi_mode_var = ttk.IntVar()
        self.is_multi_mode_var.set(0)
        self.is_multi_mode = ttk.Checkbutton(self, text="Multimode", padding=4, variable=self.is_multi_mode_var)

        self.is_notify_var = ttk.IntVar()
        self.is_notify_var.set(0)
        self.is_notify_mode = ttk.Checkbutton(self, text="Notifications", padding=4, variable=self.is_notify_var)

        self.is_popup_var = ttk.IntVar()
        self.is_popup_var.set(0)
        self.is_popup_mode = ttk.Checkbutton(self, text="Popup", padding=4, variable=self.is_popup_var)

        # download_meter = ttk.Meter(self, textright=" %",metertype="semi", metersize=180, amountused=0, bootstyle="danger")
        download_button = ttk.Button(self, text="Download", style="success", padding=4,command=self.download_call)

        self.url_label.place(relx=0.02, rely=0.1, relwidth=0.2)
        self.url_entry.place(relx=0.1, rely=0.1, relwidth=0.8)
        self.is_playlist.place(relx=0.1, rely=0.3, relwidth=0.8)
        self.is_multi_mode.place(relx=0.1, rely=0.5, relwidth=0.8)
        
        self.is_notify_mode.place(relx=0.7, rely=0.3, relwidth=0.8)
        self.is_popup_mode.place(relx=0.7, rely=0.5, relwidth=0.8)
        # download_meter.place(relx=0.1, rely=0.3, relwidth=0.8)
        download_button.place(relx=0.35, rely=0.8, relwidth=0.3)

    def download_call(self):
        pool = ThreadPoolExecutor(max_workers=MAX_THREADS)
        global videos
        
        # Get URLs from Entry
        urls = self.url_entry.get().strip().split(' ')
        if not self.is_multi_mode_var.get() and urls:
            urls = urls[:1]

        # Reset GUI to empty string
        self.url_entry_string.set("")

        try:

            # Check if Playlist is Selected
            if self.is_playlist_var.get():
                # Get Playlist URL
                playlist_url = urls[0]
                # Get Playlist Videos
                try:
                    p = Playlist(playlist_url)
                    for video in p.videos:
                        if video.watch_url not in videos:
                            videos.append(video.watch_url)
                            d = DownloadWindow(url=video.watch_url, notifications=self.is_notify_var.get(), popup=self.is_popup_var.get())
                            d.geometry(f"{WIDTH}x{HEIGHT*3}")  
                            d.minsize(WIDTH, HEIGHT*3)
                            pool.submit(d.download)
                except Exception as e:
                    e = str(e)
                    if 'list' in e:
                        e = "Invalid Playlist URL"
                    elif 'urlopen' in e:
                        e = "Check Internet Connection or Firewall"
                    elif 'age rest' in e:
                        e = "Age restricted content . Cannot Download"
                    
                    Messagebox.show_error(e,"Error")
            else:
                # Download Video(s)        
                for url in urls:
                    if url:
                        # To Avoid Multiple Downloads of Same URL/Audio
                        if url not in videos:
                            d = DownloadWindow(url=url, notifications=self.is_notify_var.get(), popup=self.is_popup_var.get())
                            d.geometry(f"{WIDTH}x{HEIGHT*3}")
                            d.minsize(WIDTH, HEIGHT*3)
                            pool.submit(d.download)
        except Exception as e:
            e = str(e)
            if 'regex' in e:
                e = "Invalid URL"
            elif 'urlopen' in e:
                e = "Check Internet Connection or Firewall"
            elif 'age rest' in e:
                e = "Age restricted content . Cannot Download"
            
            Messagebox.show_error(e,"Error")
        finally:
            # pool.shutdown()
            videos.clear()



app = App()
app.mainloop()