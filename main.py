import tkinter as tk
import cv2
from PIL import Image, ImageTk
import numpy as np
import json
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from ultralytics import YOLO
import subprocess
import os
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

DEFAULT_FONT_STYLE = ("Arial",50)
LABEL_FONT_STYLE = ("Arial",14)

def show_error(text):
    CTkMessagebox(title="Error", message=text, icon="cancel")

class Extra(ctk.CTkToplevel):
    def __init__(self, app_instance):
        super().__init__()
        self.title('extra window')
        self.app = app_instance
        self.geometry('750x500')
        self.resizable(0, 0)
        self.configure(fg_color="#333333")
        self.img_store = {}
        self.sign_dropdowns = {}
        self.sign_menus = {}
        self.sign = ["rat", "rat", "rat"]
        self.image = {}
        self.path_frame = self.create_frame(row=1, column=0)
        self.sign_frame = self.create_frame(row=2, column=0, columnspan=3)
        self.img_frame = self.create_frame(row=3, column=0, columnspan=3)
        self.add_frame = self.create_frame(row=4, column=0, columnspan=3)

        # Need to restart when opened
        for key, value in sign_options.items():
            image = Image.open(value)
            image = image.resize((100, 100))
            self.image[key] = image

        self.create_path()
        self.create_sign_label()
        self.create_submit_button()

    def browse_file(self):
        filepath = ctk.filedialog.askopenfilename()
        if filepath:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, filepath)

    def create_frame(self, row, column, columnspan=1):
        frame = ctk.CTkFrame(self, corner_radius=0, border_width=0, fg_color="#333333")
        frame.grid(row=row, column=column, columnspan=columnspan, padx=5, pady=5, sticky="nsew")
        self.grid_columnconfigure(column, weight=1)
        return frame

    def create_path(self):
        path_label = ctk.CTkLabel(self.path_frame, text="File Path:", font=LABEL_FONT_STYLE)
        path_label.grid(row=0, column=0, padx=5, pady=5)
        self.path_entry = ctk.CTkEntry(self.path_frame, font=LABEL_FONT_STYLE)
        self.path_entry.grid(row=0, column=1, padx=5, pady=5)
        browse_button = ctk.CTkButton(self.path_frame, text="Browse", command=self.browse_file, font=LABEL_FONT_STYLE)
        browse_button.grid(row=0, column=2, padx=5, pady=5)

    def create_sign_label(self):
        sign_label = ctk.CTkLabel(self.sign_frame, text=f"Sign :", font=LABEL_FONT_STYLE)
        sign_label.grid(row=0, column=1, padx=50, pady=5)
        for i in range(3):

            self.img_store[i] = ImageTk.PhotoImage(self.image["rat"])

            self.sign_dropdowns[i] = tk.Menubutton(self.img_frame, image=self.img_store[i], relief=tk.RAISED, highlightthickness=0)
            self.sign_dropdowns[i].grid(row=0, column=i, padx=50, pady=5)

            self.sign_menus[i] = tk.Menu(self.sign_dropdowns[i], tearoff=False, background="#333333", borderwidth=0)
            self.sign_dropdowns[i].config(menu=self.sign_menus[i])

            for key, value in self.image.items():
                self.img_store[str(i)+key] = ImageTk.PhotoImage(value)
                self.sign_menus[i].add_command(label="", compound=tk.LEFT, image=self.img_store[str(i)+key], command=lambda value=key, var=value, index=i: self.change_option(value, index))

    def change_option(self, key, i):
        self.img_store[i] = ImageTk.PhotoImage(self.image[key])
        self.sign_dropdowns[i].config(image=self.img_store[i])
        self.sign[i] = key

    def create_submit_button(self):
        submit = ctk.CTkButton(self.add_frame, text="Add +", font=LABEL_FONT_STYLE, command=self.add_data)
        submit.grid(row=0, column=0, padx=20, pady=20)

    def add_data(self):
        sign = self.sign
        path = self.path_entry.get()
        if path == "" or sign[0] == sign[1] or sign[1] == sign[2]:
            show_error("Path cannot be empty. Signs must be distinct.")
            return

        save_data = {
            "sign": self.sign.copy(),
            "path": path
        }
        if len(self.app.data) < 5:
            self.app.data.append(save_data)
            self.app.save_data()
            self.app.render_data()
            self.destroy()
        else:
            show_error("Maximum 5 elements allowed in data.")

