from PIL import Image
import glob
import numpy as np
import cv2
from matplotlib import pyplot as plt

def watermark_file(background, logo, x_pos, y_pos, sticker):
    ## sticker True - we have to convert to pillow
    ## sticker False - image is coming as pillow
    if sticker:
        logo = Image.fromarray(logo)
    background = cv2.cvtColor(background, cv2.COLOR_BGRA2RGBA)
    background = Image.fromarray(background, 'RGBA')

    position = (x_pos, y_pos)

    background.paste(logo, position, logo)

    final = np.array(background)
    final = cv2.cvtColor(final, cv2.COLOR_RGBA2BGRA)
    return final

def rotate_90_clockwise(imageCopyF):
    imageCopyF = cv2.rotate(imageCopyF, cv2.ROTATE_90_CLOCKWISE)
    return imageCopyF

def rotate_90_counterclockwise(imageCopyF):
    imageCopyF = cv2.rotate(imageCopyF, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return imageCopyF

def rotate_180(imageCopyF):
    imageCopyF = cv2.rotate(imageCopyF, cv2.ROTATE_180)
    return imageCopyF

def flip_vertical(imageCopyF):
    imageCopyF = cv2.flip(imageCopyF, 0)
    return imageCopyF

def flip_horizontal(imageCopyF):
    imageCopyF = cv2.flip(imageCopyF, 1)
    return imageCopyF

def scale(imageCopyF, scaleXF, scaleYF):
    (h1, w1) = imageCopyF.shape[:2]
    imageCopyF = cv2.resize(imageCopyF, (int(w1*scaleXF[0]), int(h1*scaleYF[0])))
    return imageCopyF

# histogram
def histogram(imageCopyF):
    img_bgr = imageCopyF
    color = ('b', 'g', 'r')

    for i, col in enumerate(color):
        histogram = cv2.calcHist([img_bgr], [i], None, [256], [0, 256])
        plt.plot(histogram, color=col)
        plt.xlim([0, 256])

    plt.xlabel('PIXEL')
    plt.ylabel('AMOUNT')
    plt.title("IMAGE HISTOGRAM")

    plt.show()

def upscale(imageCopyF, upscaleAmount, upscaleType):
    img = Image.fromarray(imageCopyF, 'RGBA')
    w = img.width
    h = img.height
    img_resized = img.resize((w * upscaleAmount, h*upscaleAmount), resample = upscaleType)

    reverted = np.array(img_resized)
    return reverted

def crop(imageCopyF, roi, h, w):
    croppedImage = imageCopyF[int((roi[1])*h):(int((roi[1]+roi[3])*h)), int((roi[0])*w):(int((roi[0]+roi[2])*w))]
    return croppedImage

def frame(imageCopyF, amountF, color):
    h, w = imageCopyF.shape[:2]
    imageFramed = cv2.copyMakeBorder(imageCopyF, amountF, amountF, amountF, amountF, cv2.BORDER_CONSTANT, value=color)
    resized = cv2.resize(imageFramed, (w, h))
    return resized

def combine(images, direction, order):
    pillowImages = []
    for image in images:
        pillowImages.append(Image.fromarray(image))

    if order == 'reverse':
        images = pillowImages[::-1]
    else:
        images = pillowImages

    widths, heights = zip(*(i.size for i in images))
    if direction == 'vertical':
        max_width = max(widths)
        total_height = sum(heights)
        new_im = Image.new('RGB', (max_width, total_height))

        y_offset = 0
        for im in images:
            new_im.paste(im, (0, y_offset))
            y_offset += im.size[1]
    elif direction == 'horizontal':
        total_width = sum(widths)
        max_height = max(heights)
        new_im = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

    combinedImage = np.array(new_im)
    return combinedImage

def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    resized = cv2.resize(image, dim, interpolation=inter)

    return resized

def combine_resize(images, direction, mode, order):
    combinedImage = []
    if mode == 'smallest' and direction == 'vertical':
        shape = sorted([(i.shape[0], i.shape) for i in images])[0][0]

        for image in images:
            combinedImage.append(image_resize(image, width=shape))
        if order == 'reverse':
            combinedImage = np.vstack(reversed(combinedImage))
        else:
            combinedImage = np.vstack(combinedImage)

    elif mode == 'biggest' and direction == 'vertical':
        shape = sorted([(i.shape[0], i.shape) for i in images], reverse=True)[0][0]
        for image in images:
            combinedImage.append(image_resize(image, width=shape))
        if order == 'reverse':
            combinedImage = np.vstack(reversed(combinedImage))
        else:
            combinedImage = np.vstack(combinedImage)

    elif mode == 'smallest' and direction == 'horizontal':
        shape = sorted([(i.shape[1], i.shape) for i in images])[0][0]
        print(shape)
        for image in images:
            combinedImage.append(image_resize(image, height=shape))
        if order == 'reverse':
            combinedImage = np.hstack(reversed(combinedImage))
        else:
            combinedImage = np.hstack(combinedImage)

    elif mode == 'biggest' and direction == 'horizontal':
        shape = sorted([(i.shape[1], i.shape) for i in images], reverse=True)[0][0]
        print(shape)
        for image in images:
            combinedImage.append(image_resize(image, height=shape))
        if order == 'reverse':
            combinedImage = np.hstack(reversed(combinedImage))
        else:
            combinedImage = np.hstack(combinedImage)

    return combinedImage

#image separation

def hsv(image, hue_min_1, sat_min_1, val_min_1, hue_max_1, sat_max_1, val_max_1):
    imgHsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([hue_min_1, sat_min_1, val_min_1])
    upper_red1 = np.array([hue_max_1, sat_max_1, val_max_1])
    mask1 = cv2.inRange(imgHsv, lower_red1, upper_red1)
    imgHsv = cv2.cvtColor(imgHsv, cv2.COLOR_HSV2BGR)
    imgHsv = cv2.cvtColor(imgHsv, cv2.COLOR_BGR2BGRA)
    separatedImage = cv2.bitwise_and(imgHsv, imgHsv, mask=mask1)

    return separatedImage
