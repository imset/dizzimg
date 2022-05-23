import os
import io
from math import ceil
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def generator(image, **kwargs):
    '''Generator function used to output the given final image'''
    if 'returnbytes' in kwargs:
        if kwargs['returnbytes'] == True:
            image_binary = io.BytesIO()
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            return image_binary
    else:
        if 'show' in kwargs:
            if kwargs['show'] == True:
                image.show()

        if 'save' in kwargs:
            if kwargs['save'] == True:
                if kwargs['name'] == None:
                    name = "output.png"
                elif kwargs['name'][-4:].lower() != ".png":
                    name = kwargs['name'] + ".png"
                else:
                    name = kwargs['name']
                try:
                    image.save(name, format="png")
                except FileNotFoundError:
                    #get the directory string
                    newdir = name.split("/")
                    newdir.pop()
                    newdir = "/".join(newdir)
                    os.mkdir(newdir)
                    image.save(name, format="png")
        return