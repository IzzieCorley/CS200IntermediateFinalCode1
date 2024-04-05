
#changes from v1:
#editable image
#adds dot for each movement while button1 is down
#custom hue, sat, & val instead of just size
#full canvas fill button

"""
tutorials used:
https://realpython.com/python-gui-tkinter/#controlling-layout-with-geometry-managers
https://tkdocs.com/tutorial/onepage.html
https://www.tutorialspoint.com/loading-images-in-tkinter-using-pil
"""

from tkinter import *
from PIL import Image, ImageTk, ImageDraw


#---------------------------------------------------------------------------------------------------------------------------
#--- functions that need to be defined before objects

#function: changing brush size with the slider 
brushSize = 1
def changeBrushSize(val):
    global brushSize
    brushSize = int(val)

hue = 0
def changeHue(val):
    global hue
    hue = int(val)
    updatePreview()
    
sat = 0
def changeSat(val):
    global sat
    sat = int(val)
    updatePreview()
    
value = 0
def changeValue(val):
    global value
    value = int(val)
    updatePreview()



#---------------------------------------------------------------------------------------------------------------------------
#---- making a screen, putting things on it

#make a window
window = Tk()
#give it rows & cols
window.rowconfigure(0, minsize=700, weight=1) #all rows
window.columnconfigure(0, minsize=400, weight=1) #column for brush control
window.columnconfigure(1, minsize=650, weight=0) #column for canvas


#add stuff for brush control section
    #a frame for it all to go in
penframe = Frame(master=window, bd = 10, bg="blue")
penframe.grid(row=0, column=0, sticky="nsew")


#widgets for the brush control section

    #size slider
sizebar = Scale(penframe, orient=HORIZONTAL, length=300, from_=1.0, to=30, command=changeBrushSize)
    #hue slider
huebar = Scale(penframe, orient=HORIZONTAL, length=400, from_=0.0, to=255, command=changeHue)
    #saturation slider
satbar = Scale(penframe, orient=HORIZONTAL, length=255, from_=0.0, to=255, command=changeSat)
    #value slider
valuebar = Scale(penframe, orient=HORIZONTAL, length=255, from_=0.0, to=255, command=changeValue)

    #labels the size slider
brushtitle1 = Label(penframe, text="Brush Size:")
brushtitle2 = Label(penframe, text="Hue:")
brushtitle3 = Label(penframe, text="Saturation:")
brushtitle4 = Label(penframe, text="Value:")

brushtitle1.pack()
sizebar.pack()
brushtitle2.pack()
huebar.pack()
brushtitle3.pack()
satbar.pack()
brushtitle4.pack()
valuebar.pack()


#brush preview is a small tkinter image (used cuz of the hsv)
prev = ImageTk.PhotoImage(Image.new("HSV", (30,30), color=(0,0,0)))
prevFrame = Label(penframe, image=prev)
prevFrame.pack()


#other brush options besides color:

#fill w current color button
fillButt = Button(penframe, text = "Fill Canvas With Current Color")
fillButt.pack()

#---------------------------------------------------------------------------------------------------------------------------
#setting up the canvas part of the screen
    #this frame is currently purely aesthetic, creating a grey BG behind the canvas. but the canvas is not actually "inside" it
rightcol = Frame(master=window, bd = 10, bg="grey")
rightcol.grid(row=0, column=1, sticky="nsew")



#make a canvas to be drawn upon
#this is the PIL (base-level) representation of the canvas
canv = Image.new("HSV", (500,500), color=(255,0,255))
#convert the canvas to Tk rep:
can_tk = ImageTk.PhotoImage(canv)
#create a label to put the canvas image
canframe = Label(window, image=can_tk)
canframe.grid(row=0, column=1)

#creates a pen that acts upon the PIL part of canvas
pen = ImageDraw.Draw(canv)



#--- functions that need to go after objects------------------------------------------------------------------------------------

#updates the image shown on the screen
def updateImg():
    global can_tk
    global canv
    global canframe
    can_tk = ImageTk.PhotoImage(canv)
    canframe.configure(image=can_tk)
    
#updates the preview of brush color
def updatePreview():
    global prev
    global prevFrame
    global hue
    global sat
    global value
    prev = ImageTk.PhotoImage(Image.new("HSV", (30,30), color=(hue,sat,value)))
    prevFrame.configure(image=prev)


#draws a single dot onto the pen location, based on global size and HSV
def drawDot(event):
    global pen
    global brushSize
    global hue
    global sat
    global value
    
    
    #decide bounding box of the dot
    offset = brushSize / 2
    location = [event.x - offset, event.y - offset, event.x + offset, event.y + offset]
    #draw the dot
    pen.ellipse(location, (hue,sat,value), (hue,sat,value), 1)
    
    #update the pic
    updateImg()
canframe.bind("<B1-Motion>", drawDot)

#fills canvas with current color when button fillButt is clicked
def fillCanvas():
    global hue
    global sat
    global value
    global pen
    
    pen.rectangle([(0,0),(499,499)], fill=(hue,sat,value), outline=None, width=1)
    updateImg()
fillButt.config(command=fillCanvas)


#make stuff happen now
window.mainloop()