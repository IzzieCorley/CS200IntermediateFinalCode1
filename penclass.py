from tkinter import *
from PIL import Image, ImageTk, ImageDraw

class Pen():
    #sets up initial values, and stores references to parts of the main code that it needs to access
    def __init__(self, frame, canvas):
        #save a ref to the frame this is being made inside
        self.penframe = frame
        self.canv = canvas
        
        #creating the Pil pen object that is the main point of this class
        self.brush = ImageDraw.Draw(self.canv)
        
        #values for pen settings
        self.brushSize = 1
        self.hue = 0
        self.sat = 0
        self.value = 0
        #this one in particular will be used in drawing smoother lines by remembering the last location the mouse moved to while the mouse is down
        self.lastxy = (-1,-1)
        
        #brush preview is a small tkinter image (used cuz of the hsv)
        #it goes here so we can edit it easily
        self.prev = ImageTk.PhotoImage(Image.new("HSV", (30,30), color=(0,0,0)))
        self.prevFrame = Label(self.penframe, image=self.prev)
        self.prevFrame.pack()
        
    
#-------------- setters & updaters
    def changeBrushSize(self, val):
        self.brushSize = int(val)

    def changeHue(self, val):
        self.hue = int(val)
        self.updatePreview()
        

    def changeSat(self, val):
        self.sat = int(val)
        self.updatePreview()
        

    def changeValue(self, val):
        self.value = int(val)
        self.updatePreview()
        
    #updates the preview of brush color
    def updatePreview(self):
        self.prev = ImageTk.PhotoImage(Image.new("HSV", (30,30), color=(self.hue, self.sat, self.value)))
        self.prevFrame.configure(image=self.prev)
        
    
#-------------- actually doing the act of drawing