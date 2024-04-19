#todo: fix it so that u cant switch to pen mode while the bucket fill is in progress

"""
tutorials used:
https://realpython.com/python-gui-tkinter/#controlling-layout-with-geometry-managers
https://tkdocs.com/tutorial/onepage.html
https://www.tutorialspoint.com/loading-images-in-tkinter-using-pil
https://www.baeldung.com/cs/flood-fill-algorithm
"""

from tkinter import * #for window, widget items
from PIL import Image, ImageTk, ImageDraw #for image processing
from collections import deque #data structure used to implement bucket fill

#this class handles the pen, including its related objects: the tk pen and the label that shows brush value previews
from penclass import Pen



#---------------------------------------------------------------------------------------------------------------------------
#---- making a screen, putting things on it

#make a window
window = Tk()
#give it rows & cols
window.rowconfigure(0, minsize=700, weight=1) #all rows
window.columnconfigure(0, minsize=400, weight=1) #column for brush control
window.columnconfigure(1, weight=0) #column for canvas


#---------------------------------------------------------------------------------------------------------------------------
#setting up the canvas part of the screen
rightcol = Frame(master=window, bd = 10, bg="grey")
#give the rightcol 2 rows, a small & a big one, for the status messages and the canvas itself, respectively
rightcol.rowconfigure(0, minsize = 50, weight=1)
rightcol.rowconfigure(0, weight=0)
#place the rightcol down
rightcol.grid(row=0, column=1, sticky="nsew")


#make a canvas to be drawn upon
#this is the PIL (base-level) representation of the canvas
canv = Image.new("HSV", (500,500), color=(255,0,255))
#convert the canvas to Tk rep:
can_tk = ImageTk.PhotoImage(canv)
#create a label to put the canvas image
canframe = Label(rightcol, image=can_tk)
canframe.grid(row=1, column=0)

#make a status message label
statusLabel = Label(rightcol, text="Brush Mode")
statusLabel.grid(row=0,column=0)



#---------------------------------------------------------------------------------------------------------------------------
#add stuff for brush control section
    #a frame for it all to go in
penframe = Frame(master=window, bd = 10, bg="blue")
penframe.grid(row=0, column=0, sticky="nsew")


#create the pen object that we draw with
pen = Pen(penframe, canv)

#widgets for the brush control section

    #size slider
sizebar = Scale(penframe, orient=HORIZONTAL, length=300, from_=1.0, to=30, command=pen.changeBrushSize)
    #hue slider
huebar = Scale(penframe, orient=HORIZONTAL, length=400, from_=0.0, to=255, command=pen.changeHue)
    #saturation slider
satbar = Scale(penframe, orient=HORIZONTAL, length=255, from_=0.0, to=255, command=pen.changeSat)
    #value slider
valuebar = Scale(penframe, orient=HORIZONTAL, length=255, from_=0.0, to=255, command=pen.changeValue)

    #labels for the sliders
brushtitle1 = Label(penframe, text="Brush Size:")
brushtitle2 = Label(penframe, text="Hue:")
brushtitle3 = Label(penframe, text="Saturation:")
brushtitle4 = Label(penframe, text="Value:")

#putting the sliders and their labels onto the screen, in order of top to bottom
brushtitle1.pack()
sizebar.pack()
brushtitle2.pack()
huebar.pack()
brushtitle3.pack()
satbar.pack()
brushtitle4.pack()
valuebar.pack()



#other brush options besides color:


#the buttons below get their command at the spot where their command functions are actually implemented

#fill w current color button
fillButt = Button(penframe, text = "Fill Canvas With Current Color")
fillButt.pack()

#clicking this button turns on brush mode
brushButt = Button(penframe, text = "Brush Mode")
brushButt.pack()

#clicking this button turns on fill bucket mode
bucketButt = Button(penframe, text = "Fill Bucket Mode")
bucketButt.pack()


#---------------------------------------------------------------------------------------

#updates the image shown on the screen, which is done after a single dot/line is drawn
def updateImg():
    global can_tk
    global canv
    global canframe
    can_tk = ImageTk.PhotoImage(canv)
    canframe.configure(image=can_tk)


