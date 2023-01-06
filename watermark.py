from PIL import Image
import glob
import numpy as np
import cv2

def watermark_file(background, logo, x_pos, y_pos):

    background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
    background = Image.fromarray(background, 'RGB')

    position = (x_pos, y_pos)

    background.paste(logo, position, logo)

    final = np.array(background)
    final = cv2.cvtColor(final, cv2.COLOR_RGB2BGR)
    return final

def watermark_folder(folder_path, logo_path, x_pos, y_pos, output_folder):
    
    images = []
    for f in glob.iglob(folder_path):
        images.append(np.asarray(Image.open(f)))

    images = np.array(images)
    logo = Image.open(logo_path)

    position = (x_pos, y_pos)

    for x in images:
        x.paste(logo, position, logo)
        x.save(output_folder)

    return True