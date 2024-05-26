# Youtube2Mp3
Simple GUI to Convert Youtube Video to MP3 Using pytube and ttkbootstrap

`Python 3.12.0`

# Installation 

    git clone https://github.com/Dhanay-J/Youtube2Mp3.git
    cd Youtube2Mp3
    python -m venv .
    .\Scripts\activate
    pip install -r requirements.txt
    python .\main.py
<<<<<<< HEAD
=======

# Fix for `AttributeError: module 'PIL.Image' has no attribute 'CUBIC'`
  - Edit   : \Youtube2Mp3\Lib\site-packages\ttkbootstrap\widgets.py", line 856
  - Change : img.resize((self._metersize, self._metersize), Image.CUBIC) 
  - To     : img.resize((self._metersize, self._metersize), **Image.BICUBIC**)
>>>>>>> 901a812538b55bfd84984e0e0df64617e2ccd596

# Fix for `AttributeError: module 'PIL.Image' has no attribute 'CUBIC'`
  - Edit   : \Youtube2Mp3\Lib\site-packages\ttkbootstrap\widgets.py", line 856
  - Change : img.resize((self._metersize, self._metersize), Image.CUBIC) 
  - To     : img.resize((self._metersize, self._metersize), **Image.BICUBIC**)
