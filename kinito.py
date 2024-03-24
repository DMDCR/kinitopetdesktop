import tkinter as tk
from PIL import Image, ImageTk
import os
import random
import requests
import tempfile
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame 
import sys
import time
import pystray
from pystray import MenuItem as item
import threading

# Made by DMDCR / @dmdev_ on yt

class DesktopPet(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)  # Removes window decorations
        self.attributes('-topmost', True)  # Keep the window on top
        self.wm_attributes('-transparentcolor', 'white')  # Make white transparent
        self.should_stop = threading.Event()  # Event to signal when to stop the tray icon thread
        self.setup_tray_icon()  # Setup tray icon when the object is initialized

    # Function to be called when the menu item is clicked
    def exit_action(self, icon, item):
        print('This feature is not implemented yet!')

    # Function to create and run the tray icon
    def setup_tray_icon(self):
        image = Image.open(os.path.join("other", "icon.png"))  # Path to icon.png within the "other" directory
        menu = (pystray.MenuItem('Please use Task Manager to close Kinito', self.exit_action),)
        self.icon = pystray.Icon("name", image, "KinitoPet Desktop Pet", menu)
        # Run the tray icon in a separate thread
        self.tray_thread = threading.Thread(target=self.icon.run)
        self.tray_thread.daemon = True  # Daemonize the thread so it automatically closes when the main thread ends
        self.tray_thread.start()
        
        # make him say hi on start!
        pygame.mixer.init()
        pygame.mixer.music.load(os.path.join("other", "hello.mp3"))  # Path to hello.mp3 within the "other" directory
        pygame.mixer.music.play()
        
        # Load the GIFs for your best friend
        self.gifs_directory = "models/"
        self.pet_images = {}
        for filename in os.listdir(self.gifs_directory):
            if filename.endswith('.gif'):
                pet_name = os.path.splitext(filename)[0]
                self.pet_images[pet_name] = self.load_gif(os.path.join(self.gifs_directory, filename))

        # Display your best friend
        self.pet_sprite = tk.Label(self, anchor=tk.CENTER, bg='white')
        self.pet_sprite.pack()
        self.animation_index = 0
        self.direction = 'normal'
        self.moving = True
        self.move_pet()
        self.update_animation()
        
        # Check internet connectivity
        if not self.check_internet():
            self.play_failed_internet_audio()
            time.sleep(5)  # Delay to ensure the audio starts playing
            self.destroy()

    def load_gif(self, path):
        gif = Image.open(path)
        frames = []
        try:
            while True:
                frames.append(ImageTk.PhotoImage(gif.copy()))
                gif.seek(len(frames))  # Move to next frame
        except EOFError:
            pass  # End of frames
        return frames

    def update_animation(self):
        if self.moving:
            if self.direction in self.pet_images:
                self.pet_sprite.config(image=self.pet_images[self.direction][self.animation_index])
                self.animation_index = (self.animation_index + 1) % len(self.pet_images[self.direction])
        else:
            self.pet_sprite.config(image=self.pet_images['normal'][0])  # Show normal image
        self.after(120, self.update_animation)  # Maintain frames per second

    def move_pet(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        target_x = random.randint(0, screen_width - self.pet_images['normal'][0].width())
        target_y = random.randint(0, screen_height - self.pet_images['normal'][0].height())

        current_x = self.winfo_x()
        current_y = self.winfo_y()

        dx = target_x - current_x
        dy = target_y - current_y

        if dx > 0:
            self.direction = 'right'
        elif dx < 0:
            self.direction = 'left'
        elif dy > 0:
            self.direction = 'down'
        elif dy < 0:
            self.direction = 'up'
        else:
            self.direction = 'normal'

        steps = max(abs(dx), abs(dy))

        step_x = dx / steps
        step_y = dy / steps

        self.glide_to(target_x, target_y, current_x, current_y, step_x, step_y)

    def glide_to(self, target_x, target_y, current_x, current_y, step_x, step_y):
        if (round(current_x), round(current_y)) == (target_x, target_y):
            self.moving = False
            self.play_random_audio()  # Play random audio file when pet stops
            self.after(random.randint(3000, 4000), self.random_move)  # Random stop time between 3-4 seconds
            return

        current_x += step_x
        current_y += step_y

        self.geometry(f"+{int(current_x)}+{int(current_y)}")
        self.after(30, self.glide_to, target_x, target_y, current_x, current_y, step_x, step_y)

    def random_move(self):
        self.moving = True
        self.move_pet()

    def play_random_audio(self):
        audio_files = self.fetch_github_audio_files()  # Fetch audio files from GitHub
        if audio_files:
            pygame.mixer.init()
            random_audio_file = random.choice(audio_files)
            pygame.mixer.music.load(random_audio_file)
            pygame.mixer.music.play()
        else:
            self.play_failed_internet_audio()

    def play_failed_internet_audio(self):
        audio_file_path = os.path.join("other", "failedinternet.wav")
        if os.path.exists(audio_file_path):
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file_path)
            pygame.mixer.music.play()
            # Calculate the duration of the audio file
            audio = pygame.mixer.Sound(audio_file_path)
            duration = audio.get_length()
            # After the audio finishes playing, close the application
            self.after(int(duration * 1600), self.destroy)

    def check_internet(self):
        try:
            requests.get("https://dmdtutorials.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    def fetch_github_audio_files(self):
        # GitHub repository URL and directory containing audio files
        repo_url = "https://raw.githubusercontent.com/DMDCR/kinitopetdesktop/main/"
        audio_directory = "audio/"
        kinitoread_file = "audio.kinitoread"
        url = repo_url + audio_directory + kinitoread_file

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for invalid response
            audio_files = response.text.split(",")  # Split filenames by comma
            audio_files = [audio.strip() for audio in audio_files]  # Remove leading/trailing whitespace
            audio_files = [os.path.join(audio_directory, audio) for audio in audio_files]  # Construct full paths
            return audio_files

        except requests.RequestException as e:
            print("Error fetching audio files:", e)
            self.play_failed_internet_audio()
            return []

        except Exception as e:
            print("Unexpected error:", e)
            return []

if __name__ == "__main__":
    app = DesktopPet()
    app.mainloop()
