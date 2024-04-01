import tkinter as tk
import cv2
from PIL import Image, ImageTk
import numpy as np
import json
import customtkinter as ctk


class App:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.geometry("1080x600")
        self.window.resizable(0, 0)
        self.window.title("app")

        self.main_frame = self.create_main_frame()
        self.frame1 = self.create_frame(row=1, column=0, rowspan=4, columnspan=1)
        self.frame2 = self.create_frame(row=5, column=0, rowspan=2, columnspan=1)
        self.frame3 = self.create_frame(row=1, column=1, rowspan=5, columnspan=1)
        self.frame4 = self.create_frame(row=6, column=1, rowspan=1, columnspan=1)
        self.data = []
        self.current_data = []

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
    
    def run(self):
        self.window.mainloop()



app = App()
app.run()
