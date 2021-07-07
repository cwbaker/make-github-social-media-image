#!/usr/bin/python

from github import Github
from PIL import Image, ImageDraw, ImageFont
import math
import cairosvg
import io
import argparse

class Canvas:
    def __init__(self, width, height, background_color):
        self.image = Image.new("RGB", (width, height), background_color)
        self.draw = ImageDraw.Draw(self.image)
        self.position = (0, 0)

    def set_position(self, x, y):
        self.position = (x, y)

    def advance(self, dx, dy):
        self.position = (
            math.floor(self.position[0] + dx),
            math.floor(self.position[1] + dy)
        )

    def new_line(self, font):
        self.text_size = self.draw.textsize('0123456789', font=font)
        self.position = (
            0,
            math.floor(self.position[1] + 1.1 * self.text_size[1])
        )

    def draw_text(self, text, color, font):
        self.draw.text(self.position, text, fill=color, font=font, anchor='ls')
        self.text_size = self.draw.textsize(text, font=font)
        self.advance(self.text_size[0], 0)

    def draw_icon(self, icon, mask):   
        # The vertically centered icon position should be calculated by
        # subtracting half the icon's height from the baseline position but the
        # icons themselves aren't centered within their size.  Subtracting a
        # third of the size is empirically nice for the default text and icon 
        # size of 48.
        icon_position = (self.position[0], math.floor(self.position[1] - self.text_size[1] / 2 - mask.size[1] / 3))
        self.image.paste(icon, icon_position, mask=mask)
        self.advance(mask.size[0], 0)

    def draw_background(self, icon, mask):
        canvas.image.paste(icon, canvas.position, mask=mask)

    def save(self, filename):
        self.image.save(filename)

def load_svg(filename, scale=1):
    return Image.open(
        io.BytesIO(
            cairosvg.svg2png(
                file_obj=open(filename, "rb"),
                write_to=None,
                scale=scale
            )
        )
    )

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', default='github-social-media-image.png', help='output filename')
parser.add_argument('-W', '--width', default=1280, help='image width')
parser.add_argument('-H', '--height', default=640, help='image height')
parser.add_argument('input', help='Github repository owner and name, e.g. cwbaker/forge')
args = parser.parse_args()

input = args.input
github = Github()
repo = github.get_repo(input)
output = '/output/%s' % (args.output)

width = args.width
height = args.height
background_color = '#ffe'
dark_color = '#333'
light_color = '#555'
faint_color = '#eed'
large_regular_font = ImageFont.truetype( "./SourceSerifPro-Regular.otf", 96 )
large_bold_font = ImageFont.truetype( "./SourceSerifPro-Bold.otf", 96 )
regular_font = ImageFont.truetype( "./SourceSerifPro-Regular.otf", 48 )
star = load_svg( "./octicons/icons/star-24.svg", scale=2.5 )
fork = load_svg( "./octicons/icons/repo-forked-24.svg", scale=2.5 )
mark = load_svg( "./octicons/icons/mark-github-16.svg", scale=48 )
icon = Image.new( "RGB", (60, 60), dark_color )
faint_icon = Image.new( "RGB", (768, 768), faint_color )

canvas = Canvas(width, height, background_color)

canvas.set_position(math.floor((width - mark.width) / 8), math.floor((height - mark.height) / 2))
canvas.draw_background(faint_icon, mark)

owner_size = canvas.draw.textsize('%s/' % repo.owner.login, font=large_regular_font)
repository_size = canvas.draw.textsize(repo.name, font=large_bold_font)
description_size = canvas.draw.textsize(repo.description, font=regular_font)
content_width = max(owner_size[0] + repository_size[0], description_size[0])
content_height = owner_size[1] + 2 * description_size[1]

top = math.floor((height - content_height) / 2 + owner_size[1] / 2)
left = math.floor((width - content_width) / 2)

canvas.set_position(left, top)
canvas.draw_text('%s/' % repo.owner.login, dark_color, large_regular_font)
canvas.draw_text(repo.name, dark_color, large_bold_font)

canvas.new_line(regular_font)
canvas.advance(left, 0)
canvas.draw_text(repo.description, light_color, regular_font)

canvas.new_line(regular_font)
canvas.advance(left, 8)
stars = '%d' % repo.stargazers_count
canvas.draw_icon(icon, star)
canvas.advance(8, 0)
canvas.draw_text(stars, dark_color, regular_font)
canvas.advance(24, 0)
forks = '%d' % repo.forks_count
canvas.draw_icon(icon, fork)
canvas.advance(6, 0)
canvas.draw_text(forks, dark_color, regular_font)
canvas.advance(32, 0)

canvas.save(output)
