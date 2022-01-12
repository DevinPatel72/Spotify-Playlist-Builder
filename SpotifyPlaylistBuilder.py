import spotipy
from spotipy.oauth2 import SpotifyOAuth

import random #For Random song generation

from datetime import datetime #For playlist names

#For image and video playback
import numpy as np
import cv2
import urllib.request
import vlc
from PIL import Image, ImageTk

#GUI
import tkinter as tk
import tkinter.simpledialog
import tkinter.font as font
from tkinter import messagebox

username = 'p2l598a007j3bpwksmdd752fv'

"""

Methods

"""

def authenticate_spotify():
    cid = 'd0f6b1e784824144b47580a609fbd77f'
    secret = '5857e7e2ec084185bb4afad003846a14'
    redirect_uri = 'http://127.0.0.1:8080'

    scope = 'playlist-modify-public'

    token = SpotifyOAuth(client_id=cid, client_secret=secret, redirect_uri=redirect_uri, scope=scope, username=username)

    return spotipy.Spotify(auth_manager = token)




def url_to_image(url):
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    
    return image
    
def get_track_uri(track):
    return track['uri']

def get_track_list_uri(track_list):
    list_of_uris = []
    
    for track in track_list:
        list_of_uris.append(get_track_uri(track))
    
    return list_of_uris
    

def generate_track_queue(queue_length, include_explicit = True, verbose=False):
    """Returns a random song by searching for a random word
    from the 5000 most commonly used words and picking a random
    song from the top 30 songs returned for that query.

    :verbose: Enables verbose mode.
    """

    # Get list of most commonly used words
    with open("common-words.txt") as f:
        words = f.read().split('\n')
        
    list_of_tracks_to_export = []
    search_limit = 30
    
    if queue_length >= search_limit/2:
        search_limit = queue_length*2
    
    while len(list_of_tracks_to_export) <= queue_length:
        randSearchString = random.choice(words)

        if verbose: print("Retrieving songs for query '{}'...".format(randSearchString))
        randSongs = spotifyObject.search(randSearchString, limit=search_limit)
        if verbose: print("Retrieved {} songs.".format(len(randSongs['tracks']['items'])))

        #Array of shuffled indeces so that each output in search gets checked
        # instead of it being randomly picked every time
        list_of_indeces=[]
        for i in range(0, len(randSongs)):
            list_of_indeces.append(i)
            
        random.shuffle(list_of_indeces)

        for i in range(0, len(randSongs)):
            if randSongs['tracks']['items']:
                output = randSongs['tracks']['items'][list_of_indeces[i]]
                if not include_explicit: # checks for explicit
                    if output['explicit'] == True:
                        continue
                if output['preview_url']: # checks for preview
                    list_of_tracks_to_export.append(output)
                    break
            elif verbose:
                print("There are no valid songs. Trying again.")
    
    return list_of_tracks_to_export


def get_now_string():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")
                

def create_playlist(playlist_name):
    playlist_description = "Feel free to listen through and favorite any songs you like."
    spotifyObject.user_playlist_create(user=username, name=playlist_name, public=True, description=playlist_description)


def export_playlist(playlist_name, list_of_song_uris):
    
    create_playlist(playlist_name)
    
    prePlaylist = spotifyObject.user_playlists(user=username)
    playlistID = prePlaylist['items'][0]['id']
    
    playlistURL = prePlaylist['items'][0]['external_urls']['spotify']
    
    spotifyObject.user_playlist_add_tracks(user=username, playlist_id=playlistID, tracks=list_of_song_uris)
    
    window = tk.Tk()
    window.withdraw()
    fromonk_text = "You can find your playlist at\n\n" + str(playlistURL)
    CustomDialog(window, title="Playlist URL", text=fromonk_text)
    
    window.destroy()
    window.mainloop()

    

class CustomDialog(tkinter.simpledialog.Dialog):
    
    def __init__(self, parent, title=None, text=None):
        self.data = text
        tkinter.simpledialog.Dialog.__init__(self, parent, title=title)

    def body(self, parent):
        body_font = ('Tahoma', 16)
        self.text = tk.Text(self, width=40, height=4, font=body_font)
        self.text.pack(fill="both", expand=True)

        self.text.insert("1.0", self.data)

        return self.text
    

def generate_image(image_url):
    image = url_to_image(image_url)
    b,g,r = cv2.split(image)
    img = cv2.merge((r,g,b))

    im = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=im)
    return imgtk

