# LJ Convert

**LJ Convert** is a lightweight Windows video and audio converter with a glossy Frutiger Aero-inspired interface. It can convert local video files to **MP4** or **MP3**, and it can also download and convert online videos when you have permission to use them.

Made by **LJGAMES**.

## Features

* Convert local video files to MP4
* Convert local video files to MP3
* Download permitted online videos using yt-dlp
* Clean Frutiger Aero-style interface
* Glossy blue segmented progress bar
* Small Windows desktop app
* No command prompt window when exported correctly
* Supports custom app icon when built with PyInstaller

## Preview

Add a screenshot here after you build the app:

```md
![LJ Convert Screenshot](screenshot.png)
```

## Requirements

To run the Python version, you need:

* Python 3.10 or newer
* FFmpeg
* FFprobe
* yt-dlp

For the easiest setup, place the tools inside a `bin` folder next to the Python file:

```txt
LJConvertProject/
├─ lj_convert.py
├─ app.ico
└─ bin/
   ├─ ffmpeg.exe
   ├─ ffprobe.exe
   └─ yt-dlp.exe
```

## How to Run

Install Python if you do not already have it, then run:

```bat
py lj_convert.py
```

## How to Build the EXE

Install PyInstaller:

```bat
py -m pip install pyinstaller
```

Then build the app as a single Windows EXE:

```bat
py -m PyInstaller ^
  --onefile ^
  --windowed ^
  --clean ^
  --name "LJ Convert" ^
  --icon "app.ico" ^
  --add-binary "bin\ffmpeg.exe;bin" ^
  --add-binary "bin\ffprobe.exe;bin" ^
  --add-binary "bin\yt-dlp.exe;bin" ^
  lj_convert.py
```

The finished file will be created here:

```txt
dist/LJ Convert.exe
```

## Notes About File Size

If FFmpeg, FFprobe, and yt-dlp are bundled into the EXE, the final file may be large. This is normal because FFmpeg is a large tool by itself.

For a smaller EXE, build without bundling the `bin` folder:

```bat
py -m PyInstaller ^
  --onefile ^
  --windowed ^
  --clean ^
  --name "LJ Convert" ^
  --icon "app.ico" ^
  lj_convert.py
```

With this smaller build, FFmpeg and yt-dlp need to be installed separately or available through your system PATH.

## Supported Input Files

LJ Convert supports common video formats, including:

* MP4
* MOV
* MKV
* AVI
* WEBM
* FLV
* WMV
* M4V

## Output Formats

LJ Convert currently supports:

* `.mp4` video output
* `.mp3` audio output

## Legal Notice

Only use LJ Convert with videos and audio that you own, created yourself, have permission to use, or are allowed to download and convert. The developer is not responsible for misuse of this tool.

## Credits

LJ Convert uses:

* [FFmpeg](https://ffmpeg.org/)
* [yt-dlp](https://github.com/yt-dlp/yt-dlp)
* Python Tkinter

## License

You can add your license here. For a simple open-source project, the MIT License is a common choice.

Example:

```txt
MIT License

Copyright (c) 2026 LJGAMES

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files, to deal in the Software
without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, subject to the full MIT License text.
```
