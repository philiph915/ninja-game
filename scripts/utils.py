import pygame
import os

BASE_IMG_PATH = 'data/images/'

# load a specific image as a surface
def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0,0,0))
    return img

# loads all the images in a folder (returns a list of surfaces)
def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)): # os.listdir will return a list of all files in a directory
        images.append(load_image(path + '/' + img_name))
    return images