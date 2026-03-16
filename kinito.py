import tkinter as tk
from tkinter import Menu, simpledialog, messagebox
from PIL import Image, ImageTk
import os
import sys
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


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

class IconDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("300x100")
        self.root.title("Surf Web")
        self.root.iconbitmap(default=get_resource_path("icon.ico"))
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
        self.audio_cache = {}

    def fetch_audio_files(self):
        try:
            url = f"{self.repo_url}/audio.kinitoread"
            response = requests.get(url)
            response.raise_for_status()
            audio_files = [a.strip() for a in response.text.split(',')]
            for audio_file in audio_files:
                content = self.fetch_audio_content(audio_file)
                if content:
                    self.audio_cache[audio_file] = content
            return list(self.audio_cache.keys())
        except Exception as e:
            print("Error fetching audio files:", e)
            return []

    def fetch_audio_content(self, audio_file):
        try:
            response = requests.get(f"{self.repo_url}/{audio_file}")
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error fetching audio {audio_file}:", e)
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
        # greet
        pygame.mixer.init()
        pygame.mixer.music.load(get_resource_path(os.path.join("other", "hello.mp3")))
        pygame.mixer.music.play()

    def setup_audio_fetcher(self):
        self.audio_fetcher = AudioFetcher(
            "https://raw.githubusercontent.com/DMDCR/kinitopetdesktop/main/audio"
        )

    def exit_action(self):
        self.audio_fetcher.delete_audio_files()
        self.destroy()

    def play_audio_from_memory(self, audio_content):
        AudioPlayerThread(audio_content).start()

    def surf_web(self):
        IconDialog()

    def play_audio(self, content, delay=0):
        if content:
            self.play_audio_from_memory(content)

    def setup_tray_icon(self):
        icon_image = Image.open(get_resource_path(os.path.join("other", "icon.png")))
        menu = (item('Exit', self.exit_action),)
        self.icon = pystray.Icon("name", icon_image, "KinitoPet Desktop Pet", menu)
        t = threading.Thread(target=self.icon.run)
        t.daemon = True
        t.start()

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def setup_menu(self):
        self.menu = Menu(self, tearoff=0)
        url_menu = Menu(self.menu, tearoff=0)
        url_menu.add_command(label="Search Google", command=self.search_google)
        url_menu.add_command(label="Search Wikipedia", command=self.search_wikipedia)
        url_menu.add_command(label="Search YouTube", command=self.search_yt)
        self.menu.add_cascade(label="Search", menu=url_menu)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.exit_action)

    def search_google(self):
        self.audio_fetcher.fetch_audio_files()
        self.after(0, lambda: self.play_audio(
            self.audio_fetcher.audio_cache.get("web_open.wav"),
            delay=3000
        ))
        q = simpledialog.askstring("Google Search", "Enter your query:")
        if q: webbrowser.open("https://www.google.com/search?q=" + q.replace(" ", '+'))

    def search_wikipedia(self):
        self.audio_fetcher.fetch_audio_files()
        self.after(0, lambda: self.play_audio(
            self.audio_fetcher.audio_cache.get("web_open.wav"),
            delay=3000
        ))
        q = simpledialog.askstring("Wikipedia Search", "Enter your query:")
        if q: webbrowser.open("https://en.wikipedia.org/wiki/" + q.replace(" ", '_'))

    def search_yt(self):
        self.audio_fetcher.fetch_audio_files()
        self.after(0, lambda: self.play_audio(
            self.audio_fetcher.audio_cache.get("web_open.wav"),
            delay=3000
        ))
        q = simpledialog.askstring("YouTube Search", "Enter your query:")
        if q: webbrowser.open("https://www.youtube.com/results?search_query=" + q.replace(" ", '+'))

    def setup_pet(self):
        self.pet_images = {}
        models_dir = get_resource_path("models")
        for f in os.listdir(models_dir):
            if f.endswith('.gif'):
                name = os.path.splitext(f)[0]
                self.pet_images[name] = self.load_gif(os.path.join(models_dir, f))
        self.pet_sprite = tk.Label(self, bg='white')
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
        if self.moving and self.direction in self.pet_images:
            self.pet_sprite.config(
                image=self.pet_images[self.direction][self.animation_index]
            )
            self.animation_index = (self.animation_index + 1) % len(
                self.pet_images[self.direction]
            )
        else:
            self.pet_sprite.config(image=self.pet_images['normal'][0])
        self.after(120, self.update_animation)

    def move_pet(self):
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        tx = random.randint(0, w - self.pet_images['normal'][0].width())
        ty = random.randint(0, h - self.pet_images['normal'][0].height())
        cx, cy = self.winfo_x(), self.winfo_y()
        dx, dy = tx - cx, ty - cy
        if dx>0: self.direction='right'
        elif dx<0: self.direction='left'
        elif dy>0: self.direction='down'
        elif dy<0: self.direction='up'
        else: self.direction='normal'
        steps = max(abs(dx), abs(dy)) or 1
        self.glide_to(tx, ty, cx, cy, dx/steps, dy/steps)

    def glide_to(self, tx, ty, cx, cy, sx, sy):
        if (round(cx), round(cy)) == (tx, ty):
            self.moving=False
            if self.audio_fetcher.audio_cache:
                ac = random.choice(list(self.audio_fetcher.audio_cache.values()))
                self.after(random.randint(6000,8000), lambda: self.play_audio(ac))
            self.after(random.randint(6000,8000), self.random_move)
            return
        cx, cy = cx+sx, cy+sy
        self.geometry(f"+{int(cx)}+{int(cy)}")
        self.after(30, self.glide_to, tx, ty, cx, cy, sx, sy)

    def random_move(self):
        self.moving=True
        self.move_pet()

if __name__ == "__main__":
    app = DesktopPet()
    app.mainloop()
