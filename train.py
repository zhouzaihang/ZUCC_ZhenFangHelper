from PIL import Image
import matplotlib.pyplot as plt
import os

IMAGE_HEIGHT = 27
IMAGE_WIDTH = 72
MAX_CAPTCHA = 4

imgDir = os.getcwd() + "/"
image = Image.open(imgDir + "code.gif")


def inittable(color=153):
    table = []
    for i in range(256):
        if i == color:
            table.append(0)
        else:
            table.append(1)
    return table


def preimage(image):
    im = image.convert('L').point(inittable(), '1')
    im.show()
    plt.figure("CODE")
    plt.imshow(im)
    plt.show()


preimage(image)
