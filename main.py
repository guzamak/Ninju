import tkinter as tk
import cv2
from PIL import Image, ImageTk
import numpy as np
import json
import customtkinter as ctk

DEFAULT_FONT_STYLE = ("Arial",50)
LABEL_FONT_STYLE = ("Arial",14)


class Extra(ctk.CTkToplevel):
    def __init__(self,app_instance):
        super().__init__()
        self.title('extra window')
        self.app = app_instance
        self.geometry('750x500')
        self.resizable(0,0)
        self.configure(fg_color="#333333")
        self.img_store = {}
        self.sign_dropdowns = {}
        self.sign_menus = {}
        self.sign = ["rat","rat","rat"]
        self.image = {}
        self.path_frame = self.create_frame(row=1, column=0, rowspan=1, columnspan=1)
        self.sign_frame = self.create_frame(row=2, column=0, rowspan=1, columnspan=5)
        self.img_frame = self.create_frame(row=3, column=0, rowspan=1, columnspan=5)
        self.add_frame = self.create_frame(row=4, column=0, rowspan=1, columnspan=5)

        # need restart when open 
        for key, value in (sign_options.items()):
            image = Image.open(value)
            new_width = image.width // 50
            new_height = image.height // 50
            image = image.resize((new_width, new_height))
            self.image[key] = image
            
        self.create_path()
        self.create_sign_label()
        self.create_submit_button()
        
    def browse_file(self):
        filepath = ctk.filedialog.askopenfilename()
        if filepath:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, filepath)

    def create_frame(self, row, column, rowspan=1, columnspan=1):
        frame = ctk.CTkFrame(self,corner_radius=0,border_width=0,fg_color="#333333")
        frame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew")
        for r in range(row, row + rowspan):
            self.grid_rowconfigure(r, weight=1)
        for c in range(column, column + columnspan):
            self.grid_columnconfigure(c, weight=1)
        return frame
    
    def create_path(self):
        path_label = ctk.CTkLabel(self.path_frame, text="File Path:",font=LABEL_FONT_STYLE)
        path_label.grid(row=0, column=0,padx=5,pady=30)
        self.path_entry = ctk.CTkEntry(self.path_frame,font=LABEL_FONT_STYLE)
        self.path_entry.grid(row=0, column=1, columnspan=2, padx=5)
        browse_button = ctk.CTkButton(self.path_frame, text="Browse", command=self.browse_file,font=LABEL_FONT_STYLE)
        browse_button.grid(row=0, column=3, padx=5, pady=5)  

    def create_sign_label(self):
        for i in range(3):
            sign_label = ctk.CTkLabel(self.sign_frame, text=f"Sign {i+1}:",font=LABEL_FONT_STYLE)
            sign_label.grid(row=1, column=i+1, padx=100)

            self.img_store[i] = ImageTk.PhotoImage(self.image["rat"])

            self.sign_dropdowns[i] = tk.Menubutton(self.img_frame, image=self.img_store[i], relief=tk.RAISED,highlightthickness=0)
            self.sign_dropdowns[i].grid(row=1, column=i+1, padx=50)

        
            self.sign_menus[i] = tk.Menu(self.sign_dropdowns[i], tearoff=False,background="#333333",borderwidth=0)
            self.sign_dropdowns[i].config(menu=self.sign_menus[i])

            for key, value in (self.image.items()):
                self.img_store[str(i)+key] = ImageTk.PhotoImage(value)
                self.sign_menus[i].add_command(label="", compound=tk.LEFT,image=self.img_store[str(i)+key], command=lambda value=key, var=value, index=i: self.change_option(value,index))

    def change_option(self,key,i):
        self.img_store[i] = ImageTk.PhotoImage(self.image[key])
        self.sign_dropdowns[i].config(image=self.img_store[i])
        self.sign[i] = key

    def create_submit_button(self):
        submit = ctk.CTkButton(self.add_frame, text="Add +",font=LABEL_FONT_STYLE, command=self.add_data)
        submit.pack()

    def add_data(self):
        sign = self.sign
        path = self.path_entry.get()
        if path == "" or sign[0] == sign[1] or sign[1] == sign[2]:
            return
        save_data = {
            "sign":self.sign.copy(),
            "path":path
        }
        if len(data) < 5:
            data.append(save_data)
            self.app.save_data()
            self.app.render_data(data)
            self.destroy()

class App:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.geometry("1080x600")
        self.window.resizable(0, 0)
        self.window.title("app")
        global sign_options 
        global data
        sign_options = {"rat":r"./img/rat.png",
                            "snake":r"./img/snake.png", 
                            "hare":r"./img/hare.png", 
                            "dragon":r"./img/dragon.png", 
                            "ox":r"./img/ox.png", 
                            "ram":r"./img/ram.png", 
                            "monkey":r"./img/monkey.png", 
                            "tiger":r"./img/tiger.png", 
                            "bird":r"./img/bird.png", 
                            "dog":r"./img/dog.png", 
                            "boar":r"./img/boar.png"}

        self.main_frame = self.create_main_frame()
        self.frame1 = self.create_frame(row=1, column=0, rowspan=4, columnspan=1)
        self.frame2 = self.create_frame(row=5, column=0, rowspan=2, columnspan=1)
        self.frame3 = self.create_frame(row=1, column=1, rowspan=5, columnspan=1)
        self.frame4 = self.create_frame(row=6, column=1, rowspan=1, columnspan=1)
        self.scroll_frame = self.create_scroll_frame(frame=self.frame3)
        self.current_data = []

        self.canvas = ctk.CTkCanvas(self.frame1,bg="black",borderwidth=0,highlightthickness=2, highlightbackground="#2B719E")
        self.canvas.pack(expand=True, fill="both")
        self.create_plus_button()

        data = []
        self.load_data()

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

    def use_extra_window(self):
        extra_window = Extra(self)

    def render_data(self,d):
        data = d
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        if len(d) != 0:
            for index, item in enumerate(d):
                frame = ctk.CTkFrame(self.scroll_frame,corner_radius=0,border_width=0,)
                frame.pack()
                for i in range(len(item['sign'])):
                    path = sign_options[item['sign'][i]]
                    img = Image.open(path)
                    img = img.resize((200, 200))
                    img = ImageTk.PhotoImage(img)
                    canvas = ctk.CTkCanvas(frame, width=100, height=100,bg="black",borderwidth=0,highlightthickness=2, highlightbackground="#2B719E")
                    canvas.create_image(0, 0, anchor='nw', image=img)
                    canvas.image = img = img
                    canvas.grid(row=0, column=i, padx=10, pady=10)
                label = ctk.CTkLabel(frame, text=f"Path : {item["path"]}",font=LABEL_FONT_STYLE)
                label.grid(row=1, column=0,)
                button = ctk.CTkButton(frame, text="delete", border_width=0, command=lambda d=d,index=index: self.del_data(index,d))
                button.grid(row=1, column=2)

    def del_data(self,i,d):
        d.pop(i)
        self.render_data(d)
        self.save_data()

    def render_current_data(self):
        for child in self.frame2.winfo_children():
            child.destroy()
    
    def webcam(self):
        pass
    
    def sign_detect(self):
        pass

    def save_data(self):
        with open("data.json", "w") as f:
            json.dump(data, f)

    def load_data(self):
        try:
            with open("data.json", "r") as f:
                data = json.load(f)
                self.render_data(data)
        except FileNotFoundError:
            pass

    def run(self):
        self.window.mainloop()


app = App()
app.run()
