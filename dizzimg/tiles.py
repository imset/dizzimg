import os
import io
from math import ceil
from PIL import Image, ImageDraw, ImageFont
#from colorthief import ColorThief
from pathlib import Path
import cProfile
import fast_colorthief
from . import helper

basepath = Path(__file__).parents[1]

class TileFilter(object):
    def __init__(self, style, size, bgcolor, space, rotation, image=f"{basepath}/data/img/vegeta.png"):
        self.rotation = rotation
        self.style = style.lower() or "square"
        self.image = Image.open(image)
        self.size = size or 8
        self.sizesqr = self.size*self.size
        self.bgcolor = bgcolor or "black"
        if self.bgcolor.lower() == "transparent":
            self.bgcolor = (0, 0, 0, 0)
        self.space = space

    #def generate(self, show=False, save=False, name=None, returnbytes=False):
    def generate(self, **kwargs):
        ctarray = self.ctarray()
        finalimg = self.tilestyle(self.style, colorarray=ctarray, bgcolor=self.bgcolor, space=self.space, rotation=self.rotation)
        #store in a variable and return in case we want to return a bytes object, if not generator still functions
        #generated = helper.generator(finalimg=finalimg, show=show, save=save, name=name, returnbytes=returnbytes)
        generated = helper.generator(image=finalimg, **kwargs)
        return generated


    def tilestyle(self, style, colorarray, bgcolor, space, rotation):
        #create the image that'll have circles pasted onto it
        newimg = Image.new("RGBA", (self.image.width, self.image.height), bgcolor)
        initialvals = [space, space, ceil(self.image.width/self.size)+space, ceil(self.image.height/self.size)+space]

        for i in range(self.sizesqr):
            #print(i)
            #create a subimage
            subimage = Image.new("RGBA", (ceil(self.image.width/self.size), ceil(self.image.height/self.size)), (255, 255, 255, 0))
            #draw a circle in the center of the subimage with respect to the space parameter. Circle is restricted by height or width, whatever's shorter.
            # print(newimg.height)
            # print(subimage.height)
            #first figure out if the image is tall or wide (squares work just as well with wide being False)
            if self.image.width > self.image.height:
                wide = True
            else:
                wide = False

            c = ImageDraw.Draw(subimage)

            if wide == True:
                offset = subimage.height - space
            else:
                offset = subimage.width - space

            boundbox = [(space, space), (offset, offset)]
            boundcirc = ((offset/2, offset/2), offset/2)

            if style == "circle":
                c.ellipse(boundbox, fill=colorarray[i])
            elif style == "tri" or style == "triangle":
                c.regular_polygon(bounding_circle=boundcirc, n_sides=3, fill=colorarray[i], rotation=rotation)
            elif style == "square":
                c.regular_polygon(bounding_circle=boundcirc, n_sides=4, fill=colorarray[i], rotation=rotation)
            elif style == "hex" or style == "hexagon":
                c.regular_polygon(bounding_circle=boundcirc, n_sides=6, fill=colorarray[i], rotation=rotation)
            elif style =="rounded":
                c.rounded_rectangle(boundbox, radius=12, fill=colorarray[i])

            newimg.alpha_composite(subimage, dest=(ceil(initialvals[0]), ceil(initialvals[1])))

            if not initialvals[2] >= newimg.width: 
                initialvals[0] += ceil(newimg.width/self.size)
                initialvals[2] += ceil(newimg.width/self.size)
            else:
                initialvals[1] += ceil(newimg.height/self.size)
                initialvals[3] += ceil(newimg.height/self.size)
                initialvals[2] = ceil(newimg.width/self.size)
                initialvals[0] = space
        return newimg


    def ctarray(self, image=None):

        image = image or self.image

        initialvals = [0, 0, ceil(image.width/self.size), ceil(image.height/self.size)]
        croparray = []

        #iterates over image, from left to right and top to bottom, splitting it into chunks and generating an array from it.
        for i in range(self.sizesqr):
            croparray.append(image.crop((initialvals[0], initialvals[1], initialvals[2], initialvals[3])))

            if not initialvals[2] >= image.width:
                initialvals[0] += ceil(image.width/self.size)
                initialvals[2] += ceil(image.width/self.size)
                # print("Top:")
                # print(f"({initialvals[0]}, {initialvals[1]}) to ({initialvals[2]}, {initialvals[3]})")
            else:
                initialvals[1] += ceil(image.height/self.size)
                initialvals[3] += ceil(image.height/self.size)
                initialvals[2] = ceil(image.width/self.size)
                initialvals[0] = 0
                # print("Bot:")
                # print(f"({initialvals[0]}, {initialvals[1]}) to ({initialvals[2]}, {initialvals[3]})")

            #croparray[i].show()

        colorarray = []
        for j in croparray:

            image_binary = io.BytesIO()
            j.save(image_binary, 'PNG')
            image_binary.seek(0)

            #color_thief = ColorThief(image_binary)
            try:
                colorarray.append(fast_colorthief.get_dominant_color(image_binary, quality=10))
            except Exception as e:
                if str(e) == "Empty pixels when quantize":
                    colorarray.append("white")


        return colorarray

# if __name__ == "__main__":
#     image = Dots()
#     image.generate()