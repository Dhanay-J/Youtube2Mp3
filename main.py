import sys
import threading
from tkinter import *
from ttkbootstrap.dialogs.dialogs import Messagebox
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
import os
from pytube import Playlist
from Download import Download
from concurrent.futures import ThreadPoolExecutor

WIDTH = 700
HEIGHT = 200
PATH = f"{os.environ.get('USERPROFILE')}\\Downloads\\Youtube2Mp3\\"
root_folder = os.path.dirname(os.path.abspath(__file__))


if(not os.path.exists(PATH)):    
    os.makedirs(PATH)
os.chdir(PATH)

videos = []
MAX_THREADS = 2

icon = ""
notification_audio = "" 
if sys.platform == "win32":
    icon = f"{root_folder}\\icons\\icon.ico"
else:
    icon = f"{root_folder}/icons/icon.png"

def download_call():
    pool = ThreadPoolExecutor(max_workers=MAX_THREADS)
    global videos
    
    # Get URLs from Entry
    urls = url_entry.get().strip().split(' ')
    if not is_multi_mode_var.get() and urls:
        urls = urls[:1]

    # Reset GUI to empty string
    url_entry_string.set("")

    try:

        # Check if Playlist is Selected
        if is_playlist_var.get():
            # Get Playlist URL
            playlist_url = urls[0]
            # Get Playlist Videos
            try:
                p = Playlist(playlist_url)
                for video in p.videos:
                    if video.watch_url not in videos:
                        videos.append(video.watch_url)
                        d = Download(video.watch_url)   
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
                        videos.append(url)
                        d = Download(url)
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
        pool.shutdown()
        videos.clear()

def worker():
    thread = threading.Thread(target=download_call)
    thread.start()
    


root = ttk.Window(themename="darkly")
if sys.platform == "win32":
    root.iconbitmap(icon)
else:
    root.iconphoto(True, PhotoImage(file=icon))
root.title("Youtube2MP3")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.minsize(WIDTH, HEIGHT)

"https://youtu.be/xEALTVLxrDw?list=RDxEALTVLxrDw"
"https://youtu.be/WcIcVapfqXw?list=RDxEALTVLxrDw"
"https://youtu.be/ruohUTTo8Kw" # 12 min
"https://youtu.be/pAMiPgT1m4E" #45 min

# msg_label = ttk.Label(root, text="", padding=4)
url_label = ttk.Label(root, text="URL", padding=4)
url_entry_string = ttk.StringVar()
url_entry_string.set("")
url_entry = ttk.Entry(root, textvariable=url_entry_string)

is_playlist_var = ttk.IntVar()
is_playlist_var.set(0)
is_playlist = ttk.Checkbutton(root, text="Playlist", padding=4, variable=is_playlist_var)

is_multi_mode_var = ttk.IntVar()
is_multi_mode_var.set(0)
is_multi_mode = ttk.Checkbutton(root, text="Multimode", padding=4, variable=is_multi_mode_var)


# download_meter = ttk.Meter(root, textright=" %",metertype="semi", metersize=180, amountused=0, bootstyle="danger")
download_button = ttk.Button(root, text="Download", style="success", padding=4,command=worker)

url_label.place(relx=0.02, rely=0.1, relwidth=0.2)
url_entry.place(relx=0.1, rely=0.1, relwidth=0.8)
is_playlist.place(relx=0.1, rely=0.3, relwidth=0.8)
is_multi_mode.place(relx=0.1, rely=0.5, relwidth=0.8)
# download_meter.place(relx=0.1, rely=0.3, relwidth=0.8)
download_button.place(relx=0.35, rely=0.8, relwidth=0.3)
# msg_label.place(relx=0.1, rely=0.9, relwidth=0.8)


root.mainloop()