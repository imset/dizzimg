import os
import random
import numpy
import io
from math import ceil
from PIL import Image, ImageDraw, ImageFont
#from colorthief import ColorThief
import fast_colorthief
from pathlib import Path
from . import helper

basepath = Path(__file__).parents[1]

#perspective transformation function (thanks to: https://stackoverflow.com/questions/14177744/how-does-perspective-transformation-work-in-pil)
def find_coeffs(source_coords, target_coords):
    matrix = []
    for s, t in zip(source_coords, target_coords):
        matrix.append([t[0], t[1], 1, 0, 0, 0, -s[0]*t[0], -s[0]*t[1]])
        matrix.append([0, 0, 0, t[0], t[1], 1, -s[1]*t[0], -s[1]*t[1]])
    A = numpy.matrix(matrix, dtype=float)
    B = numpy.array(source_coords).reshape(8)
    res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
    return numpy.array(res).reshape(8)

class Newcomer(object):
    def __init__(self, baseimg=f"{basepath}/data/img/newcomer.png", topimg=f"{basepath}/data/img/vegeta.png", toptext="Top Text", bottext="Bottom Text"):
        self.topimgdir = topimg
        self.topim = Image.open(self.topimgdir).convert("RGBA")
        self.baseimgdir = baseimg
        self.baseim = Image.open(self.baseimgdir).convert("RGBA")

        self.toptext = toptext
        self.bottext = bottext

        if len(self.toptext) > 20:
            print("Top Text too long - shortening to first 20 characters.")
            self.toptext = toptext[:20]
        else:
            self.toptext = toptext
        if len(self.bottext) > 30:
            print("Bottom Text too long - shortening to first 20 characters.")
            self.bottext = bottext[:30]
        else:
            self.bottext = bottext

    def generate(self, **kwargs):
        '''Method to generate the smash newcomer image. Setting show to true will cause the generated picture to be shown with 
        the default image viewer.'''
        fullbg = self.smashbg()
        finalimg = self.smashtext(img=fullbg)
        #store in a variable and return in case we want to return a bytes object, if not generator still functions
        generated = helper.generator(image=finalimg, **kwargs)
        return generated

    def smashbg(self):
        '''Overlays the smash template with the generated gradient background'''
        bg = self.gradient()

        #used to resize the image to fit the dimensions better
        rsz = (self.baseim.height / self.topim.height)

        #resize the image
        topimrsz = self.topim.resize((ceil(self.topim.width*rsz+110), ceil(self.topim.height*rsz+110)), resample=Image.Resampling.LANCZOS)

        shadowbands = topimrsz.split()
        redblk = shadowbands[0].point(lambda i: i * 0)
        greenblk = shadowbands[1].point(lambda i: i * 0)
        blueblk = shadowbands[2].point(lambda i: i * 0)
        alphablk = shadowbands[3].point(lambda i: i * 0.5)
        shadowmerge = Image.merge("RGBA", (redblk, greenblk, blueblk, alphablk))

        shadowedimg = Image.new("RGBA", (topimrsz.width+15, topimrsz.height+15), (255, 255, 255, 0))

        shadowedimg.paste(shadowmerge, (15, 15))
        shadowedimg.alpha_composite(topimrsz)

        newcomer = shadowedimg.rotate(8, expand=1)

        bg.alpha_composite(newcomer, dest=(-100,-100))
        fullbg = Image.alpha_composite(bg, self.baseim).convert("RGBA")
        return fullbg

    def gradient(self, img=None):
        '''Create a gradient background based off the two primary colors of a given image using a random mask from the /Masks/ directory.'''
        #thanks to https://stackoverflow.com/questions/32530345/pil-generating-vertical-gradient-image

        img = img or self.topimgdir

        #find dominant color of input
        #domcolors = ColorThief(img).get_palette(color_count=2, quality=5)
        domcolors = fast_colorthief.get_palette(img, color_count=2, quality=5)

        #two base colors
        base = Image.new('RGB', self.baseim.size, domcolors[0])
        top = Image.new('RGB', self.baseim.size, domcolors[1])

        #get list of masks and choose one randomly
        maskslist = os.listdir(f"{basepath}/data/img/masks/")
        chosen = Image.open(f"{basepath}/data/img/masks/{random.choice(maskslist)}").convert("L")

        #resize it up to 25%
        resize = random.uniform(1.0, 1.25)
        mask = chosen.resize((ceil(chosen.width*resize), ceil(chosen.height*resize)))

        #randomly rotate
        randrot = random.randrange(0, 359)
        mask = mask.rotate(randrot, expand=1)

        #crop it to the size of the base image (thanks to https://stackoverflow.com/questions/16646183/crop-an-image-in-the-centre-using-pil)
        lcrop = (mask.width - self.baseim.width)/2
        rcrop = (mask.width + self.baseim.width)/2
        tcrop = (mask.height - self.baseim.height)/2
        bcrop = (mask.height + self.baseim.height)/2
        mask = mask.crop((lcrop, tcrop, rcrop, bcrop))

        base.paste(top, (0, 0), mask=mask)
        return base.convert("RGBA")
        #base.show()

    def smashtext(self, toptext="Top Text", bottext="Bottom Text", img=None):
        '''Generates the text for the smash newcomer image'''
        #todo: holy shit clean this up it's so ugly

        #defaults
        img = img or self.baseim
        toptext = self.toptext or toptext
        bottext = self.bottext or bottext

        #create blank images for text
        toptxtimg = Image.new("L", (1200, 300))
        topstrokeimg = Image.new("RGBA", (1200, 300), (255, 255, 255, 0))

        bottxtimg = Image.new("L", (1200, 300))
        botstrokeimg = Image.new("RGBA", (1200, 300), (255, 255, 255, 0))

        #if toptext has a space and is over 7 characters, split by the first space after 7 characters.

        if " " in toptext[10:]:
            toptextbackhalf = toptext[10:].replace(" ", "\n", 1)
            toptext = toptext[:10] + toptextbackhalf
            #spacechk = True
        # elif " " in toptext and len(toptext) > 10:
        #     toptext = toptext.replace(" ", "\n", 1)
        #     #spacechk = True
        else:
            pass
            #spacechk = False

        bottextmid = ceil(len(bottext)/2)
        #bottext will only look for spaces after the midway point, and the second line will be shifted. Only if it's above 10 chars.
        if " " in bottext[bottextmid:] and len(bottext) > 10:
            repeat = " " * bottextmid
            bottextbackhalf = bottext[bottextmid:].replace(" ", f"\n{repeat}", 1)
            bottext = bottext[:bottextmid] + bottextbackhalf

        #determine font size by restricting text to width of 1100 and a height of 300 (effectively 550/150 after being cut in half)
        fontchk = False
        fontsize = 200
        botfontsize = 150
        while fontchk == False:
            topfnt = ImageFont.truetype(f"{basepath}/data/fonts/ariblk.ttf", fontsize)
            if topfnt.getsize_multiline(toptext)[0] > 1100 or topfnt.getsize_multiline(toptext)[1] > 300:
                fontsize -= 10
            else:
                fontchk = True

        #repeat the check for the bottom font
        botfontchk = False
        botfontsize = fontsize - 50
        while botfontchk == False:
            botfnt = ImageFont.truetype(f"{basepath}/data/fonts/ariblk.ttf", botfontsize)
            if botfnt.getsize_multiline(bottext)[0] > 1100 or botfnt.getsize_multiline(bottext)[1] > 300:
                botfontsize -= 10
            else:
                botfontchk = True

        #gets drawing context for text images
        g = ImageDraw.Draw(toptxtimg)
        d = ImageDraw.Draw(topstrokeimg)
        f = ImageDraw.Draw(bottxtimg)
        h = ImageDraw.Draw(botstrokeimg)


        #create stroke around text (thanks to https://stackoverflow.com/questions/41556771/is-there-a-way-to-outline-text-with-a-dark-line-in-pil)
        d.multiline_text((600, 150), toptext, stroke_width=10, font=topfnt, fill="black", anchor="mm", align="center")

        g.multiline_text((600, 150), toptext, font=topfnt, fill="white", anchor="mm", align="center")

        h.multiline_text((600, 150), bottext, stroke_width=10, font=botfnt, fill="black", anchor="mm")

        f.multiline_text((600, 150), bottext, font=botfnt, fill="white", anchor="mm")

        #gradient text background (thanks to https://stackoverflow.com/questions/63246100/how-to-draw-character-with-gradient-colors-using-pil)
        topgrad = Image.open(f'{basepath}/data/img/smashtxtgradient_top.png').resize((1200, 300)).convert("RGBA")
        topgrad.putalpha(toptxtimg)
        topstrokeimg.alpha_composite(topgrad)

        botgrad = Image.open(f'{basepath}/data/img/smashtxtgradient_bottom.png').resize((1200, 300)).convert("RGBA")
        botgrad.putalpha(bottxtimg)
        botstrokeimg.alpha_composite(botgrad)

        w = topstrokeimg
        v = botstrokeimg

        skew = 35

        #perspective magic
        coeffs = find_coeffs(
            [(0, 0), (1200, skew), (1200, 300), (0, 300)],
            #[(0, 0), (w.width, 0), (w.width, w.height), (0, w.height)])
            [(0, skew), (1200, 0), (1200, 300+skew), (0, 300-skew)])
        
        w = w.transform((w.width, 300+(skew*2)), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)
        v = v.transform((v.width, 300+(skew*2)), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)

        w = w.rotate(8, expand=1)
        v = v.rotate(4, expand=1)

        #antialias the text
        w = w.resize((w.width // 2, w.height // 2), resample=Image.Resampling.LANCZOS)
        v = v.resize((v.width // 2, v.height // 2), resample=Image.Resampling.LANCZOS)


        img.alpha_composite(w, dest=(470,130))
        img.alpha_composite(v, dest=(500,280))


        return img