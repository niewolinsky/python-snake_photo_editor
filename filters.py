import cv2
import numpy as np
from blend_modes import *
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw


def blur(imageCopyF, blurStrengthF):
    imageCopyF = cv2.blur(imageCopyF, (blurStrengthF, blurStrengthF))
    return imageCopyF

def sharpen(imageCopyF, sharpenAmountF):

    testImage = Image.fromarray(imageCopyF, 'RGBA')

    enhancer = ImageEnhance.Sharpness(testImage)
    testImage = enhancer.enhance(sharpenAmountF)

    resized = np.array(testImage)
    return resized

def brightness(imageCopyF, brightnessAmountF):
    testImage = Image.fromarray(imageCopyF, 'RGBA')

    enhancer = ImageEnhance.Brightness(testImage)
    testImage = enhancer.enhance(brightnessAmountF)

    resized = np.array(testImage)
    return resized

def contrast(imageCopyF, contrastAmountF):
    testImage = Image.fromarray(imageCopyF, 'RGBA')

    enhancer = ImageEnhance.Contrast(testImage)
    testImage = enhancer.enhance(contrastAmountF)

    resized = np.array(testImage)
    return resized

def color(imageCopyF, colorAmountF):

    testImage = Image.fromarray(imageCopyF, 'RGBA')

    enhancer = ImageEnhance.Color(testImage)
    testImage = enhancer.enhance(colorAmountF)

    resized = np.array(testImage)
    return resized

def temperature(imageCopyF, tempAmountF):
    kelvin_table = {
        3000: (255,180,107), 3500: (255,196,137), 4000: (255,209,163), 4500: (255,219,186), 5000: (255,228,206), 5500: (255,236,224),
        6000: (255,243,239), 6500: (255,249,253), 7000: (245,243,255), 7500: (235,238,255), 8000: (227,233,255), 8500: (220,229,255),
        9000: (214,225,255), 9500: (208,222,255), 10000:(204,219,255), 10500:(198,216,255), 11000:(195,214,255), 11500:(193,213,255),
        12000:(191,211,255), 12500:(189,210,255), 13000:(187,209,255), 13500:(185,208,255), 14000:(184,207,255), 14500:(182,206,255),
        15000:(181,205,255)}
        
    tempAmountF = kelvin_table[tempAmountF]    

    testimage = Image.fromarray(imageCopyF, 'RGBA')
    alfa = testimage.getchannel("A")
    background = Image.new("RGB", testimage.size, (255, 255, 255))
    background.paste(testimage, mask = testimage.split()[3])

    r, g, b = tempAmountF
    matrix = ( b / 255.0, 0.0, 0.0, 0.0,
               0.0, g / 255.0, 0.0, 0.0,
               0.0, 0.0, r / 255.0, 0.0 )
    im = background.convert('RGB', matrix)
    im.putalpha(alfa)
    
    reverted = np.array(im)
    return reverted

def tint(imageCopyF, tintAmountF):
    tint_table = {
        20:(255,180,107), 19:(255,187,120), 18:(255,193,132), 17:(255,199,143), 16:(255,204,153), 15:(255,209,163), 14:(255,213,173),
        13:(255,217,182), 12:(255,221,190), 11:(255,225,198), 10:(255,228,206), 9: (255,232,213), 8: (255,235,220), 7: (255,238,227),
        6:(255,240,233), 5:(255,243,239), 4:(255,245,245), 3:(255,248,251), 2:(255,249,253), 1:(254,249,255), 0:(254,250,255),
        -1:(252,247,255), -2:(249,246,255), -3:(247,245,255), -4:(245,243,255), -5:(235,238,255), -6:(227,233,255), -7:(220,229,255),
        -8:(214,225,255), -9:(208,222,255), -10:(204,219,255), -11:(198,216,255), -12:(195,214,255), -13:(193,213,255), -14:(191,211,255),
        -15:(189, 210, 255), -16:(187, 209, 255), -17:(185, 208, 255), -18:(184, 207, 255), -19:(182, 206, 255), -20:(181, 205, 255)}
        
    tintAmountF = tint_table[tintAmountF]
    
    testimage = Image.fromarray(imageCopyF, 'RGBA')
    alfa = testimage.getchannel("A")
    background = Image.new("RGB", testimage.size, (255, 255, 255))
    background.paste(testimage, mask = testimage.split()[3])

    r, g, b = tintAmountF
    matrix = ( b / 255.0, 0.0, 0.0, 0.0,
            0.0, r / 255.0, 0.0, 0.0,
            0.0, 0.0, g / 255.0, 0.0 )
    im = background.convert('RGB', matrix)
    im.putalpha(alfa)

    reverted = np.array(im)
    return reverted