#--- ACTION FUNCTIONS ------------------------------------------------------------------------------------

#ACTIONS FOR BRUSH MODE --------------------------------------------------------
    
#this value is the previous location of b1 motion

#draws a single dot onto the pen location, based on global size and HSV
def drawDot(event):
#you have to use some global variables with this stuff because you can't pass arguments to a button command function
    global pen
    
    #(abs(lastxy[0]-event.x) > 2 and abs(lastxy[1]-event.y))
    
    if pen.lastxy != (-1,-1):
        #draw small lines with the pen.line()
        if pen.brushSize <= 7:
            location = [(pen.lastxy[0], pen.lastxy[1]), (event.x, event.y)]
            #draw dot 
            pen.brush.line(location, (pen.hue, pen.sat, pen.value), pen.brushSize, "curve")
            
            #update last xy to be new
            lastxy = (event.x, event.y)
            
        #if the brush is bigger than 7, using pen.line() looks wrong. so we use pen.ellipse() for bgiger lines
        else:
            #decide bounding box of the dot
            offset = pen.brushSize / 2
            location = [event.x - offset, event.y - offset, event.x + offset, event.y + offset]
            #draw the dot
            pen.brush.ellipse(location, (pen.hue, pen.sat, pen.value), (pen.hue, pen.sat, pen.value), 1)
        
            
    #update last x & y
    pen.lastxy = (event.x, event.y)
    #update the pic
    updateImg()



#this resets the last x & y so that the next time you click & drag, it doesnt draw a line from the last place u let up ur mouse to the new place ur clicking
def mouseUp(event):
    global pen
    pen.lastxy = (-1,-1)


 
#fills canvas with current color when button fillButt is clicked
def fillCanvas():
    #you have to use global variables with this stuff because you can't pass arguments to a button command function
    global pen
    
    pen.brush.rectangle([(0,0),(499,499)], fill=(pen.hue,pen.sat,pen.value), outline=None, width=1)
    updateImg()

#ACTIONS FOR FILL BUCKET MODE ---------------------------------------------------------

filling = False

#this is a helper function for BucketFill that takes a single xy coordinate, and a desired color, and decides whether the coord is in the range and also the target color.
    #Returns true when the pixel is in range and is the color we're trying to replace
def isValid(canv, pixels, x, y, targetColor, visited):
    #check if it's valid range at all
    if x >= canv.width or x < 0 or y >= canv.height or y < 0:
        return False
    #if it was a valid range then check if its been visited before
    if visited[y][x] == True:
        return False
    
    #if it hasnt been visited before lets check if it's the same color as the field we're trying to fill
    
    #2 edge cases to handle first:
    #all values of value = 0 are black, regardless of h or s
    if targetColor[2] == 0:
        #"if it's not also black..."
        if pixels[x,y][2] != 0:
            return False
    #all values of value = 255 and saturation = 0 are white regardless of hue
    if targetColor[1] == 0 and targetColor[2] == 255:
        if pixels[x,y][1] != 0 and pixels[x,y][2] != 255:
            return False
    #if it's not black or white, we can just check if it has equality of all 3 fields:
    if pixels[x,y] != targetColor:
        return False
    
    #if we got this far then we're good to go
    return True
    
    
'''
#edge case for color detection to consider later:
all colors where value = 0 are black, regardless of H and S
all colors where value = 255 and sat = 0 are white, regardless of H
'''
    
