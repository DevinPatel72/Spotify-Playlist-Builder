# Built in Linux

import PyInstaller.__main__

PyInstaller.__main__.run([
    "--onefile", "--nowindow",
    "SpotifyPlaylistBuilder.py",
    "--clean",
    "--distpath=executable", "--workpath=executable/build",
    "--add-data=images/70x70_red_x.png:images",
    "--add-data=images/88x70_green_checkmark.png:images",
    "--add-data=images/spotify_logo.png:images",
    "--add-data=common-words.txt:.",
    "--add-data=credentials/spotify.ini:credentials",
    "--paths=spotify-env/lib/python3.10/site-packages",
    "--add-binary=/usr/lib/x86_64-linux-gnu/vlc:vlc",
    "--hidden-import=PIL._tkinter_finder"
])