def colorbalance(imageCopyF, CYAN_RED , MAGENTA_GREEN, BLUE_YELLOW):
    
    b,g,r,a = cv2.split(imageCopyF)
    imageCopyFNoAlpha = cv2.merge((b,g,r))

    LAB_IMAGE = cv2.cvtColor(imageCopyFNoAlpha, cv2.COLOR_BGR2LAB)
    CYAN_RED *= 5
    MAGENTA_GREEN *= 5
    BLUE_YELLOW *= 5
    if CYAN_RED > 0:
        #np.add(LAB_IMAGE[...,0], int(CYAN_RED/16), out=LAB_IMAGE[...,0], casting="unsafe")
        np.add(LAB_IMAGE[...,1], int(CYAN_RED/5), out=LAB_IMAGE[...,1], casting="unsafe")
        np.add(LAB_IMAGE[...,2], int(CYAN_RED/7), out=LAB_IMAGE[...,2], casting="unsafe")
    if CYAN_RED < 0:
        #np.add(LAB_IMAGE[...,0], int(-1 * (CYAN_RED/16)), out=LAB_IMAGE[...,0], casting="unsafe")
        np.add(LAB_IMAGE[...,1], int(CYAN_RED/10), out=LAB_IMAGE[...,1], casting="unsafe")
        np.add(LAB_IMAGE[...,2], int(CYAN_RED/40), out=LAB_IMAGE[...,2], casting="unsafe")
    
    if BLUE_YELLOW > 0:
        #np.add(LAB_IMAGE[...,0], int(BLUE_YELLOW/16), out=LAB_IMAGE[...,0], casting="unsafe")
        np.add(LAB_IMAGE[...,1], int(-1 * (BLUE_YELLOW/35)), out=LAB_IMAGE[...,1], casting="unsafe")
        np.add(LAB_IMAGE[...,2], int(BLUE_YELLOW/4), out=LAB_IMAGE[...,2], casting="unsafe")
    if BLUE_YELLOW < 0:
        #np.add(LAB_IMAGE[...,0], int(-1 * (BLUE_YELLOW/16)), out=LAB_IMAGE[...,0], casting="unsafe")
        np.add(LAB_IMAGE[...,1], int(-1 * (BLUE_YELLOW/5)), out=LAB_IMAGE[...,1], casting="unsafe")
        np.add(LAB_IMAGE[...,2], int(BLUE_YELLOW/4), out=LAB_IMAGE[...,2], casting="unsafe")

    if MAGENTA_GREEN > 0: 
        #np.add(LAB_IMAGE[...,0], int(MAGENTA_GREEN/16), out=LAB_IMAGE[...,0], casting="unsafe")
        np.add(LAB_IMAGE[...,1], int(-1 * (MAGENTA_GREEN/8)), out=LAB_IMAGE[...,1], casting="unsafe")
        np.add(LAB_IMAGE[...,2], int(MAGENTA_GREEN/8), out=LAB_IMAGE[...,2], casting="unsafe")
    if MAGENTA_GREEN < 0: 
        #np.add(LAB_IMAGE[...,0], int(-1 * MAGENTA_GREEN/16), out=LAB_IMAGE[...,0], casting="unsafe")
        np.add(LAB_IMAGE[...,1], int(-1 * MAGENTA_GREEN/4), out=LAB_IMAGE[...,1], casting="unsafe")
        np.add(LAB_IMAGE[...,2], int(MAGENTA_GREEN/6), out=LAB_IMAGE[...,2], casting="unsafe")


    resized = cv2.cvtColor(LAB_IMAGE, cv2.COLOR_Lab2BGR)
    b2,g2,r2 = cv2.split(resized)
    finalimage = cv2.merge((b2,g2,r2,a))

    return finalimage

def erosion(imageCopyF, erosionAmountF):
    kernel = np.array([[0, 1, 0],
                        [1, 1, 1],
                        [0, 1, 0]], np.uint8)

    erosion = cv2.erode(imageCopyF, kernel, iterations = erosionAmountF)

    resized = np.array(erosion)
    return resized

