import cv2
from PIL import Image
import numpy as np
from ultralytics import YOLO


model = YOLO("last (1).pt")
model.predict(source="0",show=True)