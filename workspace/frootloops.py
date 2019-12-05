## Justin Wong, 12-5-19
##
## Floopify
##
## Editing an image for average colors and matching to given colors,
##  in order to make a mosaic of a froot loops image
##  using froot loops colors.

from PIL import Image, ImageDraw
import math

## from someone else's color palette. they're really bright...
##red = (255, 0, 0)
##orange = (248, 149, 33)
##yellow = (255, 231, 0)
##green = (124, 255, 0)
##purple = (201, 0, 255)
##blue = (0, 223, 255)

black = (0, 0, 0)
white = (255, 255, 255)

## sampled from actual image, color picker tool
red = (225, 96, 98)
orange = (225, 116, 55)
yellow = (240, 204, 94)
green = (127, 179, 99)
purple = (146, 123, 139)
blue = (105, 175, 181)

color_options = [red, yellow, green, purple, blue, orange, black, white]
# notes: 1 froot loop ~ 3/5 in, or 86.67 pixels for this image
radius = 87 / 2

original = Image.open('frootloops.jpeg')
w, h = original.size

# average color of a section of an image
def avg_color_of(boundary, image=original):
    section = image.crop(boundary)
    section = section.quantize(1)   # section becomes avg pixel color
    section = section.convert('RGB')# necessary for getpixel to return a tuple 
    return section.getpixel((1, 1)) # arbitrary pixel in this region

# find froot loop color closest to given color
def closest_color(this_color):
    distances = [color_distance(this_color, loop_color)
                 for loop_color in color_options]
    min_dist = min(distances)
    min_index = distances.index(min_dist)
    return color_options[min_index]

def color_distance(c1, c2, is_weighted=False):
    # popularly weighted distances for human eye perception
    green_heavy = {'r':0.30, 'g':0.59, 'b':0.11}
    even = {'r':0.33, 'g':0.33, 'b':0.33}
    
    weights = {}
    if is_weighted:
        weights = green_heavy
    else:
        weights = even
        
    d = (((c1[0] - c2[0]) * weights['r']) ** 2 +
         ((c1[1] - c2[1]) * weights['g']) ** 2 +
         ((c1[2] - c2[2]) * weights['b']) ** 2)
    return math.sqrt(d)

# image of empty circles packed by hexagon pattern
def empty_circles_img():
    
    centers = circle_centers()
    blank = Image.new('RGB', (w, h), white)
    draw = ImageDraw.Draw(blank)
    draw_empty_circles_on(draw, centers)
    blank.save('circles.png')

# draw circles on ImageDraw object given centers
def draw_empty_circles_on(draw, centers):
    for row in centers:
        for center in row:
            boundary = boundary_around(center)
            empty_circle(draw, boundary)

# draw black circle outline on ImageDraw object given boundary    
def empty_circle(draw, boundary):
    draw.arc(boundary, 0, 360, black)

# start top left justified, hexagon packing full circles
def circle_centers():
    centers = []

    num_cols = math.floor( w / (radius * 2) )
    row_inc = radius * math.sqrt(3)
    col_inc = 2 * radius
    row_start = radius
    col_start = 0
    num_circles = 0
    r = 0
    while (row_start + r + r * radius * math.sqrt(3)) < h:
        if r % 2 == 0:  # even row, left justified
            col_start = radius
            num_circles = num_cols
        else:   # odd row, inset and one shorter
            col_start = 2 * radius
            num_circles = num_cols - 1
        row = [(col_start + c * col_inc, row_start + r * row_inc)
               for c in range(num_circles)]
        centers.append(row)
        r += 1
    return centers

# square box region around center point; returns tuple
def boundary_around(center):
    boundary = (center[0] - radius,
                center[1] - radius,
                center[0] + radius,
                center[1] + radius)
    return boundary

# checks a pixel's alpha channel for 255 (png silhouettes will have it)           
def is_black(color):
    return color[3] == 255

###########################################
#                                         #
#    FINAL IMAGE CONVERSION FUNCTIONS     #
#                                         #
###########################################

# convert whole image into averages of squared regions
def quantize(size=87):
    quantized = Image.new('RGB', (w, h), white)

    box_w = size
    box_h = size
    cols = int(w / box_w)
    rows = int(h / box_h)

    for r in range(rows):
        for c in range(cols):
            boundary = (c * box_w,
                        r * box_h,
                        (c + 1) * box_w,
                        (r + 1) * box_h)   # L, U, R, D
            color_of_section = avg_color_of(boundary)
            quantized.paste(closest_color(color_of_section), boundary)
                # fills boundary with given color

    quantized.save('quantized' + str(size) + '.png')
    print('quantize finished')

# convert whole image by every pixel. Takes a while.
def pixelify(filename='pixelify'):
    modified = Image.new('RGB', (w, h), white)
    for c in range(w):
        for r in range(h):
            p = original.getpixel((c, r))
            modified.putpixel((c, r), closest_color(p))
    modified.save(filename + '.png')
    print('pixelify finished')

# convert silhouette sections into average of circle (froot loop) regions 
def floopify(silhouette_img, filename='floopify'):
    
    floopified = Image.new('RGB', (w, h), white)
    draw = ImageDraw.Draw(floopified)

    circles = circle_centers()

    for row in circles:
        for point in row:
            boundary = boundary_around(point)
            
            if is_black(silhouette_img.getpixel(point)):
                color_of_section = avg_color_of(boundary)
                draw.ellipse(boundary,
                             #color_of_section,
                             closest_color(color_of_section),
                             black)
            else:
                empty_circle(draw, boundary)
    floopified.save(filename + '.png')
    print('floopify finished')

def main():
    everything = Image.new('RGBA', (w, h), (0, 0, 0, 255)) #all black silhouette
    toucan_and_bowl = Image.open('bowlandtoucanblack.png')
    toucan = Image.open('toucanblack.png')
    bowl = Image.open('bowlblack.png')
    # ^ silhouette options 

    floopify(toucan_and_bowl)

    quantize(20)

    pixelify()
            
main()