def dilatation(imageCopyF, dilatationAmountF):
    kernel = np.array([[0, 1, 0],
                        [1, 1, 1],
                        [0, 1, 0]], np.uint8)

    dilatation = cv2.dilate(imageCopyF, kernel, iterations = dilatationAmountF)

    resized = np.array(dilatation)
    return resized

def denoise(imageCopyF, luminanceAmountF, colorAmountF, smoothAmountF):
    denoise = cv2.fastNlMeansDenoisingColored(imageCopyF, None, luminanceAmountF, colorAmountF, smoothAmountF, 15) 

    return denoise

def lum(imageCopyF, denoiseAmountF):

    denoise = cv2.fastNlMeansDenoising(imageCopyF, None, denoiseAmountF, 7, 7) 
    return denoise

def grayscale(imageCopyF):
    grayImage = cv2.cvtColor(imageCopyF, cv2.COLOR_BGRA2GRAY)

    ## RANDOM CODE TO EXPAND 2 CHANNELED IMAGE TO 3 CHANNELS ?? ##
    stacked_img = np.stack((grayImage,)*4, axis=-1)

    return stacked_img

def sepia(imageCopyF):
    filt = cv2.transform(imageCopyF, np.matrix([[ 0.272, 0.534, 0.131, 0.000], [ 0.349, 0.686, 0.168, 0.000], [ 0.393, 0.769, 0.189, 0.000], [1, 1, 1, 1]]))

    # Check wich entries have a value greather than 255 and set it to 255
    filt[np.where(filt>255)] = 255

    # Create an image from the array
    return np.array(filt, np.uint8)

def negative(imageCopyF):
    
    testimage = Image.fromarray(imageCopyF, 'RGBA')
    alfa = testimage.getchannel("A")
    background = Image.new("RGB", testimage.size, (255, 255, 255))
    background.paste(testimage, mask = testimage.split()[3])

    im = ImageOps.invert(background)
    im.putalpha(alfa)

    return np.array(im)

def emboss(imageCopyF):
    testimage = Image.fromarray(imageCopyF, 'RGBA')
    alfa = testimage.getchannel("A")
    background = Image.new("RGB", testimage.size, (255, 255, 255))
    background.paste(testimage, mask = testimage.split()[3])

    im = background.filter(ImageFilter.EMBOSS)
    im.putalpha(alfa)

    return np.array(im)

def diff(imageCopyF):
    b,g,r,a = cv2.split(imageCopyF)
    imageCopyFNoAlpha = cv2.merge((b,g,r))

    kernel = np.array([[0, -1, -1],
                        [1, 0, -1],
                        [1, 1, 0]])
    imgEmboss = cv2.filter2D(imageCopyFNoAlpha, -1, kernel)

    b2,g2,r2 = cv2.split(imgEmboss)
    finalimage = cv2.merge((b2,g2,r2,a))

    return finalimage

def blackandwhite(imageCopyF):
    grayImage = cv2.cvtColor(imageCopyF, cv2.COLOR_BGRA2GRAY)
  
    (thresh, blackAndWhiteImage) = cv2.threshold(grayImage, 127, 255, cv2.THRESH_BINARY)
    ## RANDOM CODE TO EXPAND 2 CHANNELED IMAGE TO 3 CHANNELS ?? ##
    stacked_img = np.stack((blackAndWhiteImage,)*4, axis=-1)

    return stacked_img

def interpolate(f_co, t_co, interval):
    det_co =[(t - f) / interval for f , t in zip(f_co, t_co)]
    for i in range(interval):
        yield [round(f + det * i) for f, det in zip(f_co, det_co)]