def bucketFill(event):
    global filling
    if not filling:
        filling = True
        global canv #access the canvas to edit it
        global pen #access the pen to get the HSV values
        #the user cannot do other things til the fill is done 
        modePaused()
        
        #access the pixels of the image we're working with, as a 2D array
        pixels = canv.load()
        
        #save the color of the pixel we clicked on, so we can convert other pix's to this color
        targetColor = pixels[event.x, event.y]
        #it is in the format of (hue 0-255, sat 0-255, val 0-255)
        #and the new color we want is the pen's current HSV
        newColor = (pen.hue, pen.sat, pen.value)
        
        #create an array that maps each pixel of the canvas to a value, T or F, whether we've visited the pixel
            #during the BFS we're about to do
        visited = []
        for y in range(canv.height):
            row = []
            for x in range(canv.width):
                row.append((x,y))
            visited.append(row)
        #NOTE That this implementation of visited is [column][row]
        

        #create a queue for storing pixels to look at individually during our BFS
        queue = deque()
        
        #now we'll add our first pixel
        queue.append((event.x, event.y))
        visited[event.y][event.x] = True
        
        #now we're gonna loop through til weve run out of valid 4-connected pixels
        #to help loop we're going to create a helper array that helps us look at different rows/columns
        deltax = [1, -1, 0, 0]
        deltay = [0, 0, 1, -1]
        
        while len(queue) > 0:
            #dequeue the pixel, look at it for this loop
            currentPixel = queue.popleft()
                #reminder: currentPixel is a tuple of (x,y) values
            #if its in our queue then we know it's valid so let's give it the new color
                #we access the index of the pixels object that corresponds to the currentpixel tuple
            pixels[currentPixel[0], currentPixel[1]] = newColor
            
            #now let's look at its 4-connected neighbors and add them to the queue if theyre valid
            for i in range(4):
                #using deltax/y to calculate the row and column we're looking towards
                rowLookedAt = currentPixel[0] + deltax[i]
                colLookedAt = currentPixel[1] + deltay[i]
                #check if this current pixel is valid (exists in range, unvisited, and the color we're trying to replace)
                if isValid(canv, pixels, rowLookedAt, colLookedAt, targetColor, visited):
                    #change corresponding entry in Visited
                    visited[colLookedAt][rowLookedAt] = True
                    #add its coords to queue
                    queue.append((rowLookedAt, colLookedAt))
        
            #visited[col][row] = True
        
        
        
        
        #now we're done, we can show the results and allow the user to do things again
        updateImg()
        modeBucket()
        filling = False
    


#--------------------------------------------------------------------------------------------------------------
#here is where ACTION FUNCTIONS are given their ability to be called/not called, based on what tool is active at the moment (brush or fill bucket)

def modeBrush():
    global canframe
    #this binds the function to the event of left mouse going up
    canframe.bind("<ButtonRelease-1>", mouseUp)
    #the canvas waits until there's motion, then draws a dot
    canframe.bind("<B1-Motion>", drawDot)
    canframe.unbind("<Button-1>")
    
    global fillButt
    fillButt.config(state=NORMAL)
    #this line of code links the press of FillButton to filling the whole canvas
    
    global bucketButt
    bucketButt.config(state=NORMAL)
    
    #now update the message
    global statusLabel
    statusLabel.configure(text="Brush Mode")

def modeBucket():
    global canframe
    #this makes the canvas no longer watch for movement of the pen in order to draw lines / update line drawing data
    canframe.unbind("<ButtonRelease-1>")
    canframe.unbind("<B1-Motion>")
    #this makes you do a bucket fill when you click
    canframe.bind("<Button-1>", bucketFill)
    
    global fillButt
    fillButt.config(state=NORMAL)
    global brushButt
    brushButt.config(state=NORMAL)
    global bucketButt
    bucketButt.config(state=NORMAL)
    
    #now update the message
    global statusLabel
    statusLabel.configure(text="Fill Bucket Mode")

def modePaused():
    global canframe
    #this makes the canvas no longer watch for movement of the pen in order to draw lines / update line drawing data
    canframe.unbind("<ButtonRelease-1>")
    canframe.unbind("<B1-Motion>")
    canframe.unbind("<Button-1>")
    
    #you cant change any states/press any buttons while paused
    global fillButt
    #this stops you from covering the canvas while the fill tool is in action
    fillButt.config(state=DISABLED)
    
    global brushButt
    brushButt.config(state=DISABLED)
    
    global bucketButt
    bucketButt.config(state=DISABLED)

    
    #now update the message
    global statusLabel
    statusLabel.configure(text="Loading...")



fillButt.config(command=fillCanvas)
brushButt.config(command=modeBrush)
bucketButt.config(command=modeBucket)

#to set up, at the start, bind events to brush mode 
modeBrush()




#make stuff happen now (this makes the tk window object actually do its thing, like opening a window and waiting for events)
window.mainloop()