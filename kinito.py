import tkinter as tk
from tkinter import Menu, simpledialog, messagebox
from PIL import Image, ImageTk
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import random
import requests
import pygame
import threading
import pystray
from pystray import MenuItem as item
import webbrowser
import tempfile
import io

class IconDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("300x100")
        self.root.title("Surf Web")
        self.root.iconbitmap(default="icon.ico")
        self.url_entry = tk.Entry(self.root, width=40)
        self.url_entry.pack(pady=10)
        self.url_entry.focus_set()
        self.open_button = tk.Button(self.root, text="Search", command=self.open_url)
        self.open_button.pack()
        self.root.mainloop()

    def open_url(self):
        url = self.url_entry.get()
        if url:
            webbrowser.open(url)
            self.root.destroy()
        else:
            messagebox.showwarning("Empty URL", "Please enter a URL.")

class AudioFetcher:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.audio_cache = {}  # Dictionary to hold audio content

    def fetch_audio_files(self):
        try:
            kinitoread_file = "audio.kinitoread"
            url = f"{self.repo_url}/{kinitoread_file}"

            response = requests.get(url)
            response.raise_for_status()
            audio_files = response.text.split(",")
            audio_files = [audio.strip() for audio in audio_files]

            for audio_file in audio_files:
                audio_content = self.fetch_audio_content(audio_file)
                if audio_content:
                    self.audio_cache[audio_file] = audio_content

            print("Audio cache:", self.audio_cache)

            return list(self.audio_cache.keys())

        except requests.RequestException as e:
            print("Error fetching audio files:", e)
            return []

    def fetch_audio_content(self, audio_file):
        try:
            audio_url = f"{self.repo_url}/{audio_file}"
            response = requests.get(audio_url)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            print(f"Error fetching audio content for {audio_file}: {e}")
            return None

    def delete_audio_files(self):
        self.audio_cache.clear()

class AudioPlayerThread(threading.Thread):
    def __init__(self, audio_content):
        super().__init__()
        self.audio_content = audio_content

    def run(self):
        pygame.mixer.init()
        audio_file = io.BytesIO(self.audio_content)
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

class DesktopPet(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.wm_attributes('-transparentcolor', 'white')
        self.should_stop = threading.Event()
        self.setup_tray_icon()
        self.setup_menu()
        self.setup_pet()
        self.bind("<Button-3>", self.show_menu)
        self.setup_audio_fetcher() 
#        self.say_hello()

    def setup_audio_fetcher(self):
        self.audio_fetcher = AudioFetcher("https://raw.githubusercontent.com/DMDCR/kinitopetdesktop/main/audio")

    def exit_action(self):
        self.audio_fetcher.delete_audio_files()
        self.destroy()

    def play_audio_from_memory(self, audio_content):
        player_thread = AudioPlayerThread(audio_content)
        player_thread.start()

    def surf_web(self):
        IconDialog()

    def play_audio(self, audio_content, delay=0):
        if audio_content:
            self.play_audio_from_memory(audio_content)

    def setup_tray_icon(self):
        image = Image.open(os.path.join("other", "icon.png"))
        menu = (item('Exit', self.exit_action),)
        self.icon = pystray.Icon("name", image, "KinitoPet Desktop Pet", menu)
        self.tray_thread = threading.Thread(target=self.icon.run)
        self.tray_thread.daemon = True
        self.tray_thread.start()

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def setup_menu(self):
        self.menu = Menu(self, tearoff=0)
        url_menu = Menu(self.menu, tearoff=0)
        url_menu.add_command(label="Search Google", command=self.search_google)
        url_menu.add_command(label="Search Wikipedia", command=self.search_wikipedia)
        self.menu.add_cascade(label="Search", menu=url_menu)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.exit_action)

    def search_google(self):
        audio_files = self.audio_fetcher.fetch_audio_files()
        self.after(0, lambda: self.play_audio(self.audio_fetcher.audio_cache.get("web_open.wav"), delay=3000))
        query = simpledialog.askstring("Google Search", "Enter your Google search query:")
        if query:
            webbrowser.open("https://www.google.com/search?q=" + query.replace(" ", "+"))

    def search_wikipedia(self):
        audio_files = self.audio_fetcher.fetch_audio_files()
        self.after(0, lambda: self.play_audio(self.audio_fetcher.audio_cache.get("web_open.wav"), delay=3000))
        query = simpledialog.askstring("Wikipedia Search", "Enter your Wikipedia search query:")
        if query:
            webbrowser.open("https://en.wikipedia.org/wiki/" + query.replace(" ", "_"))

    def setup_pet(self):
        self.pet_images = {}
        for filename in os.listdir("models/"):
            if filename.endswith('.gif'):
                pet_name = os.path.splitext(filename)[0]
                self.pet_images[pet_name] = self.load_gif(os.path.join("models/", filename))

        self.pet_sprite = tk.Label(self, anchor=tk.CENTER, bg='white')
        self.pet_sprite.pack()
        self.animation_index = 0
        self.direction = 'normal'
        self.moving = True
        self.move_pet()
        self.update_animation()

    def load_gif(self, path):
        gif = Image.open(path)
        frames = []
        try:
            while True:
                frames.append(ImageTk.PhotoImage(gif.copy()))
                gif.seek(len(frames))
        except EOFError:
            pass
        return frames

    def update_animation(self):
        if self.moving:
            if self.direction in self.pet_images:
                self.pet_sprite.config(image=self.pet_images[self.direction][self.animation_index])
                self.animation_index = (self.animation_index + 1) % len(self.pet_images[self.direction])
        else:
            self.pet_sprite.config(image=self.pet_images['normal'][0])
        self.after(120, self.update_animation)

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
            if self.audio_fetcher.audio_cache:  # Check if audio cache is not empty
                audio_content = random.choice(list(self.audio_fetcher.audio_cache.values()))
                self.after(random.randint(3000, 4000), lambda: self.play_audio(audio_content))  
            self.after(random.randint(3000, 4000), self.random_move)
            return

        current_x += step_x
        current_y += step_y

        self.geometry(f"+{int(current_x)}+{int(current_y)}")
        self.after(30, self.glide_to, target_x, target_y, current_x, current_y, step_x, step_y)

    def random_move(self):
        self.moving = True
        self.move_pet()

# I removed the hello feature because i was too lazy to fix it. it also was kinda annoying :|

#     def say_hello(self):
#        audio_files = self.audio_fetcher.fetch_audio_files()
#        if audio_files:
#            audio_content = self.audio_fetcher.audio_cache.get("audio/hello.mp3")  # Fetching 'hello.mp3'
#            if audio_content:
#                self.after(random.randint(3000, 4000), lambda: self.play_audio_from_memory(audio_content))  # Play audio after a random delay
#            else:
#                print("Audio file 'hello.mp3' not found in the repository.")
#        else:
#            print("No audio files fetched from the repository.")

if __name__ == "__main__":
    app = DesktopPet()
    app.mainloop()
