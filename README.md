# Youtube2Mp3
Simple GUI to Convert Youtube Video to MP3 Using pytube and ttkbootstrap

`Python 3.12.0`

- Installation
    - `git clone https://github.com/Dhanay-J/Youtube2Mp3.git`
    - `cd Youtube2Mp3`
    - `python -m venv .`
    - `.\Scripts\activate`
    - `pip install -r requirements.txt`
    - `python .\main.py`

- Fix for | AttributeError: module 'PIL.Image' has no attribute 'CUBIC'
      - Goto \Youtube2Mp3\Lib\site-packages\ttkbootstrap\widgets.py", line 856
      - Change `img.resize((self._metersize, self._metersize), Image.CUBIC)` to
          `img.resize((self._metersize, self._metersize), Image.BICUBIC)`

