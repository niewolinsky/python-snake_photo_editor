###### SNAKE PHOTO EDITOR - MASTER BRANCH - VER. 1.0 ######
### EXTERNAL IMPORTS ###
import cv2                                                          # LIBRARY FOR OPENCV, MOST OF IMAGE MANIPULATIONS
import cvui                                                         # LIBRARY FOR UI, BASED ON OPENCV
import numpy as np                                                  # LIBRARY FOR LIST AND ARRAY MODIFICATIONS
import os                                                           # LIBRARY NEEDED FOR WINDOWS INTEGRATION
import imghdr                                                       # LIBRARY USED TO IDENTIFY FILES TYPE
import time                                                         # LIBRARY FOR TIME CONVERSIONS
from PIL import Image                                               # LIBRARY FOR GENERAL USE ON IMAGES
from tkinter import messagebox, sys, Tk, colorchooser, filedialog, simpledialog   # LIBRARY FOR UI, MODAL WINDOWS
import imutils
### LOCAL IMPORTS ###
import filters as filters                                           # FILTERS STORED IN SEPARATE FILE
import tools as tools                                               # TOOLS STORED IN SEPARATE FILE

## GENERAL USE FUNCTIONS ###
def message_window(window_text, message_text, flag):
    Tk().withdraw()

    if flag == 'info':
        messagebox.showinfo(window_text, message_text)
    elif flag == 'error':
        messagebox.showerror(window_text, message_text)
    elif flag == 'warning':
        messagebox.showwarning(window_text, message_text)
    else:
        return

def ask_window(window_text, message_text, flag):
    Tk().withdraw()

    if flag == 'okcancel':
        answer = messagebox.askokcancel(window_text, message_text)
        return answer
    else:
        return

def image_reset():
    global isImageLoaded, imagesVersion, imagesCurrent, isLightModeActive
    imagesPath.clear()
    loadedImages.clear()
    loadedImagesThumbnails.clear()
    if isLightModeActive == False:
        loadedImages.append(cv2.imread('Graphics/start-screen.png', cv2.IMREAD_UNCHANGED))
    else:
        loadedImages.append(cv2.imread('Graphics/start-screen-light.png', cv2.IMREAD_UNCHANGED))
    changesList.clear()
    changesList.append(loadedImages)
    imagesVersion = len(changesList) - 1
    imagesCurrent = 0

    isImageLoaded = False

def open_image():
    if isImageLoaded:
        os.startfile(imagesPath[imagesCurrent])
    else:
        message_window('FAILED TO OPEN IMAGE', 'You need to load your image first!', 'error')

def load_image():
    global isImageLoaded, imagesVersion, imagesCurrent
    # CHOOSING IMAGE WITH PREFIX OF EXTENSIONS
    Tk().withdraw()
    if isBatchModeActive == True:
        filepath = filedialog.askopenfilenames(title="Load images...", filetypes=[('Image Files', ['.jpeg', '.jpg', '.png', '.tiff', '.tif', '.bmp'])])
    else:
        filepath = filedialog.askopenfilename(title="Load image...", filetypes=[('Image Files', ['.jpeg', '.jpg', '.png', '.tiff', '.tif', '.bmp'])])
    # HANDLING EXCEPTIONS
    if filepath != '':
        imagesPath.clear()
        loadedImages.clear()
        loadedImagesThumbnails.clear()
        if isBatchModeActive == True:
            for path in filepath:
                imagesPath.append(path)
                loadedImages.append(cv2.cvtColor(cv2.imread(path, cv2.IMREAD_UNCHANGED), cv2.COLOR_BGR2BGRA))
            for image in loadedImages:
                x = Image.fromarray(image, 'RGBA')
                x.thumbnail((199, 199))
                xConverted = np.array(x)
                loadedImagesThumbnails.append(xConverted)
        else:
            imagesPath.append(filepath)
            tempImage = cv2.imread(filepath, -1)
            tempImage = cv2.cvtColor(tempImage, cv2.COLOR_BGR2BGRA)
            loadedImages.append(tempImage)
        changesList.clear()
        changesList.append(loadedImages)
        imagesVersion = len(changesList) - 1
        imagesCurrent = 0
        isImageLoaded = True

    else:
        pass

def centering_image(image, frameX, frameY, startX, startY):
    (height, width) = image.shape[:2]
    x = 0
    y = 0
    if width < frameX:
        x = int(((frameX - width)/2) + startX)
    elif width == frameX:
        x = startX
    if height < frameY:
        y = int(((frameY - height)/2) + startY)
    elif height == frameY:
        y = startY
    return (x, y)

def image_resize(image, width=1100, height=713):
    global h, w
    (h, w) = image.shape[:2]

    imageToResize = Image.fromarray(image, 'RGBA')
    imageToResize.thumbnail((width, height))
    resizedImage = np.array(imageToResize)
    return resizedImage

def add_to_changes(build, string=''):
    global imagesVersion, changesList, MACRO_LIST
    # IF THE CHANGE WAS MADE ON THE LAST VERSION OF IMAGE, JUST ADD A NEW CHANGE TO LIST
    # OTHERWISE INSERT A CHANGE IN BETWEEN OTHER CHANGES, AND DELETE FOLLOWING CHANGES
    if imagesVersion == len(changesList) - 1:
        changesList.append(build)
        imagesVersion = len(changesList) - 1
    else:
        count = len(changesList) - 1 - imagesVersion
        while (count):
            changesList.pop(-1)
            count -= 1
        imagesVersion = len(changesList) - 1
        changesList.append(build)
        imagesVersion = len(changesList) - 1

    if MACRO_RECORD == True:
        MACRO_LIST.append(string)

def is_window_open(name):
    return cv2.getWindowProperty(name, cv2.WND_PROP_AUTOSIZE) != -1

def open_window(name):
    cvui.init(name)

def close_window(name):
    cv2.destroyWindow(name)
    cv2.waitKey(1)

def choose_color():
    # variable to store hexadecimal code of color
    try:
        color_code = colorchooser.askcolor(title="Choose color")
        color_code_p = color_code[1]
        color_code_p = color_code_p[1:]
        color_code_literal = '0x' + color_code_p.upper()
        color_code_integer = int(color_code_literal, 16)
        lista = list(color_code)
        lista[1] = color_code_integer
        lista[0] = tuple(reversed(lista[0]))
        tup = tuple(lista)
        return tup
    except TypeError:
        message_window("NO COLOR CHOOSED", "You did not choose a color.", 'info')
        tup = ((255, 255, 255), 16777215)
        return tup

def execute_macro(filename=''):
    file1 = open(f'Macros/{filename}', 'r')
    lines = file1.readlines()

    for line in lines:
        build = []
        for image in changesList[imagesVersion]:
            img = eval(line.strip())
            build.append(img)
        add_to_changes(build)

def save_macro():
    number_of_files = 0

    for top, dirs, files in os.walk('Macros/'):
        for file in files:
            number_of_files += 1

    for function in MACRO_LIST:
        print(function,  file=open(f'Macros/macro{number_of_files+1}.txt', 'a'))

    return os.listdir('Macros/')

def rgb2hex(r,g,b):
    x = "{:02x}{:02x}{:02x}".format(r,g,b)
    color_code_literal = '0x' + x.upper()
    color_code_integer = int(color_code_literal, 16)
    return color_code_integer