def play_track_audio(track, volume=50):
    
    #plays preview audio
    try:
        preview_url = track['preview_url']
        player = vlc.MediaPlayer(preview_url)
        player.audio_set_volume(volume)
        player.play()
        return player
    except:
        messagebox.showwarning("Preview Unavailable", "No audio preview is available.")
        return


def like(current_track):
    list_of_liked_tracks.append(current_track)


class swipe_window:
    
    volume = 50
    
    def __init__(self, current_track, iterator):
        swipe_window.make_window(current_track=current_track, iterator=iterator)
        
    def set_volume(new_volume):
        swipe_window.volume = new_volume    
    
    
    def make_window(current_track, iterator):
        window_height = 800
        window_width = 1200



        window = tk.Tk()
        window.title("Spotify Swipe")
        #---------------------------------------------------------------------

        like_image = tk.PhotoImage(file = r"88x70_green_checkmark.png")
        dislike_image = tk.PhotoImage(file = r"70x70_red_x.png")

        #Canvas
        canvas = tk.Canvas(window, height=window_height , width=window_width)
        canvas.pack()

        #Frame
        frame = tk.Frame(window,height=window_height, width=window_width, bg='white')
        frame.place(relwidth=1, relheight=1)
        
        
        #Track Title, Artist, Album
        label_font = ('Tahoma', 18)
        tk.Label(frame, font=label_font, background='white', text="Name: " + current_track['name']).pack()
        tk.Label(frame, font=label_font, background='white', text="Artist: " + current_track['artists'][0]['name']).pack()
        tk.Label(frame, font=label_font, background='white', text="Album: " + current_track['album']['name']).pack()


        #Cover Art
        cover_art_url = current_track['album']['images'][0]['url']
        cover_art = generate_image(cover_art_url)

        cover_art_label = tk.Label(frame, image=cover_art, bg='white')
        cover_art_label.place(relx=0.25, rely=0.15)


        #Buttons
        like_button = tk.Button(frame, image=like_image, bg='white', borderwidth=3, command=lambda: [player.stop(), like(current_track), swipe_window.refresh(window, iterator=iterator)])
        like_button.place(relx=0.85, rely=0.45)

        dislike_button = tk.Button(frame, image=dislike_image, bg='white', borderwidth=3, command=lambda: [player.stop(), swipe_window.refresh(window, iterator=iterator)])
        dislike_button.place(relx=0.1, rely=0.45)
        
        
        #Volume Slider
        volume_slider = tk.Scale(frame, from_=100, to=0, sliderlength=25, label="Volume", command=lambda x:[player.audio_set_volume(int(x)), swipe_window.set_volume(int(x))])
        volume_slider.set(swipe_window.volume)
        volume_slider.place(relx=0.05, rely=0.8)

        
        #Quit Button
        quit_font = font.Font(family='Tahoma')
        quit_button = tk.Button(frame, width=10, height=2, text="Quit", font=quit_font, bg='white', borderwidth=3, command=lambda: [player.stop(), swipe_window.refresh(window, iterator=iterator+queue_length)])
        quit_button.place(relx=0.90, rely=0.92)

        #Preview audio
        player = play_track_audio(current_track, volume=swipe_window.volume)


        #---------------------------------------------------------------------
        window.mainloop()
        
    def refresh(window, iterator):
        if iterator+1 >= queue_length:
            swipe_window.close_window(window)
        else:
            window.destroy()
            swipe_window.make_window(current_track=track_queue[iterator+1],iterator=iterator+1)
        
    def close_window(window):
        messagebox.showinfo("End of Queue", "You liked " + str(len(list_of_liked_tracks)) + " songs.")
        window.destroy()



