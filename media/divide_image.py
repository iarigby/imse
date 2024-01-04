from PIL import Image
from itertools import product
import os
img = Image.open("59866.jpg")

w, h = img.size

name = "image"
dir_out = "images"
d = int(w/5)
grid = product(range(0, h - h % d, d), range(0, w - w % d, d))
for i, j in grid:
    box = (j, i, j + d, i + d)
    out = os.path.join(dir_out, f'{name}_{i}_{j}.png')
    img.crop(box).save(out)