def blend(imageCopyF, opacityAmountF, overlayFrameF, blendTypeF, color1=None, color2=None, gradientMode=False):
    if gradientMode == False:
        overlayFrameF = cv2.resize(overlayFrameF, (imageCopyF.shape[1], imageCopyF.shape[0]), interpolation = cv2.INTER_AREA)
        frma = overlayFrameF
        frma_float = frma.astype(float)

    else:
        dim = list(imageCopyF.shape)
        dim = tuple(reversed(dim[:-1]))
        gradient = Image.new('RGBA', dim, color=0)
        draw = ImageDraw.Draw(gradient)
        f_co = color1
        t_co = color2
        for i, color in enumerate(interpolate(f_co, t_co, dim[0] * 2)):
            draw.line([(i, 0), (0, i)], tuple(color), width=1)
        frma = np.array(gradient)
        frma_float = frma.astype(float)

    bgra = imageCopyF
    bgra_float = bgra.astype(float)

    if blendTypeF == 1:
        blended_img_float = normal(bgra_float, frma_float, opacityAmountF)
    elif blendTypeF == 2:
        blended_img_float = multiply(bgra_float, frma_float, opacityAmountF)
    elif blendTypeF == 3:
        blended_img_float = darken_only(bgra_float, frma_float, opacityAmountF)
    elif blendTypeF == 4:
        blended_img_float = lighten_only(bgra_float, frma_float, opacityAmountF)
    elif blendTypeF == 5:
        blended_img_float = dodge(bgra_float, frma_float, opacityAmountF)
    elif blendTypeF == 6:
        blended_img_float = overlay(bgra_float, frma_float, opacityAmountF)
    elif blendTypeF == 7:
        blended_img_float = soft_light(bgra_float, frma_float, opacityAmountF)
    elif blendTypeF == 8:
        blended_img_float = hard_light(bgra_float, frma_float, opacityAmountF)
    elif blendTypeF == 9:
        blended_img_float = difference(bgra_float, frma_float, opacityAmountF)

    # Display blended image
    bgra_uint8 = blended_img_float.astype(np.uint8)  # Convert image to OpenCV native display format

    return bgra_uint8

def histogram_normalization(imageCopyF):

    testimage = Image.fromarray(imageCopyF, 'RGBA')
    alfa = testimage.getchannel("A")
    background = Image.new("RGB", testimage.size, (255, 255, 255))
    background.paste(testimage, mask = testimage.split()[3])

    im = ImageOps.equalize(background)
    im.putalpha(alfa)


    return np.array(im)

def histogram_autocontrast(imageCopyF, contrast):

    testimage = Image.fromarray(imageCopyF, 'RGBA')
    alfa = testimage.getchannel("A")
    background = Image.new("RGB", testimage.size, (255, 255, 255))
    background.paste(testimage, mask = testimage.split()[3])

    im = ImageOps.autocontrast(background, 3, None, None, contrast)
    im.putalpha(alfa)

    return np.array(im)

# def histogram_canvas(imageCopyF):
#     imageCopyF = cv2.cvtColor(imageCopyF, cv2.COLOR_BGRA2RGB)
#     bins = np.arange(256).reshape(256,1)
#     im = imageCopyF
#     h = np.zeros((300,256,3))
#     h[:] = (50,50,50)
#     color = [ (255,0,0),(0,255,0),(0,0,255) ]
#     for ch, col in enumerate(color):

#         hist_item = cv2.calcHist([im],[ch],None,[256],[0,256])
#         cv2.normalize(hist_item,hist_item,0,255,cv2.NORM_MINMAX)
#         hist=np.int32(np.around(hist_item))
#         pts = np.int32(np.column_stack((bins,hist)))
#         cv2.polylines(h,[pts],False,col)

#     y=np.flipud(h)
#     return y

def pix(imageCopyF, amountF):
    (h1, w1) = imageCopyF.shape[:2]
    sizeF = 0
    if(amountF == 5):
        sizeF = 0.03
    if(amountF == 4):
        sizeF = 0.04
    if(amountF == 3):
        sizeF = 0.05
    if(amountF == 2):
        sizeF = 0.06
    if(amountF == 1):
        sizeF = 0.07
    imageCopyF = cv2.resize(imageCopyF, (int(w1*sizeF), int(h1*sizeF)))
    imageCopyF = cv2.resize(imageCopyF, (w1, h1))
    return imageCopyF

def Reverse(tuples):
    new_tup = ()
    for k in reversed(tuples):
        new_tup = new_tup + (k,)
    return new_tup

def putText(frame, img, text, xy, font, scale, color, thick, line):
    #print(xy, font, scale, color, thick, line)
    cv2.putText(frame, text, xy, font, scale, color, thick, line, False)

    logo = Image.fromarray(frame)

    background = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    background = Image.fromarray(background, 'RGBA')

    position = xy

    background.paste(logo, position, logo)

    final = np.array(background)
    final = cv2.cvtColor(final, cv2.COLOR_RGBA2BGRA)
    return final