class App:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.geometry("1080x600")
        self.window.resizable(0, 0)
        self.window.title("app")
        global sign_options 
        sign_options = {
                        "bird": r"./img/bird.png",
                        "boar": r"./img/boar.png",
                        "dog": r"./img/dog.png",
                        "dragon": r"./img/dragon.png",
                        "hare": r"./img/hare.png",
                        "horse": r"./img/horse.png",
                        "monkey": r"./img/monkey.png",
                        "ox": r"./img/ox.png",
                        "ram": r"./img/ram.png",
                        "rat": r"./img/rat.png",
                        "snake": r"./img/snake.png",
                        "tiger": r"./img/tiger.png"
                        }
        self.main_frame = self.create_main_frame()
        self.frame1 = self.create_frame(row=1, column=0, rowspan=4, columnspan=1)
        self.frame2 = self.create_frame(row=5, column=0, rowspan=2, columnspan=1)
        self.frame3 = self.create_frame(row=1, column=1, rowspan=5, columnspan=1)
        self.frame4 = self.create_frame(row=6, column=1, rowspan=1, columnspan=1)
        self.scroll_frame = self.create_scroll_frame(frame=self.frame3)
        self.video_cap = cv2.VideoCapture(0)
        self.sign_count = 0
        self.sign_before = ""
        self.model = YOLO("last (1).pt")
        self.current_data = []

        self.canvas = ctk.CTkCanvas(self.frame1,bg="black",borderwidth=0,highlightthickness=2, highlightbackground="#2B719E")
        self.canvas.pack(expand=True, fill="both")
        self.create_plus_button()
        self.create_clear_current_data()

        self.data = []
        self.load_data()
        self.update_webcam()

    def create_main_frame(self):
        frame = ctk.CTkFrame(self.window,border_width=0)
        frame.pack(expand=True, fill="both")
        return frame
    
    def create_frame(self, row, column, rowspan=1, columnspan=1):
        frame = ctk.CTkFrame(self.main_frame,corner_radius=0,border_width=0,)
        frame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew")
        for r in range(row, row + rowspan):
            self.main_frame.grid_rowconfigure(r, weight=1)
        for c in range(column, column + columnspan):
            self.main_frame.grid_columnconfigure(c, weight=1)
        return frame
    
    def create_scroll_frame(self,frame):
        width = frame.winfo_width()
        height = frame.winfo_height()
        sf = ctk.CTkScrollableFrame(frame,width=width,height=height,border_width=0,corner_radius=0,fg_color="#333333")
        sf.pack(expand=True, fill="both")
        return sf

    def create_plus_button(self):
        button = ctk.CTkButton(self.frame4,text="+",font=DEFAULT_FONT_STYLE,border_width=0,command=self.use_extra_window,fg_color="#333333" ,hover_color="#333333",corner_radius=0)
        button.pack(expand=True, fill="both")

    def create_clear_current_data(self):
        button = ctk.CTkButton(self.frame2,text="reset",command=self.clear_current_data)
        button.grid(row=2, column=0, padx=10, pady=10)

    def use_extra_window(self):
        extra_window = Extra(self)

    def render_data(self):
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        if len(self.data) != 0:
            for index, item in enumerate(self.data):
                frame = ctk.CTkFrame(self.scroll_frame, corner_radius=0, border_width=0)
                frame.pack()

                canvas_width = 100
                canvas_height = 100

                for i in range(len(item['sign'])):
                    path = sign_options[item['sign'][i]]
                    img = Image.open(path)
                    img = img.resize((canvas_width, canvas_height))
                    img = ImageTk.PhotoImage(img)
                    
                    canvas = ctk.CTkCanvas(frame, width=canvas_width, height=canvas_height, bg="black", borderwidth=0, highlightthickness=2, highlightbackground="#2B719E")
                    canvas.create_image(0, 0, anchor='nw', image=img)
                    canvas.image = img
                    canvas.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

                label = ctk.CTkLabel(frame, text=f"Path: {item['path'][:20]}...", font=LABEL_FONT_STYLE)
                label.grid(row=1, column=0, columnspan=len(item['sign']), padx=10, pady=(0, 10), sticky="ew")

                button = ctk.CTkButton(frame, text="Delete", border_width=0, command=lambda index=index: self.del_data(index))
                button.grid(row=2, column=0, columnspan=len(item['sign']), padx=10, pady=(0, 10), sticky="ew")

    def del_data(self,i):
        self.data.pop(i)
        self.render_data()
        self.save_data()

    def render_current_data(self):
        for child in self.frame2.winfo_children():
            child.destroy()
            self.create_clear_current_data()
        if len(self.current_data) != 0:
            canvas_width = 125
            canvas_height = 125
            for index, item in enumerate(self.current_data):
                path = sign_options[item]
                img = Image.open(path)
                img = img.resize((canvas_width, canvas_height))
                img = ImageTk.PhotoImage(img)

                canvas = ctk.CTkCanvas(self.frame2, width=canvas_width, height=canvas_height, bg="black", borderwidth=0, highlightthickness=2, highlightbackground="#2B719E")
                canvas.create_image(0, 0, anchor='nw', image=img)
                canvas.image = img
                canvas.grid(row=1, column=index, padx=10, pady=10)

    def clear_current_data(self):
        self.current_data = []
        self.render_current_data()

    def run_path(self):
        for i, item in enumerate(self.data):
            if item["sign"] == self.current_data:
               os.startfile(r"{}".format(item["path"]))
        self.clear_current_data()

    def add_current_data(self,class_index):
        time_threshold = 25
        if len(class_index) != 0 and len(self.current_data) < 3:
            class_list = list(sign_options.keys())
            value = class_list[int(class_index[0])]
            if self.sign_before != "":
                if self.sign_before == value:
                    self.sign_count += 1
                    if self.sign_count == time_threshold:
                        self.current_data.append(value)
                        self.render_current_data()
                else:
                    self.sign_count = 0
                    self.sign_before = value
            else:
                self.sign_count = 1
                self.sign_before = value
        if len(self.current_data) == 3:
            self.run_path()
    
    def update_webcam(self):
        _, img = self.video_cap.read()
        class_index = []
        if _:
            self.frame1.update_idletasks() 
            self.current_img = img

            pil_img = Image.fromarray(cv2.cvtColor(self.current_img, cv2.COLOR_BGR2RGB))
            canvas_width = self.frame1.winfo_width()
            canvas_height = self.frame1.winfo_height()
            img_width, img_height = pil_img.size
 
            if img_width > canvas_width or img_height > canvas_height:
                scale = max(canvas_width / img_width, canvas_height / img_height)
                img_width = int(img_width * scale) 
                img_height = int(img_height * scale) 
                 
            x = (canvas_width - img_width) / 2
            y = (canvas_height - img_height) / 2
            pil_img = pil_img.resize((img_width,img_height))
            results = self.model.predict(pil_img,device=device)
            box = results[0].boxes.cpu().numpy()
            class_index = box.cls
            img = Image.fromarray(cv2.cvtColor(results[0].plot(), cv2.COLOR_BGR2RGB))
            self.webcam = ImageTk.PhotoImage(image=img)
            self.canvas.delete("all")
            self.canvas.create_image(x,y, image=self.webcam, anchor="nw")

        self.add_current_data(class_index)
        self.window.after(15, self.update_webcam)

    def save_data(self):
        with open("data.json", "w") as f:
            json.dump(self.data, f)

    def load_data(self):
        try:
            with open("data.json", "r") as f:
                self.data = json.load(f)
                self.render_data()
        except FileNotFoundError:
            pass

    def run(self):
        self.window.mainloop()


app = App()
app.run()
