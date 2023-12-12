import os
import pygame
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image, ImageTk
from io import BytesIO
from tkinter import PhotoImage
from tkinter import font
import json

class MusicPlayerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Music Player")
        root.configure(bg='#2c2c2c')  # Set the background color to dark gray
        root.geometry("830x600")

        standard_font = ("Arial", 11, "bold")
        # Set the transparency of the window
        root.attributes('-alpha', 0.95)  # Adjust the value as needed, e.g., 0.95 for 95% opacity
        # Font settings
        time_label_font = ("Arial", 10, "bold")
        song_name_font = ("Arial", 12, "bold")
        search_entry_font = font.Font(family="Arial", size=12, weight="bold")
        self.playlists = {}  # Key: playlist name, Value: list of song file paths
        # Add this line to initialize playlist_selected
        self.playlist_selected = False
        # Initialize Pygame mixer
        pygame.mixer.init()

        # Variables
        self.track_list = []
        self.current_track_index = 0
        self.music_folder = "D:\\Media\\Music"
        self.is_playing = False
        self.is_paused = False
        self.default_album_art_path = os.path.join(os.path.dirname(__file__), 'images\\album_art.png')
        self.load_playlists()  # Load playlists on startup

        # Load control button images
        play_icon_path = os.path.join(os.path.dirname(__file__), 'images\\play_icon.png')
        play_icon_image = PhotoImage(file=play_icon_path)  # Update path as needed
        play_icon_image = play_icon_image.subsample(2, 2)

        stop_icon_path = os.path.join(os.path.dirname(__file__), 'images\\stop_icon.png')
        stop_icon_image = PhotoImage(file=stop_icon_path)  # Update path as needed
        stop_icon_image = stop_icon_image.subsample(2, 2)

        next_icon_path = os.path.join(os.path.dirname(__file__), 'images\\next_icon.png')
        next_icon_image = PhotoImage(file=next_icon_path)  # Update path as needed
        next_icon_image = next_icon_image.subsample(2, 2)

        prev_icon_path = os.path.join(os.path.dirname(__file__), 'images\\previous_icon.png')
        prev_icon_image = PhotoImage(file=prev_icon_path)  # Update path as needed
        prev_icon_image = prev_icon_image.subsample(2, 2)

        # Left Frame for Songs List and Load Button
        self.left_frame = tk.Frame(root, bg='#2c2c2c')
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a frame that will act as the border
        border_frame = tk.Frame(self.left_frame, bg='#ff8c00', bd=2)
        border_frame.pack(fill=tk.X, padx=2, pady=2)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(border_frame, textvariable=self.search_var, bg='#2c2c2c', fg='white', insertbackground='#ff8c00', font=search_entry_font)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Assuming you have a search icon image named 'search_icon.png' in the same directory as your script
        search_icon_path = os.path.join(os.path.dirname(__file__), 'images\\search_icon.png')
        search_icon_image = PhotoImage(file=search_icon_path)

        # Resize the image using 'subsample'. The arguments (x, y) will reduce the image size by those factors. 
        # If the image is 64x64 and you want to make it 32x32, you would use subsample(2, 2).
        search_icon_image = search_icon_image.subsample(3, 3)  # Adjust the subsample values as needed

        self.search_button = tk.Button(border_frame, image=search_icon_image, command=self.search_songs, bg='#ff8c00', borderwidth=0)
        self.search_button.image = search_icon_image  # Keep a reference
        self.search_button.pack(side=tk.LEFT)

        # Songs Listbox
        self.track_listbox = tk.Listbox(self.left_frame, bg='#2c2c2c', fg='white', selectbackground='black')
        self.track_listbox.pack(fill=tk.BOTH, expand=True)
        self.track_listbox.bind("<Double-1>", self.play_selected_song)  # Bind double-click event
        self.track_listbox.bind('<Button-3>', self.on_right_click)

        # Automatically load music list if the directory exists
        if os.path.exists(self.music_folder):
            self.populate_music_list()

        # Load Button
        self.load_button = tk.Button(self.left_frame, text='Load Music Folder', command=self.load_music_folder, bg='#ff8c00', fg='black')
        self.load_button.pack(fill=tk.X)

        self.playlist_listbox = tk.Listbox(self.left_frame, bg='#2c2c2c', fg='white', selectbackground='black', height=1)
        self.playlist_listbox.pack(fill=tk.BOTH, expand=True)

        # Populate the playlist listbox
        self.populate_playlist_listbox()

        # Bind double-click event
        self.playlist_listbox.bind("<Double-1>", self.on_playlist_double_clicked)
        self.playlist_listbox.bind('<Button-3>', self.on_playlist_right_click)

        self.create_playlist_button = tk.Button(self.left_frame, text='Create Playlist', command=self.create_playlist_ui, bg='#ff8c00', fg='black')
        self.create_playlist_button.pack(fill=tk.X)

        # Right Frame for Song Details
        self.right_frame = tk.Frame(root, bg='#2c2c2c')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Song Image Placeholder
        self.song_image_label = tk.Label(self.right_frame, text='Song Image', bg='black', width=20, height=10)
        self.song_image_label.pack(anchor='center', pady=50)

        # Song Name Label
        self.song_name_label = tk.Label(self.right_frame, text='Song Name', bg='#2c2c2c', fg='white', font=song_name_font)
        self.song_name_label.pack()

        # Frame for Time Labels
        self.time_labels_frame = tk.Frame(self.right_frame, bg='#2c2c2c')
        self.time_labels_frame.pack()

        # Current Time Label
        self.current_time_label = tk.Label(self.time_labels_frame, text='00:00', bg='#2c2c2c', fg='#ff8c00', font=time_label_font)
        self.current_time_label.pack(side=tk.LEFT)

        # Separator Label (Optional, for aesthetic purpose)
        self.separator_label = tk.Label(self.time_labels_frame, text='/', bg='#2c2c2c', fg='#ff8c00', font=time_label_font)
        self.separator_label.pack(side=tk.LEFT)

        # Track Duration Label
        self.track_duration_label = tk.Label(self.time_labels_frame, text='00:00', bg='#2c2c2c', fg='#ff8c00', font=time_label_font)
        self.track_duration_label.pack(side=tk.LEFT)

        # Control Buttons Frame
        self.controls_frame = tk.Frame(self.right_frame, bg='#2c2c2c')
        self.controls_frame.pack(anchor='center', pady=28)

        # Progress Bar
        # self.progress = ttk.Progressbar(self.controls_frame, orient='horizontal', mode='determinate', length=100)
        # self.progress.pack(fill=tk.X)

        # Previous Button
        self.prev_button = tk.Button(self.controls_frame, image=prev_icon_image, command=self.prev_track, bg='#ff8c00', borderwidth=0)
        self.prev_button.image = prev_icon_image  # Keep a reference
        self.prev_button.pack(side=tk.LEFT, padx=7)

        # Play/Pause Button
        self.play_pause_button = tk.Button(self.controls_frame, image=play_icon_image, command=self.toggle_play_pause, bg='#ff8c00', borderwidth=0)
        self.play_pause_button.image = play_icon_image  # Keep a reference
        self.play_pause_button.pack(side=tk.LEFT, padx=7)

        # Stop Button
        self.stop_button = tk.Button(self.controls_frame, image=stop_icon_image, command=self.stop_music, bg='#ff8c00', borderwidth=0)
        self.stop_button.image = stop_icon_image  # Keep a reference
        self.stop_button.pack(side=tk.LEFT, padx=7)

        # Next Button
        self.next_button = tk.Button(self.controls_frame, image=next_icon_image, command=self.next_track, bg='#ff8c00', borderwidth=0)
        self.next_button.image = next_icon_image  # Keep a reference
        self.next_button.pack(side=tk.LEFT, padx=7)

        # Center the control buttons
        self.controls_frame.pack(anchor='center')

        # Update the font for buttons and labels
        self.load_button.configure(font=standard_font)
        self.track_listbox.configure(font=standard_font)
        self.playlist_listbox.configure(font=standard_font)
        self.song_image_label.configure(font=standard_font)
        self.song_name_label.configure(font=standard_font)
        # self.song_details_label.configure(font=standard_font)  # Uncomment if you use it

    def on_playlist_right_click(self, event):
        try:
            selected_index = self.playlist_listbox.nearest(event.y)
            self.playlist_listbox.select_clear(0, tk.END)
            self.playlist_listbox.select_set(selected_index)
            selected_playlist = self.playlist_listbox.get(selected_index)
        except IndexError:
            return  # No playlist selected

        # Create a right-click menu
        right_click_menu = tk.Menu(self.root, tearoff=0)
        right_click_menu.add_command(label="Delete Playlist", command=lambda: self.delete_playlist(selected_playlist))
        right_click_menu.add_command(label="Rename Playlist", command=lambda: self.rename_playlist(selected_playlist))

        right_click_menu.tk_popup(event.x_root, event.y_root)

    def delete_playlist(self, playlist_name):
        if messagebox.askyesno("Delete Playlist", f"Are you sure you want to delete '{playlist_name}'?"):
            del self.playlists[playlist_name]
            self.save_playlists()
            self.populate_playlist_listbox()

    def rename_playlist(self, old_name):
        new_name = simpledialog.askstring("Rename Playlist", "Enter new playlist name:", initialvalue=old_name)
        if new_name and new_name != old_name:
            self.playlists[new_name] = self.playlists.pop(old_name)
            self.save_playlists()
            self.populate_playlist_listbox()

    def populate_playlist_listbox(self):
        self.playlist_listbox.delete(0, tk.END)  # Clear existing items
        for playlist in self.playlists.keys():
            self.playlist_listbox.insert(tk.END, playlist)

    def on_playlist_double_clicked(self, event):
        selected_index = self.playlist_listbox.curselection()
        self.playlist_selected = True
        if selected_index:
            selected_playlist = self.playlist_listbox.get(selected_index)
            self.play_playlist(selected_playlist)

    def on_right_click(self, event):
        # Get the selected song
        try:
            selected_index = self.track_listbox.nearest(event.y)
            self.track_listbox.select_clear(0, tk.END)
            self.track_listbox.select_set(selected_index)
            selected_song = self.track_listbox.get(selected_index)
        except IndexError:
            return  # No song selected

        # Create a right-click menu
        right_click_menu = tk.Menu(self.root, tearoff=0)

        if self.playlist_selected:
            # Add option to remove song from playlist
            right_click_menu.add_command(
                label="Remove from Playlist", 
                command=lambda: self.remove_song_from_playlist(selected_index)
            )

        add_to_playlist_menu = tk.Menu(right_click_menu, tearoff=0)
        # Populate the submenu with playlists
        for playlist in self.playlists.keys():
            add_to_playlist_menu.add_command(label=playlist, command=lambda pl=playlist: self.add_song_to_playlist(selected_song, pl))

        right_click_menu.add_cascade(label="Add to Playlist", menu=add_to_playlist_menu)
        right_click_menu.tk_popup(event.x_root, event.y_root)

    def remove_song_from_playlist(self, song_index):
        # Get the name of the currently selected playlist
        playlist_name = self.playlist_listbox.get(tk.ACTIVE)
        if playlist_name and playlist_name in self.playlists:
            # Remove the song from the playlist
            del self.playlists[playlist_name][song_index]
            self.save_playlists()
            # Refresh the song listbox to reflect the removal
            self.play_playlist(playlist_name)

    def create_playlist_ui(self):
        # Create a simple input dialog to get the playlist name from the user
        playlist_name = simpledialog.askstring("Playlist", "Enter playlist name:")
        if playlist_name:
            self.create_playlist(playlist_name)
            self.populate_playlist_listbox()

    def create_playlist(self, playlist_name):
        if playlist_name not in self.playlists:
            self.playlists[playlist_name] = []
            self.save_playlists()

    def add_song_to_playlist(self, song_name, playlist_name):
        if playlist_name in self.playlists:
            self.playlist_selected = True
            # Store only the song name with extension
            song_file = song_name + '.mp3'
            self.playlists[playlist_name].append(song_file)
            self.save_playlists()

    def play_playlist(self, playlist_name):
        if playlist_name in self.playlists:
            # Clear the current track list and the listbox
            self.track_list = []
            self.track_listbox.delete(0, tk.END)

            # Load tracks from the selected playlist
            playlist_tracks = [os.path.join(self.music_folder, name) for name in self.playlists[playlist_name]]
            self.track_list = playlist_tracks

            # Repopulate the listbox with playlist tracks
            for track_path in playlist_tracks:
                track_name = os.path.basename(track_path)  # Get the base name of the file
                track_name_without_extension = os.path.splitext(track_name)[0]  # Remove the file extension
                self.track_listbox.insert(tk.END, track_name_without_extension)

            # If the playlist has songs, play the first song
            if self.track_list:
                self.current_track_index = 0
                self.play_music(0)

    def save_playlists(self):
        # Convert full paths to just file names before saving
        playlists_to_save = {}
        for playlist_name, track_paths in self.playlists.items():
            playlists_to_save[playlist_name] = [os.path.basename(path) for path in track_paths]
    
        with open('playlists.json', 'w') as file:
            json.dump(playlists_to_save, file)

    def load_playlists(self):
        try:
            with open('playlists.json', 'r') as file:
                loaded_playlists = json.load(file)
                self.playlists = {}
                for playlist_name, track_names in loaded_playlists.items():
                    self.playlists[playlist_name] = [os.path.join(self.music_folder, name) for name in track_names]
        except (FileNotFoundError, json.JSONDecodeError):
            self.playlists = {}

    def search_songs(self):
        search_term = self.search_var.get().lower()
        self.populate_music_list(search_term)

    def update_playback_time(self):
        if self.is_playing and not self.is_paused:
            # Get the current playback time
            current_time = pygame.mixer.music.get_pos() // 1000  # Convert to seconds
            formatted_time = self.format_time(current_time)
            self.current_time_label.config(text=formatted_time)

        # Schedule this method to run again after 1 second
        self.root.after(1000, self.update_playback_time)

    def format_time(self, seconds):
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def check_and_play_next(self):
        if not pygame.mixer.music.get_busy() and self.is_playing:
            self.next_track()
        # Schedule the method to run again after 1000 milliseconds
        self.root.after(1000, self.check_and_play_next)

    def populate_music_list(self, search_term=''):
        self.track_list = [f for f in os.listdir(self.music_folder) if f.endswith('.mp3')]
        self.track_listbox.delete(0, tk.END)
        for track in self.track_list:
            track_name_without_extension = os.path.splitext(track)[0]
            if search_term in track_name_without_extension.lower():
                self.track_listbox.insert(tk.END, track_name_without_extension)

    def extract_album_art(self, track_path):
        try:
            file = MP3(track_path, ID3=ID3)
            # Check for album art
            for tag in file.tags.values():
                if isinstance(tag, APIC):
                    album_art = Image.open(BytesIO(tag.data))
                    return album_art
        except Exception as e:
            print(f"Error extracting album art: {e}")
        return None  # Return None if no album art is found or an error occurs
    
    def update_song_selection(self):
        # Clear previous selection
        for i in range(self.track_listbox.size()):
            self.track_listbox.itemconfig(i, {'bg': '#2c2c2c', 'fg': 'white'})

        # Highlight the current track
        if self.current_track_index is not None:
            self.track_listbox.selection_clear(0, tk.END)
            self.track_listbox.selection_set(self.current_track_index)
            self.track_listbox.activate(self.current_track_index)
            self.track_listbox.itemconfig(self.current_track_index, {'fg': '#ff8c00'})
            self.track_listbox.see(self.current_track_index)  # Ensure the current track is visible

    def load_music_folder(self):
        self.music_folder = filedialog.askdirectory()
        if self.music_folder:
            self.playlist_selected = False  # No playlist is selected
            self.track_list = [f for f in os.listdir(self.music_folder) if f.endswith('.mp3')]
            self.track_listbox.delete(0, tk.END)
            for track in self.track_list:
                track_name_without_extension = os.path.splitext(track)[0]
                self.track_listbox.insert(tk.END, track_name_without_extension)

    def play_selected_song(self, event=None):
        """Play the selected song from the list."""
        selected_index = self.track_listbox.curselection()
        if selected_index:
            self.play_music(selected_index[0])

    def toggle_play_pause(self):
        if not self.track_list:
            return

        if not self.is_playing or self.is_paused:
            self.resume_music()
        else:
            self.pause_music()

    def play_music(self, track_index=None):
        if track_index is not None:
            self.current_track_index = track_index
        else:
            selected_index = self.track_listbox.curselection()
            if selected_index:
                self.current_track_index = selected_index[0]

        if self.playlist_selected:
            track_path = self.track_list[self.current_track_index]
        else:
            track_name = self.track_list[self.current_track_index]
            track_path = os.path.abspath(os.path.join(self.music_folder, track_name))

        # Extract just the song name without the full path
        track_name_without_extension = os.path.splitext(os.path.basename(track_path))[0]

        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            # Change the button to show the 'pause' icon
            pause_icon_path = os.path.join(os.path.dirname(__file__), 'images\\pause_icon.png')
            pause_icon_image = PhotoImage(file=pause_icon_path).subsample(2, 2)  # Assuming you want to resize
            self.play_pause_button.config(image=pause_icon_image)
            self.play_pause_button.image = pause_icon_image  # Keep a reference

            # Update the song name label with the current track's name
            self.song_name_label.config(text=track_name_without_extension)
            # Update the selection in the listbox
            self.update_song_selection()
        
            # Get and display the track duration
            audio = MP3(track_path)
            duration = int(audio.info.length)
            self.track_duration_label.config(text=self.format_time(duration))
        
            # Extract and display album art
            album_art = self.extract_album_art(track_path)
            if album_art:
                # Resize the image to fit the label
                album_art = album_art.resize((200, 200), Image.Resampling.LANCZOS)
                album_art_photo = ImageTk.PhotoImage(album_art)
                self.song_image_label.config(image=album_art_photo, width=200, height=200)
                self.song_image_label.image = album_art_photo  # Keep a reference
            else:
                # Display the default album art if no album art is found
                default_art = Image.open(self.default_album_art_path)
                default_art = default_art.resize((200, 200), Image.Resampling.LANCZOS)
                default_art_photo = ImageTk.PhotoImage(default_art)
                self.song_image_label.config(image=default_art_photo, width=200, height=200)
                self.song_image_label.image = default_art_photo  # Keep a reference

            # Start the loop to check for the end of the song
            self.root.after(1000, self.check_and_play_next)

            # Start updating the playback time
            self.update_playback_time()

        except pygame.error as e:
            messagebox.showerror("Error playing track", f"An error occurred: {e}")

    def pause_music(self):
        pygame.mixer.music.pause()
        self.is_playing = False
        self.is_paused = True
        # Change the button to show the 'play' icon
        play_icon_path = os.path.join(os.path.dirname(__file__), 'images\\play_icon.png')
        play_icon_image = PhotoImage(file=play_icon_path).subsample(2, 2)  # Assuming you want to resize
        self.play_pause_button.config(image=play_icon_image)
        self.play_pause_button.image = play_icon_image  # Keep a reference


    def resume_music(self):
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            self.play_music()
        self.is_playing = True
        # Change the button to show the 'pause' icon
        pause_icon_path = os.path.join(os.path.dirname(__file__), 'images\\pause_icon.png')
        pause_icon_image = PhotoImage(file=pause_icon_path).subsample(2, 2)  # Assuming you want to resize
        self.play_pause_button.config(image=pause_icon_image)
        self.play_pause_button.image = pause_icon_image  # Keep a reference

    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        # Change the button to show the 'play' icon
        play_icon_path = os.path.join(os.path.dirname(__file__), 'images\\play_icon.png')
        play_icon_image = PhotoImage(file=play_icon_path).subsample(2, 2)  # Assuming you want to resize
        self.play_pause_button.config(image=play_icon_image)
        self.play_pause_button.image = play_icon_image  # Keep a reference


    def next_track(self):
        if self.track_list:  # Check if the list is not empty
            self.current_track_index = (self.current_track_index + 1) % len(self.track_list)
            self.play_music(self.current_track_index)
            self.is_playing = True  # Make sure to set this flag

    def prev_track(self):
        if self.track_list:  # Check if the list is not empty
            self.current_track_index = (self.current_track_index - 1) % len(self.track_list)
            self.play_music(self.current_track_index)

# Main
if __name__ == "__main__":
    root = tk.Tk()
    gui = MusicPlayerGUI(root)
    root.mainloop()