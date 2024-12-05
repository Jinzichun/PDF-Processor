import numpy as np
from PIL import Image, ImageEnhance

def invert_colors_rgb(img):
    arr = np.array(img)
    inverted_arr = 255 - arr
    return Image.fromarray(inverted_arr, 'RGB')

def convert_to_grayscale(img):
    return img.convert('L')

def enhance_contrast(img, contrast_factor=2.0):
    gray_img = img.convert('L')
    enhancer = ImageEnhance.Contrast(gray_img)
    return enhancer.enhance(contrast_factor)

def crop_white_borders(img, margin=3):
    img_array = np.array(img)
    if img_array.shape[2] == 4:  # If alpha channel exists
        img_array = img_array[:, :, :3]
    gray = np.mean(img_array, axis=2)
    coords = np.column_stack(np.where(gray < 250))
    if coords.size == 0:
        return img
    top_left = coords.min(axis=0) - margin
    bottom_right = coords.max(axis=0) + margin
    top_left = np.maximum(0, top_left)
    bottom_right = np.minimum([img_array.shape[0], img_array.shape[1]], bottom_right)
    return img.crop((top_left[1], top_left[0], bottom_right[1], bottom_right[0]))

def clean_gray_dots(img, tolerance=5, min_brightness=50, max_brightness=200):
    arr = np.array(img)
    R, G, B = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)
    diff_rg, diff_rb, diff_gb = np.abs(R - G), np.abs(R - B), np.abs(G - B)
    gray_mask = (diff_rg <= tolerance) & (diff_rb <= tolerance) & (diff_gb <= tolerance)
    brightness = (R + G + B) / 3
    brightness_mask = (brightness >= min_brightness) & (brightness <= max_brightness)
    gray_pixels = gray_mask & brightness_mask
    arr[gray_pixels] = [255, 255, 255]
    return Image.fromarray(arr.astype('uint8'), 'RGB')