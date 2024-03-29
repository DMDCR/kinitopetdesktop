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
        self.say_hello()

    def exit_action(self):
        self.destroy()

    def surf_web(self):
        IconDialog()

    def play_audio(self, audio_path):
        if os.path.exists(audio_path):
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()

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
        url_menu.add_command(label="Surf the web! (Open a website)", command=self.surf_web)
        url_menu.add_command(label="Search Google", command=self.search_google)
        url_menu.add_command(label="Search Wikipedia", command=self.search_wikipedia)
        self.menu.add_cascade(label="Search", menu=url_menu)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.exit_action)

    def search_google(self):
        self.play_audio(os.path.join("other", "search_web.wav"))
        query = simpledialog.askstring("Google Search", "Enter your Google search query:")
        if query:
            webbrowser.open("https://www.google.com/search?q=" + query)

    def search_wikipedia(self):
        self.play_audio(os.path.join("other", "search_web.wav"))
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
            audio_path = random.choice(self.fetch_github_audio_files())
            self.play_audio(audio_path)
            self.after(random.randint(3000, 4000), self.random_move)
            return

        current_x += step_x
        current_y += step_y

        self.geometry(f"+{int(current_x)}+{int(current_y)}")
        self.after(30, self.glide_to, target_x, target_y, current_x, current_y, step_x, step_y)

    def random_move(self):
        self.moving = True
        self.move_pet()

    def say_hello(self):
        audio_url = "other/hello.mp3"
        self.play_audio(audio_url)

    def fetch_github_audio_files(self):
        repo_url = "https://raw.githubusercontent.com/DMDCR/kinitopetdesktop/main/"
        audio_directory = "audio/"
        kinitoread_file = "audio.kinitoread"
        url = repo_url + audio_directory + kinitoread_file

        try:
            response = requests.get(url)
            response.raise_for_status()
            audio_files = response.text.split(",")  
            audio_files = [audio.strip() for audio in audio_files]  
            audio_files = [os.path.join(audio_directory, audio) for audio in audio_files]  
            return audio_files

        except requests.RequestException as e:
            print("Error fetching audio files:", e)
            return []

        except Exception as e:
            print("Unexpected error:", e)
            return []

if __name__ == "__main__":
    app = DesktopPet()
    app.mainloop()