### INTERFACE GENERATION FUNCTIONS ###
def generate_interface():
    global imagesVersion, IAREA_CHANGE_STATE, IAREA_ORIGINAL_STATE, isBatchModeActive, isLightModeActive, MACRO_RECORD
    if isLightModeActive == False:
        if cvui.button(FRAME_MAIN, 5, 5, cv2.imread('Graphics/revert1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/revert2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/revert3.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                imagesVersion = 0

        if cvui.button(FRAME_MAIN, 55, 5, cv2.imread('Graphics/undo1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/undo2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/undo3.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                if imagesVersion > 0:
                    imagesVersion -= 1

        if cvui.button(FRAME_MAIN, 105, 5, cv2.imread('Graphics/redo1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/redo2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/redo3.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                if imagesVersion != len(changesList) - 1:
                    imagesVersion += 1

        if cvui.button(FRAME_MAIN, 155, 5, cv2.imread('Graphics/apply1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/apply2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/apply3.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                imagesVersion = len(changesList) - 1

        IAREA_CHANGE_STATE = cvui.iarea(205, 5, 40, 40)
        cvui.button(FRAME_MAIN, 205, 5, cv2.imread('Graphics/chang1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/chang2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/chang3.png', cv2.IMREAD_UNCHANGED))

        IAREA_ORIGINAL_STATE = cvui.iarea(255, 5, 40, 40)
        cvui.button(FRAME_MAIN, 255, 5, cv2.imread('Graphics/orig1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/orig2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/orig3.png', cv2.IMREAD_UNCHANGED))

        if MACRO_RECORD == False:
            if cvui.button(FRAME_MAIN, 345, 7, cv2.imread('Graphics/macrooff1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macrooff2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macrooff3.png', cv2.IMREAD_UNCHANGED)):
                if isImageLoaded == False:
                    message_window("Load Image!", "Load your image first.", 'error')
                else:
                    open_window(WINDOW_SETTINGS_MACRO)
        else:
            if cvui.button(FRAME_MAIN, 345, 7, cv2.imread('Graphics/macroon1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macroon2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macroon3.png', cv2.IMREAD_UNCHANGED)):
                if isImageLoaded == False:
                    message_window("Load Image!", "Load your image first.", 'error')
                else:
                    open_window(WINDOW_SETTINGS_MACRO)

        if cvui.button(FRAME_MAIN, 305, 10, cv2.imread('Graphics/light1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/light2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/light3.png', cv2.IMREAD_UNCHANGED)):
            isLightModeActive = not(isLightModeActive)

        if cvui.button(FRAME_MAIN, 945, 5, cv2.imread('Graphics/batch1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/batch2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/batch3.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                isBatchModeActive = True
            elif ask_window("Switch to batch edition?", "You are about to switch to batch edition mode, all unsaved progress will be lost.", 'okcancel') == True:
                image_reset()
                isBatchModeActive = True
            else:
                pass

    else:
        if cvui.button(FRAME_MAIN, 5, 5, cv2.imread('Graphics/revert1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/revert2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/revert3_light.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                imagesVersion = 0

        if cvui.button(FRAME_MAIN, 55, 5, cv2.imread('Graphics/undo1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/undo2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/undo3_light.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                if imagesVersion > 0:
                    imagesVersion -= 1

        if cvui.button(FRAME_MAIN, 105, 5, cv2.imread('Graphics/redo1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/redo2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/redo3_light.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                if imagesVersion != len(changesList) - 1:
                    imagesVersion += 1

        if cvui.button(FRAME_MAIN, 155, 5, cv2.imread('Graphics/apply1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/apply2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/apply3_light.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                imagesVersion = len(changesList) - 1

        IAREA_CHANGE_STATE = cvui.iarea(205, 5, 40, 40)
        cvui.button(FRAME_MAIN, 205, 5, cv2.imread('Graphics/chang1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/chang2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/chang3_light.png', cv2.IMREAD_UNCHANGED))

        IAREA_ORIGINAL_STATE = cvui.iarea(255, 5, 40, 40)
        cvui.button(FRAME_MAIN, 255, 5, cv2.imread('Graphics/orig1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/orig2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/orig3_light.png', cv2.IMREAD_UNCHANGED))

        if MACRO_RECORD == False:
            if cvui.button(FRAME_MAIN, 345, 7, cv2.imread('Graphics/macrooff1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macrooff2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macrooff3_light.png', cv2.IMREAD_UNCHANGED)):
                if isImageLoaded == False:
                    message_window("Load Image!", "Load your image first.", 'error')
                else:
                    open_window(WINDOW_SETTINGS_MACRO)
        else:
            if cvui.button(FRAME_MAIN, 345, 7, cv2.imread('Graphics/macroon1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macroon2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macroon3_light.png', cv2.IMREAD_UNCHANGED)):
                if isImageLoaded == False:
                    message_window("Load Image!", "Load your image first.", 'error')
                else:
                    open_window(WINDOW_SETTINGS_MACRO)

        if cvui.button(FRAME_MAIN, 305, 10, cv2.imread('Graphics/dark1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/dark2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/dark3.png', cv2.IMREAD_UNCHANGED)):
            isLightModeActive = not(isLightModeActive)

        if cvui.button(FRAME_MAIN, 945, 5, cv2.imread('Graphics/batch1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/batch2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/batch3_light.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                isBatchModeActive = True
            elif ask_window("Switch to batch edition?", "You are about to switch to batch edition mode, all unsaved progress will be lost.", 'okcancel') == True:
                image_reset()
                isBatchModeActive = True
            else:
                pass

    cvui.window(FRAME_MAIN, 1110, 5, 250, 270, 'Corrections & Effects', windowHeader, windowBody, windowText)

    if cvui.button(FRAME_MAIN, 1115, 30, 115, 40, 'Sharpness', buttonDefault, buttonOut, buttonOver, windowText):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                open_window(WINDOW_SETTINGS_SHARPNESS)

    if cvui.button(FRAME_MAIN, 1240, 30, 115, 40, 'Brightness', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_SETTINGS_BRIGHTNESS)

    if cvui.button(FRAME_MAIN, 1240, 80, 115, 40, 'Common', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_SETTINGS_COMMON)

    if cvui.button(FRAME_MAIN, 1115, 80, 115, 40, 'Color', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_SETTINGS_COLOR)

    if cvui.button(FRAME_MAIN, 1240, 130, 115, 40, 'Morphology', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_SETTINGS_MORPH)

    if cvui.button(FRAME_MAIN, 1115, 130, 115, 40, 'Denoise', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            global FILTER_DENOISE_COLOR_AMOUNT_LAST, FILTER_DENOISE_LUMINANCE_AMOUNT_LAST, FILTER_DENOISE_SMOOTH_AMOUNT_LAST, FILTER_USE_DENOISE
            FILTER_USE_DENOISE = [True]
            FILTER_DENOISE_COLOR_AMOUNT_LAST = sys.maxsize
            FILTER_DENOISE_LUMINANCE_AMOUNT_LAST = sys.maxsize
            FILTER_DENOISE_SMOOTH_AMOUNT_LAST = sys.maxsize
            open_window(WINDOW_SETTINGS_DENOISE)

    if cvui.button(FRAME_MAIN, 1240, 180, 115, 40, 'Colorfill', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            global FILTER_COLORFILL_AMOUNT_LAST, FILTER_USE_COLORFILL_TYPE_6
            FILTER_AMOUNT_LAST = sys.maxsize
            FILTER_USE_COLORFILL_TYPE_6 = [True]
            open_window(WINDOW_SETTINGS_COLORFILL)
    cvui.rect(FRAME_MAIN, 1330, 185, 15, 30, FILTER_COLORFILL_COLOR[1], FILTER_COLORFILL_COLOR[1])

    if cvui.button(FRAME_MAIN, 1115, 230, 115, 40, 'Transformations', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_TOOLS_TRANSFORMATIONS)

    if cvui.button(FRAME_MAIN, 1115, 180, 115, 40, 'Normalization', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_FILTERS_NORMALIZATION)

    if cvui.button(FRAME_MAIN, 1240, 230, 115, 40, 'Pixelization', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            global FILTER_USE_PIX
            FILTER_USE_PIX = [True]
            open_window(WINDOW_SETTINGS_PIX)

    cvui.window(FRAME_MAIN, 1110, 280, 250, 170, 'Insert', windowHeader, windowBody, windowText)

    if cvui.button(FRAME_MAIN, 1115, 305, 115, 40, 'Overlays', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            global FILTER_USE_OVERLAY_TYPE_6
            FILTER_USE_OVERLAY_TYPE_6 = [True]
            open_window(WINDOW_SETTINGS_OVERLAYS)

    if cvui.button(FRAME_MAIN, 1240, 305, 115, 40, 'Textures', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            global FILTER_USE_TEXTURES
            FILTER_USE_TEXTURES = [True]
            open_window(WINDOW_SETTINGS_TEXTURES)

    if cvui.button(FRAME_MAIN, 1240, 405, 115, 40, 'Text', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_SETTINGS_TEXT)
    cvui.rect(FRAME_MAIN, 1330, 410, 15, 30, TEXT_USE_COLOR[1], TEXT_USE_COLOR[1])

    if cvui.button(FRAME_MAIN, 1115, 405, 115, 40, 'Frame', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            global FILTER_USE_FRAME
            FILTER_USE_FRAME = [True]
            open_window(WINDOW_SETTINGS_FRAME)
    cvui.rect(FRAME_MAIN, 1205, 410, 15, 30, FILTER_FRAME_COLOR[1], FILTER_FRAME_COLOR[1])

    if cvui.button(FRAME_MAIN, 1240, 355, 115, 40, 'Sticker', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_TOOLS_STICKER)

    if cvui.button(FRAME_MAIN, 1115, 355, 115, 40, 'Watermark', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_TOOLS_WATERMARK)

    cvui.window(FRAME_MAIN, 1110, 455, 250, 120, 'Tools', windowHeader, windowBody, windowText)

    if cvui.button(FRAME_MAIN, 1115, 480, 115, 40, 'Histogram', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            tools.histogram(changesList[imagesVersion][imagesCurrent])

    if cvui.button(FRAME_MAIN, 1240, 480, 115, 40, 'Upscale', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_TOOLS_UPSCALE)

    if cvui.button(FRAME_MAIN, 1240, 530, 115, 40, 'HSV Separation', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            global FILTER_USE_HSV
            FILTER_USE_HSV = [True]
            open_window(WINDOW_SETTINGS_HSV)

    cvui.window(FRAME_MAIN, 1110, 580, 250, 140, 'Details', windowHeader, windowBody, windowText)
    if isImageLoaded:
        (h, w) = changesList[imagesVersion][imagesCurrent].shape[:2]
        cvui.text(FRAME_MAIN, 1115, 615, "Dimensions: " + str(w) + " X " + str(h), 0.4, textColor)
        cvui.text(FRAME_MAIN, 1115, 637, "Size: " + str(int(os.path.getsize(imagesPath[0]) / 1024)) + " kB", 0.4, textColor)
        image_type = 'jpeg' if (str(imghdr.what(imagesPath[0])) == 'None') else str(imghdr.what(imagesPath[0]))
        cvui.text(FRAME_MAIN, 1115, 657, "Type: " + image_type, 0.4, textColor)
        cvui.text(FRAME_MAIN, 1115, 679, "Created: " + time.ctime(os.path.getctime(imagesPath[0])), 0.4, textColor)
        cvui.text(FRAME_MAIN, 1115, 700, "Modified: " + time.ctime(os.path.getmtime(imagesPath[0])), 0.4, textColor)

    if isLightModeActive == False:
        if cvui.button(FRAME_MAIN, 1110, 725, cv2.imread('Graphics/open1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/open2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/open3.png', cv2.IMREAD_UNCHANGED)):
            load_image()

        if cvui.button(FRAME_MAIN, 1180, 725, cv2.imread('Graphics/look1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/look2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/look3.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                open_image()

        if cvui.button(FRAME_MAIN, 1250, 725, cv2.imread('Graphics/save1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/save2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/save3.png', cv2.IMREAD_UNCHANGED)):
            # OVERWRITING THE INITIAL IMAGE DIRECTORY WITH THE IMAGE USED IN PROGRAM USING GLOBAL VARIABLES
            if isImageLoaded:
                open_window(WINDOW_SETTINGS_SAVE)
            else:
                message_window('CAN NOT SAVE', 'You need to load your image first!', 'warning')

        if cvui.button(FRAME_MAIN, 1320, 725, cv2.imread('Graphics/about1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/about2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/about3.png', cv2.IMREAD_UNCHANGED)):
            open_window(WINDOW_SETTINGS_ABOUT)
    else:
        if cvui.button(FRAME_MAIN, 1110, 725, cv2.imread('Graphics/open1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/open2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/open3_light.png', cv2.IMREAD_UNCHANGED)):
            load_image()

        if cvui.button(FRAME_MAIN, 1180, 725, cv2.imread('Graphics/look1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/look2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/look3_light.png', cv2.IMREAD_UNCHANGED)):
            open_image()

        if cvui.button(FRAME_MAIN, 1250, 725, cv2.imread('Graphics/save1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/save2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/save3_light.png', cv2.IMREAD_UNCHANGED)):
            # OVERWRITING THE INITIAL IMAGE DIRECTORY WITH THE IMAGE USED IN PROGRAM USING GLOBAL VARIABLES
            if isImageLoaded:
                open_window(WINDOW_SETTINGS_SAVE)
            else:
                message_window('CAN NOT SAVE', 'You need to load your image first!', 'warning')

        if cvui.button(FRAME_MAIN, 1320, 725, cv2.imread('Graphics/about1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/about2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/about3_light.png', cv2.IMREAD_UNCHANGED)):
            open_window(WINDOW_SETTINGS_ABOUT)

def generate_batch_interface():
    global imagesVersion, IAREA_CHANGE_STATE, IAREA_ORIGINAL_STATE, isBatchModeActive, imagesCurrent, isListViewModeActive, viewHeight, yStart, isLightModeActive
    if isLightModeActive == False:
        if cvui.button(FRAME_MAIN, 5, 5, cv2.imread('Graphics/revert1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/revert2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/revert3.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                imagesVersion = 0

        if cvui.button(FRAME_MAIN, 55, 5, cv2.imread('Graphics/undo1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/undo2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/undo3.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                if imagesVersion > 0:
                    imagesVersion -= 1

        if cvui.button(FRAME_MAIN, 105, 5, cv2.imread('Graphics/redo1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/redo2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/redo3.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                if imagesVersion != len(changesList) - 1:
                    imagesVersion += 1

        if cvui.button(FRAME_MAIN, 155, 5, cv2.imread('Graphics/apply1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/apply2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/apply3.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                imagesVersion = len(changesList) - 1

        IAREA_CHANGE_STATE = cvui.iarea(205, 5, 40, 40)
        cvui.button(FRAME_MAIN, 205, 5, cv2.imread('Graphics/chang1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/chang2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/chang3.png', cv2.IMREAD_UNCHANGED))

        IAREA_ORIGINAL_STATE = cvui.iarea(255, 5, 40, 40)
        cvui.button(FRAME_MAIN, 255, 5, cv2.imread('Graphics/orig1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/orig2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/orig3.png', cv2.IMREAD_UNCHANGED))

        if MACRO_RECORD == False:
            if cvui.button(FRAME_MAIN, 345, 7, cv2.imread('Graphics/macrooff1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macrooff2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macrooff3.png', cv2.IMREAD_UNCHANGED)):
                if isImageLoaded == False:
                    message_window("Load Image!", "Load your image first.", 'error')
                else:
                    open_window(WINDOW_SETTINGS_MACRO)
        else:
            if cvui.button(FRAME_MAIN, 345, 7, cv2.imread('Graphics/macroon1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macroon2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macroon3.png', cv2.IMREAD_UNCHANGED)):
                if isImageLoaded == False:
                    message_window("Load Image!", "Load your image first.", 'error')
                else:
                    open_window(WINDOW_SETTINGS_MACRO)

        if cvui.button(FRAME_MAIN, 305, 10, cv2.imread('Graphics/light1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/light2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/light3.png', cv2.IMREAD_UNCHANGED)):
            isLightModeActive = not(isLightModeActive)

        if cvui.button(FRAME_MAIN, 440, 10, cv2.imread('Graphics/right1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/right2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/right3.png', cv2.IMREAD_UNCHANGED)):
            if (imagesCurrent - 1 >= 0):
                imagesCurrent -= 1

        cvui.rect(FRAME_MAIN, 510, 10, 80, 30, 0x515A5A)

        cvui.text(FRAME_MAIN, 540, 20, f'{imagesCurrent+1}/{len(loadedImages)}', 0.4, textColor)

        if cvui.button(FRAME_MAIN, 600, 10, cv2.imread('Graphics/left1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/left2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/left3.png', cv2.IMREAD_UNCHANGED)):
            if (imagesCurrent + 1 < len(loadedImages)):
                imagesCurrent += 1

        if cvui.button(FRAME_MAIN, 820, 5, cv2.imread('Graphics/list1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/list2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/list3.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == True:
                isListViewModeActive = not(isListViewModeActive)
            else:
                message_window("NO IMAGES LOADED", "You need to load your images first.", 'info')

        if cvui.button(FRAME_MAIN, 945, 5, cv2.imread('Graphics/single1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/single2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/single3.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                isBatchModeActive = False
                isListViewModeActive = False
            elif ask_window("Switch to single edition?", "You are about to switch to single edition mode, all unsaved progress will be lost.", 'okcancel') == True:
                image_reset()
                isBatchModeActive = False
                isListViewModeActive = False
            else:
                pass
    else:
        if cvui.button(FRAME_MAIN, 5, 5, cv2.imread('Graphics/revert1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/revert2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/revert_light3.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                imagesVersion = 0

        if cvui.button(FRAME_MAIN, 55, 5, cv2.imread('Graphics/undo1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/undo2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/undo3_light.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                if imagesVersion > 0:
                    imagesVersion -= 1

        if cvui.button(FRAME_MAIN, 105, 5, cv2.imread('Graphics/redo1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/redo2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/redo3_light.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                if imagesVersion != len(changesList) - 1:
                    imagesVersion += 1

        if cvui.button(FRAME_MAIN, 155, 5, cv2.imread('Graphics/apply1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/apply2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/apply3_light.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                imagesVersion = len(changesList) - 1

        IAREA_CHANGE_STATE = cvui.iarea(205, 5, 40, 40)
        cvui.button(FRAME_MAIN, 205, 5, cv2.imread('Graphics/chang1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/chang2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/chang3_light.png', cv2.IMREAD_UNCHANGED))

        IAREA_ORIGINAL_STATE = cvui.iarea(255, 5, 40, 40)
        cvui.button(FRAME_MAIN, 255, 5, cv2.imread('Graphics/orig1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/orig2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/orig3_light.png', cv2.IMREAD_UNCHANGED))

        if MACRO_RECORD == False:
            if cvui.button(FRAME_MAIN, 345, 7, cv2.imread('Graphics/macrooff1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macrooff2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macrooff3_light.png', cv2.IMREAD_UNCHANGED)):
                if isImageLoaded == False:
                    message_window("Load Image!", "Load your image first.", 'error')
                else:
                    open_window(WINDOW_SETTINGS_MACRO)
        else:
            if cvui.button(FRAME_MAIN, 345, 7, cv2.imread('Graphics/macroon1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macroon2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/macroon3_light.png', cv2.IMREAD_UNCHANGED)):
                if isImageLoaded == False:
                    message_window("Load Image!", "Load your image first.", 'error')
                else:
                    open_window(WINDOW_SETTINGS_MACRO)

        if cvui.button(FRAME_MAIN, 305, 10, cv2.imread('Graphics/dark1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/dark2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/dark3.png', cv2.IMREAD_UNCHANGED)):
            isLightModeActive = not(isLightModeActive)

        if cvui.button(FRAME_MAIN, 440, 10, cv2.imread('Graphics/right1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/right2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/right3_light.png', cv2.IMREAD_UNCHANGED)):
            if (imagesCurrent - 1 >= 0):
                imagesCurrent -= 1

        cvui.rect(FRAME_MAIN, 510, 10, 80, 30, 0x515A5A)
        cvui.text(FRAME_MAIN, 540, 20, f'{imagesCurrent+1}/{len(loadedImages)}', 0.4, textColor)

        if cvui.button(FRAME_MAIN, 600, 10, cv2.imread('Graphics/left1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/left2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/left3_light.png', cv2.IMREAD_UNCHANGED)):
            if (imagesCurrent + 1 < len(loadedImages)):
                imagesCurrent += 1

        if cvui.button(FRAME_MAIN, 820, 5, cv2.imread('Graphics/list1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/list2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/list3_light.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == True:
                isListViewModeActive = not(isListViewModeActive)
            else:
                message_window("NO IMAGES LOADED", "You need to load your images first.", 'info')

        if cvui.button(FRAME_MAIN, 945, 5, cv2.imread('Graphics/single1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/single2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/single3_light.png', cv2.IMREAD_UNCHANGED)):
            if isImageLoaded == False:
                isBatchModeActive = False
                isListViewModeActive = False
            elif ask_window("Switch to single edition?", "You are about to switch to single edition mode, all unsaved progress will be lost.", 'okcancel') == True:
                image_reset()
                isBatchModeActive = False
                isListViewModeActive = False
            else:
                pass

    cvui.window(FRAME_MAIN, 1110, 5, 250, 270, 'Corrections & Effects', windowHeader, windowBody, windowText)

    if cvui.button(FRAME_MAIN, 1115, 30, 115, 40, 'Sharpness', buttonDefault, buttonOut, buttonOver, windowText):
            if isImageLoaded == False:
                message_window("Load Image!", "Load your image first.", 'error')
            else:
                open_window(WINDOW_SETTINGS_SHARPNESS)

    if cvui.button(FRAME_MAIN, 1240, 30, 115, 40, 'Brightness', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_SETTINGS_BRIGHTNESS)

    if cvui.button(FRAME_MAIN, 1240, 80, 115, 40, 'Common', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_SETTINGS_COMMON)

    if cvui.button(FRAME_MAIN, 1115, 80, 115, 40, 'Color', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_SETTINGS_COLOR)

    if cvui.button(FRAME_MAIN, 1240, 130, 115, 40, 'Morphology', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_SETTINGS_MORPH)

    if cvui.button(FRAME_MAIN, 1115, 130, 115, 40, 'Denoise', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            global FILTER_DENOISE_COLOR_AMOUNT_LAST, FILTER_DENOISE_LUMINANCE_AMOUNT_LAST, FILTER_DENOISE_SMOOTH_AMOUNT_LAST, FILTER_USE_DENOISE
            FILTER_USE_DENOISE = [True]
            FILTER_DENOISE_COLOR_AMOUNT_LAST = sys.maxsize
            FILTER_DENOISE_LUMINANCE_AMOUNT_LAST = sys.maxsize
            FILTER_DENOISE_SMOOTH_AMOUNT_LAST = sys.maxsize
            open_window(WINDOW_SETTINGS_DENOISE)

    if cvui.button(FRAME_MAIN, 1240, 180, 115, 40, 'Colorfill', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            global FILTER_COLORFILL_AMOUNT_LAST, FILTER_USE_COLORFILL_TYPE_6
            FILTER_AMOUNT_LAST = sys.maxsize
            FILTER_USE_COLORFILL_TYPE_6 = [True]
            open_window(WINDOW_SETTINGS_COLORFILL)
    cvui.rect(FRAME_MAIN, 1330, 185, 15, 30, FILTER_COLORFILL_COLOR[1], FILTER_COLORFILL_COLOR[1])

    if cvui.button(FRAME_MAIN, 1115, 230, 115, 40, 'Transformations', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_TOOLS_TRANSFORMATIONS)

    if cvui.button(FRAME_MAIN, 1115, 180, 115, 40, 'Normalization', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_FILTERS_NORMALIZATION)

    if cvui.button(FRAME_MAIN, 1240, 230, 115, 40, 'Pixelization', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            global FILTER_USE_PIX
            FILTER_USE_PIX = [True]
            open_window(WINDOW_SETTINGS_PIX)

    cvui.window(FRAME_MAIN, 1110, 280, 250, 170, 'Insert', windowHeader, windowBody, windowText)

    if cvui.button(FRAME_MAIN, 1115, 305, 115, 40, 'Overlays', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            global FILTER_USE_OVERLAY_TYPE_6
            FILTER_USE_OVERLAY_TYPE_6 = [True]
            open_window(WINDOW_SETTINGS_OVERLAYS)

    if cvui.button(FRAME_MAIN, 1240, 305, 115, 40, 'Textures', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            global FILTER_USE_TEXTURES
            FILTER_USE_TEXTURES = [True]
            open_window(WINDOW_SETTINGS_TEXTURES)

    if cvui.button(FRAME_MAIN, 1240, 405, 115, 40, 'Text', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_SETTINGS_TEXT)
    cvui.rect(FRAME_MAIN, 1330, 410, 15, 30, TEXT_USE_COLOR[1], TEXT_USE_COLOR[1])

    if cvui.button(FRAME_MAIN, 1115, 405, 115, 40, 'Frame', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            global FILTER_USE_FRAME
            FILTER_USE_FRAME = [True]
            open_window(WINDOW_SETTINGS_FRAME)
    cvui.rect(FRAME_MAIN, 1205, 410, 15, 30, FILTER_FRAME_COLOR[1], FILTER_FRAME_COLOR[1])

    if cvui.button(FRAME_MAIN, 1240, 355, 115, 40, 'Sticker', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_TOOLS_STICKER)

    if cvui.button(FRAME_MAIN, 1115, 355, 115, 40, 'Watermark', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_TOOLS_WATERMARK)

    cvui.window(FRAME_MAIN, 1110, 455, 250, 120, 'Tools', windowHeader, windowBody, windowText)

    if cvui.button(FRAME_MAIN, 1115, 480, 115, 40, 'Histogram', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            tools.histogram(changesList[imagesVersion][imagesCurrent])

    if cvui.button(FRAME_MAIN, 1240, 480, 115, 40, 'Upscale', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_TOOLS_UPSCALE)

    if cvui.button(FRAME_MAIN, 1115, 530, 240, 40, 'Combine', buttonDefault, buttonOut, buttonOver, windowText):
        if isImageLoaded == False:
            message_window("Load Image!", "Load your image first.", 'error')
        else:
            open_window(WINDOW_TOOLS_COMBINE)

    cvui.checkbox(FRAME_MAIN, 670, 16, 'Only Current Photo', CURRENT_ONLY_APPLY, textColor)

    cvui.window(FRAME_MAIN, 1110, 580, 250, 140, 'Details', windowHeader, windowBody, windowText)
    if isImageLoaded:
        (h, w) = changesList[imagesVersion][imagesCurrent].shape[:2]
        cvui.text(FRAME_MAIN, 1115, 615, "Dimensions: " + str(w) + " X " + str(h), 0.4, textColor)
        cvui.text(FRAME_MAIN, 1115, 637, "Size: " + str(int(os.path.getsize(imagesPath[imagesCurrent]) / 1024)) + " kB", 0.4, textColor)
        image_type = 'jpeg' if (str(imghdr.what(imagesPath[imagesCurrent])) == 'None') else str(imghdr.what(imagesPath[imagesCurrent]))
        cvui.text(FRAME_MAIN, 1115, 657, "Type: " + image_type, 0.4, textColor)
        cvui.text(FRAME_MAIN, 1115, 679, "Created: " + time.ctime(os.path.getctime(imagesPath[imagesCurrent])), 0.4, textColor)
        cvui.text(FRAME_MAIN, 1115, 700, "Modified: " + time.ctime(os.path.getmtime(imagesPath[imagesCurrent])), 0.4, textColor)

    if isLightModeActive == False:
        if cvui.button(FRAME_MAIN, 1110, 725, cv2.imread('Graphics/open1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/open2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/open3.png', cv2.IMREAD_UNCHANGED)):
            load_image()

        if cvui.button(FRAME_MAIN, 1180, 725, cv2.imread('Graphics/look1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/look2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/look3.png', cv2.IMREAD_UNCHANGED)):
            open_image()

        if cvui.button(FRAME_MAIN, 1250, 725, cv2.imread('Graphics/save1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/save2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/save3.png', cv2.IMREAD_UNCHANGED)):
            # OVERWRITING THE INITIAL IMAGE DIRECTORY WITH THE IMAGE USED IN PROGRAM USING GLOBAL VARIABLES
            if isImageLoaded:
                open_window(WINDOW_SETTINGS_SAVE)
            else:
                message_window('CAN NOT SAVE', 'You need to load your image first!', 'warning')

        if cvui.button(FRAME_MAIN, 1320, 725, cv2.imread('Graphics/about1.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/about2.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/about3.png', cv2.IMREAD_UNCHANGED)):
            open_window(WINDOW_SETTINGS_ABOUT)
    else:
        if cvui.button(FRAME_MAIN, 1110, 725, cv2.imread('Graphics/open1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/open2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/open3_light.png', cv2.IMREAD_UNCHANGED)):
            load_image()

        if cvui.button(FRAME_MAIN, 1180, 725, cv2.imread('Graphics/look1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/look2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/look3_light.png', cv2.IMREAD_UNCHANGED)):
            open_image()

        if cvui.button(FRAME_MAIN, 1250, 725, cv2.imread('Graphics/save1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/save2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/save3_light.png', cv2.IMREAD_UNCHANGED)):
            # OVERWRITING THE INITIAL IMAGE DIRECTORY WITH THE IMAGE USED IN PROGRAM USING GLOBAL VARIABLES
            if isImageLoaded:
                open_window(WINDOW_SETTINGS_SAVE)
            else:
                message_window('CAN NOT SAVE', 'You need to load your image first!', 'warning')

        if cvui.button(FRAME_MAIN, 1320, 725, cv2.imread('Graphics/about1_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/about2_light.png', cv2.IMREAD_UNCHANGED), cv2.imread('Graphics/about3_light.png', cv2.IMREAD_UNCHANGED)):
            open_window(WINDOW_SETTINGS_ABOUT)

    if isListViewModeActive == True:
        viewHeight = 513
        x, y = (0, 0)

        cvui.rect(FRAME_MAIN, 4, 50, 200, 200, 0x515A5A)
        if (imagesCurrent-2 >= 0):
            x, y = centering_image(loadedImagesThumbnails[imagesCurrent-2], 200, 200, 5, 51)
            cvui.image(FRAME_MAIN, x, y, loadedImagesThumbnails[imagesCurrent-2])
            cvui.rect(FRAME_MAIN, 184, 51, 20, 20, 0x515A5A, 0x515A5A)
            cvui.text(FRAME_MAIN, 190, 56, str(imagesCurrent-2+1), 0.4, textColor)
        cvui.rect(FRAME_MAIN, 204, 50, 200, 200, 0x515A5A)
        if (imagesCurrent-1 >= 0):
            x, y = centering_image(loadedImagesThumbnails[imagesCurrent-1], 200, 200, 205, 51)
            cvui.image(FRAME_MAIN, x, y, loadedImagesThumbnails[imagesCurrent-1])
            cvui.rect(FRAME_MAIN, 384, 51, 20, 20, 0x515A5A, 0x515A5A)
            cvui.text(FRAME_MAIN, 390, 56, str(imagesCurrent-1+1), 0.4, textColor)
        cvui.rect(FRAME_MAIN, 405, 50, 300, 200, 0xFF5733)
        x, y = centering_image(loadedImagesThumbnails[imagesCurrent], 300, 200, 406, 51)
        cvui.image(FRAME_MAIN, x, y, loadedImagesThumbnails[imagesCurrent])
        cvui.rect(FRAME_MAIN, 684, 51, 20, 20, 0xFF5733, 0xFF5733)
        cvui.text(FRAME_MAIN, 690, 56, str(imagesCurrent+1), 0.4, textColor)
        cvui.rect(FRAME_MAIN, 706, 50, 200, 200, 0x515A5A)
        if (imagesCurrent+1 < len(loadedImagesThumbnails)):
            x, y = centering_image(loadedImagesThumbnails[imagesCurrent+1], 200, 200, 707, 51)
            cvui.image(FRAME_MAIN, x, y, loadedImagesThumbnails[imagesCurrent+1])
            cvui.rect(FRAME_MAIN, 886, 51, 20, 20, 0x515A5A, 0x515A5A)
            cvui.text(FRAME_MAIN, 892, 56, str(imagesCurrent+1+1), 0.4, textColor)
        cvui.rect(FRAME_MAIN, 906, 50, 200, 200, 0x515A5A)
        if (imagesCurrent+2 < len(loadedImagesThumbnails)):
            x, y = centering_image(loadedImagesThumbnails[imagesCurrent+2], 200, 200, 907, 51)
            cvui.image(FRAME_MAIN, x, y, loadedImagesThumbnails[imagesCurrent+2])
            cvui.rect(FRAME_MAIN, 1086, 50, 20, 20, 0x515A5A, 0x515A5A)
            cvui.text(FRAME_MAIN, 1092, 56, str(imagesCurrent+2+1), 0.4, textColor)

    else:
        viewHeight = 713

def generate_interface_settings_sharpness():
    global FILTER_USE_BLUR, FILTER_USE_SHARPEN
    cvui.context(WINDOW_SETTINGS_SHARPNESS)
    FRAME_SETTINGS_SHARPNESS[:] = frameColor1
    cvui.window(FRAME_SETTINGS_SHARPNESS, 5, 5, 240, 225, 'SHARPNESS SETTINGS', windowHeader, windowBody, windowText)

    cvui.checkbox(FRAME_SETTINGS_SHARPNESS, 10, 30, 'Blur', FILTER_USE_BLUR, textColor)
    if FILTER_USE_BLUR[0]:
        FILTER_USE_SHARPEN = [False]
    cvui.text(FRAME_SETTINGS_SHARPNESS, 100, 50, 'strength', 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_SHARPNESS, 25, 50, 200, FILTER_BLUR_AMOUNT, 1, 100, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    if cvui.button(FRAME_SETTINGS_SHARPNESS, 225, 65, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_BLUR_AMOUNT[0] < 100:
            FILTER_BLUR_AMOUNT[0] = FILTER_BLUR_AMOUNT[0] + 1
    if cvui.button(FRAME_SETTINGS_SHARPNESS, 10, 65, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_BLUR_AMOUNT[0] > 1:
            FILTER_BLUR_AMOUNT[0] = FILTER_BLUR_AMOUNT[0] - 1

        cvui.checkbox(FRAME_SETTINGS_SHARPNESS, 10, 30, 'Sharpen', FILTER_USE_SHARPEN, textColor)

    cvui.checkbox(FRAME_SETTINGS_SHARPNESS, 10, 115, 'Sharpen', FILTER_USE_SHARPEN, textColor)
    if FILTER_USE_SHARPEN[0]:
        FILTER_USE_BLUR = [False]
    cvui.text(FRAME_SETTINGS_SHARPNESS, 100, 135, 'strength', 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_SHARPNESS, 25, 135, 200, FILTER_SHARPEN_AMOUNT, 1, 20, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    if cvui.button(FRAME_SETTINGS_SHARPNESS, 225, 150, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_SHARPEN_AMOUNT[0] < 20:
            FILTER_SHARPEN_AMOUNT[0] = FILTER_SHARPEN_AMOUNT[0] + 1
    if cvui.button(FRAME_SETTINGS_SHARPNESS, 10, 150, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_SHARPEN_AMOUNT[0] > 1:
            FILTER_SHARPEN_AMOUNT[0] = FILTER_SHARPEN_AMOUNT[0] - 1

    if cvui.button(FRAME_SETTINGS_SHARPNESS, 10, 195, 60, 30, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_USE_BLUR[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.blur(image, FILTER_BLUR_AMOUNT[0])
                build.append(img)
            add_to_changes(build, f'filters.blur(image, {FILTER_BLUR_AMOUNT[0]})')
        if FILTER_USE_SHARPEN[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.sharpen(image, FILTER_SHARPEN_AMOUNT[0])
                build.append(img)
            add_to_changes(build, f'filters.sharpen(image, {FILTER_SHARPEN_AMOUNT[0]})')
        FILTER_USE_BLUR = [False]
        FILTER_USE_SHARPEN = [False]
    if cvui.button(FRAME_SETTINGS_SHARPNESS, 180, 195, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_SHARPNESS)
        return

    cvui.imshow(WINDOW_SETTINGS_SHARPNESS, FRAME_SETTINGS_SHARPNESS)

def generate_interface_settings_bright_contr():
    global FILTER_USE_BRIGHTNESS, FILTER_USE_CONTRAST
    cvui.context(WINDOW_SETTINGS_BRIGHTNESS)
    FRAME_SETTINGS_BRIGHTNESS[:] = frameColor1
    cvui.window(FRAME_SETTINGS_BRIGHTNESS, 5, 5, 240, 220, 'BRIGHTNESS SETTINGS', windowHeader, windowBody, windowText)

    cvui.checkbox(FRAME_SETTINGS_BRIGHTNESS, 10, 30, 'Brightness', FILTER_USE_BRIGHTNESS, textColor)
    if FILTER_USE_BRIGHTNESS[0]:
        FILTER_USE_CONTRAST = [False]
    cvui.text(FRAME_SETTINGS_BRIGHTNESS, 110, 55, 'value', 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_BRIGHTNESS, 25, 55, 200, FILTER_BRIGHTNESS_AMOUNT, 0.0, 2.0, 0.01, '%.2Lf', cvui.TRACKBAR_DISCRETE, 0.01, windowText)
    if cvui.button(FRAME_SETTINGS_BRIGHTNESS, 225, 70, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_BRIGHTNESS_AMOUNT[0] < 2.0:
            FILTER_BRIGHTNESS_AMOUNT[0] += 0.01
        else:
            FILTER_BRIGHTNESS_AMOUNT[0] = 2
    if cvui.button(FRAME_SETTINGS_BRIGHTNESS, 10, 70, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_BRIGHTNESS_AMOUNT[0] > 0.0:
            FILTER_BRIGHTNESS_AMOUNT[0] -= 0.01
        else:
            FILTER_BRIGHTNESS_AMOUNT[0] = 0

    cvui.checkbox(FRAME_SETTINGS_BRIGHTNESS, 10, 110, 'Contrast', FILTER_USE_CONTRAST, textColor)
    if FILTER_USE_CONTRAST[0]:
        FILTER_USE_BRIGHTNESS = [False]
    cvui.text(FRAME_SETTINGS_BRIGHTNESS, 110, 135, 'value', 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_BRIGHTNESS, 25, 135, 200, FILTER_CONTRAST_AMOUNT, 0.0, 2.0, 0.01, '%.2Lf', cvui.TRACKBAR_DISCRETE, 0.01, windowText)
    if cvui.button(FRAME_SETTINGS_BRIGHTNESS, 225, 150, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_CONTRAST_AMOUNT[0] < 2.0:
            FILTER_CONTRAST_AMOUNT[0] += 0.01
        else:
            FILTER_CONTRAST_AMOUNT[0] = 2
    if cvui.button(FRAME_SETTINGS_BRIGHTNESS, 10, 150, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_CONTRAST_AMOUNT[0] > 0.0:
            FILTER_CONTRAST_AMOUNT[0] -= 0.01
        else:
            FILTER_CONTRAST_AMOUNT[0] = 0

    if cvui.button(FRAME_SETTINGS_BRIGHTNESS, 10, 190, 60, 30, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_USE_BRIGHTNESS[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.brightness(image, FILTER_BRIGHTNESS_AMOUNT[0])
                build.append(img)
            add_to_changes(build, f'filters.brightness(image, {FILTER_BRIGHTNESS_AMOUNT[0]})')
        if FILTER_USE_CONTRAST[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.contrast(image, FILTER_CONTRAST_AMOUNT[0])
                build.append(img)
            add_to_changes(build, f'filters.contrast(image, {FILTER_CONTRAST_AMOUNT[0]})')
        FILTER_USE_BRIGHTNESS = [False]
        FILTER_USE_CONTRAST = [False]
    if cvui.button(FRAME_SETTINGS_BRIGHTNESS, 180, 190, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_BRIGHTNESS)
        return

    cvui.imshow(WINDOW_SETTINGS_BRIGHTNESS, FRAME_SETTINGS_BRIGHTNESS)

def generate_interface_settings_common():
    global FILTER_USE_SEPIA, FILTER_USE_GRAYSCALE, FILTER_USE_BLACKANDWHITE, FILTER_USE_NEGATIVE, FILTER_USE_EMBOSS, FILTER_USE_DIFF
    cvui.context(WINDOW_SETTINGS_COMMON)
    FRAME_SETTINGS_COMMON[:] = frameColor1
    cvui.window(FRAME_SETTINGS_COMMON, 5, 5, 240, 180, 'COMMON SETTINGS', windowHeader, windowBody, windowText)
    cvui.checkbox(FRAME_SETTINGS_COMMON, 10, 35, 'Use Sepia', FILTER_USE_SEPIA, textColor)
    if FILTER_USE_SEPIA[0]:
        FILTER_USE_GRAYSCALE = [False]
        FILTER_USE_BLACKANDWHITE = [False]
        FILTER_USE_NEGATIVE = [False]
        FILTER_USE_EMBOSS = [False]
        FILTER_USE_DIFF = [False]
    cvui.checkbox(FRAME_SETTINGS_COMMON, 10, 75, 'Use Grayscale', FILTER_USE_GRAYSCALE, textColor)
    if FILTER_USE_GRAYSCALE[0]:
        FILTER_USE_SEPIA = [False]
        FILTER_USE_BLACKANDWHITE = [False]
        FILTER_USE_NEGATIVE = [False]
        FILTER_USE_EMBOSS = [False]
        FILTER_USE_DIFF = [False]
    cvui.checkbox(FRAME_SETTINGS_COMMON, 130, 35, 'Use B&W', FILTER_USE_BLACKANDWHITE, textColor)
    if FILTER_USE_BLACKANDWHITE[0]:
        FILTER_USE_SEPIA = [False]
        FILTER_USE_GRAYSCALE = [False]
        FILTER_USE_NEGATIVE = [False]
        FILTER_USE_EMBOSS = [False]
        FILTER_USE_DIFF = [False]
    cvui.checkbox(FRAME_SETTINGS_COMMON, 130, 75, 'Use Negative', FILTER_USE_NEGATIVE, textColor)
    if FILTER_USE_NEGATIVE[0]:
        FILTER_USE_SEPIA = [False]
        FILTER_USE_GRAYSCALE = [False]
        FILTER_USE_BLACKANDWHITE = [False]
        FILTER_USE_EMBOSS = [False]
        FILTER_USE_DIFF = [False]
    cvui.checkbox(FRAME_SETTINGS_COMMON, 10, 115, 'Use Emboss', FILTER_USE_EMBOSS, textColor)
    if FILTER_USE_EMBOSS[0]:
        FILTER_USE_NEGATIVE = [False]
        FILTER_USE_SEPIA = [False]
        FILTER_USE_GRAYSCALE = [False]
        FILTER_USE_BLACKANDWHITE = [False]
        FILTER_USE_DIFF = [False]
    cvui.checkbox(FRAME_SETTINGS_COMMON, 130, 115, 'Use Difference', FILTER_USE_DIFF, textColor)
    if FILTER_USE_DIFF[0]:
        FILTER_USE_NEGATIVE = [False]
        FILTER_USE_SEPIA = [False]
        FILTER_USE_GRAYSCALE = [False]
        FILTER_USE_BLACKANDWHITE = [False]
        FILTER_USE_EMBOSS = [False]
    if cvui.button(FRAME_SETTINGS_COMMON, 10, 150, 60, 30, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_USE_SEPIA[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.sepia(image)
                build.append(img)
            add_to_changes(build, f'filters.sepia(image)')
        if FILTER_USE_GRAYSCALE[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.grayscale(image)
                build.append(img)
            add_to_changes(build, f'filters.grayscale(image)')
        if FILTER_USE_BLACKANDWHITE[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.blackandwhite(image)
                build.append(img)
            add_to_changes(build, f'filters.blackandwhite(image)')
        if FILTER_USE_NEGATIVE[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.negative(image)
                build.append(img)
            add_to_changes(build, f'filters.negative(image)')
        if FILTER_USE_EMBOSS[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.emboss(image)
                build.append(img)
            add_to_changes(build, f'filters.emboss(image)')
        if FILTER_USE_DIFF[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.diff(image)
                build.append(img)
            add_to_changes(build, f'filters.diff(image)')
        FILTER_USE_SEPIA = [False]
        FILTER_USE_GRAYSCALE = [False]
        FILTER_USE_BLACKANDWHITE = [False]
        FILTER_USE_NEGATIVE = [False]
        FILTER_USE_EMBOSS = [False]
        FILTER_USE_DIFF = [False]

    if cvui.button(FRAME_SETTINGS_COMMON, 180, 150, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_COMMON)
        return

    cvui.imshow(WINDOW_SETTINGS_COMMON, FRAME_SETTINGS_COMMON)

def generate_interface_settings_color():
    global FILTER_USE_SATURATION, FILTER_USE_TEMPERATURE, FILTER_USE_TINT, FILTER_USE_COLORBALANCE
    cvui.context(WINDOW_SETTINGS_COLOR)
    FRAME_SETTINGS_COLOR[:] = frameColor1
    cvui.window(FRAME_SETTINGS_COLOR, 5, 5, 240, 505, 'COLOR SETTINGS', windowHeader, windowBody, windowText)

    cvui.checkbox(FRAME_SETTINGS_COLOR, 10, 30, 'Saturation', FILTER_USE_SATURATION, textColor)
    if FILTER_USE_SATURATION[0]:
        FILTER_USE_TEMPERATURE = [False]
        FILTER_USE_TINT = [False]
        FILTER_USE_COLORBALANCE = [False]
    cvui.text(FRAME_SETTINGS_COLOR, 105, 55, 'value', 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_COLOR, 25, 55, 200, FILTER_SATURATION_AMOUNT, 0, 2, 1.0, '%.2Lf', cvui.TRACKBAR_DISCRETE, 0.01, windowText)
    if cvui.button(FRAME_SETTINGS_COLOR, 225, 70, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_SATURATION_AMOUNT[0] < 2.0:
            FILTER_SATURATION_AMOUNT[0] += 0.01
        else:
            FILTER_SATURATION_AMOUNT[0] = 2
    if cvui.button(FRAME_SETTINGS_COLOR, 10, 70, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_SATURATION_AMOUNT[0] > 0.0:
            FILTER_SATURATION_AMOUNT[0] -= 0.01
        else:
            FILTER_SATURATION_AMOUNT[0] = 0

    cvui.checkbox(FRAME_SETTINGS_COLOR, 10, 100, 'Temperature', FILTER_USE_TEMPERATURE, textColor)
    if FILTER_USE_TEMPERATURE[0]:
        FILTER_USE_SATURATION = [False]
        FILTER_USE_TINT = [False]
        FILTER_USE_COLORBALANCE = [False]
    cvui.text(FRAME_SETTINGS_COLOR, 105, 125, 'value', 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_COLOR, 25, 125, 200, FILTER_TEMPERATURE_AMOUNT, 3000, 15000, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 500, windowText)
    if cvui.button(FRAME_SETTINGS_COLOR, 225, 140, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_TEMPERATURE_AMOUNT[0] < 15000:
            FILTER_TEMPERATURE_AMOUNT[0] += 500
        else:
            FILTER_TEMPERATURE_AMOUNT[0] = 15000
    if cvui.button(FRAME_SETTINGS_COLOR, 10, 140, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_TEMPERATURE_AMOUNT[0] > 3000:
            FILTER_TEMPERATURE_AMOUNT[0] -= 500
        else:
            FILTER_TEMPERATURE_AMOUNT[0] = 3000

    cvui.checkbox(FRAME_SETTINGS_COLOR, 10, 170, 'Tint', FILTER_USE_TINT, textColor)
    if FILTER_USE_TINT[0]:
        FILTER_USE_SATURATION = [False]
        FILTER_USE_TEMPERATURE = [False]
        FILTER_USE_COLORBALANCE = [False]
    cvui.text(FRAME_SETTINGS_COLOR, 105, 195, 'value', 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_COLOR, 25, 195, 200, FILTER_TINT_AMOUNT, -20, 20, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    if cvui.button(FRAME_SETTINGS_COLOR, 225, 210, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_TINT_AMOUNT[0] < 20:
            FILTER_TINT_AMOUNT[0] += 1
        else:
            FILTER_TINT_AMOUNT[0] = 20
    if cvui.button(FRAME_SETTINGS_COLOR, 10, 210, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_TINT_AMOUNT[0] > -20:
            FILTER_TINT_AMOUNT[0] -= 1
        else:
            FILTER_TINT_AMOUNT[0] = -20

    cvui.checkbox(FRAME_SETTINGS_COLOR, 10, 250, 'Color Balance', FILTER_USE_COLORBALANCE, textColor)
    if FILTER_USE_COLORBALANCE[0]:
        FILTER_USE_SATURATION = [False]
        FILTER_USE_TEMPERATURE = [False]
        FILTER_USE_TINT = [False]
    cvui.text(FRAME_SETTINGS_COLOR, 25, 280, 'CYAN', 0.4, textColor)
    cvui.text(FRAME_SETTINGS_COLOR, 195, 280, 'RED', 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_COLOR, 25, 290, 200, FILTER_CYANRED_AMOUNT, -20, 20, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    if cvui.button(FRAME_SETTINGS_COLOR, 225, 305, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_CYANRED_AMOUNT[0] < 20:
            FILTER_CYANRED_AMOUNT[0] += 1
        else:
            FILTER_CYANRED_AMOUNT[0] = 20
    if cvui.button(FRAME_SETTINGS_COLOR, 10, 305, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_CYANRED_AMOUNT[0] > -20:
            FILTER_CYANRED_AMOUNT[0] -= 1
        else:
            FILTER_CYANRED_AMOUNT[0] = -20

    cvui.text(FRAME_SETTINGS_COLOR, 25, 340, 'MAGENTA', 0.4, textColor)
    cvui.text(FRAME_SETTINGS_COLOR, 185, 340, 'GREEN', 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_COLOR, 25, 350, 200, FILTER_MAGENTAGREEN_AMOUNT, -20, 20, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    if cvui.button(FRAME_SETTINGS_COLOR, 225, 365, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_MAGENTAGREEN_AMOUNT[0] < 20:
            FILTER_MAGENTAGREEN_AMOUNT[0] += 1
        else:
            FILTER_MAGENTAGREEN_AMOUNT[0] = 20
    if cvui.button(FRAME_SETTINGS_COLOR, 10, 365, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_MAGENTAGREEN_AMOUNT[0] > -20:
            FILTER_MAGENTAGREEN_AMOUNT[0] -= 1
        else:
            FILTER_MAGENTAGREEN_AMOUNT[0] = -20

    cvui.text(FRAME_SETTINGS_COLOR, 25, 395, 'BLUE', 0.4, textColor)
    cvui.text(FRAME_SETTINGS_COLOR, 185, 395, 'YELLOW', 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_COLOR, 25, 410, 200, FILTER_BLUEYELLOW_AMOUNT, -20, 20, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    if cvui.button(FRAME_SETTINGS_COLOR, 225, 425, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_BLUEYELLOW_AMOUNT[0] < 20:
            FILTER_BLUEYELLOW_AMOUNT[0] += 1
        else:
            FILTER_BLUEYELLOW_AMOUNT[0] = 20
    if cvui.button(FRAME_SETTINGS_COLOR, 10, 425, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_BLUEYELLOW_AMOUNT[0] > -20:
            FILTER_BLUEYELLOW_AMOUNT[0] -= 1
        else:
            FILTER_BLUEYELLOW_AMOUNT[0] = -20

    if cvui.button(FRAME_SETTINGS_COLOR, 10, 475, 60, 30, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_USE_SATURATION[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.color(image, FILTER_SATURATION_AMOUNT[0])
                build.append(img)
            add_to_changes(build, f'filters.color(image, {FILTER_SATURATION_AMOUNT[0]})')
        if FILTER_USE_TEMPERATURE[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.temperature(image, FILTER_TEMPERATURE_AMOUNT[0])
                build.append(img)
            add_to_changes(build, f'filters.temperature(image, {FILTER_TEMPERATURE_AMOUNT[0]})')
        if FILTER_USE_TINT[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.tint(image, FILTER_TINT_AMOUNT[0])
                build.append(img)
            add_to_changes(build, f'filters.tint(image, {FILTER_TINT_AMOUNT[0]})')
        if FILTER_USE_COLORBALANCE[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.colorbalance(image, FILTER_CYANRED_AMOUNT[0], FILTER_MAGENTAGREEN_AMOUNT[0], FILTER_BLUEYELLOW_AMOUNT[0])
                build.append(img)
            add_to_changes(build, f'filters.colorbalance(image, {FILTER_CYANRED_AMOUNT[0]}, {FILTER_MAGENTAGREEN_AMOUNT[0]}, {FILTER_BLUEYELLOW_AMOUNT[0]})')

        FILTER_USE_TINT = [False]
        FILTER_USE_SATURATION = [False]
        FILTER_USE_TEMPERATURE = [False]
        FILTER_USE_COLORBALANCE = [False]
    if cvui.button(FRAME_SETTINGS_COLOR, 180, 475, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_COLOR)
        return

    cvui.imshow(WINDOW_SETTINGS_COLOR, FRAME_SETTINGS_COLOR)

def generate_interface_settings_morph():
    global FILTER_USE_EROSION, FILTER_USE_DILATATION
    cvui.context(WINDOW_SETTINGS_MORPH)
    FRAME_SETTINGS_MORPH[:] = frameColor1
    cvui.window(FRAME_SETTINGS_MORPH, 5, 5, 240, 225, 'MORPHOLOGY SETTINGS', windowHeader, windowBody, windowText)

    cvui.checkbox(FRAME_SETTINGS_MORPH, 10, 30, 'Dilatate', FILTER_USE_DILATATION, textColor)
    if FILTER_USE_DILATATION[0]:
        FILTER_USE_EROSION = [False]
    cvui.text(FRAME_SETTINGS_MORPH, 99, 55, 'iterations', 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_MORPH, 25, 50, 200, FILTER_DILATATION_AMOUNT, 0, 10, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    if cvui.button(FRAME_SETTINGS_MORPH, 225, 65, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_DILATATION_AMOUNT[0] < 10:
            FILTER_DILATATION_AMOUNT[0] += 1
        else:
            FILTER_DILATATION_AMOUNT[0] = 10
    if cvui.button(FRAME_SETTINGS_MORPH, 10, 65, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_DILATATION_AMOUNT[0] > 0:
            FILTER_DILATATION_AMOUNT[0] -= 1
        else:
            FILTER_DILATATION_AMOUNT[0] = 0

    cvui.checkbox(FRAME_SETTINGS_MORPH, 10, 110, 'Erode', FILTER_USE_EROSION, textColor)
    if FILTER_USE_EROSION[0]:
        FILTER_USE_DILATATION = [False]
    cvui.text(FRAME_SETTINGS_MORPH, 99, 135, 'iterations', 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_MORPH, 25, 130, 200, FILTER_EROSION_AMOUNT, 0, 10, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    if cvui.button(FRAME_SETTINGS_MORPH, 225, 145, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_EROSION_AMOUNT[0] < 10:
            FILTER_EROSION_AMOUNT[0] += 1
        else:
            FILTER_EROSION_AMOUNT[0] = 10
    if cvui.button(FRAME_SETTINGS_MORPH, 10, 145, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_EROSION_AMOUNT[0] > 0:
            FILTER_EROSION_AMOUNT[0] -= 1
        else:
            FILTER_EROSION_AMOUNT[0] = 0

    if cvui.button(FRAME_SETTINGS_MORPH, 10, 195, 60, 30, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_USE_EROSION[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.erosion(image, FILTER_EROSION_AMOUNT[0])
                build.append(img)
            add_to_changes(build, f'filters.erosion(image, {FILTER_EROSION_AMOUNT[0]})')
        if FILTER_USE_DILATATION[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.dilatation(image, FILTER_DILATATION_AMOUNT[0])
                build.append(img)
            add_to_changes(build, f'filters.dilatation(image, {FILTER_DILATATION_AMOUNT[0]})')

        FILTER_USE_EROSION = [False]
        FILTER_USE_DILATATION = [False]
    if cvui.button(FRAME_SETTINGS_MORPH, 180, 195, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_MORPH)
        return

    cvui.imshow(WINDOW_SETTINGS_MORPH, FRAME_SETTINGS_MORPH)

def generate_interface_settings_denoise():
    global FILTER_USE_DENOISE, IAREA_DENOISE_STATE
    cvui.context(WINDOW_SETTINGS_DENOISE)
    FRAME_SETTINGS_DENOISE[:] = frameColor1
    cvui.window(FRAME_SETTINGS_DENOISE, 5, 5, 240, 250, 'DENOISE SETTINGS', windowHeader, windowBody, windowText)
    cvui.checkbox(FRAME_SETTINGS_DENOISE, 10, 30, 'Denoise', FILTER_USE_DENOISE, textColor)
    IAREA_DENOISE_STATE = cvui.iarea(5, 5, 240, 290)

    cvui.trackbar(FRAME_SETTINGS_DENOISE, 25, 55, 200, FILTER_DENOISE_LUMINANCE_AMOUNT, 0, 10, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    cvui.text(FRAME_SETTINGS_DENOISE, 95, 55, 'luminance', 0.4, textColor)
    if cvui.button(FRAME_SETTINGS_DENOISE, 225, 70, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_DENOISE_LUMINANCE_AMOUNT[0] < 10:
            FILTER_DENOISE_LUMINANCE_AMOUNT[0] += 1
        else:
            FILTER_DENOISE_LUMINANCE_AMOUNT[0] = 10
    if cvui.button(FRAME_SETTINGS_DENOISE, 10, 70, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_DENOISE_LUMINANCE_AMOUNT[0] > 0:
            FILTER_DENOISE_LUMINANCE_AMOUNT[0] -= 1
        else:
            FILTER_DENOISE_LUMINANCE_AMOUNT[0] = 0

    cvui.trackbar(FRAME_SETTINGS_DENOISE, 25, 110, 200, FILTER_DENOISE_COLOR_AMOUNT, 0, 20, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    cvui.text(FRAME_SETTINGS_DENOISE, 111, 110, 'color', 0.4, textColor)
    if cvui.button(FRAME_SETTINGS_DENOISE, 225, 125, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_DENOISE_COLOR_AMOUNT[0] < 20:
            FILTER_DENOISE_COLOR_AMOUNT[0] += 1
        else:
            FILTER_DENOISE_COLOR_AMOUNT[0] = 20
    if cvui.button(FRAME_SETTINGS_DENOISE, 10, 125, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_DENOISE_COLOR_AMOUNT[0] > 0:
            FILTER_DENOISE_COLOR_AMOUNT[0] -= 1
        else:
            FILTER_DENOISE_COLOR_AMOUNT[0] = 0

    cvui.trackbar(FRAME_SETTINGS_DENOISE, 25, 167, 200, FILTER_DENOISE_SMOOTH_AMOUNT, 1, 9, 2, '%.0Lf', cvui.TRACKBAR_DISCRETE, 2, windowText)
    cvui.text(FRAME_SETTINGS_DENOISE, 90, 157, 'smoothness', 0.4, textColor)
    if cvui.button(FRAME_SETTINGS_DENOISE, 225, 182, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_DENOISE_SMOOTH_AMOUNT[0] < 9:
            FILTER_DENOISE_SMOOTH_AMOUNT[0] += 2
        else:
            FILTER_DENOISE_SMOOTH_AMOUNT[0] = 9
    if cvui.button(FRAME_SETTINGS_DENOISE, 10, 182, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_DENOISE_SMOOTH_AMOUNT[0] > 1:
            FILTER_DENOISE_SMOOTH_AMOUNT[0] -= 2
        else:
            FILTER_DENOISE_SMOOTH_AMOUNT[0] = 1

    if cvui.button(FRAME_SETTINGS_DENOISE, 10, 220, 60, 30, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_USE_DENOISE[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.denoise(image, FILTER_DENOISE_LUMINANCE_AMOUNT[0], FILTER_DENOISE_COLOR_AMOUNT[0], FILTER_DENOISE_SMOOTH_AMOUNT[0])
                build.append(img)
            add_to_changes(build, f'filters.denoise(image, {FILTER_DENOISE_LUMINANCE_AMOUNT[0]}, {FILTER_DENOISE_COLOR_AMOUNT[0]}, {FILTER_DENOISE_SMOOTH_AMOUNT[0]})')

        FILTER_USE_DENOISE = [False]

    if cvui.button(FRAME_SETTINGS_DENOISE, 180, 220, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_DENOISE)
        return

    cvui.imshow(WINDOW_SETTINGS_DENOISE, FRAME_SETTINGS_DENOISE)

def generate_interface_settings_save():
    cvui.context(WINDOW_SETTINGS_SAVE)
    FRAME_SETTINGS_SAVE[:] = frameColor1
    cvui.window(FRAME_SETTINGS_SAVE, 5, 5, 495, 305, 'SINGLE FILE SAVING', windowHeader, windowBody, windowText)
    cvui.trackbar(FRAME_SETTINGS_SAVE, 120, 180, 350, FILTER_SAVE_AMOUNT, 1, 100, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)

    cvui.text(FRAME_SETTINGS_SAVE, 150, 50, "Path: " + imagesPath[0], 0.4, textColor)
    cvui.text(FRAME_SETTINGS_SAVE, 150, 100, "Save as new filename", 0.4, textColor)
    cvui.text(FRAME_SETTINGS_SAVE, 150, 150, "Save as new filename with JPG extension", 0.4, textColor)
    cvui.text(FRAME_SETTINGS_SAVE, 30, 198, "JPEG Quality", 0.4, textColor)
    cvui.text(FRAME_SETTINGS_SAVE, 30, 230, "We recommend to save your photo at quality 95 or better.", 0.4, textColor)
    cvui.text(FRAME_SETTINGS_SAVE, 30, 245, "The higher the value, the better the image quality and larger the file.", 0.4, textColor)

    if cvui.button(FRAME_SETTINGS_SAVE, 30, 40, 100, 30, 'Overwrite', buttonDefault, buttonOut, buttonOver, windowText):
        cv2.imwrite(imagesPath[0], changesList[imagesVersion][imagesCurrent])

    if cvui.button(FRAME_SETTINGS_SAVE, 30, 90, 100, 30, 'Save as...', buttonDefault, buttonOut, buttonOver, windowText):
        filepath = filedialog.asksaveasfilename(title="Choose saving location.", filetypes=(('PNG','*.png'), ('BMP', ('*.bmp', '*.jdib'))), defaultextension='')
        # IF NAME OF FILE AND PATH IS CHOOSEN
        if filepath:
            cv2.imwrite(filepath, changesList[imagesVersion][imagesCurrent])
        else:
            message_window("FILE WAS NOT CHOSEN", "You need to choose a file!", 'error')

    if cvui.button(FRAME_SETTINGS_SAVE, 30, 140, 100, 30, 'Save as JPG', buttonDefault, buttonOut, buttonOver, windowText):
        filepath = filedialog.asksaveasfilename(title="Choose saving location.",  filetypes=(('JPG', '*.jpg'), ('JPEG','*.jpeg'), ('JPE', '*.jpe')), defaultextension='*.jpg')
        # IF NAME OF FILE AND PATH IS CHOOSEN
        if filepath:
            cv2.imwrite(filepath, changesList[imagesVersion][imagesCurrent], (cv2.IMWRITE_JPEG_QUALITY, FILTER_SAVE_AMOUNT[0]))
        else:
            message_window("FILE WAS NOT CHOSEN", "You need to choose a file!", 'error')

    if cvui.button(FRAME_SETTINGS_SAVE, 30, 270, 60, 30, 'PREVIEW', buttonDefault, buttonOut, buttonOver, windowText):
        open_window(WINDOW_SETTINGS_PREVIEW)

    if isBatchModeActive == True:
        if cvui.button(FRAME_SETTINGS_SAVE, 195, 270, 120, 30, 'ALL IMAGES SAVE', buttonDefault, buttonOut, buttonOver, windowText):
            open_window(WINDOW_SETTINGS_BATCHSAVE)
            close_window(WINDOW_SETTINGS_SAVE)
            return

    if cvui.button(FRAME_SETTINGS_SAVE, 430, 270, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_SAVE)
        return

    cvui.imshow(WINDOW_SETTINGS_SAVE, FRAME_SETTINGS_SAVE)

def generate_interface_settings_batchsave():
    cvui.context(WINDOW_SETTINGS_BATCHSAVE)
    FRAME_SETTINGS_BATCHSAVE[:] = frameColor1
    cvui.window(FRAME_SETTINGS_BATCHSAVE, 5, 5, 340, 325, 'BATCH FILE SAVING', windowHeader, windowBody, windowText)

    if cvui.button(FRAME_SETTINGS_BATCHSAVE, 10, 30, 330, 40, 'Overwrite original files', buttonDefault, buttonOut, buttonOver, windowText):
        for index, image in enumerate(changesList[imagesVersion]):
            cv2.imwrite(imagesPath[index], image)

    #! THIS IS NOT WITHOUT CHANGING EXTENSION
    if cvui.button(FRAME_SETTINGS_BATCHSAVE, 10, 80, 330, 40, 'Save in a folder without changing extension...', buttonDefault, buttonOut, buttonOver, windowText):
        folderpath = filedialog.askdirectory()
        for index, image in enumerate(changesList[imagesVersion]):
            image_type = 'jpeg' if (str(imghdr.what(imagesPath[index])) == 'None') else str(imghdr.what(imagesPath[index]))
            cv2.imwrite(f'{folderpath}/{index}.{image_type}', image)

    if cvui.button(FRAME_SETTINGS_BATCHSAVE, 10, 130, 330, 40, 'Save in a folder as .png extension...', buttonDefault, buttonOut, buttonOver, windowText):
        folderpath = filedialog.askdirectory()
        for index, image in enumerate(changesList[imagesVersion]):
            cv2.imwrite(f'{folderpath}/{index}.png', image)

    if cvui.button(FRAME_SETTINGS_BATCHSAVE, 10, 180, 330, 40, 'Save in a folder as .jpg extension...', buttonDefault, buttonOut, buttonOver, windowText):
        folderpath = filedialog.askdirectory()
        for index, image in enumerate(changesList[imagesVersion]):
            cv2.imwrite(f'{folderpath}/{index}.jpg', image, (cv2.IMWRITE_JPEG_QUALITY, FILTER_SAVE_AMOUNT[0]))

    cvui.text(FRAME_SETTINGS_BATCHSAVE, 150, 230, 'jpeg quality', 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_BATCHSAVE, 0, 230, 340, FILTER_SAVE_AMOUNT, 1, 100, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)

    if cvui.button(FRAME_SETTINGS_BATCHSAVE, 10, 295, 60, 30, 'PREVIEW', buttonDefault, buttonOut, buttonOver, windowText):
        open_window(WINDOW_SETTINGS_PREVIEW)

    if cvui.button(FRAME_SETTINGS_BATCHSAVE, 95, 295, 160, 30, 'CURRENT IMAGE SAVE', buttonDefault, buttonOut, buttonOver, windowText):
        open_window(WINDOW_SETTINGS_SAVE)
        close_window(WINDOW_SETTINGS_BATCHSAVE)
        return

    if cvui.button(FRAME_SETTINGS_BATCHSAVE, 280, 295, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_BATCHSAVE)
        return

    cvui.imshow(WINDOW_SETTINGS_BATCHSAVE, FRAME_SETTINGS_BATCHSAVE)

def generate_interface_settings_preview():
    #! WE HAVE TO DELETE IMAGE AFTER LEAVING THE FRAME WITH MOUSE SOMEHOW #
    global FILTER_SAVE_AMOUNT_LAST, temp_image, temp_imageResized, saveImageOnce
    cvui.context(WINDOW_SETTINGS_PREVIEW)
    FRAME_SETTINGS_PREVIEW[:] = frameColor1
    cvui.window(FRAME_SETTINGS_PREVIEW, 5, 5, 690, 570, 'PREVIEW SETTINGS', windowHeader, windowBody, windowText)
    cvui.text(FRAME_SETTINGS_PREVIEW, 30, 50, "JPEG Quality", 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_PREVIEW, 100, 30, 350, FILTER_SAVE_AMOUNT, 1, 100, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)

    ## PYTHON NEEDS THE IMAGE TO BE SAVED, SO WE SAVE IT ONCE ##
    if saveImageOnce:
         cv2.imwrite(temp_filepath, changesList[imagesVersion][imagesCurrent])
         saveImageOnce = False

    ## IF FILTER ISN'T CHANGED, JUST COPY THE LAST USED IMAGE TO PREVIEW ##
    ## AND SAVE SOME MEMORY ##
    if FILTER_SAVE_AMOUNT[0] == FILTER_SAVE_AMOUNT_LAST:
        temp_imageResized[:] = temp_image[:]
        cvui.image(FRAME_SETTINGS_PREVIEW, 30, 80, temp_imageResized)
        cvui.text(FRAME_SETTINGS_PREVIEW, 450, 50, "Size: " + (str(int(os.path.getsize(temp_filepath)/1024)) + " kB"), 0.4, textColor)

    ## ELSE SAVE THE IMAGE DYNAMICALLY IN TEMP FOLDER ##
    ## READ IT AND SHOW TO USER ##
    else:
        if cv2.imwrite(temp_filepath, changesList[imagesVersion][imagesCurrent], (cv2.IMWRITE_JPEG_QUALITY, FILTER_SAVE_AMOUNT[0])):
            cvui.text(FRAME_SETTINGS_PREVIEW, 450, 50, "Size: " + (str(int(os.path.getsize(temp_filepath)/1024)) + " kB"), 0.4, textColor)

            temp_image = cv2.imread(temp_filepath, cv2.IMREAD_COLOR)
            temp_image = cv2.resize(temp_image,(640,480))
            temp_imageResized = temp_image
            cvui.image(FRAME_SETTINGS_PREVIEW, 30, 80, temp_imageResized)

            FILTER_SAVE_AMOUNT_LAST = FILTER_SAVE_AMOUNT[0]

    if cvui.button(FRAME_SETTINGS_PREVIEW, 610, 40, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_PREVIEW)
        return

    cvui.imshow(WINDOW_SETTINGS_PREVIEW, FRAME_SETTINGS_PREVIEW)

def generate_interface_tools_watermark():
    global imageCopy, imageVersion, imagePath
    global WINDOW_TOOLS_WATERMARK_STATE, WATERMARK_SCALE_AMOUNT, temp_watermarkPath, isWatermarkLoaded, WATERMARK_USE_LEFT_UPPER, WATERMARK_USE_RIGHT_UPPER, WATERMARK_USE_LEFT_DOWN, WATERMARK_USE_RIGHT_DOWN
    global WATERMARK_X_POSITION, WATERMARK_Y_POSITION, water_mark_shape, changesList, finalWatermark
    APPLY_WATERMARK_X_POSITION = 0
    APPLY_WATERMARK_Y_POSITION = 0
    APPLY_OFFSET_X_POSITION = 0
    APPLY_OFFSET_Y_POSITION = 0
    cvui.context(WINDOW_TOOLS_WATERMARK)
    FRAME_TOOLS_WATERMARK[:] = frameColor1
    cvui.window(FRAME_TOOLS_WATERMARK, 5, 5, 350, 490, 'WATERMARK SETTINGS', windowHeader, windowBody, windowText)

    h, w, _ = changesList[imagesVersion][imagesCurrent].shape

    ##LOADING WATERMARK##
    if cvui.button(FRAME_TOOLS_WATERMARK, 15, 35, 60, 120, 'LOAD', buttonDefault, buttonOut, buttonOver, windowText):
        Tk().withdraw()
        temp_watermarkPath = filedialog.askopenfilename(title="Wybierz watermark", filetypes=[('Image Files', '.png')])

        if temp_watermarkPath == '':
            message_window("NO WATERMARK HAS BEEN LOADED", "Failed to load the watermark.", 'warning')
        else:
            isWatermarkLoaded = True

    cvui.rect(FRAME_TOOLS_WATERMARK, 100, 35, 245, 120, 0x515A5A)
    ##WATERMARK USED TO PASTE ONTO IMAGE##
    if isWatermarkLoaded:
        finalWatermark = Image.open(temp_watermarkPath).convert("RGBA")

        # Just to be sure, changing mode
        if finalWatermark.mode == "P":
            finalWatermark = finalWatermark.convert("RGB")

        if finalWatermark.mode == "RGB":
            a_channel = Image.new('L', finalWatermark.size, 255)   # 'L' 8-bit pixels, black and white
            finalWatermark.putalpha(a_channel)

        width, height = finalWatermark.size

        if WATERMARK_SCALE_AMOUNT[0] <= 100:
            final_watermark_height = (height * WATERMARK_SCALE_AMOUNT[0])/100
            final_watermark_width = (width * WATERMARK_SCALE_AMOUNT[0])/100
            finalWatermark.thumbnail((final_watermark_width, final_watermark_height))
        elif WATERMARK_SCALE_AMOUNT[0] > 100:
            final_watermark_height = int((height * WATERMARK_SCALE_AMOUNT[0])/100)
            final_watermark_width = int((width * WATERMARK_SCALE_AMOUNT[0])/100)

            finalWatermark = finalWatermark.resize((final_watermark_width, final_watermark_height), Image.BICUBIC)

    ##PREVIEW OF WATERMARK##
    if isWatermarkLoaded:
        temp_pillow_image = Image.open(temp_watermarkPath)
        temp_pillow_image.thumbnail((244, 119))
        temp_background = Image.new("RGB", temp_pillow_image.size, (50,50,50))
        temp_background.paste(temp_pillow_image, (0, 0), temp_pillow_image)
        temp_background.convert('RGB')
        temp_watermark_array = np.array(temp_background)
        final_temp_watermark = cv2.cvtColor(temp_watermark_array, cv2.COLOR_RGB2BGR)

        cvui.image(FRAME_TOOLS_WATERMARK, 101, 36, final_temp_watermark)

    ##SCALING TRACKBAR OF WATERMARK##
    cvui.text(FRAME_TOOLS_WATERMARK, 155, 180, "%scale", 0.4, textColor)
    cvui.trackbar(FRAME_TOOLS_WATERMARK, 25, 180, 305, WATERMARK_SCALE_AMOUNT, 1, 200, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)

    if cvui.button(FRAME_TOOLS_WATERMARK, 330, 195, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if WATERMARK_SCALE_AMOUNT[0] < 200:
            WATERMARK_SCALE_AMOUNT[0] = WATERMARK_SCALE_AMOUNT[0] + 1
    if cvui.button(FRAME_TOOLS_WATERMARK, 10, 195, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if WATERMARK_SCALE_AMOUNT[0] > 1:
            WATERMARK_SCALE_AMOUNT[0] = WATERMARK_SCALE_AMOUNT[0] - 1

    ##PREDEFINIED POSITIONS OF WATERMARK##
    cvui.rect(FRAME_TOOLS_WATERMARK, 90, 240, 180, 84, 0xffffff)

    if cvui.button(FRAME_TOOLS_WATERMARK, 92, 242, 80, 30, 'TOP-LEFT', buttonDefault, buttonOut, buttonOver, windowText):
        if isWatermarkLoaded:
            WATERMARK_X_POSITION = 20
            WATERMARK_Y_POSITION = 20
    if cvui.button(FRAME_TOOLS_WATERMARK, 188, 242, 80, 30, 'TOP-RIGHT', buttonDefault, buttonOut, buttonOver, windowText):
        if isWatermarkLoaded:
            WATERMARK_X_POSITION = w - final_watermark_width - 20
            WATERMARK_Y_POSITION = 20
    if cvui.button(FRAME_TOOLS_WATERMARK, 92, 292, 80, 30, 'BOT-LEFT', buttonDefault, buttonOut, buttonOver, windowText):
        if isWatermarkLoaded:
            WATERMARK_X_POSITION = 20
            WATERMARK_Y_POSITION = h - final_watermark_height - 20
    if cvui.button(FRAME_TOOLS_WATERMARK, 188, 292, 80, 30,'BOT-RIGHT', buttonDefault, buttonOut, buttonOver, windowText):
        if isWatermarkLoaded:
            WATERMARK_X_POSITION = w - final_watermark_width - 20
            WATERMARK_Y_POSITION = h - final_watermark_height - 20
    cvui.text(FRAME_TOOLS_WATERMARK, 152, 278, 'POSITION', 0.4, textColor)

    if cvui.button(FRAME_TOOLS_WATERMARK, 150, 345, 60, 30, 'UP', buttonDefault, buttonOut, buttonOver, windowText):
        if isWatermarkLoaded:
            WATERMARK_Y_POSITION -= 5
    if cvui.button(FRAME_TOOLS_WATERMARK, 210, 380, 60, 30, 'RIGHT', buttonDefault, buttonOut, buttonOver, windowText):
        if isWatermarkLoaded:
            WATERMARK_X_POSITION += 5
    if cvui.button(FRAME_TOOLS_WATERMARK, 90, 380, 60, 30, 'LEFT', buttonDefault, buttonOut, buttonOver, windowText):
        if isWatermarkLoaded:
            WATERMARK_X_POSITION -= 5
    if cvui.button(FRAME_TOOLS_WATERMARK, 150, 415, 60, 30, 'BOTTOM', buttonDefault, buttonOut, buttonOver, windowText):
        if isWatermarkLoaded:
            WATERMARK_Y_POSITION += 5
    cvui.text(FRAME_TOOLS_WATERMARK, 164, 390, 'MOVE', 0.4, textColor)

    if cvui.button(FRAME_TOOLS_WATERMARK, 10, 450, 90, 40, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):

        if isWatermarkLoaded:

            build = []
            for image in changesList[imagesVersion]:
                new_h, new_w, _ = image.shape
                APPLY_OFFSET_X_POSITION = new_w / w
                APPLY_OFFSET_Y_POSITION = new_h / h
                APPLY_WATERMARK_X_POSITION = WATERMARK_X_POSITION * APPLY_OFFSET_X_POSITION
                APPLY_WATERMARK_Y_POSITION = WATERMARK_Y_POSITION * APPLY_OFFSET_Y_POSITION
                img = tools.watermark_file(image, finalWatermark, int(APPLY_WATERMARK_X_POSITION), int(APPLY_WATERMARK_Y_POSITION), False)
                build.append(img)
            add_to_changes(build)
            message_window("WATERMARK ADDED", "Watermark has been successfully applied.", 'info')
            close_window(WINDOW_TOOLS_WATERMARK)
            return
        else:
            message_window("NO WATERMARK LOADED", "You need to load your watermark first!", 'error')
    if cvui.button(FRAME_TOOLS_WATERMARK, 260, 450, 90, 40, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_TOOLS_WATERMARK)
        return

    cvui.imshow(WINDOW_TOOLS_WATERMARK, FRAME_TOOLS_WATERMARK)

def generate_interface_settings_colorfill():
    global FILTER_COLORFILL_FRAME, FILTER_COLORFILL_COLOR, FILTER_COLORFILL_COLOR_2, IAREA_COLORFILL_STATE, FILTER_COLORFILL_AMOUNT_LAST
    global FILTER_USE_COLORFILL_TYPE_1, FILTER_USE_COLORFILL_TYPE_2, FILTER_USE_COLORFILL_TYPE_3, FILTER_USE_COLORFILL_TYPE_4, FILTER_USE_COLORFILL_TYPE_5
    global FILTER_USE_COLORFILL_TYPE_6, FILTER_USE_COLORFILL_TYPE_7, FILTER_USE_COLORFILL_TYPE_8, FILTER_USE_COLORFILL_TYPE_9
    cvui.context(WINDOW_SETTINGS_COLORFILL)
    FRAME_SETTINGS_COLORFILL[:] = (30, 30, 30)
    FILTER_COLORFILL_FRAME = np.zeros((20, 20, 4), np.uint8)

    cvui.window(FRAME_SETTINGS_COLORFILL, 5, 5, 310, 410, 'COLORFILL SETTINGS', windowHeader, windowBody, windowText)
    if cvui.button(FRAME_SETTINGS_COLORFILL, 150, 160, 160, 50, 'COLOR PICKER...', buttonDefault, buttonOut, buttonOver, windowText):
        root = Tk()
        root.withdraw()
        FILTER_COLORFILL_COLOR = choose_color()
        test = list(FILTER_COLORFILL_COLOR)
        test2 = list(test[0])
        test2.append(255)
        test3 = tuple(test2)
        test[0] = test3
        FILTER_COLORFILL_COLOR = test

        root.destroy()
        cvui.update()

        if FILTER_COLORFILL_AMOUNT[0] < 1.0:
            FILTER_COLORFILL_AMOUNT[0] += 0.01
        else:
            FILTER_COLORFILL_AMOUNT[0] -= 0.01
    cvui.rect(FRAME_SETTINGS_COLORFILL, 10, 162, 128, 46, FILTER_COLORFILL_COLOR[1], FILTER_COLORFILL_COLOR[1])

    FILTER_COLORFILL_FRAME[:] = FILTER_COLORFILL_COLOR[0]
    IAREA_COLORFILL_STATE = cvui.iarea(0, 305, 300, 60)

    cvui.checkbox(FRAME_SETTINGS_COLORFILL, 10, 40, 'NORMAL', FILTER_USE_COLORFILL_TYPE_1, textColor)
    if FILTER_USE_COLORFILL_TYPE_1[0]:
        FILTER_USE_COLORFILL_TYPE_2 = [False]
        FILTER_USE_COLORFILL_TYPE_3 = [False]
        FILTER_USE_COLORFILL_TYPE_4 = [False]
        FILTER_USE_COLORFILL_TYPE_5 = [False]
        FILTER_USE_COLORFILL_TYPE_6 = [False]
        FILTER_USE_COLORFILL_TYPE_7 = [False]
        FILTER_USE_COLORFILL_TYPE_8 = [False]
        FILTER_USE_COLORFILL_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_COLORFILL, 110, 40, 'MULTIPLY', FILTER_USE_COLORFILL_TYPE_2, textColor)
    if FILTER_USE_COLORFILL_TYPE_2[0]:
        FILTER_USE_COLORFILL_TYPE_1 = [False]
        FILTER_USE_COLORFILL_TYPE_3 = [False]
        FILTER_USE_COLORFILL_TYPE_4 = [False]
        FILTER_USE_COLORFILL_TYPE_5 = [False]
        FILTER_USE_COLORFILL_TYPE_6 = [False]
        FILTER_USE_COLORFILL_TYPE_7 = [False]
        FILTER_USE_COLORFILL_TYPE_8 = [False]
        FILTER_USE_COLORFILL_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_COLORFILL, 215, 40, 'DARKEN', FILTER_USE_COLORFILL_TYPE_3, textColor)
    if FILTER_USE_COLORFILL_TYPE_3[0]:
        FILTER_USE_COLORFILL_TYPE_1 = [False]
        FILTER_USE_COLORFILL_TYPE_2 = [False]
        FILTER_USE_COLORFILL_TYPE_4 = [False]
        FILTER_USE_COLORFILL_TYPE_5 = [False]
        FILTER_USE_COLORFILL_TYPE_6 = [False]
        FILTER_USE_COLORFILL_TYPE_7 = [False]
        FILTER_USE_COLORFILL_TYPE_8 = [False]
        FILTER_USE_COLORFILL_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_COLORFILL, 10, 80, 'LIGHTEN', FILTER_USE_COLORFILL_TYPE_4, textColor)
    if FILTER_USE_COLORFILL_TYPE_4[0]:
        FILTER_USE_COLORFILL_TYPE_1 = [False]
        FILTER_USE_COLORFILL_TYPE_2 = [False]
        FILTER_USE_COLORFILL_TYPE_3 = [False]
        FILTER_USE_COLORFILL_TYPE_5 = [False]
        FILTER_USE_COLORFILL_TYPE_6 = [False]
        FILTER_USE_COLORFILL_TYPE_7 = [False]
        FILTER_USE_COLORFILL_TYPE_8 = [False]
        FILTER_USE_COLORFILL_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_COLORFILL, 110, 80, 'DODGE', FILTER_USE_COLORFILL_TYPE_5, textColor)
    if FILTER_USE_COLORFILL_TYPE_5[0]:
        FILTER_USE_COLORFILL_TYPE_1 = [False]
        FILTER_USE_COLORFILL_TYPE_2 = [False]
        FILTER_USE_COLORFILL_TYPE_3 = [False]
        FILTER_USE_COLORFILL_TYPE_4 = [False]
        FILTER_USE_COLORFILL_TYPE_6 = [False]
        FILTER_USE_COLORFILL_TYPE_7 = [False]
        FILTER_USE_COLORFILL_TYPE_8 = [False]
        FILTER_USE_COLORFILL_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_COLORFILL, 215, 80, 'OVERLAY', FILTER_USE_COLORFILL_TYPE_6, textColor)
    if FILTER_USE_COLORFILL_TYPE_6[0]:
        FILTER_USE_COLORFILL_TYPE_1 = [False]
        FILTER_USE_COLORFILL_TYPE_2 = [False]
        FILTER_USE_COLORFILL_TYPE_3 = [False]
        FILTER_USE_COLORFILL_TYPE_4 = [False]
        FILTER_USE_COLORFILL_TYPE_5 = [False]
        FILTER_USE_COLORFILL_TYPE_7 = [False]
        FILTER_USE_COLORFILL_TYPE_8 = [False]
        FILTER_USE_COLORFILL_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_COLORFILL, 10, 120, 'SOFT LIGHT', FILTER_USE_COLORFILL_TYPE_7, textColor)
    if FILTER_USE_COLORFILL_TYPE_7[0]:
        FILTER_USE_COLORFILL_TYPE_1 = [False]
        FILTER_USE_COLORFILL_TYPE_2 = [False]
        FILTER_USE_COLORFILL_TYPE_3 = [False]
        FILTER_USE_COLORFILL_TYPE_4 = [False]
        FILTER_USE_COLORFILL_TYPE_5 = [False]
        FILTER_USE_COLORFILL_TYPE_6 = [False]
        FILTER_USE_COLORFILL_TYPE_8 = [False]
        FILTER_USE_COLORFILL_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_COLORFILL, 110, 120, 'HARD LIGHT', FILTER_USE_COLORFILL_TYPE_8, textColor)
    if FILTER_USE_COLORFILL_TYPE_8[0]:
        FILTER_USE_COLORFILL_TYPE_1 = [False]
        FILTER_USE_COLORFILL_TYPE_2 = [False]
        FILTER_USE_COLORFILL_TYPE_3 = [False]
        FILTER_USE_COLORFILL_TYPE_4 = [False]
        FILTER_USE_COLORFILL_TYPE_5 = [False]
        FILTER_USE_COLORFILL_TYPE_6 = [False]
        FILTER_USE_COLORFILL_TYPE_7 = [False]
        FILTER_USE_COLORFILL_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_COLORFILL, 215, 120, 'DIFFERENCE', FILTER_USE_COLORFILL_TYPE_9, textColor)
    if FILTER_USE_COLORFILL_TYPE_9[0]:
        FILTER_USE_COLORFILL_TYPE_1 = [False]
        FILTER_USE_COLORFILL_TYPE_2 = [False]
        FILTER_USE_COLORFILL_TYPE_3 = [False]
        FILTER_USE_COLORFILL_TYPE_4 = [False]
        FILTER_USE_COLORFILL_TYPE_5 = [False]
        FILTER_USE_COLORFILL_TYPE_6 = [False]
        FILTER_USE_COLORFILL_TYPE_7 = [False]
        FILTER_USE_COLORFILL_TYPE_8 = [False]

    cvui.checkbox(FRAME_SETTINGS_COLORFILL, 10, 225, 'Use gradient fill', FILTER_USE_COLORFILL_GRADIENT, textColor)
    cvui.rect(FRAME_SETTINGS_COLORFILL, 180, 247, 128, 46, FILTER_COLORFILL_COLOR_2[1], FILTER_COLORFILL_COLOR_2[1])
    cvui.rect(FRAME_SETTINGS_COLORFILL, 7, 222, 306, 75, 0x585858)
    if cvui.button(FRAME_SETTINGS_COLORFILL, 10, 245, 120, 50, 'SECOND COLOR...', buttonDefault, buttonOut, buttonOver, windowText):
        root = Tk()
        root.withdraw()
        FILTER_COLORFILL_COLOR_2 = choose_color()
        test = list(FILTER_COLORFILL_COLOR_2)
        test2 = list(test[0])
        test2.append(255)
        test3 = tuple(test2)
        test[0] = test3
        FILTER_COLORFILL_COLOR_2 = test

        root.destroy()
        cvui.update()

        if FILTER_COLORFILL_AMOUNT[0] < 1.0:
            FILTER_COLORFILL_AMOUNT[0] += 0.01
        else:
            FILTER_COLORFILL_AMOUNT[0] -= 0.01

    if cvui.button(FRAME_SETTINGS_COLORFILL, 136, 245, 36, 50, 'SWAP', buttonDefault, buttonOut, buttonOver, windowText):
        temp = FILTER_COLORFILL_COLOR_2
        FILTER_COLORFILL_COLOR_2 = FILTER_COLORFILL_COLOR
        FILTER_COLORFILL_COLOR = temp
        if FILTER_COLORFILL_AMOUNT[0] < 1.0:
            FILTER_COLORFILL_AMOUNT[0] += 0.01
        else:
            FILTER_COLORFILL_AMOUNT[0] -= 0.01

    cvui.trackbar(FRAME_SETTINGS_COLORFILL, 25, 315, 270, FILTER_COLORFILL_AMOUNT, 0.0, 1.0, 1.0, '%.2Lf', cvui.TRACKBAR_DISCRETE, 0.01, windowText)
    if cvui.button(FRAME_SETTINGS_COLORFILL, 295, 330, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_COLORFILL_AMOUNT[0] < 1.0:
            FILTER_COLORFILL_AMOUNT[0] += 0.01
        else:
            FILTER_COLORFILL_AMOUNT[0] = 1.0
    if cvui.button(FRAME_SETTINGS_COLORFILL, 10, 330, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_COLORFILL_AMOUNT[0] > 0:
            FILTER_COLORFILL_AMOUNT[0] -= 0.01
        else:
            FILTER_COLORFILL_AMOUNT[0] = 0
    cvui.text(FRAME_SETTINGS_COLORFILL, 140, 315, 'opacity', 0.4, textColor)


    if cvui.button(FRAME_SETTINGS_COLORFILL, 10, 370, 90, 40, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_USE_COLORFILL_TYPE_1[0]:
            build = []
            for image in changesList[imagesVersion]:
                FILTER_COLORFILL_FRAME = np.zeros(image.shape, np.uint8)
                FILTER_COLORFILL_FRAME[:] = FILTER_COLORFILL_COLOR[0]
                img = filters.blend(image, FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 1, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0])
                build.append(img)
            add_to_changes(build)
        if FILTER_USE_COLORFILL_TYPE_2[0]:
            build = []
            for image in changesList[imagesVersion]:
                FILTER_COLORFILL_FRAME = np.zeros(image.shape, np.uint8)
                FILTER_COLORFILL_FRAME[:] = FILTER_COLORFILL_COLOR[0]
                img = filters.blend(image, FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 2, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0])
                build.append(img)
            add_to_changes(build)
        if FILTER_USE_COLORFILL_TYPE_3[0]:
            build = []
            for image in changesList[imagesVersion]:
                FILTER_COLORFILL_FRAME = np.zeros(image.shape, np.uint8)
                FILTER_COLORFILL_FRAME[:] = FILTER_COLORFILL_COLOR[0]
                img = filters.blend(image, FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 3, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0])
                build.append(img)
            add_to_changes(build)
        if FILTER_USE_COLORFILL_TYPE_4[0]:
            build = []
            for image in changesList[imagesVersion]:
                FILTER_COLORFILL_FRAME = np.zeros(image.shape, np.uint8)
                FILTER_COLORFILL_FRAME[:] = FILTER_COLORFILL_COLOR[0]
                img = filters.blend(image, FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 4, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0])
                build.append(img)
            add_to_changes(build)
        if FILTER_USE_COLORFILL_TYPE_5[0]:
            build = []
            for image in changesList[imagesVersion]:
                FILTER_COLORFILL_FRAME = np.zeros(image.shape, np.uint8)
                FILTER_COLORFILL_FRAME[:] = FILTER_COLORFILL_COLOR[0]
                img = filters.blend(image, FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 5, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0])
                build.append(img)
            add_to_changes(build)
        if FILTER_USE_COLORFILL_TYPE_6[0]:
            build = []
            for image in changesList[imagesVersion]:
                FILTER_COLORFILL_FRAME = np.zeros(image.shape, np.uint8)
                FILTER_COLORFILL_FRAME[:] = FILTER_COLORFILL_COLOR[0]
                img = filters.blend(image, FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 6, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0])
                build.append(img)
            add_to_changes(build)
        if FILTER_USE_COLORFILL_TYPE_7[0]:
            build = []
            for image in changesList[imagesVersion]:
                FILTER_COLORFILL_FRAME = np.zeros(image.shape, np.uint8)
                FILTER_COLORFILL_FRAME[:] = FILTER_COLORFILL_COLOR[0]
                img = filters.blend(image, FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 7, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0])
                build.append(img)
            add_to_changes(build)
        if FILTER_USE_COLORFILL_TYPE_8[0]:
            build = []
            for image in changesList[imagesVersion]:
                FILTER_COLORFILL_FRAME = np.zeros(image.shape, np.uint8)
                FILTER_COLORFILL_FRAME[:] = FILTER_COLORFILL_COLOR[0]
                img = filters.blend(image, FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 8, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0])
                build.append(img)
            add_to_changes(build)
        if FILTER_USE_COLORFILL_TYPE_9[0]:
            build = []
            for image in changesList[imagesVersion]:
                FILTER_COLORFILL_FRAME = np.zeros(image.shape, np.uint8)
                FILTER_COLORFILL_FRAME[:] = FILTER_COLORFILL_COLOR[0]
                img = filters.blend(image, FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 9, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0])
                build.append(img)
            add_to_changes(build)

        FILTER_USE_COLORFILL_TYPE_1 = [False]
        FILTER_USE_COLORFILL_TYPE_2 = [False]
        FILTER_USE_COLORFILL_TYPE_3 = [False]
        FILTER_USE_COLORFILL_TYPE_4 = [False]
        FILTER_USE_COLORFILL_TYPE_5 = [False]
        FILTER_USE_COLORFILL_TYPE_6 = [False]
        FILTER_USE_COLORFILL_TYPE_7 = [False]
        FILTER_USE_COLORFILL_TYPE_8 = [False]
        FILTER_USE_COLORFILL_TYPE_9 = [False]

    if cvui.button(FRAME_SETTINGS_COLORFILL, 220, 370, 90, 40, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_COLORFILL)
        return

    cvui.imshow(WINDOW_SETTINGS_COLORFILL, FRAME_SETTINGS_COLORFILL)

def generate_interface_tools_sticker():
    global STICKER_SCALE_AMOUNT, temp_stickerPath, isStickerLoaded, STICKER_USE_LEFT_UPPER, STICKER_USE_RIGHT_UPPER, STICKER_USE_LEFT_DOWN, STICKER_USE_RIGHT_DOWN
    global STICKER_X_POSITION, STICKER_Y_POSITION, finalSticker, stickersCurrent, stickersImages
    APPLY_STICKER_X_POSITION = 0
    APPLY_STICKER_Y_POSITION = 0
    APPLY_OFFSET_X_POSITION = 0
    APPLY_OFFSET_Y_POSITION = 0
    cvui.context(WINDOW_TOOLS_STICKER)
    FRAME_TOOLS_STICKER[:] = frameColor1
    cvui.window(FRAME_TOOLS_STICKER, 5, 5, 370, 615, 'STICKER SETTINGS', windowHeader, windowBody, windowText)

    finalSticker = stickersImages[stickersCurrent]


    finalSticker = cv2.cvtColor(finalSticker, cv2.COLOR_BGRA2RGBA)
    h, w, _ = changesList[imagesVersion][imagesCurrent].shape
    finalSticker = imutils.rotate(finalSticker, angle=STICKER_ROTATE_AMOUNT[0])

    temp_Sticker = Image.fromarray(finalSticker, 'RGBA')
    width, height = temp_Sticker.size
    final_sticker_height = int((height * STICKER_SCALE_AMOUNT[0])/100)
    final_sticker_width = int((width * STICKER_SCALE_AMOUNT[0])/100)
    test = temp_Sticker.resize((final_sticker_width, final_sticker_height), Image.BICUBIC)
    finalSticker = np.array(test)


    cvui.rect(FRAME_TOOLS_STICKER, 85, 35, 200, 200, 0x515A5A)

    if cvui.button(FRAME_TOOLS_STICKER, 30, 35, 50, 200, '<-' , buttonDefault, buttonOut, buttonOver, windowText):
        if stickersCurrent > 0:
            stickersCurrent -= 1

    cvui.text(FRAME_TOOLS_STICKER, 160, 245, f'{stickersCurrent+1}/{len(stickersImages)}', 0.4, textColor)

    if cvui.button(FRAME_TOOLS_STICKER, 290, 35, 50, 200, '->', buttonDefault, buttonOut, buttonOver, windowText):
        if stickersCurrent < len(stickersImages) - 1:
            stickersCurrent += 1

    ##PREVIEW OF STICKER##
    temp_pillow_image = Image.fromarray(cv2.cvtColor(stickersImages[stickersCurrent], cv2.COLOR_BGRA2RGBA))
    temp_pillow_image.thumbnail((199, 199))
    temp_background = Image.new("RGB", temp_pillow_image.size, (50,50,50))
    temp_background.paste(temp_pillow_image, (0, 0), temp_pillow_image)
    temp_background.convert('RGB')
    temp_sticker_array = np.array(temp_background)
    final_temp_sticker = cv2.cvtColor(temp_sticker_array, cv2.COLOR_RGB2BGR)

    x, y = centering_image(final_temp_sticker, 200, 200, 86, 36)
    cvui.image(FRAME_TOOLS_STICKER, x, y, final_temp_sticker)

    ##PREDEFINIED POSITIONS OF STICKER##
    cvui.rect(FRAME_TOOLS_STICKER, 95, 270, 180, 84, 0xffffff)

    if cvui.button(FRAME_TOOLS_STICKER, 96, 272, 80, 30, 'TOP-LEFT', buttonDefault, buttonOut, buttonOver, windowText):
            STICKER_X_POSITION = 20
            STICKER_Y_POSITION = 20
    if cvui.button(FRAME_TOOLS_STICKER, 194, 272, 80, 30, 'TOP-RIGHT', buttonDefault, buttonOut, buttonOver, windowText):
            STICKER_X_POSITION = w - final_sticker_width - 20
            STICKER_Y_POSITION = 20
    if cvui.button(FRAME_TOOLS_STICKER, 96, 322, 80, 30, 'BOT-LEFT', buttonDefault, buttonOut, buttonOver, windowText):
            STICKER_X_POSITION = 20
            STICKER_Y_POSITION = h - final_sticker_height - 20
    if cvui.button(FRAME_TOOLS_STICKER, 194, 322, 80, 30,'BOT-RIGHT', buttonDefault, buttonOut, buttonOver, windowText):
            STICKER_X_POSITION = w - final_sticker_width - 20
            STICKER_Y_POSITION = h - final_sticker_height - 20
    cvui.text(FRAME_TOOLS_STICKER, 157, 307, 'POSITION', 0.4, textColor)

    if cvui.button(FRAME_TOOLS_STICKER, 155, 360, 60, 30, 'UP', buttonDefault, buttonOut, buttonOver, windowText):
            STICKER_Y_POSITION -= 5
    if cvui.button(FRAME_TOOLS_STICKER, 215, 395, 60, 30, 'RIGHT', buttonDefault, buttonOut, buttonOver, windowText):
            STICKER_X_POSITION += 5
    if cvui.button(FRAME_TOOLS_STICKER, 95, 395, 60, 30, 'LEFT', buttonDefault, buttonOut, buttonOver, windowText):
            STICKER_X_POSITION -= 5
    if cvui.button(FRAME_TOOLS_STICKER, 155, 430, 60, 30, 'BOTTOM', buttonDefault, buttonOut, buttonOver, windowText):
            STICKER_Y_POSITION += 5
    cvui.text(FRAME_TOOLS_STICKER, 169, 405, 'MOVE', 0.4, textColor)

    ##ROTATE TRACKBAR OF STICKER##
    cvui.text(FRAME_TOOLS_STICKER, 145, 475, "%rotate sticker", 0.4, textColor)
    cvui.trackbar(FRAME_TOOLS_STICKER, 25, 475, 330, STICKER_ROTATE_AMOUNT, 0, 360, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    if cvui.button(FRAME_TOOLS_STICKER, 355, 490, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if STICKER_ROTATE_AMOUNT[0] < 360:
            STICKER_ROTATE_AMOUNT[0] = STICKER_ROTATE_AMOUNT[0] + 1
    if cvui.button(FRAME_TOOLS_STICKER, 10, 490, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if STICKER_ROTATE_AMOUNT[0] > 0:
            STICKER_ROTATE_AMOUNT[0] = STICKER_ROTATE_AMOUNT[0] - 1

    ##SCALING TRACKBAR OF STICKER##
    cvui.text(FRAME_TOOLS_STICKER, 145, 525, "%scale sticker", 0.4, textColor)
    cvui.trackbar(FRAME_TOOLS_STICKER, 25, 525, 330, STICKER_SCALE_AMOUNT, 1, 200, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    if cvui.button(FRAME_TOOLS_STICKER, 355, 540, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if STICKER_SCALE_AMOUNT[0] < 200:
            STICKER_SCALE_AMOUNT[0] = STICKER_SCALE_AMOUNT[0] + 1
    if cvui.button(FRAME_TOOLS_STICKER, 10, 540, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if STICKER_SCALE_AMOUNT[0] > 1:
            STICKER_SCALE_AMOUNT[0] = STICKER_SCALE_AMOUNT[0] - 1

    if cvui.button(FRAME_TOOLS_STICKER, 10, 575, 90, 40, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):
        build = []
        for image in changesList[imagesVersion]:
            new_h, new_w, _ = image.shape
            APPLY_OFFSET_X_POSITION = new_w / w
            APPLY_OFFSET_Y_POSITION = new_h / h
            APPLY_STICKER_X_POSITION = STICKER_X_POSITION * APPLY_OFFSET_X_POSITION
            APPLY_STICKER_Y_POSITION = STICKER_Y_POSITION * APPLY_OFFSET_Y_POSITION
            img = tools.watermark_file(image, finalSticker, int(APPLY_STICKER_X_POSITION), int(APPLY_STICKER_Y_POSITION), True)
            build.append(img)
            add_to_changes(build)

            message_window("STICKER ADDED", "Sticker has been successfully applied.", 'info')
            close_window(WINDOW_TOOLS_STICKER)
            return
    if cvui.button(FRAME_TOOLS_STICKER, 280, 575, 90, 40, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_TOOLS_STICKER)
        return

    cvui.imshow(WINDOW_TOOLS_STICKER, FRAME_TOOLS_STICKER)

def generate_interface_tools_transformations():
    cvui.context(WINDOW_TOOLS_TRANSFORMATIONS)
    FRAME_TOOLS_TRANSFORMATIONS[:] = frameColor1
    cvui.window(FRAME_TOOLS_TRANSFORMATIONS, 5, 5, 290, 450, 'TRANSFORMATIONS SETTINGS', windowHeader, windowBody, windowText)

    if isLightModeActive == False:
        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 10, 30, cv2.imread('Graphics/-901.png'), cv2.imread('Graphics/-902.png'), cv2.imread('Graphics/-903.png')):
            build = []
            for image in changesList[imagesVersion]:
                img = tools.rotate_90_clockwise(image)
                build.append(img)
            add_to_changes(build, f'tools.rotate_90_clockwise(image)')

        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 85, 30, cv2.imread('Graphics/901.png'), cv2.imread('Graphics/902.png'), cv2.imread('Graphics/903.png')):
            build = []
            for image in changesList[imagesVersion]:
                img = tools.rotate_90_counterclockwise(image)
                build.append(img)
            add_to_changes(build, f'tools.rotate_90_counterclockwise(image)')

        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 160, 30, cv2.imread('Graphics/vert1.png'), cv2.imread('Graphics/vert2.png'), cv2.imread('Graphics/vert3.png')):
            build = []
            for image in changesList[imagesVersion]:
                img = tools.flip_vertical(image)
                build.append(img)
            add_to_changes(build, f'tools.flip_vertical(image)')

        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 160, 90, cv2.imread('Graphics/horiz1.png'), cv2.imread('Graphics/horiz2.png'), cv2.imread('Graphics/horiz3.png')):
            build = []
            for image in changesList[imagesVersion]:
                img = tools.flip_horizontal(image)
                build.append(img)
            add_to_changes(build, f'tools.flip_horizontal(image)')

        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 10, 90, cv2.imread('Graphics/1801.png'), cv2.imread('Graphics/1802.png'), cv2.imread('Graphics/1803.png')):
            build = []
            for image in changesList[imagesVersion]:
                img = tools.rotate_180(image)
                build.append(img)
            add_to_changes(build, f'tools.rotate_180(image)')

        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 8, 150, cv2.imread('Graphics/crop1.png'), cv2.imread('Graphics/crop2.png'), cv2.imread('Graphics/crop3.png')):
            if isBatchModeActive == False:
                imageToResize = Image.fromarray(changesList[imagesVersion][imagesCurrent], 'RGBA')
                imageToResize.thumbnail((1100, 713))
                resizedImage = np.array(imageToResize)

                (cropH1, cropW1) = changesList[imagesVersion][imagesCurrent].shape[:2]
                (cropH2, cropW2) = resizedImage.shape[:2]
                cropH = cropH1/cropH2
                cropW = cropW1/cropW2

                roi = cv2.selectROI('WIN', resizedImage, True)
                close_window('WIN')

                if roi != (0, 0 ,0 ,0):
                    build = []
                    for image in changesList[imagesVersion]:
                        img = tools.crop(image, roi, cropH, cropW)
                        build.append(img)
                    add_to_changes(build)
                else:
                    message_window("NO CROP AREA", "Crop area was not selected.", 'info')
                    pass
            else:
                message_window("CROP UNAVAIABLE IN BATCH MODE", "Crop is unavaiable in batch edition mode.", 'warning')
                pass
    else:
        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 10, 30, cv2.imread('Graphics/-901_light.png'), cv2.imread('Graphics/-902_light.png'), cv2.imread('Graphics/-903_light.png')):
            build = []
            for image in changesList[imagesVersion]:
                img = tools.rotate_90_clockwise(image)
                build.append(img)
            add_to_changes(build, f'tools.rotate_90_clockwise(image)')

        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 85, 30, cv2.imread('Graphics/901_light.png'), cv2.imread('Graphics/902_light.png'), cv2.imread('Graphics/903_light.png')):
            build = []
            for image in changesList[imagesVersion]:
                img = tools.rotate_90_counterclockwise(image)
                build.append(img)
            add_to_changes(build, f'tools.rotate_90_counterclockwise(image)')

        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 160, 30, cv2.imread('Graphics/vert1_light.png'), cv2.imread('Graphics/vert2_light.png'), cv2.imread('Graphics/vert3_light.png')):
            build = []
            for image in changesList[imagesVersion]:
                img = tools.flip_vertical(image)
                build.append(img)
            add_to_changes(build, f'tools.flip_vertical(image)')

        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 160, 90, cv2.imread('Graphics/horiz1_light.png'), cv2.imread('Graphics/horiz2_light.png'), cv2.imread('Graphics/horiz3_light.png')):
            build = []
            for image in changesList[imagesVersion]:
                img = tools.flip_horizontal(image)
                build.append(img)
            add_to_changes(build, f'tools.flip_horizontal(image)')

        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 10, 90, cv2.imread('Graphics/1801_light.png'), cv2.imread('Graphics/1802_light.png'), cv2.imread('Graphics/1803_light.png')):
            build = []
            for image in changesList[imagesVersion]:
                img = tools.rotate_180(image)
                build.append(img)
            add_to_changes(build, f'tools.rotate_180(image)')

        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 8, 150, cv2.imread('Graphics/crop1_light.png'), cv2.imread('Graphics/crop2_light.png'), cv2.imread('Graphics/crop3_light.png')):
            if isBatchModeActive == False:
                imageToResize = Image.fromarray(changesList[imagesVersion][imagesCurrent], 'RGBA')
                imageToResize.thumbnail((1100, 713))
                resizedImage = np.array(imageToResize)

                (cropH1, cropW1) = changesList[imagesVersion][imagesCurrent].shape[:2]
                (cropH2, cropW2) = resizedImage.shape[:2]
                cropH = cropH1/cropH2
                cropW = cropW1/cropW2

                roi = cv2.selectROI('WIN', resizedImage, True)
                close_window('WIN')

                if roi != (0, 0 ,0 ,0):
                    build = []
                    for image in changesList[imagesVersion]:
                        img = tools.crop(image, roi, cropH, cropW)
                        build.append(img)
                    add_to_changes(build)
                else:
                    message_window("NO CROP AREA", "Crop area was not selected.", 'info')
                    pass
            else:
                message_window("CROP UNAVAIABLE IN BATCH MODE", "Crop is unavaiable in batch edition mode.", 'warning')
                pass

    cvui.checkbox(FRAME_TOOLS_TRANSFORMATIONS, 200, 305, 'Keep ratio', TRANSFORMATIONS_USE_RATIO, textColor)
    cvui.text(FRAME_TOOLS_TRANSFORMATIONS, 78, 271, '%width', 0.4, textColor)
    cvui.text(FRAME_TOOLS_TRANSFORMATIONS, 74, 321, '%height', 0.4, textColor)
    if TRANSFORMATIONS_USE_RATIO[0] == True:
        cvui.trackbar(FRAME_TOOLS_TRANSFORMATIONS, 25, 270, 150, TRANSFORMATIONS_SCALE_AMOUNT_X, 0.01, 2, 0.01, '%.2Lf', cvui.TRACKBAR_DISCRETE, 0.01, windowText)
        cvui.trackbar(FRAME_TOOLS_TRANSFORMATIONS, 25, 320, 150, TRANSFORMATIONS_SCALE_AMOUNT_X, 0.01, 2, 0.01, '%.2Lf', cvui.TRACKBAR_DISCRETE, 0.01, windowText)

        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 175, 305, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
            if TRANSFORMATIONS_SCALE_AMOUNT_X[0] < 2:
                TRANSFORMATIONS_SCALE_AMOUNT_X[0] = TRANSFORMATIONS_SCALE_AMOUNT_X[0] + 0.01
                TRANSFORMATIONS_SCALE_AMOUNT_Y[0] = TRANSFORMATIONS_SCALE_AMOUNT_X[0] + 0.01
        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 10, 305, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
            if TRANSFORMATIONS_SCALE_AMOUNT_X[0] > 0.01:
                TRANSFORMATIONS_SCALE_AMOUNT_X[0] = TRANSFORMATIONS_SCALE_AMOUNT_X[0] - 0.01
                TRANSFORMATIONS_SCALE_AMOUNT_Y[0] = TRANSFORMATIONS_SCALE_AMOUNT_X[0] - 0.01

    else:
        cvui.trackbar(FRAME_TOOLS_TRANSFORMATIONS, 25, 270, 150, TRANSFORMATIONS_SCALE_AMOUNT_X, 0.01, 2, 0.01, '%.2Lf', cvui.TRACKBAR_DISCRETE, 0.01, windowText)
        cvui.trackbar(FRAME_TOOLS_TRANSFORMATIONS, 25, 320, 150, TRANSFORMATIONS_SCALE_AMOUNT_Y, 0.01, 2, 0.01, '%.2Lf', cvui.TRACKBAR_DISCRETE, 0.01, windowText)

        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 175, 285, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
            if TRANSFORMATIONS_SCALE_AMOUNT_X[0] < 2:
                TRANSFORMATIONS_SCALE_AMOUNT_X[0] = TRANSFORMATIONS_SCALE_AMOUNT_X[0] + 0.01
        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 10, 285, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
            if TRANSFORMATIONS_SCALE_AMOUNT_X[0] > 0.01:
                TRANSFORMATIONS_SCALE_AMOUNT_X[0] = TRANSFORMATIONS_SCALE_AMOUNT_X[0] - 0.01

        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 175, 335, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
            if TRANSFORMATIONS_SCALE_AMOUNT_Y[0] < 2:
                TRANSFORMATIONS_SCALE_AMOUNT_Y[0] = TRANSFORMATIONS_SCALE_AMOUNT_Y[0] + 0.01
        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 10, 335, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
            if TRANSFORMATIONS_SCALE_AMOUNT_Y[0] > 0.01:
                TRANSFORMATIONS_SCALE_AMOUNT_Y[0] = TRANSFORMATIONS_SCALE_AMOUNT_Y[0] - 0.01

    if isLightModeActive == False:
        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 8, 210, cv2.imread('Graphics/scale1.png'), cv2.imread('Graphics/scale2.png'), cv2.imread('Graphics/scale3.png')):
            if TRANSFORMATIONS_USE_RATIO[0] == True:
                build = []
                for image in changesList[imagesVersion]:
                    img = tools.scale(image, TRANSFORMATIONS_SCALE_AMOUNT_X, TRANSFORMATIONS_SCALE_AMOUNT_X)
                    build.append(img)
                add_to_changes(build)
            else:
                build = []
                for image in changesList[imagesVersion]:
                    img = tools.scale(image, TRANSFORMATIONS_SCALE_AMOUNT_X, TRANSFORMATIONS_SCALE_AMOUNT_Y)
                    build.append(img)
                add_to_changes(build)
    else:
        if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 8, 210, cv2.imread('Graphics/scale1_light.png'), cv2.imread('Graphics/scale2_light.png'), cv2.imread('Graphics/scale3_light.png')):
            if TRANSFORMATIONS_USE_RATIO[0] == True:
                build = []
                for image in changesList[imagesVersion]:
                    img = tools.scale(image, TRANSFORMATIONS_SCALE_AMOUNT_X, TRANSFORMATIONS_SCALE_AMOUNT_X)
                    build.append(img)
                add_to_changes(build)
            else:
                build = []
                for image in changesList[imagesVersion]:
                    img = tools.scale(image, TRANSFORMATIONS_SCALE_AMOUNT_X, TRANSFORMATIONS_SCALE_AMOUNT_Y)
                    build.append(img)
                add_to_changes(build)

    w1 = int(w*TRANSFORMATIONS_SCALE_AMOUNT_X[0])
    h1 = int(h*TRANSFORMATIONS_SCALE_AMOUNT_Y[0])

    cvui.text(FRAME_TOOLS_TRANSFORMATIONS, 10, 380, "Before: " + str(w) + " X " + str(h), 0.4, textColor)
    cvui.text(FRAME_TOOLS_TRANSFORMATIONS, 10, 400, "After:   " + str(w1) + " X " + str(h1), 0.4, textColor)

    if cvui.button(FRAME_TOOLS_TRANSFORMATIONS, 100, 420, 100, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_TOOLS_TRANSFORMATIONS)
        return

    cvui.imshow(WINDOW_TOOLS_TRANSFORMATIONS, FRAME_TOOLS_TRANSFORMATIONS)

def generate_interface_tools_upscale():
    global imageCopy, imageVersion, imagePath, UPSCALE_USE_TYPE_AMOUNT
    global UPSCALE_USE_AMOUNT, UPSCALE_USE_TYPE_CHOICE_1
    global UPSCALE_USE_TYPE_CHOICE_2, UPSCALE_USE_TYPE_CHOICE_3, UPSCALE_USE_TYPE_CHOICE_4, UPSCALE_USE_TYPE_CHOICE_5, UPSCALE_USE_TYPE_CHOICE_6
    cvui.context(WINDOW_TOOLS_UPSCALE)
    FRAME_TOOLS_UPSCALE[:] = frameColor1
    cvui.window(FRAME_TOOLS_UPSCALE, 5, 5, 230, 270, 'UPSCALE SETTINGS', windowHeader, windowBody, windowText)

    cvui.text(FRAME_TOOLS_UPSCALE, 10, 35, "UPSCALE AMOUNT", 0.4, textColor)
    if cvui.button(FRAME_TOOLS_UPSCALE, 10, 60, 100, 30, 'Input UPSCALE', buttonDefault, buttonOut, buttonOver, windowText):
        root = Tk()
        root.withdraw()
        UPSCALE_USE_AMOUNT = simpledialog.askinteger("Input", "UPSCALE X AMOUNT")
        if UPSCALE_USE_AMOUNT > 16:
            UPSCALE_USE_AMOUNT = 16
        elif UPSCALE_USE_AMOUNT < 2:
            UPSCALE_USE_AMOUNT = 2
        root.destroy()
        cvui.update()

    cvui.rect(FRAME_TOOLS_UPSCALE, 10, 100, 100, 20, 0x515A5A)
    cvui.text(FRAME_TOOLS_UPSCALE, 45, 105, "x", 0.4, textColor)
    cvui.text(FRAME_TOOLS_UPSCALE, 55, 105, str(UPSCALE_USE_AMOUNT), 0.4, textColor)

    cvui.text(FRAME_TOOLS_UPSCALE, 150, 35, "ALGORITHM", 0.4, textColor)
    cvui.checkbox(FRAME_TOOLS_UPSCALE, 150, 55, 'Nearest', UPSCALE_USE_TYPE_CHOICE_1, textColor)
    if UPSCALE_USE_TYPE_CHOICE_1[0]:
        UPSCALE_USE_TYPE_AMOUNT = 0
        UPSCALE_USE_TYPE_CHOICE_2 = [False]
        UPSCALE_USE_TYPE_CHOICE_3 = [False]
        UPSCALE_USE_TYPE_CHOICE_4 = [False]
        UPSCALE_USE_TYPE_CHOICE_5 = [False]
        UPSCALE_USE_TYPE_CHOICE_6 = [False]

    cvui.checkbox(FRAME_TOOLS_UPSCALE, 150, 85, 'Box', UPSCALE_USE_TYPE_CHOICE_2, textColor)
    if UPSCALE_USE_TYPE_CHOICE_2[0]:
        UPSCALE_USE_TYPE_AMOUNT = 1
        UPSCALE_USE_TYPE_CHOICE_1 = [False]
        UPSCALE_USE_TYPE_CHOICE_3 = [False]
        UPSCALE_USE_TYPE_CHOICE_4 = [False]
        UPSCALE_USE_TYPE_CHOICE_5 = [False]
        UPSCALE_USE_TYPE_CHOICE_6 = [False]

    cvui.checkbox(FRAME_TOOLS_UPSCALE, 150, 115, 'Bilinear', UPSCALE_USE_TYPE_CHOICE_3, textColor)
    if UPSCALE_USE_TYPE_CHOICE_3[0]:
        UPSCALE_USE_TYPE_AMOUNT = 2
        UPSCALE_USE_TYPE_CHOICE_1 = [False]
        UPSCALE_USE_TYPE_CHOICE_2 = [False]
        UPSCALE_USE_TYPE_CHOICE_4 = [False]
        UPSCALE_USE_TYPE_CHOICE_5 = [False]
        UPSCALE_USE_TYPE_CHOICE_6 = [False]

    cvui.checkbox(FRAME_TOOLS_UPSCALE, 150, 145, 'Hamming', UPSCALE_USE_TYPE_CHOICE_4, textColor)
    if UPSCALE_USE_TYPE_CHOICE_4[0]:
        UPSCALE_USE_TYPE_AMOUNT = 3
        UPSCALE_USE_TYPE_CHOICE_1 = [False]
        UPSCALE_USE_TYPE_CHOICE_2 = [False]
        UPSCALE_USE_TYPE_CHOICE_3 = [False]
        UPSCALE_USE_TYPE_CHOICE_5 = [False]
        UPSCALE_USE_TYPE_CHOICE_6 = [False]

    cvui.checkbox(FRAME_TOOLS_UPSCALE, 150, 175, 'Bicubic', UPSCALE_USE_TYPE_CHOICE_5, textColor)
    if UPSCALE_USE_TYPE_CHOICE_5[0]:
        UPSCALE_USE_TYPE_AMOUNT = 4
        UPSCALE_USE_TYPE_CHOICE_1 = [False]
        UPSCALE_USE_TYPE_CHOICE_2 = [False]
        UPSCALE_USE_TYPE_CHOICE_3 = [False]
        UPSCALE_USE_TYPE_CHOICE_4 = [False]
        UPSCALE_USE_TYPE_CHOICE_6 = [False]

    cvui.checkbox(FRAME_TOOLS_UPSCALE, 150, 205, 'Lanczos', UPSCALE_USE_TYPE_CHOICE_6, textColor)
    if UPSCALE_USE_TYPE_CHOICE_6[0]:
        UPSCALE_USE_TYPE_AMOUNT = 5
        UPSCALE_USE_TYPE_CHOICE_1 = [False]
        UPSCALE_USE_TYPE_CHOICE_2 = [False]
        UPSCALE_USE_TYPE_CHOICE_3 = [False]
        UPSCALE_USE_TYPE_CHOICE_4 = [False]
        UPSCALE_USE_TYPE_CHOICE_5 = [False]

    if cvui.button(FRAME_TOOLS_UPSCALE, 10, 240, 60, 30, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):
            build = []
            for image in changesList[imagesVersion]:
                img = tools.upscale(image, UPSCALE_USE_AMOUNT, UPSCALE_USE_TYPE_AMOUNT)
                build.append(img)
            add_to_changes(build)

    if cvui.button(FRAME_TOOLS_UPSCALE, 170, 240, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_TOOLS_UPSCALE)
        return

    cvui.imshow(WINDOW_TOOLS_UPSCALE, FRAME_TOOLS_UPSCALE)

def generate_interface_filters_normalization():
    global NORMALIZATION_USE_EQUALIZE, NORMALIZATION_USE_AUTOCONTRAST, NORMALIZATION_USE_PRESERVETONE
    cvui.context(WINDOW_FILTERS_NORMALIZATION)
    FRAME_FILTERS_NORMALIZATION[:] = frameColor1
    cvui.window(FRAME_FILTERS_NORMALIZATION, 5, 5, 260, 150, 'NORMALIZATION SETTINGS', windowHeader, windowBody, windowText)

    cvui.checkbox(FRAME_FILTERS_NORMALIZATION, 15, 35, 'Equalize', NORMALIZATION_USE_EQUALIZE, textColor)
    if NORMALIZATION_USE_EQUALIZE[0]:
        NORMALIZATION_USE_AUTOCONTRAST = [False]
        NORMALIZATION_USE_PRESERVETONE = [False]

    cvui.checkbox(FRAME_FILTERS_NORMALIZATION, 140, 35, 'Auto-contrast', NORMALIZATION_USE_AUTOCONTRAST, textColor)
    cvui.checkbox(FRAME_FILTERS_NORMALIZATION, 150, 60, 'Preserve Tone', NORMALIZATION_USE_PRESERVETONE, textColor)
    if NORMALIZATION_USE_AUTOCONTRAST[0]:
        NORMALIZATION_USE_EQUALIZE = [False]
    else:
        NORMALIZATION_USE_PRESERVETONE = [False]

    if cvui.button(FRAME_FILTERS_NORMALIZATION, 10, 120, 60, 30, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):
        if NORMALIZATION_USE_EQUALIZE[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.histogram_normalization(image)
                build.append(img)
            add_to_changes(build, f'filters.histogram_normalization(image)')
        if NORMALIZATION_USE_AUTOCONTRAST[0]:
            if NORMALIZATION_USE_PRESERVETONE[0]:
                build = []
                for image in changesList[imagesVersion]:
                    img = filters.histogram_autocontrast(image, True)
                    build.append(img)
                add_to_changes(build, f'filters.histogram_autocontrast(image, {True})')
            else:
                build = []
                for image in changesList[imagesVersion]:
                    img = filters.histogram_autocontrast(image, False)
                    build.append(img)
                add_to_changes(build, f'filters.histogram_autocontrast(image, {False})')
                NORMALIZATION_USE_EQUALIZE = [False]
        NORMALIZATION_USE_PRESERVETONE = [False]
        NORMALIZATION_USE_EQUALIZE = [False]
        NORMALIZATION_USE_AUTOCONTRAST = [False]
    if cvui.button(FRAME_FILTERS_NORMALIZATION, 95, 120, 80, 30, 'HISTOGRAM', buttonDefault, buttonOut, buttonOver, windowText):
        tools.histogram(changesList[imagesVersion][imagesCurrent])
    if cvui.button(FRAME_FILTERS_NORMALIZATION, 200, 120, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_FILTERS_NORMALIZATION)
        return

    cvui.imshow(WINDOW_FILTERS_NORMALIZATION, FRAME_FILTERS_NORMALIZATION)

def generate_interface_settings_pix():
    global FILTER_USE_PIX
    cvui.context(WINDOW_SETTINGS_PIX)
    FRAME_SETTINGS_PIX[:] = frameColor1
    cvui.window(FRAME_SETTINGS_PIX, 5, 5, 240, 155, 'PIXELIZATION SETTINGS', windowHeader, windowBody, windowText)

    cvui.checkbox(FRAME_SETTINGS_PIX, 10, 30, 'Pixelization', FILTER_USE_PIX, textColor)
    cvui.text(FRAME_SETTINGS_PIX, 100, 55, 'strength', 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_PIX, 25, 55, 200, FILTER_PIX_AMOUNT, 1, 5, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    if cvui.button(FRAME_SETTINGS_PIX, 225, 70, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_PIX_AMOUNT[0] < 5:
            FILTER_PIX_AMOUNT[0] = FILTER_PIX_AMOUNT[0] + 1
    if cvui.button(FRAME_SETTINGS_PIX, 10, 70, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_PIX_AMOUNT[0] > 1:
            FILTER_PIX_AMOUNT[0] = FILTER_PIX_AMOUNT[0] - 1

    if cvui.button(FRAME_SETTINGS_PIX, 10, 125, 60, 30, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText) and FILTER_USE_PIX[0] == True:
        build = []
        for image in changesList[imagesVersion]:
            img = filters.pix(image, FILTER_PIX_AMOUNT[0])
            build.append(img)
        add_to_changes(build, f'filters.pix(image, {FILTER_PIX_AMOUNT[0]})')

        FILTER_USE_PIX = [False]
    if cvui.button(FRAME_SETTINGS_PIX, 180, 125, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_PIX)
        return

    cvui.imshow(WINDOW_SETTINGS_PIX, FRAME_SETTINGS_PIX)

def generate_interface_settings_frame():
    global FILTER_USE_FRAME, FILTER_FRAME_COLOR, FILTER_FRAME_AMOUNT
    cvui.context(WINDOW_SETTINGS_FRAME)
    FRAME_SETTINGS_FRAME[:] = frameColor1
    cvui.window(FRAME_SETTINGS_FRAME, 5, 5, 265, 260, 'FRAME SETTINGS', windowHeader, windowBody, windowText)

    cvui.checkbox(FRAME_SETTINGS_FRAME, 10, 30, 'Use Frame', FILTER_USE_FRAME, textColor)
    if cvui.button(FRAME_SETTINGS_FRAME, 15, 50, 134, 45, 'COLOR PICKER...', buttonDefault, buttonOut, buttonOver, windowText):
        root = Tk()
        root.withdraw()
        FILTER_FRAME_COLOR = choose_color()
        ## CREATING LIST FROM TUPLE COLOR
        test = list(FILTER_FRAME_COLOR)
        ## CREATING LIST FROM BGR TUPLE
        test2 = list(test[0])
        ## ADDING FOURTH CHANNEL TO BGR
        test2.append(255)
        ## CONVERTING BACK
        test3 = tuple(test2)
        ## CHANGING BGR TO BGRA FROM INITIAL LIST
        test[0] = test3
        ## GOING BACK TO CVUI NAMES
        FILTER_FRAME_COLOR = test

        root.destroy()
        cvui.update()
    cvui.rect(FRAME_SETTINGS_FRAME, 158, 52, 98, 41, FILTER_FRAME_COLOR[1], FILTER_FRAME_COLOR[1])

    cvui.rect(FRAME_SETTINGS_FRAME, 10, 110, 255, 110, 0xFFFFFF)
    cvui.text(FRAME_SETTINGS_FRAME, 100, 120, 'FRAME AREA', 0.4, textColor)

    if cvui.button(FRAME_SETTINGS_FRAME, 15, 140, 70, 30, 'SMALL', buttonDefault, buttonOut, buttonOver, windowText):
        FILTER_FRAME_AMOUNT[0] = 5
    if cvui.button(FRAME_SETTINGS_FRAME, 102, 140, 70, 30, 'MEDIUM', buttonDefault, buttonOut, buttonOver, windowText):
        FILTER_FRAME_AMOUNT[0] = 25
    if cvui.button(FRAME_SETTINGS_FRAME, 189, 140, 70, 30, 'LARGE', buttonDefault, buttonOut, buttonOver, windowText):
        FILTER_FRAME_AMOUNT[0] = 50

    if cvui.button(FRAME_SETTINGS_FRAME, 60, 185, 40, 20, '<-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_FRAME_AMOUNT[0]>=1:
            FILTER_FRAME_AMOUNT[0] = FILTER_FRAME_AMOUNT[0] - 1
    cvui.text(FRAME_SETTINGS_FRAME, 105, 183, str(FILTER_FRAME_AMOUNT[0]) + 'px', 1.0, textColor)
    if cvui.button(FRAME_SETTINGS_FRAME, 185, 185, 40, 20, '->', buttonDefault, buttonOut, buttonOver, windowText):
        FILTER_FRAME_AMOUNT[0] = FILTER_FRAME_AMOUNT[0] + 1

    if cvui.button(FRAME_SETTINGS_FRAME, 10, 230, 60, 30, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText) and FILTER_USE_FRAME[0] == True:
        build = []
        for image in changesList[imagesVersion]:
            img = tools.frame(image, FILTER_FRAME_AMOUNT[0], FILTER_FRAME_COLOR[0])
            build.append(img)
        add_to_changes(build, f'tools.frame(image, {FILTER_FRAME_AMOUNT[0]}, {FILTER_FRAME_COLOR[0]})')

        FILTER_USE_FRAME = [False]
    if cvui.button(FRAME_SETTINGS_FRAME, 205, 230, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_FRAME)
        return

    cvui.imshow(WINDOW_SETTINGS_FRAME, FRAME_SETTINGS_FRAME)

def generate_interface_tools_combine():
    global imageCopy, imageVersion, imagePath
    global COMBINE_DIRECTION_VERTICAL, COMBINE_DIRECTION_HORIZONTAL, COMBINE_MODE_BIGGEST, COMBINE_MODE_SMALLEST, COMBINE_MODE_NORESIZE, COMBINE_ORDER_NORMAL, COMBINE_ORDER_REVERSE

    cvui.context(WINDOW_TOOLS_COMBINE)
    FRAME_TOOLS_COMBINE[:] = frameColor1
    cvui.window(FRAME_TOOLS_COMBINE, 5, 5, 280, 220, 'COMBINE SETTINGS', windowHeader, windowBody, windowText)

    cvui.text(FRAME_TOOLS_COMBINE, 110, 35, 'DIRECTION:', 0.4, textColor)

    cvui.checkbox(FRAME_TOOLS_COMBINE, 54, 55, 'VERTICAL', COMBINE_DIRECTION_VERTICAL, textColor)
    if COMBINE_DIRECTION_VERTICAL[0]:
        COMBINE_DIRECTION_HORIZONTAL = [False]

    cvui.checkbox(FRAME_TOOLS_COMBINE, 154, 55, 'HORIZONTAL', COMBINE_DIRECTION_HORIZONTAL, textColor)
    if COMBINE_DIRECTION_HORIZONTAL[0]:
        COMBINE_DIRECTION_VERTICAL = [False]

    cvui.text(FRAME_TOOLS_COMBINE, 112, 90, 'RESIZING:', 0.4, textColor)

    cvui.checkbox(FRAME_TOOLS_COMBINE, 10, 110, 'BIGGEST', COMBINE_MODE_BIGGEST, textColor)
    if COMBINE_MODE_BIGGEST[0]:
        COMBINE_MODE_SMALLEST = [False]
        COMBINE_MODE_NORESIZE = [False]

    cvui.checkbox(FRAME_TOOLS_COMBINE, 90, 110, 'SMALLEST', COMBINE_MODE_SMALLEST, textColor)
    if COMBINE_MODE_SMALLEST[0]:
        COMBINE_MODE_BIGGEST = [False]
        COMBINE_MODE_NORESIZE = [False]

    cvui.checkbox(FRAME_TOOLS_COMBINE, 180, 110, 'NO RESIZING', COMBINE_MODE_NORESIZE, textColor)
    if COMBINE_MODE_NORESIZE[0]:
        COMBINE_MODE_SMALLEST = [False]
        COMBINE_MODE_BIGGEST = [False]

    cvui.text(FRAME_TOOLS_COMBINE, 116, 145, 'ORDER:', 0.4, textColor)

    cvui.checkbox(FRAME_TOOLS_COMBINE, 54, 165, 'IN-ORDER', COMBINE_ORDER_NORMAL, textColor)
    if COMBINE_ORDER_NORMAL[0]:
        COMBINE_ORDER_REVERSE = [False]

    cvui.checkbox(FRAME_TOOLS_COMBINE, 154, 165, 'REVERSED', COMBINE_ORDER_REVERSE, textColor)
    if COMBINE_ORDER_REVERSE[0]:
        COMBINE_ORDER_NORMAL = [False]

    if cvui.button(FRAME_TOOLS_COMBINE, 10, 190, 150, 30, 'SAVE COMBINED IMAGE', buttonDefault, buttonOut, buttonOver, windowText):
        filepath = filedialog.asksaveasfilename(title="Choose saving location.", filetypes=(('PNG','*.png'), ('BMP', ('*.bmp', '*.jdib')), ('GIF', '*.gif'), ('JPG', '*.jpg'), ('JPEG','*.jpeg'), ('JPE', '*.jpe')), defaultextension='*.jpg')
        # IF NAME OF FILE AND PATH IS CHOOSEN

        if COMBINE_ORDER_REVERSE[0]:
            combineOrder = 'reverse'
        else:
            combineOrder = 'normal'

        if filepath:
            if COMBINE_DIRECTION_VERTICAL[0] == True:
                if COMBINE_MODE_BIGGEST[0]:
                    combinedImage = tools.combine_resize(changesList[imagesVersion], 'vertical', 'biggest', combineOrder)
                    cv2.imwrite(filepath, combinedImage)
                elif COMBINE_MODE_SMALLEST[0]:
                    combinedImage = tools.combine_resize(changesList[imagesVersion], 'vertical', 'smallest', combineOrder)
                    cv2.imwrite(filepath, combinedImage)
                elif COMBINE_MODE_NORESIZE[0]:
                    combinedImage = tools.combine(changesList[imagesVersion], 'vertical', combineOrder)
                    cv2.imwrite(filepath, combinedImage)
                else:
                    pass

            if COMBINE_DIRECTION_HORIZONTAL[0] == True:
                if COMBINE_MODE_BIGGEST[0]:
                    combinedImage = tools.combine_resize(changesList[imagesVersion], 'horizontal', 'biggest', combineOrder)
                    cv2.imwrite(filepath, combinedImage)
                elif COMBINE_MODE_SMALLEST[0]:
                    combinedImage = tools.combine_resize(changesList[imagesVersion], 'horizontal', 'smallest', combineOrder)
                    cv2.imwrite(filepath, combinedImage)
                elif COMBINE_MODE_NORESIZE[0]:
                    combinedImage = tools.combine(changesList[imagesVersion], 'horizontal', combineOrder)
                    cv2.imwrite(filepath, combinedImage)
                else:
                    pass
        else:
            message_window("FILE WAS NOT CHOSEN", "You need to choose a file!", 'error')

    if cvui.button(FRAME_TOOLS_COMBINE, 200, 190, 80, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_TOOLS_COMBINE)
        return

    cvui.imshow(WINDOW_TOOLS_COMBINE, FRAME_TOOLS_COMBINE)

def generate_interface_settings_textures():
    global FILTER_USE_TEXTURES, texturesCurrent, IAREA_TEXTURES_STATE, texturesPreview
    cvui.context(WINDOW_SETTINGS_TEXTURES)
    FRAME_SETTINGS_TEXTURES[:] = frameColor2
    cvui.window(FRAME_SETTINGS_TEXTURES, 5, 5, 255, 330, 'TEXTURES SETTINGS', windowHeader, windowBody, windowText)
    cvui.checkbox(FRAME_SETTINGS_TEXTURES, 10, 30, 'Use texture', FILTER_USE_TEXTURES, textColor)

    if cvui.button(FRAME_SETTINGS_TEXTURES, 10, 55, 30, 175, '<-', buttonDefault, buttonOut, buttonOver, windowText):
        if texturesCurrent > 0:
            texturesCurrent -= 1
            texturesPreview = cv2.imread(texturesPath[texturesCurrent], cv2.IMREAD_UNCHANGED)
            texturesPreview = image_resize(texturesPreview, width=175)
    if cvui.button(FRAME_SETTINGS_TEXTURES, 225, 55, 30, 175, '->', buttonDefault, buttonOut, buttonOver, windowText):
        if texturesCurrent != len(texturesPath) - 1:
            texturesCurrent += 1
            texturesPreview = cv2.imread(texturesPath[texturesCurrent], cv2.IMREAD_UNCHANGED)
            texturesPreview = image_resize(texturesPreview, width=175)

    cvui.rect(FRAME_SETTINGS_TEXTURES, 45, 55, 175, 175, 0x515A5A)
    cvui.image(FRAME_SETTINGS_TEXTURES, 45, 55, texturesPreview)

    if cvui.button(FRAME_SETTINGS_TEXTURES, 240, 260, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_TEXTURE_AMOUNT[0] < 1:
            FILTER_TEXTURE_AMOUNT[0] = FILTER_TEXTURE_AMOUNT[0] + 0.01
    if cvui.button(FRAME_SETTINGS_TEXTURES, 10, 260, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_TEXTURE_AMOUNT[0] > 0.01:
            FILTER_TEXTURE_AMOUNT[0] = FILTER_TEXTURE_AMOUNT[0] - 0.01
    IAREA_TEXTURES_STATE = cvui.iarea(0, 230, 260, 200)
    cvui.trackbar(FRAME_SETTINGS_TEXTURES, 25, 245, 210, FILTER_TEXTURE_AMOUNT, 0.0, 1.0, 1.0, '%.2Lf', cvui.TRACKBAR_DISCRETE, 0.01, windowText)
    cvui.text(FRAME_SETTINGS_TEXTURES, 115, 245, 'opacity', 0.4, textColor)

    if cvui.button(FRAME_SETTINGS_TEXTURES, 10, 300, 60, 30, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_USE_TEXTURES[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.blend(image, FILTER_TEXTURE_AMOUNT[0], cv2.imread(texturesPath[texturesCurrent], cv2.IMREAD_UNCHANGED), 2)
                build.append(img)
            add_to_changes(build)
            FILTER_USE_TEXTURES = [False]
    if cvui.button(FRAME_SETTINGS_TEXTURES, 195, 300, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_TEXTURES)
        return

    cvui.imshow(WINDOW_SETTINGS_TEXTURES, FRAME_SETTINGS_TEXTURES)

def generate_interface_settings_overlays():
    global FILTER_USE_OVERLAY_TYPE_1, FILTER_USE_OVERLAY_TYPE_2, FILTER_USE_OVERLAY_TYPE_3, FILTER_USE_OVERLAY_TYPE_4, FILTER_USE_OVERLAY_TYPE_5
    global FILTER_USE_OVERLAY_TYPE_6, FILTER_USE_OVERLAY_TYPE_7, FILTER_USE_OVERLAY_TYPE_8, FILTER_USE_OVERLAY_TYPE_9
    global overlaysCurrent, IAREA_OVERLAYS_STATE, overlaysPreview

    cvui.context(WINDOW_SETTINGS_OVERLAYS)
    FRAME_SETTINGS_OVERLAYS[:] = frameColor2
    cvui.window(FRAME_SETTINGS_OVERLAYS, 5, 5, 310, 460, 'OVERLAYS SETTINGS', windowHeader, windowBody, windowText)
    cvui.checkbox(FRAME_SETTINGS_OVERLAYS, 10, 40, 'NORMAL', FILTER_USE_OVERLAY_TYPE_1, textColor)
    if FILTER_USE_OVERLAY_TYPE_1[0]:
        FILTER_USE_OVERLAY_TYPE_2 = [False]
        FILTER_USE_OVERLAY_TYPE_3 = [False]
        FILTER_USE_OVERLAY_TYPE_4 = [False]
        FILTER_USE_OVERLAY_TYPE_5 = [False]
        FILTER_USE_OVERLAY_TYPE_6 = [False]
        FILTER_USE_OVERLAY_TYPE_7 = [False]
        FILTER_USE_OVERLAY_TYPE_8 = [False]
        FILTER_USE_OVERLAY_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_OVERLAYS, 110, 40, 'MULTIPLY', FILTER_USE_OVERLAY_TYPE_2, textColor)
    if FILTER_USE_OVERLAY_TYPE_2[0]:
        FILTER_USE_OVERLAY_TYPE_1 = [False]
        FILTER_USE_OVERLAY_TYPE_3 = [False]
        FILTER_USE_OVERLAY_TYPE_4 = [False]
        FILTER_USE_OVERLAY_TYPE_5 = [False]
        FILTER_USE_OVERLAY_TYPE_6 = [False]
        FILTER_USE_OVERLAY_TYPE_7 = [False]
        FILTER_USE_OVERLAY_TYPE_8 = [False]
        FILTER_USE_OVERLAY_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_OVERLAYS, 215, 40, 'DARKEN', FILTER_USE_OVERLAY_TYPE_3, textColor)
    if FILTER_USE_OVERLAY_TYPE_3[0]:
        FILTER_USE_OVERLAY_TYPE_1 = [False]
        FILTER_USE_OVERLAY_TYPE_2 = [False]
        FILTER_USE_OVERLAY_TYPE_4 = [False]
        FILTER_USE_OVERLAY_TYPE_5 = [False]
        FILTER_USE_OVERLAY_TYPE_6 = [False]
        FILTER_USE_OVERLAY_TYPE_7 = [False]
        FILTER_USE_OVERLAY_TYPE_8 = [False]
        FILTER_USE_OVERLAY_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_OVERLAYS, 10, 80, 'LIGHTEN', FILTER_USE_OVERLAY_TYPE_4, textColor)
    if FILTER_USE_OVERLAY_TYPE_4[0]:
        FILTER_USE_OVERLAY_TYPE_1 = [False]
        FILTER_USE_OVERLAY_TYPE_2 = [False]
        FILTER_USE_OVERLAY_TYPE_3 = [False]
        FILTER_USE_OVERLAY_TYPE_5 = [False]
        FILTER_USE_OVERLAY_TYPE_6 = [False]
        FILTER_USE_OVERLAY_TYPE_7 = [False]
        FILTER_USE_OVERLAY_TYPE_8 = [False]
        FILTER_USE_OVERLAY_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_OVERLAYS, 110, 80, 'DODGE', FILTER_USE_OVERLAY_TYPE_5, textColor)
    if FILTER_USE_OVERLAY_TYPE_5[0]:
        FILTER_USE_OVERLAY_TYPE_1 = [False]
        FILTER_USE_OVERLAY_TYPE_2 = [False]
        FILTER_USE_OVERLAY_TYPE_3 = [False]
        FILTER_USE_OVERLAY_TYPE_4 = [False]
        FILTER_USE_OVERLAY_TYPE_6 = [False]
        FILTER_USE_OVERLAY_TYPE_7 = [False]
        FILTER_USE_OVERLAY_TYPE_8 = [False]
        FILTER_USE_OVERLAY_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_OVERLAYS, 215, 80, 'OVERLAY', FILTER_USE_OVERLAY_TYPE_6, textColor)
    if FILTER_USE_OVERLAY_TYPE_6[0]:
        FILTER_USE_OVERLAY_TYPE_1 = [False]
        FILTER_USE_OVERLAY_TYPE_2 = [False]
        FILTER_USE_OVERLAY_TYPE_3 = [False]
        FILTER_USE_OVERLAY_TYPE_4 = [False]
        FILTER_USE_OVERLAY_TYPE_5 = [False]
        FILTER_USE_OVERLAY_TYPE_7 = [False]
        FILTER_USE_OVERLAY_TYPE_8 = [False]
        FILTER_USE_OVERLAY_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_OVERLAYS, 10, 120, 'SOFT LIGHT', FILTER_USE_OVERLAY_TYPE_7, textColor)
    if FILTER_USE_OVERLAY_TYPE_7[0]:
        FILTER_USE_OVERLAY_TYPE_1 = [False]
        FILTER_USE_OVERLAY_TYPE_2 = [False]
        FILTER_USE_OVERLAY_TYPE_3 = [False]
        FILTER_USE_OVERLAY_TYPE_4 = [False]
        FILTER_USE_OVERLAY_TYPE_5 = [False]
        FILTER_USE_OVERLAY_TYPE_6 = [False]
        FILTER_USE_OVERLAY_TYPE_8 = [False]
        FILTER_USE_OVERLAY_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_OVERLAYS, 110, 120, 'HARD LIGHT', FILTER_USE_OVERLAY_TYPE_8, textColor)
    if FILTER_USE_OVERLAY_TYPE_8[0]:
        FILTER_USE_OVERLAY_TYPE_1 = [False]
        FILTER_USE_OVERLAY_TYPE_2 = [False]
        FILTER_USE_OVERLAY_TYPE_3 = [False]
        FILTER_USE_OVERLAY_TYPE_4 = [False]
        FILTER_USE_OVERLAY_TYPE_5 = [False]
        FILTER_USE_OVERLAY_TYPE_6 = [False]
        FILTER_USE_OVERLAY_TYPE_7 = [False]
        FILTER_USE_OVERLAY_TYPE_9 = [False]
    cvui.checkbox(FRAME_SETTINGS_OVERLAYS, 215, 120, 'DIFFERENCE', FILTER_USE_OVERLAY_TYPE_9, textColor)
    if FILTER_USE_OVERLAY_TYPE_9[0]:
        FILTER_USE_OVERLAY_TYPE_1 = [False]
        FILTER_USE_OVERLAY_TYPE_2 = [False]
        FILTER_USE_OVERLAY_TYPE_3 = [False]
        FILTER_USE_OVERLAY_TYPE_4 = [False]
        FILTER_USE_OVERLAY_TYPE_5 = [False]
        FILTER_USE_OVERLAY_TYPE_6 = [False]
        FILTER_USE_OVERLAY_TYPE_7 = [False]
        FILTER_USE_OVERLAY_TYPE_8 = [False]

    if cvui.button(FRAME_SETTINGS_OVERLAYS, 27, 155, 30, 200, '<-', buttonDefault, buttonOut, buttonOver, windowText):
        if overlaysCurrent > 0:
            overlaysCurrent -= 1
            overlaysPreview = cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED)
            overlaysPreview = image_resize(overlaysPreview, width=200)

    if cvui.button(FRAME_SETTINGS_OVERLAYS, 266, 155, 30, 200, '->', buttonDefault, buttonOut, buttonOver, windowText):
        if overlaysCurrent != len(overlaysPath) - 1:
            overlaysCurrent += 1
            overlaysPreview = cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED)
            overlaysPreview = image_resize(overlaysPreview, width=200)

    cvui.rect(FRAME_SETTINGS_OVERLAYS, 62, 155, 175, 175, 0x515A5A)
    cvui.image(FRAME_SETTINGS_OVERLAYS, 62, 155, overlaysPreview)
    if cvui.button(FRAME_SETTINGS_OVERLAYS, 295, 380, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_OVERLAY_AMOUNT[0] < 1:
            FILTER_OVERLAY_AMOUNT[0] = FILTER_OVERLAY_AMOUNT[0] + 0.01
    if cvui.button(FRAME_SETTINGS_OVERLAYS, 10, 380, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_OVERLAY_AMOUNT[0] > 0.01:
            FILTER_OVERLAY_AMOUNT[0] = FILTER_OVERLAY_AMOUNT[0] - 0.01
    IAREA_OVERLAYS_STATE = cvui.iarea(0, 350, 300, 200)
    cvui.trackbar(FRAME_SETTINGS_OVERLAYS, 25, 365, 270, FILTER_OVERLAY_AMOUNT, 0.0, 1.0, 1.0, '%.2Lf', cvui.TRACKBAR_DISCRETE, 0.01, windowText)
    cvui.text(FRAME_SETTINGS_OVERLAYS, 145, 365, 'opacity', 0.4, textColor)

    if cvui.button(FRAME_SETTINGS_OVERLAYS, 10, 420, 90, 40, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):
        if FILTER_USE_OVERLAY_TYPE_1[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.blend(image, FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 1)
                build.append(img)
            add_to_changes(build)

        if FILTER_USE_OVERLAY_TYPE_2[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.blend(image, FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 2)
                build.append(img)
            add_to_changes(build)

        if FILTER_USE_OVERLAY_TYPE_3[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.blend(image, FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 3)
                build.append(img)
            add_to_changes(build)

        if FILTER_USE_OVERLAY_TYPE_4[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.blend(image, FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 4)
                build.append(img)
            add_to_changes(build)

        if FILTER_USE_OVERLAY_TYPE_5[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.blend(image, FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 5)
                build.append(img)
            add_to_changes(build)

        if FILTER_USE_OVERLAY_TYPE_6[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.blend(image, FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 6)
                build.append(img)
            add_to_changes(build)

        if FILTER_USE_OVERLAY_TYPE_7[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.blend(image, FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 7)
                build.append(img)
            add_to_changes(build)

        if FILTER_USE_OVERLAY_TYPE_8[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.blend(image, FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 8)
                build.append(img)
            add_to_changes(build)

        if FILTER_USE_OVERLAY_TYPE_9[0]:
            build = []
            for image in changesList[imagesVersion]:
                img = filters.blend(image, FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 9)
                build.append(img)
            add_to_changes(build)

        FILTER_USE_OVERLAY_TYPE_1 = [False]
        FILTER_USE_OVERLAY_TYPE_2 = [False]
        FILTER_USE_OVERLAY_TYPE_3 = [False]
        FILTER_USE_OVERLAY_TYPE_4 = [False]
        FILTER_USE_OVERLAY_TYPE_5 = [False]
        FILTER_USE_OVERLAY_TYPE_6 = [False]
        FILTER_USE_OVERLAY_TYPE_7 = [False]
        FILTER_USE_OVERLAY_TYPE_8 = [False]
        FILTER_USE_OVERLAY_TYPE_9 = [False]
    if cvui.button(FRAME_SETTINGS_OVERLAYS, 220, 420, 90, 40, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_OVERLAYS)
        return

    cvui.imshow(WINDOW_SETTINGS_OVERLAYS, FRAME_SETTINGS_OVERLAYS)

def generate_interface_tools_macro():
    global MACRO_RECORD, macrosCurrent, macrosPath
    cvui.context(WINDOW_SETTINGS_MACRO)
    FRAME_SETTINGS_MACRO[:] = frameColor1
    cvui.window(FRAME_SETTINGS_MACRO, 5, 5, 240, 180, 'MACRO SETTINGS', windowHeader, windowBody, windowText)

    if MACRO_RECORD == False:
        if cvui.button(FRAME_SETTINGS_MACRO, 6, 6, 238, 45, 'START RECORDING MACRO', buttonDefault, buttonOut, buttonOver, windowText):
            MACRO_RECORD = True

        if macrosPath:
            cvui.text(FRAME_SETTINGS_MACRO, 100, 105, f'{macrosPath[macrosCurrent][:-4]}', 0.4, textColor)

    else:
        if cvui.button(FRAME_SETTINGS_MACRO, 6, 6, 238, 45, 'STOP RECORDING MACRO', buttonDefault, buttonOut, buttonOver, windowText):
            MACRO_RECORD = False
            macrosPath = save_macro()
            MACRO_LIST.clear()

        cvui.text(FRAME_SETTINGS_MACRO, 94, 105, 'recording...', 0.4, textColor)

    cvui.text(FRAME_SETTINGS_MACRO, 73, 67, 'browse macros...', 0.4, textColor)

    if cvui.button(FRAME_SETTINGS_MACRO, 20, 85, 40, 35, '<-', buttonDefault, buttonOut, buttonOver, windowText):
        if (macrosCurrent - 1 >= 0):
            macrosCurrent -= 1

    cvui.rect(FRAME_SETTINGS_MACRO, 62, 85, 126, 35, 0x515A5A)
    cvui.rect(FRAME_SETTINGS_MACRO, 62, 85, 126, 15, 0x515A5A, 0x515A5A)
    cvui.text(FRAME_SETTINGS_MACRO, 110, 87, f'{macrosCurrent+1}/{len(macrosPath)}', 0.4, textColor)

    if cvui.button(FRAME_SETTINGS_MACRO, 190, 85, 40, 35, '->', buttonDefault, buttonOut, buttonOver, windowText):
        if (macrosCurrent + 1 < len(macrosPath)):
            macrosCurrent += 1

    if cvui.button(FRAME_SETTINGS_MACRO, 10, 150, 110, 30, 'EXECUTE', buttonDefault, buttonOut, buttonOver, windowText) and MACRO_RECORD == False:
        execute_macro(macrosPath[macrosCurrent])

    if cvui.button(FRAME_SETTINGS_MACRO, 130, 150, 110, 30, 'DELETE', buttonDefault, buttonOut, buttonOver, windowText):
        if macrosPath:
            os.remove(f'Macros/{macrosPath[macrosCurrent]}')
            macrosPath = os.listdir('Macros/')
            macrosCurrent = 0

    cvui.imshow(WINDOW_SETTINGS_MACRO, FRAME_SETTINGS_MACRO)

def generate_interface_tools_text():
    global TOOLS_TEXT_VALUE, TEXT_X_POSITION, TEXT_Y_POSITION, TEXT_SCALE_AMOUNT, FILTER_USE_TEXT, temp_text_frame, TEXT_ADD_POSITION
    global TEXT_USE_FONT, TEXT_USE_FONT_1, TEXT_USE_FONT_2, TEXT_USE_FONT_3, TEXT_USE_FONT_4, TEXT_THICKNESS_AMOUNT, TEXT_USE_COLOR
    cvui.context(WINDOW_SETTINGS_TEXT)
    FRAME_SETTINGS_TEXT[:] = (30, 30, 30)
    cvui.window(FRAME_SETTINGS_TEXT, 5, 5, 250, 540, 'TEXT SETTINGS', windowHeader, windowBody, windowText)

    FILTER_USE_TEXT = [True]
    (h1, w1) = changesList[imagesVersion][imagesCurrent].shape[:2]
    temp_text_frame = np.zeros((h1, w1, 4), np.uint8)
    temp_text_frame[:] = (255,255,255,0)
    if cvui.button(FRAME_SETTINGS_TEXT, 10, 30, 100, 30, 'Add text', buttonDefault, buttonOut, buttonOver, windowText):
        root = Tk()
        root.withdraw()
        TOOLS_TEXT_VALUE = simpledialog.askstring("Input", "Write down your text")
        root.destroy()
        cvui.update()
    (final_text_width, final_text_height), baseline = cv2.getTextSize(TOOLS_TEXT_VALUE, TEXT_USE_FONT, TEXT_SCALE_AMOUNT[0], TEXT_THICKNESS_AMOUNT[0])
    TEMP_SCALE_AMOUNT = round(TEXT_SCALE_AMOUNT[0],1)
    if cvui.button(FRAME_SETTINGS_TEXT, 140+30, 37, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if TEXT_SCALE_AMOUNT[0] > 0.2:
            TEXT_SCALE_AMOUNT[0] = TEXT_SCALE_AMOUNT[0] - 0.1
    cvui.text(FRAME_SETTINGS_TEXT, 100+30, 40, 'Scale', 0.4, textColor)
    cvui.text(FRAME_SETTINGS_TEXT, 165+31, 40, str(TEMP_SCALE_AMOUNT), 0.4, textColor)
    if cvui.button(FRAME_SETTINGS_TEXT, 200+30, 37, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if TEXT_SCALE_AMOUNT[0] < 4.9:
            TEXT_SCALE_AMOUNT[0] = TEXT_SCALE_AMOUNT[0] + 0.1

    cvui.checkbox(FRAME_SETTINGS_TEXT, 40, 70, 'Sans-serif', TEXT_USE_FONT_1, textColor)
    if TEXT_USE_FONT_1[0]:
        TEXT_USE_FONT = cv2.FONT_HERSHEY_DUPLEX
        TEXT_USE_FONT_2 = [False]
        TEXT_USE_FONT_3 = [False]
        TEXT_USE_FONT_4 = [False]
    cvui.checkbox(FRAME_SETTINGS_TEXT, 160, 70, 'Serif', TEXT_USE_FONT_2, textColor)
    if TEXT_USE_FONT_2[0]:
        TEXT_USE_FONT = cv2.FONT_HERSHEY_TRIPLEX
        TEXT_USE_FONT_1 = [False]
        TEXT_USE_FONT_3 = [False]
        TEXT_USE_FONT_4 = [False]
    cvui.checkbox(FRAME_SETTINGS_TEXT, 40, 100, 'Handwritten', TEXT_USE_FONT_3, textColor)
    if TEXT_USE_FONT_3[0]:
        TEXT_USE_FONT = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
        TEXT_USE_FONT_1 = [False]
        TEXT_USE_FONT_2 = [False]
        TEXT_USE_FONT_4 = [False]
    cvui.checkbox(FRAME_SETTINGS_TEXT, 160, 100, 'Italic', TEXT_USE_FONT_4, textColor)
    if TEXT_USE_FONT_4[0]:
        TEXT_USE_FONT = cv2.FONT_ITALIC
        TEXT_USE_FONT_1 = [False]
        TEXT_USE_FONT_2 = [False]
        TEXT_USE_FONT_3 = [False]

    cvui.trackbar(FRAME_SETTINGS_TEXT, 31, 130, 200, TEXT_THICKNESS_AMOUNT, 1, 4, 0.1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    cvui.text(FRAME_SETTINGS_TEXT, 102, 130, 'thickness')

    if cvui.button(FRAME_SETTINGS_TEXT, 10, 180, 140, 50, 'COLOR PICKER...', buttonDefault, buttonOut, buttonOver, windowText):
            root = Tk()
            root.withdraw()
            TEXT_USE_COLOR = choose_color()
            test = list(TEXT_USE_COLOR)
            test[0]= tuple(reversed(test[0]))
            test2 = list(test[0])
            test2.append(255)
            test3 = tuple(test2)

            test[0] = test3
            TEXT_USE_COLOR = test

            root.destroy()
            cvui.update()
    cvui.rect(FRAME_SETTINGS_TEXT, 160, 183, 90, 44, TEXT_USE_COLOR[1], TEXT_USE_COLOR[1])

    cvui.rect(FRAME_SETTINGS_TEXT, 41, 240, 180, 84, 0xffffff)
    if cvui.button(FRAME_SETTINGS_TEXT, 43, 242, 80, 30, 'TOP-LEFT', buttonDefault, buttonOut, buttonOver, windowText):
            TEXT_X_POSITION = 20
            TEXT_Y_POSITION = 20 + (final_text_height/2)
    if cvui.button(FRAME_SETTINGS_TEXT, 140, 242, 80, 30, 'TOP-RIGHT', buttonDefault, buttonOut, buttonOver, windowText):
            TEXT_X_POSITION = (w1/2) - (final_text_width/2) - 20
            TEXT_Y_POSITION = 20 + (final_text_height/2)
    if cvui.button(FRAME_SETTINGS_TEXT, 42, 291, 80, 30, 'BOT-LEFT', buttonDefault, buttonOut, buttonOver, windowText):
            TEXT_X_POSITION = 20
            TEXT_Y_POSITION = (h1/2) - (final_text_height/2) - 20
    if cvui.button(FRAME_SETTINGS_TEXT, 139, 291, 80, 30,'BOT-RIGHT', buttonDefault, buttonOut, buttonOver, windowText):
            TEXT_X_POSITION = (w1/2) - (final_text_width/2) - 20
            TEXT_Y_POSITION = (h1/2) - (final_text_height/2) - 20
    cvui.text(FRAME_SETTINGS_TEXT, 102, 277, 'POSITION', 0.4, textColor)

    cvui.trackbar(FRAME_SETTINGS_TEXT, 31, 340, 200, TEXT_ADD_POSITION, 1, 100, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    cvui.text(FRAME_SETTINGS_TEXT, 90, 340, 'text step move')

    if cvui.button(FRAME_SETTINGS_TEXT, 225, 355, 15, 15, '+', buttonDefault, buttonOut, buttonOver, windowText):
        if TEXT_ADD_POSITION[0] < 100:
            TEXT_ADD_POSITION[0] = TEXT_ADD_POSITION[0] + 1
    if cvui.button(FRAME_SETTINGS_TEXT, 22, 355, 15, 15, '-', buttonDefault, buttonOut, buttonOver, windowText):
        if TEXT_ADD_POSITION[0] > 1:
            TEXT_ADD_POSITION[0] = TEXT_ADD_POSITION[0] - 1


    if cvui.button(FRAME_SETTINGS_TEXT, 101, 399, 60, 30, 'UP', buttonDefault, buttonOut, buttonOver, windowText):
            TEXT_Y_POSITION -= TEXT_ADD_POSITION[0]
    if cvui.button(FRAME_SETTINGS_TEXT, 161, 433, 60, 30, 'RIGHT', buttonDefault, buttonOut, buttonOver, windowText):
            TEXT_X_POSITION += TEXT_ADD_POSITION[0]
    if cvui.button(FRAME_SETTINGS_TEXT, 41, 433, 60, 30, 'LEFT', buttonDefault, buttonOut, buttonOver, windowText):
            TEXT_X_POSITION -= TEXT_ADD_POSITION[0]
    if cvui.button(FRAME_SETTINGS_TEXT, 101, 469, 60, 30, 'BOTTOM', buttonDefault, buttonOut, buttonOver, windowText):
            TEXT_Y_POSITION += TEXT_ADD_POSITION[0]
    cvui.text(FRAME_SETTINGS_TEXT, 113, 444, 'MOVE', 0.4, textColor)

    if cvui.button(FRAME_SETTINGS_TEXT, 10, 510, 80, 30, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):

        build = []
        for image in changesList[imagesVersion]:

            img = filters.putText(temp_text_frame,image,TOOLS_TEXT_VALUE, (int(TEXT_X_POSITION),
            int(TEXT_Y_POSITION)), TEXT_USE_FONT, TEXT_SCALE_AMOUNT[0], TEXT_USE_COLOR[0], TEXT_THICKNESS_AMOUNT[0], cv2.LINE_AA)
            build.append(img)
            add_to_changes(build)

        message_window("TEXT ADDED", "Text has been successfully applied.", 'info')
        close_window(WINDOW_SETTINGS_TEXT)
        return

    if cvui.button(FRAME_SETTINGS_TEXT, 170, 510, 80, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_TEXT)
        return

    cvui.imshow(WINDOW_SETTINGS_TEXT, FRAME_SETTINGS_TEXT)

def generate_interface_settings_about():
    global ape
    cvui.context(WINDOW_SETTINGS_ABOUT)
    FRAME_SETTINGS_ABOUT[:] = frameColor2
    cvui.window(FRAME_SETTINGS_ABOUT, 5, 5, 310, 450, 'ABOUT', windowHeader, windowBody, windowText)

    if isLightModeActive == True:
        cvui.image(FRAME_SETTINGS_ABOUT, 85, 55, cv2.imread('Graphics/ape2.png', cv2.IMREAD_UNCHANGED))
    else:
        cvui.image(FRAME_SETTINGS_ABOUT, 85, 55, cv2.imread('Graphics/ape1.png', cv2.IMREAD_UNCHANGED))

    cvui.text(FRAME_SETTINGS_ABOUT, 70, 30, "SNAKE PHOTO EDITOR", 0.6, textColor)
    cvui.text(FRAME_SETTINGS_ABOUT, 135, 260, "v. 1.0.0", 0.6, textColor)
    cvui.text(FRAME_SETTINGS_ABOUT, 130, 305, "CREDITS:", 0.5, textColor)
    cvui.text(FRAME_SETTINGS_ABOUT, 10, 330, "Przemyslaw Niewolinski - programmer", 0.35, textColor)
    cvui.text(FRAME_SETTINGS_ABOUT, 10, 350, "Krzysztof Mika - graphics designer, co-programmer", 0.35, textColor)
    cvui.text(FRAME_SETTINGS_ABOUT, 10, 370, "Marcin Mateja - programmer", 0.35, textColor)
    cvui.text(FRAME_SETTINGS_ABOUT, 10, 390, "Patryk Namyslo - product owner, programmer", 0.35, textColor)

    if cvui.button(FRAME_SETTINGS_ABOUT, 130, 420, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_ABOUT)
        return

    cvui.imshow(WINDOW_SETTINGS_ABOUT, FRAME_SETTINGS_ABOUT)

def generate_interface_tools_hsv():
    global FILTER_USE_HSV
    cvui.context(WINDOW_SETTINGS_HSV)
    FRAME_SETTINGS_HSV[:] = frameColor1

    cvui.window(FRAME_SETTINGS_HSV, 5, 5, 450, 230, 'HSV SEPARATION SETTINGS', windowHeader, windowBody, windowText)
    cvui.checkbox(FRAME_SETTINGS_HSV, 10, 30, 'HSV', FILTER_USE_HSV, textColor)

    cvui.text(FRAME_SETTINGS_HSV, 25-10, 510-440, "HUE:", 0.4, textColor)
    cvui.text(FRAME_SETTINGS_HSV, 140-10, 490-440, "MIN", 0.4, textColor)
    cvui.text(FRAME_SETTINGS_HSV, 340-10, 490-440, "MAX", 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_HSV, 55-10, 490-440, 200, hue_min_1, 0, 179, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    cvui.trackbar(FRAME_SETTINGS_HSV, 255-10, 490-440, 200, hue_max_1, 0, 179, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    cvui.text(FRAME_SETTINGS_HSV, 25-10, 560-440, "SAT:", 0.4, textColor)
    cvui.text(FRAME_SETTINGS_HSV, 140-10, 540-440, "MIN", 0.4, textColor)
    cvui.text(FRAME_SETTINGS_HSV, 340-10, 540-440, "MAX", 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_HSV, 55-10, 540-440, 200, sat_min_1, 0, 255, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    cvui.trackbar(FRAME_SETTINGS_HSV, 255-10, 540-440, 200, sat_max_1, 0, 255, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    cvui.text(FRAME_SETTINGS_HSV, 25-10, 610-440, "VAL:", 0.4, textColor)
    cvui.text(FRAME_SETTINGS_HSV, 140-10, 590-440, "MIN", 0.4, textColor)
    cvui.text(FRAME_SETTINGS_HSV, 340-10, 590-440, "MAX", 0.4, textColor)
    cvui.trackbar(FRAME_SETTINGS_HSV, 55-10, 590-440, 200, val_min_1, 0, 255, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)
    cvui.trackbar(FRAME_SETTINGS_HSV, 255-10, 590-440, 200, val_max_1, 0, 255, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1, windowText)

    if cvui.button(FRAME_SETTINGS_HSV, 10, 200, 60, 30, 'APPLY', buttonDefault, buttonOut, buttonOver, windowText):
        build = []
        for image in changesList[imagesVersion]:
            img = tools.hsv(changesList[imagesVersion][imagesCurrent], hue_min_1[0], sat_min_1[0], val_min_1[0], hue_max_1[0], sat_max_1[0], val_max_1[0])
            build.append(img)
        add_to_changes(build, f'tools.hsv(image, {hue_min_1[0]}, {sat_min_1[0]}, {val_min_1[0]}, {hue_max_1[0]}, {sat_max_1[0]}, {val_max_1[0]})')

        FILTER_USE_HSV = [False]
    if cvui.button(FRAME_SETTINGS_HSV, 390, 200, 60, 30, 'CLOSE', buttonDefault, buttonOut, buttonOver, windowText):
        close_window(WINDOW_SETTINGS_HSV)
        return

    cvui.imshow(WINDOW_SETTINGS_HSV, FRAME_SETTINGS_HSV)

### WINDOWS AND FRAMES ###
WINDOW_MAIN = 'SNAKE PHOTO EDITOR - SPRINT 3'
FRAME_MAIN = np.zeros((768, 1366, 4), np.uint8)

WINDOW_SETTINGS_SHARPNESS = 'SHARPNESS'
FRAME_SETTINGS_SHARPNESS = np.zeros((235, 250, 3), np.uint8)

WINDOW_SETTINGS_BRIGHTNESS = 'BRIGHTNESS'
FRAME_SETTINGS_BRIGHTNESS = np.zeros((230, 250, 3), np.uint8)

WINDOW_SETTINGS_COMMON = 'COMMON'
FRAME_SETTINGS_COMMON = np.zeros((190, 250, 3), np.uint8)

WINDOW_SETTINGS_COLORFILL = 'COLORFILL'
FRAME_SETTINGS_COLORFILL = np.zeros((420, 320, 3), np.uint8)

WINDOW_SETTINGS_COLOR = 'COLOR'
FRAME_SETTINGS_COLOR = np.zeros((515, 250, 3), np.uint8)

WINDOW_SETTINGS_MORPH = 'MORPHOLOGY'
FRAME_SETTINGS_MORPH = np.zeros((235, 250, 3), np.uint8)

WINDOW_SETTINGS_DENOISE = 'DENOISE'
FRAME_SETTINGS_DENOISE = np.zeros((260, 250, 3), np.uint8)

WINDOW_SETTINGS_SAVE = 'SAVE'
FRAME_SETTINGS_SAVE = np.zeros((315, 505, 3), np.uint8)

WINDOW_SETTINGS_BATCHSAVE = 'BATCH SAVE'
FRAME_SETTINGS_BATCHSAVE = np.zeros((335, 350, 3), np.uint8)

WINDOW_SETTINGS_PREVIEW = 'PREVIEW'
FRAME_SETTINGS_PREVIEW = np.zeros((580, 700, 3), np.uint8)

WINDOW_TOOLS_WATERMARK = 'WATERMARK'
FRAME_TOOLS_WATERMARK = np.zeros((500, 360, 3), np.uint8)

WINDOW_TOOLS_STICKER = 'STICKER'
FRAME_TOOLS_STICKER = np.zeros((625, 380, 3), np.uint8)

WINDOW_TOOLS_TRANSFORMATIONS = 'TRANSFORMATIONS'
FRAME_TOOLS_TRANSFORMATIONS = np.zeros((460, 300, 3), np.uint8)

WINDOW_TOOLS_UPSCALE = 'UPSCALE'
FRAME_TOOLS_UPSCALE = np.zeros((280, 240, 3), np.uint8)

WINDOW_FILTERS_NORMALIZATION = 'NORMALIZATION'
FRAME_FILTERS_NORMALIZATION = np.zeros((160, 270, 3), np.uint8)

WINDOW_TOOLS_COMBINE = 'COMBINE'
FRAME_TOOLS_COMBINE = np.zeros((230, 290, 3), np.uint8)

WINDOW_SETTINGS_PIX = 'PIXELIZATION'
FRAME_SETTINGS_PIX = np.zeros((165, 250, 3), np.uint8)

WINDOW_SETTINGS_FRAME = 'FRAME'
FRAME_SETTINGS_FRAME = np.zeros((270, 275, 3), np.uint8)

WINDOW_SETTINGS_TEXTURES = 'TEXTURES'
FRAME_SETTINGS_TEXTURES = np.zeros((340, 265, 4), np.uint8)

WINDOW_SETTINGS_OVERLAYS = 'OVERLAYS'
FRAME_SETTINGS_OVERLAYS = np.zeros((470, 320, 4), np.uint8)

WINDOW_SETTINGS_MACRO = 'MACRO'
FRAME_SETTINGS_MACRO = np.zeros((190, 250, 3), np.uint8)

WINDOW_SETTINGS_TEXT = 'TEXT'
FRAME_SETTINGS_TEXT = np.zeros((550, 260, 3), np.uint8)

WINDOW_SETTINGS_ABOUT = 'ABOUT'
FRAME_SETTINGS_ABOUT = np.zeros((460, 320, 4), np.uint8)

WINDOW_SETTINGS_HSV = 'HSV SEPARATION'
FRAME_SETTINGS_HSV = np.zeros((240, 460, 3), np.uint8)

### CVUI VARIABLES ###
FILTER_BLUR_AMOUNT = [1]
FILTER_USE_BLUR = [False]

FILTER_SHARPEN_AMOUNT = [1]
FILTER_USE_SHARPEN = [False]

FILTER_BRIGHTNESS_AMOUNT = [1]
FILTER_USE_BRIGHTNESS = [False]

FILTER_CONTRAST_AMOUNT = [1]
FILTER_USE_CONTRAST = [False]

FILTER_USE_SEPIA = [False]
FILTER_USE_GRAYSCALE = [False]
FILTER_USE_BLACKANDWHITE = [False]
FILTER_USE_NEGATIVE = [False]
FILTER_USE_EMBOSS = [False]
FILTER_USE_DIFF = [False]

FILTER_COLORFILL_AMOUNT = [1]
FILTER_COLORFILL_AMOUNT_LAST = sys.maxsize
FILTER_COLORFILL_COLOR = [(255, 255, 255, 255), 0xFFFFFF]
FILTER_COLORFILL_COLOR_2 = [(255, 255, 255, 255), 0xFFFFFF]
FILTER_USE_COLORFILL_GRADIENT = [False]
FILTER_USE_COLORFILL_TYPE_1 = [False]
FILTER_USE_COLORFILL_TYPE_2 = [False]
FILTER_USE_COLORFILL_TYPE_3 = [False]
FILTER_USE_COLORFILL_TYPE_4 = [False]
FILTER_USE_COLORFILL_TYPE_5 = [False]
FILTER_USE_COLORFILL_TYPE_6 = [False]
FILTER_USE_COLORFILL_TYPE_7 = [False]
FILTER_USE_COLORFILL_TYPE_8 = [False]
FILTER_USE_COLORFILL_TYPE_9 = [False]
FILTER_USE_COLORFILL_FRAME = []

FILTER_SATURATION_AMOUNT = [1]
FILTER_USE_SATURATION = [False]

FILTER_USE_TEMPERATURE = [False]
FILTER_TEMPERATURE_AMOUNT = [6500]

FILTER_USE_TINT = [False]
FILTER_TINT_AMOUNT = [0]

FILTER_USE_TINT = [False]
FILTER_TINT_AMOUNT = [1]

FILTER_USE_COLORBALANCE = [False]
FILTER_CYANRED_AMOUNT = [0]
FILTER_MAGENTAGREEN_AMOUNT = [0]
FILTER_BLUEYELLOW_AMOUNT = [0]

FILTER_EROSION_AMOUNT = [0]
FILTER_USE_EROSION = [False]

FILTER_DILATATION_AMOUNT = [0]
FILTER_USE_DILATATION = [False]

FILTER_DENOISE_LUMINANCE_AMOUNT = [0]
FILTER_DENOISE_COLOR_AMOUNT = [0]
FILTER_DENOISE_SMOOTH_AMOUNT = [5]
FILTER_DENOISE_LUMINANCE_AMOUNT_LAST = sys.maxsize
FILTER_DENOISE_COLOR_AMOUNT_LAST = sys.maxsize
FILTER_DENOISE_SMOOTH_AMOUNT_LAST = sys.maxsize
FILTER_USE_DENOISE = [False]

FILTER_SAVE_AMOUNT = [100]
FILTER_SAVE_AMOUNT_LAST = sys.maxsize

WATERMARK_SCALE_AMOUNT = [100]
WATERMARK_USE_LEFT_UPPER = [False]
WATERMARK_USE_RIGHT_UPPER = [False]
WATERMARK_USE_LEFT_DOWN = [False]
WATERMARK_USE_RIGHT_DOWN = [False]
WATERMARK_X_POSITION = 20
WATERMARK_Y_POSITION = 20

STICKER_ROTATE_AMOUNT = [0]
STICKER_SCALE_AMOUNT = [100]
STICKER_USE_LEFT_UPPER = [False]
STICKER_USE_RIGHT_UPPER = [False]
STICKER_USE_LEFT_DOWN = [False]
STICKER_USE_RIGHT_DOWN = [False]
STICKER_X_POSITION = 20
STICKER_Y_POSITION = 20

TRANSFORMATIONS_SCALE_AMOUNT_X = [1]
TRANSFORMATIONS_SCALE_AMOUNT_Y = [1]
TRANSFORMATIONS_USE_RATIO = [False]

NORMALIZATION_USE_EQUALIZE = [False]
NORMALIZATION_USE_AUTOCONTRAST = [False]
NORMALIZATION_USE_PRESERVETONE = [False]

UPSCALE_USE_TYPE_CHOICE_1 = [True]
UPSCALE_USE_TYPE_CHOICE_2 = [False]
UPSCALE_USE_TYPE_CHOICE_3 = [False]
UPSCALE_USE_TYPE_CHOICE_4 = [False]
UPSCALE_USE_TYPE_CHOICE_5 = [False]
UPSCALE_USE_TYPE_CHOICE_6 = [False]
UPSCALE_USE_AMOUNT = 2

COMBINE_DIRECTION_HORIZONTAL = [False]
COMBINE_DIRECTION_VERTICAL = [False]
COMBINE_MODE_BIGGEST = [False]
COMBINE_MODE_SMALLEST = [False]
COMBINE_MODE_NORESIZE = [False]
COMBINE_ORDER_NORMAL = [False]
COMBINE_ORDER_REVERSE =  [False]

FILTER_PIX_AMOUNT = [1]
FILTER_USE_PIX = [False]

FILTER_USE_FRAME = [False]
FILTER_FRAME_AMOUNT = [5]
FILTER_FRAME_COLOR = [(255, 255, 255, 255), 0xFFFFFF]

FILTER_USE_TEXTURES = [False]
FILTER_TEXTURE_AMOUNT = [1]
FILTER_TEXTURE_AMOUNT_LAST = sys.maxsize
FILTER_TEXTURE_CURRENT = 0
FILTER_TEXTURE_CURRENT_LAST = sys.maxsize

FILTER_USE_OVERLAY_TYPE_1 = [False]
FILTER_USE_OVERLAY_TYPE_2 = [False]
FILTER_USE_OVERLAY_TYPE_3 = [False]
FILTER_USE_OVERLAY_TYPE_4 = [False]
FILTER_USE_OVERLAY_TYPE_5 = [False]
FILTER_USE_OVERLAY_TYPE_6 = [False]
FILTER_USE_OVERLAY_TYPE_7 = [False]
FILTER_USE_OVERLAY_TYPE_8 = [False]
FILTER_USE_OVERLAY_TYPE_9 = [False]
FILTER_OVERLAY_AMOUNT = [1]
FILTER_OVERLAY_AMOUNT_LAST = sys.maxsize

MACRO_RECORD = False
MACRO_LIST = []

TOOLS_TEXT_VALUE = ""
TEXT_SCALE_AMOUNT = [0.8]
TEXT_X_POSITION = 20
TEXT_Y_POSITION = 20
FILTER_USE_TEXT = [False]
TEXT_USE_FONT = cv2.FONT_HERSHEY_DUPLEX
TEXT_USE_FONT_1 = [True]                        #sans-serif
TEXT_USE_FONT_2 = [False]                       #serif
TEXT_USE_FONT_3 = [False]                       #handwriting
TEXT_USE_FONT_4 = [False]                       #italic
TEXT_THICKNESS_AMOUNT = [1]                     #text thickness
TEXT_USE_COLOR = [(255,255,255,255), 0xFFFFFF]  #text color
TEXT_ADD_POSITION = [25]                        #how much pixel text move

FILTER_USE_HSV = [False]
hue_min_1 = [0]
hue_max_1 = [179]
sat_min_1 = [0]
sat_max_1 = [255]
val_min_1 = [0]
val_max_1 = [255]

### VARIABLES ###
temp_text_frame = np.zeros((0, 0, 4), np.uint8)
xStart = 5
yStart = 50
temp_filepath = "temp/temp.jpg"             # TEMP FILEPATH TO PREVIEW JPG IMG
colorfillCurrent = 0
colorfillCurrent_LAST = sys.maxsize
overlayCurrent = 0
overlayCurrent_LAST = sys.maxsize
CURRENT_ONLY_APPLY = [False]

##WATERMARK VARIABLES
temp_watermarkPath = ""                     # TEMP WATERMARK PATH
finalWatermark = ""
isWatermarkLoaded = False

isImageLoaded = False
temp_image = np.zeros((640,480), np.uint8)
temp_imageResized = np.zeros((640,480), np.uint8)
saveImageOnce = True
IAREA_CHANGE_STATE = 5                      #THIS CHECKS IF BUTTON FOR PREVIEW CHANGES WAS CLICKED (LAST CHANGE), STATE IS SET TO 5, BEACAUSE 5 MEANS MOUSE IS OUT OF THE RANGE
IAREA_ORIGINAL_STATE = 5                    #-        (COMPARE TO ORIGINAL)
IAREA_DENOISE_STATE = 5
IAREA_COLORFILL_STATE = 5
IAREA_TEXTURES_STATE = 5
IAREA_OVERLAYS_STATE = 5
isBatchModeActive = False
isLightModeActive = False
isListViewModeActive = False
imagesCurrent_LAST = sys.maxsize
viewHeight = 713

### MACRO VARIABLES ###
macrosPath = os.listdir('Macros/')
macrosCurrent = 0

### IMAGE VARIABLES ###
imagesPath = []
loadedImages = []
loadedImagesThumbnails = []
loadedImages.append(cv2.imread('Graphics/start-screen.png', cv2.IMREAD_UNCHANGED))
changesList = []
changesList.append(loadedImages)
imagesVersion = len(changesList) - 1
imagesCurrent = 0
currentImageResized = image_resize(changesList[imagesVersion][imagesCurrent], height=viewHeight)
currentImagePreview = np.zeros(currentImageResized.shape, np.uint8)
currentPreviewBuild = np.zeros(currentImageResized.shape, np.uint8)
backgroundImage = cv2.imread('Graphics/photo-background.png', cv2.IMREAD_UNCHANGED)

### GRAPHICS VARIABLES ###
texturesPath = []
texturesCurrent = 0
texturesCurrent_LAST = sys.maxsize
for top, dirs, files in os.walk('Graphics/textures/'):
    for file in files:
        texturesPath.append(os.path.join(top, file))
texturesPreview = cv2.imread(texturesPath[texturesCurrent], cv2.IMREAD_UNCHANGED)
texturesPreview = image_resize(texturesPreview, width=175)

overlaysPath = []
overlaysCurrent = 0
overlaysCurrent_LAST = sys.maxsize
for top, dirs, files in os.walk('Graphics/overlays/'):
    for file in files:
        overlaysPath.append(os.path.join(top, file))
overlaysPreview = cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED)
overlaysPreview = image_resize(overlaysPreview, width=200)

finalSticker = ""
stickersImages = []
stickersCurrent = 0
for top, dirs, files in os.walk('Graphics/stickers/'):
    for file in files:
        stickersImages.append(cv2.imread(os.path.join(top, file), -1))

cvui.init(WINDOW_MAIN)
while True:
    cvui.context(WINDOW_MAIN)
    if isLightModeActive == True:
        frameColor1 = (208, 208, 208)
        frameColor2 = (208, 208, 208, 208)
        windowText = (0x56, 0x56, 0x56)
        windowHeader = (0x84, 0x84, 0x84)
        windowBody = (0xAF, 0xAF, 0xAF)
        buttonDefault = (0xBC, 0xBC, 0xBC)
        buttonOut = (0xAC, 0xAC, 0xAC)
        buttonOver = (0xCD, 0xCD, 0xCD)
        textColor = 0x565656
        backgroundImage = cv2.imread('Graphics/photo-background_light.png', cv2.IMREAD_UNCHANGED)
        if isImageLoaded == False:
            image_reset()
    else:
        frameColor1 = (30, 30, 30)
        frameColor2 = (30, 30, 30, 30)
        windowText = (0xCE, 0xCE, 0xCE)
        windowHeader = (0x21, 0x21, 0x21)
        windowBody = (0x31, 0x31, 0x31)
        buttonDefault = (0x42, 0x42, 0x42)
        buttonOut = (0x52, 0x52, 0x52)
        buttonOver = (0x32, 0x32, 0x32)
        textColor = 0xc0c0c0
        backgroundImage = cv2.imread('Graphics/photo-background.png', cv2.IMREAD_UNCHANGED)
        if isImageLoaded == False:
            image_reset()

    FRAME_MAIN[:] = frameColor2

    # THIS IF-ELSE CHECKS WHETHER OR NOT THE BUTTON WAS CLICKED BY A MOUSE, AND DISPLAYS A DIFFERENT VERSION OF IMAGE FOR THE TIME BEING
    if IAREA_CHANGE_STATE == cvui.DOWN:
        currentImageResized = image_resize(changesList[len(changesList) - 2][imagesCurrent], height=viewHeight)
        currentImagePreview = np.zeros(currentImageResized.shape, np.uint8)
        currentImagePreview[:] = currentImageResized[:]
    elif IAREA_ORIGINAL_STATE == cvui.DOWN:
        currentImageResized = image_resize(changesList[0][imagesCurrent], height=viewHeight)
        currentImagePreview = np.zeros(currentImageResized.shape, np.uint8)
        currentImagePreview[:] = currentImageResized[:]
    else:
        currentImageResized = image_resize(changesList[imagesVersion][imagesCurrent], height=viewHeight)
        currentImagePreview = np.zeros(currentImageResized.shape, np.uint8)
        currentImagePreview[:] = currentImageResized[:]

    #? FILTERS PREVIEW GENERATION START ?#
    if FILTER_USE_BLUR[0]:
        currentImageResized = image_resize(filters.blur(changesList[imagesVersion][imagesCurrent], FILTER_BLUR_AMOUNT[0]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]

    if FILTER_USE_SHARPEN[0]:
        currentImageResized = image_resize(filters.sharpen(changesList[imagesVersion][imagesCurrent], FILTER_SHARPEN_AMOUNT[0]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]

    if FILTER_USE_BRIGHTNESS[0]:
        currentImageResized = image_resize(filters.brightness(changesList[imagesVersion][imagesCurrent], FILTER_BRIGHTNESS_AMOUNT[0]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]
    if FILTER_USE_CONTRAST[0]:
        currentImageResized = image_resize(filters.contrast(changesList[imagesVersion][imagesCurrent], FILTER_CONTRAST_AMOUNT[0]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]

    if FILTER_USE_TEXT[0]:
        currentImageResized = image_resize(filters.putText(temp_text_frame,changesList[imagesVersion][imagesCurrent],TOOLS_TEXT_VALUE, (int(TEXT_X_POSITION),
        int(TEXT_Y_POSITION)), TEXT_USE_FONT, TEXT_SCALE_AMOUNT[0], TEXT_USE_COLOR[0], TEXT_THICKNESS_AMOUNT[0], cv2.LINE_AA), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]

    if FILTER_USE_SEPIA[0]:
        currentImageResized = image_resize(filters.sepia(changesList[imagesVersion][imagesCurrent]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]
    if FILTER_USE_GRAYSCALE[0]:
        currentImageResized = image_resize(filters.grayscale(changesList[imagesVersion][imagesCurrent]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]
    if FILTER_USE_BLACKANDWHITE[0]:
        currentImageResized = image_resize(filters.blackandwhite(changesList[imagesVersion][imagesCurrent]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]
    if FILTER_USE_NEGATIVE[0]:
        currentImageResized = image_resize(filters.negative(changesList[imagesVersion][imagesCurrent]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]
    if FILTER_USE_EMBOSS[0]:
        currentImageResized = image_resize(filters.emboss(changesList[imagesVersion][imagesCurrent]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]
    if FILTER_USE_DIFF[0]:
        currentImageResized = image_resize(filters.diff(changesList[imagesVersion][imagesCurrent]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]

    if isWatermarkLoaded:
        currentImageResized = image_resize(tools.watermark_file(changesList[imagesVersion][imagesCurrent], finalWatermark, int(WATERMARK_X_POSITION), int(WATERMARK_Y_POSITION), False), height=713)
        currentImagePreview[:] = currentImageResized[:]

    if is_window_open(WINDOW_TOOLS_STICKER):
        currentImageResized = image_resize(tools.watermark_file(changesList[imagesVersion][imagesCurrent], finalSticker, int(STICKER_X_POSITION), int(STICKER_Y_POSITION), True), height=713)
        currentImagePreview[:] = currentImageResized[:]

    if FILTER_USE_SATURATION[0]:
        currentImageResized = image_resize(filters.color(changesList[imagesVersion][imagesCurrent], FILTER_SATURATION_AMOUNT[0]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]
    if FILTER_USE_TEMPERATURE[0]:
        currentImageResized = image_resize(filters.temperature(changesList[imagesVersion][imagesCurrent], FILTER_TEMPERATURE_AMOUNT[0]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]
    if FILTER_USE_TINT[0]:
        currentImageResized = image_resize(filters.tint(changesList[imagesVersion][imagesCurrent], FILTER_TINT_AMOUNT[0]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]
    if FILTER_USE_COLORBALANCE[0]:
        currentImageResized = image_resize(filters.colorbalance(changesList[imagesVersion][imagesCurrent], FILTER_CYANRED_AMOUNT[0], FILTER_MAGENTAGREEN_AMOUNT[0], FILTER_BLUEYELLOW_AMOUNT[0]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]

    if FILTER_USE_EROSION[0]:
        currentImageResized = image_resize(filters.erosion(changesList[imagesVersion][imagesCurrent], FILTER_EROSION_AMOUNT[0]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]
    if FILTER_USE_DILATATION[0]:
        currentImageResized = image_resize(filters.dilatation(changesList[imagesVersion][imagesCurrent], FILTER_DILATATION_AMOUNT[0]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]

    if NORMALIZATION_USE_EQUALIZE[0]:
        currentImageResized = image_resize(filters.histogram_normalization(changesList[imagesVersion][imagesCurrent]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]

    if NORMALIZATION_USE_AUTOCONTRAST[0]:
        if NORMALIZATION_USE_PRESERVETONE[0]:
            currentImageResized = image_resize(filters.histogram_autocontrast(changesList[imagesVersion][imagesCurrent], True), height=viewHeight)
            currentImagePreview[:] = currentImageResized[:]
        else:
            currentImageResized = image_resize(filters.histogram_autocontrast(changesList[imagesVersion][imagesCurrent], False), height=viewHeight)
            currentImagePreview[:] = currentImageResized[:]

    if FILTER_USE_DENOISE[0]:
        if (FILTER_DENOISE_LUMINANCE_AMOUNT[0] == FILTER_DENOISE_LUMINANCE_AMOUNT_LAST and FILTER_DENOISE_COLOR_AMOUNT[0] == FILTER_DENOISE_COLOR_AMOUNT_LAST and FILTER_DENOISE_SMOOTH_AMOUNT[0] == FILTER_DENOISE_SMOOTH_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST) or IAREA_DENOISE_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.denoise(changesList[imagesVersion][imagesCurrent], FILTER_DENOISE_LUMINANCE_AMOUNT[0], FILTER_DENOISE_COLOR_AMOUNT[0], FILTER_DENOISE_SMOOTH_AMOUNT[0]), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_DENOISE_LUMINANCE_AMOUNT_LAST = FILTER_DENOISE_LUMINANCE_AMOUNT[0]
            FILTER_DENOISE_COLOR_AMOUNT_LAST = FILTER_DENOISE_COLOR_AMOUNT[0]
            FILTER_DENOISE_SMOOTH_AMOUNT_LAST = FILTER_DENOISE_SMOOTH_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent

    if FILTER_USE_COLORFILL_TYPE_1[0]:
        colorfillCurrent = 1
        if (FILTER_COLORFILL_AMOUNT[0] == FILTER_COLORFILL_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and colorfillCurrent == colorfillCurrent_LAST) or IAREA_COLORFILL_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 1, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0]), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_COLORFILL_AMOUNT_LAST = FILTER_COLORFILL_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            colorfillCurrent_LAST = colorfillCurrent
    if FILTER_USE_COLORFILL_TYPE_2[0]:
        colorfillCurrent = 2
        if (FILTER_COLORFILL_AMOUNT[0] == FILTER_COLORFILL_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and colorfillCurrent == colorfillCurrent_LAST) or IAREA_COLORFILL_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 2, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0]), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_COLORFILL_AMOUNT_LAST = FILTER_COLORFILL_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            colorfillCurrent_LAST = colorfillCurrent
    if FILTER_USE_COLORFILL_TYPE_3[0]:
        colorfillCurrent = 3
        if (FILTER_COLORFILL_AMOUNT[0] == FILTER_COLORFILL_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and colorfillCurrent == colorfillCurrent_LAST) or IAREA_COLORFILL_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 3, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0]), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_COLORFILL_AMOUNT_LAST = FILTER_COLORFILL_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            colorfillCurrent_LAST = colorfillCurrent
    if FILTER_USE_COLORFILL_TYPE_4[0]:
        colorfillCurrent = 4
        if (FILTER_COLORFILL_AMOUNT[0] == FILTER_COLORFILL_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and colorfillCurrent == colorfillCurrent_LAST) or IAREA_COLORFILL_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 4, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0]), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_COLORFILL_AMOUNT_LAST = FILTER_COLORFILL_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            colorfillCurrent_LAST = colorfillCurrent
    if FILTER_USE_COLORFILL_TYPE_5[0]:
        colorfillCurrent = 5
        if (FILTER_COLORFILL_AMOUNT[0] == FILTER_COLORFILL_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and colorfillCurrent == colorfillCurrent_LAST) or IAREA_COLORFILL_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 5, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0]), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_COLORFILL_AMOUNT_LAST = FILTER_COLORFILL_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            colorfillCurrent_LAST = colorfillCurrent
    if FILTER_USE_COLORFILL_TYPE_6[0]:
        colorfillCurrent = 6
        if (FILTER_COLORFILL_AMOUNT[0] == FILTER_COLORFILL_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and colorfillCurrent == colorfillCurrent_LAST) or IAREA_COLORFILL_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 6, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0]), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_COLORFILL_AMOUNT_LAST = FILTER_COLORFILL_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            colorfillCurrent_LAST = colorfillCurrent
    if FILTER_USE_COLORFILL_TYPE_7[0]:
        colorfillCurrent = 7
        if (FILTER_COLORFILL_AMOUNT[0] == FILTER_COLORFILL_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and colorfillCurrent == colorfillCurrent_LAST) or IAREA_COLORFILL_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 7, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0]), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_COLORFILL_AMOUNT_LAST = FILTER_COLORFILL_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            colorfillCurrent_LAST = colorfillCurrent
    if FILTER_USE_COLORFILL_TYPE_8[0]:
        colorfillCurrent = 8
        if (FILTER_COLORFILL_AMOUNT[0] == FILTER_COLORFILL_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and colorfillCurrent == colorfillCurrent_LAST) or IAREA_COLORFILL_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 8, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0]), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_COLORFILL_AMOUNT_LAST = FILTER_COLORFILL_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            colorfillCurrent_LAST = colorfillCurrent
    if FILTER_USE_COLORFILL_TYPE_9[0]:
        colorfillCurrent = 9
        if (FILTER_COLORFILL_AMOUNT[0] == FILTER_COLORFILL_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and colorfillCurrent == colorfillCurrent_LAST) or IAREA_COLORFILL_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_COLORFILL_AMOUNT[0], FILTER_COLORFILL_FRAME, 9, FILTER_COLORFILL_COLOR[0], FILTER_COLORFILL_COLOR_2[0], FILTER_USE_COLORFILL_GRADIENT[0]), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_COLORFILL_AMOUNT_LAST = FILTER_COLORFILL_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            colorfillCurrent_LAST = colorfillCurrent

    if FILTER_USE_PIX[0]:
        currentImageResized = image_resize(filters.pix(changesList[imagesVersion][imagesCurrent], FILTER_PIX_AMOUNT[0]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]

    if FILTER_USE_FRAME[0]:
        currentImageResized = image_resize(tools.frame(changesList[imagesVersion][imagesCurrent], FILTER_FRAME_AMOUNT[0], FILTER_FRAME_COLOR[0]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]

    if FILTER_USE_TEXTURES[0]:
        if (FILTER_TEXTURE_AMOUNT[0] == FILTER_TEXTURE_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and texturesCurrent == texturesCurrent_LAST) or IAREA_TEXTURES_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_TEXTURE_AMOUNT[0], cv2.imread(texturesPath[texturesCurrent], cv2.IMREAD_UNCHANGED), 2), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            imagesCurrent_LAST = imagesCurrent
            FILTER_TEXTURE_AMOUNT_LAST = FILTER_TEXTURE_AMOUNT[0]
            texturesCurrent_LAST = texturesCurrent

    if FILTER_USE_OVERLAY_TYPE_1[0]:
        overlayCurrent = 1
        if (FILTER_OVERLAY_AMOUNT[0] == FILTER_OVERLAY_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and overlaysCurrent == overlaysCurrent_LAST and overlayCurrent == overlayCurrent_LAST) or IAREA_OVERLAYS_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 1), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_OVERLAY_AMOUNT_LAST = FILTER_OVERLAY_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            overlaysCurrent_LAST = overlaysCurrent
            overlayCurrent_LAST = overlayCurrent
    if FILTER_USE_OVERLAY_TYPE_2[0]:
        overlayCurrent = 2
        if (FILTER_OVERLAY_AMOUNT[0] == FILTER_OVERLAY_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and overlaysCurrent == overlaysCurrent_LAST and overlayCurrent == overlayCurrent_LAST) or IAREA_OVERLAYS_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 2), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_OVERLAY_AMOUNT_LAST = FILTER_OVERLAY_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            overlaysCurrent_LAST = overlaysCurrent
            overlayCurrent_LAST = overlayCurrent
    if FILTER_USE_OVERLAY_TYPE_3[0]:
        overlayCurrent = 3
        if (FILTER_OVERLAY_AMOUNT[0] == FILTER_OVERLAY_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and overlaysCurrent == overlaysCurrent_LAST and overlayCurrent == overlayCurrent_LAST) or IAREA_OVERLAYS_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 3), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_OVERLAY_AMOUNT_LAST = FILTER_OVERLAY_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            overlaysCurrent_LAST = overlaysCurrent
            overlayCurrent_LAST = overlayCurrent
    if FILTER_USE_OVERLAY_TYPE_4[0]:
        overlayCurrent = 4
        if (FILTER_OVERLAY_AMOUNT[0] == FILTER_OVERLAY_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and overlaysCurrent == overlaysCurrent_LAST and overlayCurrent == overlayCurrent_LAST) or IAREA_OVERLAYS_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 4), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_OVERLAY_AMOUNT_LAST = FILTER_OVERLAY_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            overlaysCurrent_LAST = overlaysCurrent
            overlayCurrent_LAST = overlayCurrent
    if FILTER_USE_OVERLAY_TYPE_5[0]:
        overlayCurrent = 5
        if (FILTER_OVERLAY_AMOUNT[0] == FILTER_OVERLAY_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and overlaysCurrent == overlaysCurrent_LAST and overlayCurrent == overlayCurrent_LAST) or IAREA_OVERLAYS_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 5), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_OVERLAY_AMOUNT_LAST = FILTER_OVERLAY_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            overlaysCurrent_LAST = overlaysCurrent
            overlayCurrent_LAST = overlayCurrent
    if FILTER_USE_OVERLAY_TYPE_6[0]:
        overlayCurrent = 6
        if (FILTER_OVERLAY_AMOUNT[0] == FILTER_OVERLAY_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and overlaysCurrent == overlaysCurrent_LAST and overlayCurrent == overlayCurrent_LAST) or IAREA_OVERLAYS_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 6), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_OVERLAY_AMOUNT_LAST = FILTER_OVERLAY_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            overlaysCurrent_LAST = overlaysCurrent
            overlayCurrent_LAST = overlayCurrent
    if FILTER_USE_OVERLAY_TYPE_7[0]:
        overlayCurrent = 7
        if (FILTER_OVERLAY_AMOUNT[0] == FILTER_OVERLAY_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and overlaysCurrent == overlaysCurrent_LAST and overlayCurrent == overlayCurrent_LAST) or IAREA_OVERLAYS_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 7), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_OVERLAY_AMOUNT_LAST = FILTER_OVERLAY_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            overlaysCurrent_LAST = overlaysCurrent
            overlayCurrent_LAST = overlayCurrent
    if FILTER_USE_OVERLAY_TYPE_8[0]:
        overlayCurrent = 8
        if (FILTER_OVERLAY_AMOUNT[0] == FILTER_OVERLAY_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and overlaysCurrent == overlaysCurrent_LAST and overlayCurrent == overlayCurrent_LAST) or IAREA_OVERLAYS_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 8), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_OVERLAY_AMOUNT_LAST = FILTER_OVERLAY_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            overlaysCurrent_LAST = overlaysCurrent
            overlayCurrent_LAST = overlayCurrent
    if FILTER_USE_OVERLAY_TYPE_9[0]:
        overlayCurrent = 9
        if (FILTER_OVERLAY_AMOUNT[0] == FILTER_OVERLAY_AMOUNT_LAST and imagesCurrent == imagesCurrent_LAST and overlaysCurrent == overlaysCurrent_LAST and overlayCurrent == overlayCurrent_LAST) or IAREA_OVERLAYS_STATE == cvui.DOWN:
            currentImagePreview[:] = currentPreviewBuild[:]
        else:
            currentPreviewBuild = image_resize(filters.blend(changesList[imagesVersion][imagesCurrent], FILTER_OVERLAY_AMOUNT[0], cv2.imread(overlaysPath[overlaysCurrent], cv2.IMREAD_UNCHANGED), 9), height=viewHeight)
            currentImagePreview[:] = currentPreviewBuild[:]
            FILTER_OVERLAY_AMOUNT_LAST = FILTER_OVERLAY_AMOUNT[0]
            imagesCurrent_LAST = imagesCurrent
            overlaysCurrent_LAST = overlaysCurrent
            overlayCurrent_LAST = overlayCurrent

    if FILTER_USE_HSV[0]:
        currentImageResized = image_resize(tools.hsv(changesList[imagesVersion][imagesCurrent], hue_min_1[0], sat_min_1[0], val_min_1[0], hue_max_1[0], sat_max_1[0], val_max_1[0]), height=viewHeight)
        currentImagePreview[:] = currentImageResized[:]

    cvui.image(FRAME_MAIN, 5, 50, backgroundImage)
    if isListViewModeActive:
        xStart, yStart = centering_image(currentImagePreview, 1100, 513, 5, 250)
    else:
        xStart, yStart = centering_image(currentImagePreview, 1100, 713, 5, 50)
    cvui.image(FRAME_MAIN, xStart, yStart, currentImagePreview)

    if isBatchModeActive == False:
        generate_interface()
    else:
        generate_batch_interface()

    cvui.imshow(WINDOW_MAIN, FRAME_MAIN)

    #? WINDOW HANDLING START ?#
    if is_window_open(WINDOW_SETTINGS_SHARPNESS) == True:
        generate_interface_settings_sharpness()
    else:
        FILTER_USE_BLUR = [False]
        FILTER_USE_SHARPEN = [False]

    if is_window_open(WINDOW_SETTINGS_BRIGHTNESS) == True:
        generate_interface_settings_bright_contr()
    else:
        FILTER_USE_BRIGHTNESS = [False]
        FILTER_USE_CONTRAST = [False]

    if is_window_open(WINDOW_SETTINGS_COMMON) == True:
        generate_interface_settings_common()
    else:
        FILTER_USE_SEPIA = [False]
        FILTER_USE_GRAYSCALE = [False]
        FILTER_USE_BLACKANDWHITE = [False]
        FILTER_USE_NEGATIVE = [False]
        FILTER_USE_EMBOSS = [False]
        FILTER_USE_DIFF = [False]

    if is_window_open(WINDOW_SETTINGS_COLOR) == True:
        generate_interface_settings_color()
    else:
        FILTER_USE_SATURATION = [False]
        FILTER_USE_TINT = [False]
        FILTER_USE_TEMPERATURE = [False]
        FILTER_USE_COLORBALANCE = [False]

    if is_window_open(WINDOW_SETTINGS_MORPH) == True:
        generate_interface_settings_morph()
    else:
        FILTER_USE_EROSION = [False]
        FILTER_USE_DILATATION = [False]

    if is_window_open(WINDOW_SETTINGS_DENOISE) == True:
        generate_interface_settings_denoise()
    else:
        FILTER_USE_DENOISE = [False]
        FILTER_USE_LUM = [False]

    if is_window_open(WINDOW_SETTINGS_SAVE) == True:
        generate_interface_settings_save()
    else:
        FILTER_SAVE_AMOUNT_LAST = sys.maxsize

    if is_window_open(WINDOW_SETTINGS_BATCHSAVE) == True:
        generate_interface_settings_batchsave()
    else:
        FILTER_SAVE_AMOUNT_LAST = sys.maxsize

    if is_window_open(WINDOW_SETTINGS_PREVIEW) == True:
        generate_interface_settings_preview()
    else:
        if len(os.listdir('temp')) != 1:
            os.remove(temp_filepath)

    if is_window_open(WINDOW_TOOLS_WATERMARK) == True:
        generate_interface_tools_watermark()
    else:
        isWatermarkLoaded = False

    if is_window_open(WINDOW_TOOLS_STICKER) == True:
        generate_interface_tools_sticker()
    else:
        isStickerLoaded = False

    if is_window_open(WINDOW_SETTINGS_COLORFILL) == True:
        generate_interface_settings_colorfill()
    else:
        FILTER_USE_COLORFILL_TYPE_1 = [False]
        FILTER_USE_COLORFILL_TYPE_2 = [False]
        FILTER_USE_COLORFILL_TYPE_3 = [False]
        FILTER_USE_COLORFILL_TYPE_4 = [False]
        FILTER_USE_COLORFILL_TYPE_5 = [False]
        FILTER_USE_COLORFILL_TYPE_6 = [False]
        FILTER_USE_COLORFILL_TYPE_7 = [False]
        FILTER_USE_COLORFILL_TYPE_8 = [False]
        FILTER_USE_COLORFILL_TYPE_9 = [False]

    if is_window_open(WINDOW_TOOLS_TRANSFORMATIONS) == True:
        generate_interface_tools_transformations()
    else:
        pass

    if is_window_open(WINDOW_FILTERS_NORMALIZATION) == True:
        generate_interface_filters_normalization()
    else:
        NORMALIZATION_USE_PRESERVETONE = [False]
        NORMALIZATION_USE_EQUALIZE = [False]
        NORMALIZATION_USE_AUTOCONTRAST = [False]

    if is_window_open(WINDOW_TOOLS_UPSCALE) == True:
        generate_interface_tools_upscale()
    else:
        UPSCALE_USE_TYPE_CHOICE_1 = [True]
        UPSCALE_USE_TYPE_CHOICE_2 = [False]
        UPSCALE_USE_TYPE_CHOICE_3 = [False]
        UPSCALE_USE_TYPE_CHOICE_4 = [False]
        UPSCALE_USE_TYPE_CHOICE_5 = [False]
        UPSCALE_USE_TYPE_CHOICE_6 = [False]
        UPSCALE_USE_TYPE_AMOUNT = 2

    if is_window_open(WINDOW_TOOLS_COMBINE) == True:
        generate_interface_tools_combine()
    else:
        pass

    if is_window_open(WINDOW_SETTINGS_PIX) == True:
        generate_interface_settings_pix()
    else:
        FILTER_USE_PIX = [False]

    if is_window_open(WINDOW_SETTINGS_FRAME) == True:
        generate_interface_settings_frame()
    else:
        FILTER_USE_FRAME = [False]

    if is_window_open(WINDOW_SETTINGS_TEXTURES) == True:
        generate_interface_settings_textures()
    else:
        FILTER_USE_TEXTURES = [False]

    if is_window_open(WINDOW_SETTINGS_OVERLAYS) == True:
        generate_interface_settings_overlays()
    else:
        FILTER_USE_OVERLAY_TYPE_1 = [False]
        FILTER_USE_OVERLAY_TYPE_2 = [False]
        FILTER_USE_OVERLAY_TYPE_3 = [False]
        FILTER_USE_OVERLAY_TYPE_4 = [False]
        FILTER_USE_OVERLAY_TYPE_5 = [False]
        FILTER_USE_OVERLAY_TYPE_6 = [False]
        FILTER_USE_OVERLAY_TYPE_7 = [False]
        FILTER_USE_OVERLAY_TYPE_8 = [False]
        FILTER_USE_OVERLAY_TYPE_9 = [False]

    if is_window_open(WINDOW_SETTINGS_MACRO) == True:
        generate_interface_tools_macro()
    else:
        pass

    if is_window_open(WINDOW_SETTINGS_TEXT) == True:
        generate_interface_tools_text()
    else:
        FILTER_USE_TEXT = [False]

    if is_window_open(WINDOW_SETTINGS_ABOUT) == True:
        generate_interface_settings_about()
    else:
        pass

    if is_window_open(WINDOW_SETTINGS_HSV) == True:
        generate_interface_tools_hsv()
    else:
        FILTER_USE_HSV = [False]
    #? WINDOW HANDLING END ?#

    #? KEYBOARD SHORTCUTS START ?#
    key = cv2.waitKey(45)

    if key == 27 or cv2.getWindowProperty(WINDOW_MAIN, cv2.WND_PROP_ASPECT_RATIO) < 0:
        break

    if isBatchModeActive == False:
        if key == ord('b') or key == ord('B'):
            if isImageLoaded == False:
                isBatchModeActive = True
            elif ask_window("Switch to batch edition?", "You are about to switch to batch edition mode, all unsaved progress will be lost.", 'okcancel') == True:
                image_reset()
                isBatchModeActive = True
            else:
                pass
        if key == ord('s') or key == ord('S'):
            if isImageLoaded:
                open_window(WINDOW_SETTINGS_SAVE)
            else:
                message_window('CAN NOT SAVE', 'You need to load your image first!', 'warning')

    else:
        if key == ord('b') or key == ord('B'):
            if isImageLoaded == False:
                isBatchModeActive = False
                isListViewModeActive = False
            elif ask_window("Switch to single edition?", "You are about to switch to single edition mode, all unsaved progress will be lost.", 'okcancel') == True:
                image_reset()
                isBatchModeActive = False
                isListViewModeActive = False
        else:
            pass

        if key == ord('v') or key == ord('V'):
            if isImageLoaded == True:
                isListViewModeActive = not(isListViewModeActive)
            else:
                message_window("NO IMAGES LOADED", "You need to load your images first.", 'info')
        if key == ord('s') or key == ord('S'):
            if isImageLoaded:
                open_window(WINDOW_SETTINGS_BATCHSAVE)
            else:
                message_window('CAN NOT SAVE', 'You need to load your image first!', 'warning')
        if key == ord('.'):
            if (imagesCurrent + 1 < len(loadedImages)):
                imagesCurrent += 1
        if key == ord(','):
            if (imagesCurrent - 1 >= 0):
                imagesCurrent -= 1

    if key == ord('z') or key == ord('Z'):
        if imagesVersion > 0:
            imagesVersion -= 1

    if key == ord('y') or key == ord('Y'):
        if imagesVersion != len(changesList) - 1:
            imagesVersion += 1

    if key == ord('r') or key == ord('R'):
        imagesVersion = 0

    if key == ord('t') or key == ord('T'):
        imagesVersion = len(changesList) - 1

    if key == ord('u') or key == ord('U'):
        IAREA_CHANGE_STATE = cvui.DOWN

    if key == ord('i') or key == ord('I'):
        IAREA_ORIGINAL_STATE = cvui.DOWN

    if key == ord('o') or key == ord('O'):
        load_image()

    if key == ord('l') or key == ord('L'):
        isLightModeActive = not(isLightModeActive)
    #? KEYBOARD SHORTCUTS END ?#

    #? MOUSE EVENTS START ?#
    if cvui.mouse(cvui.MIDDLE_BUTTON, cvui.DOWN):
        colorsBGR = FRAME_MAIN[cvui.mouse().y, cvui.mouse().x]
        colorsBGR = (int(colorsBGR[0]), int(colorsBGR[1]), int(colorsBGR[2]), 255)
        colorsRGB = (int(colorsBGR[2]), int(colorsBGR[1]), int(colorsBGR[0]), 255)
        FILTER_COLORFILL_COLOR = (colorsBGR, rgb2hex(colorsBGR[2], colorsBGR[1], colorsBGR[0]))
        FILTER_FRAME_COLOR = (colorsBGR, rgb2hex(colorsBGR[2], colorsBGR[1], colorsBGR[0]))
        TEXT_USE_COLOR = (colorsRGB, rgb2hex(colorsBGR[2], colorsBGR[1], colorsBGR[0]))
    #? MOUSE EVENTS END ?#