"""

Input User Settings

"""
class title_window:
    
    queue_length = -1 # number of songs to put in like/dislike queue
    playlist_name = ""
    include_explicit = True
    start_program = False
    
    def __init__(self):
        title_window.make_window()
        
    
    def get_include_explicit(include_explicit):
        return title_window.include_explicit
    
    def set_include_explicit(input_include_explicit):
        title_window.include_explicit = input_include_explicit
    
    def get_start_program(start_program):
        return title_window.start_program
    
    def set_start_program(input_start_program):
        title_window.start_program = input_start_program
    
    def get_playlist_name(playlist_name):
        return title_window.playlist_name
    
    def set_playlist_name(input_playlist_name):
        title_window.playlist_name = input_playlist_name
    
    def get_queue_length(queue_length):
        return title_window.queue_length
    
    
    def set_queue_length(input_queue_length):
        title_window.queue_length = input_queue_length
            


    def make_window():
        #GUI START

        root = tk.Tk()
        root.title("Spotify Swipe")

        #Canvas and Frame
        window_height = 800
        window_width = 1000

        canvas = tk.Canvas(root, height=window_height , width=window_width)
        canvas.pack()

        #Frame
        frame = tk.Frame(root, height=window_height, width=window_width, bg='white')
        frame.place(relwidth=1, relheight=1)



        #Title Greet
        label_font = ('Tahoma', 28)
        tk.Label(frame, font=label_font, background='white', text="Welcome to Spotify Swipe").pack()


        #Image Logo
        spotify_logo = tk.PhotoImage(file = r"spotify_logo.png")
        tk.Label(frame, image=spotify_logo, bg='white').pack(pady=20)


        #Playlist name input
        playlist_name_frame = tk.Frame(frame, height=175, width=800, bg='light gray', highlightbackground='black', highlightthickness=2)
        playlist_name_frame.pack(pady=15)

        label_font = ('Tahoma', 12)
        playlist_name_label = tk.Label(playlist_name_frame, text="Name of your playlist:", font=label_font, background='light gray')
        playlist_name_label.pack(side=tk.LEFT, padx=20, pady=10)

        playlist_name_field = tk.Entry(playlist_name_frame, borderwidth=3)
        playlist_name_field.pack(side=tk.RIGHT, padx=20)
        

        #Queue length input
        queue_length_frame = tk.Frame(frame, height=175, width=800, bg='light gray', highlightbackground='black', highlightthickness=2)
        queue_length_frame.pack(pady=15)

        label_font = ('Tahoma', 12)
        queue_label = tk.Label(queue_length_frame, text="How many songs do you\nwant to listen to?", font=label_font, background='light gray')
        queue_label.pack(side=tk.LEFT, padx=20, pady=10)

        queue_field = tk.Entry(queue_length_frame, borderwidth=3)
        queue_field.pack(side=tk.RIGHT, padx=20)
        
        
        #Exclude Explicit
        explicit_button_frame = tk.Frame(frame, height=175, width=500, bg='light gray', highlightbackground='black', highlightthickness=2)
        explicit_button_frame.pack(pady=15)
        
        label_font = ('Tahoma', 12)
        explicit_label = tk.Label(explicit_button_frame, text="Exclude explicit songs?", font=label_font, background='light gray')
        explicit_label.pack(side=tk.LEFT, padx=20, pady=10)

        var = tk.IntVar()
        explicit_checkbox = tk.Checkbutton(explicit_button_frame, borderwidth=3, bg='light gray', variable=var)
        explicit_checkbox.pack(side=tk.RIGHT, padx=20)


        #Start Queue button
        start_font = font.Font(family='Tahoma')
        start_button = tk.Button(frame, width=10, height=2, text="Start\nSwiping", font=start_font, bg='white', borderwidth=3, command=lambda:[title_window.start_button_pressed(root, playlist_name_field.get(), queue_field.get(), var.get())])
        start_button.place(relx=0.89,rely=0.92)


        root.mainloop()

        #GUI END

    def start_button_pressed(window, input_playlist_name, input_queue_number, input_include_explicit):
        title_window.set_playlist_name(input_playlist_name)
        
        title_window.set_include_explicit(not input_include_explicit)
        
        try:
            queue_length = int(input_queue_number)
            
            if queue_length <= 0:
                messagebox.showinfo("Invalid Input","Please type in a number greater than zero.")
                return
            
            title_window.set_queue_length(queue_length)
            title_window.set_start_program(True)
            window.destroy()
        except:
            messagebox.showinfo("Invalid Input","Please type in an integer value.")

"""

Main

"""

window = title_window()

queue_length = window.get_queue_length()
playlist_name = window.get_playlist_name()
include_explicit = window.get_include_explicit()
start_program = window.get_start_program()

if start_program:

    if not playlist_name.isalnum() and len(playlist_name) <= 0:
        playlist_name = "SpotifySwipe -- " + get_now_string()
    else:
        playlist_name = playlist_name + " -- " + get_now_string()

    spotifyObject = authenticate_spotify()

    list_of_liked_tracks = []

    track_queue = generate_track_queue(queue_length, include_explicit=include_explicit)
    iterator = 0



    window = swipe_window(track_queue[iterator], iterator=iterator)

    if(len(list_of_liked_tracks) > 0):
        export_playlist(playlist_name, get_track_list_uri(list_of_liked_tracks))
