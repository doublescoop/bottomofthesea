import cv2
import os 
from PIL import Image
from numpy import imag


def prepareFrames(videofile: str, second: int) -> list:
    path = os.path.join(os.getcwd(),videofile)
    video = cv2.VideoCapture(path)

    totalFrames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    FPS = int(video.get(cv2.CAP_PROP_FPS))
    
    prefix = os.path.splitext(videofile)[0]
    start = int(FPS*(int(second)-1))

    images = []
    if start < totalFrames:
        for i in range(FPS):
            video.set(cv2.CAP_PROP_POS_FRAMES,start+i)
            img = video.read()[1]
            # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Image.fromarray(img).show()
            images.append(img)

    # print('preparing frames',len(images),images)

    return images
    
def prepareFrames_save(videofile: str, second: int):
    path = os.path.join(os.getcwd(),videofile)
    video = cv2.VideoCapture(path)

    totalFrames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f'{totalFrames} frames in total')

    FPS = int(video.get(cv2.CAP_PROP_FPS))
    print(f'{FPS} frames per second')
    
    prefix = os.path.splitext(videofile)[0]
    start = int(FPS*(int(second)-1))

    images = []
    os.makedirs('tmp', exist_ok=True)
    if start < totalFrames:
        for i in range(FPS):
            video.set(cv2.CAP_PROP_POS_FRAMES,start+i)
            img = video.read()[1]

            #save png ver test quality 
            cv2.imwrite(os.path.join(os.path.split(path)[0],'tmp', "{}.png".format(str(i).zfill(4))), img, [int(cv2.IMWRITE_PNG_COMPRESSION),0])


def prepareFrames_ffmpeg(videofile:str, second: int):
    path = os.path.join(os.getcwd(),videofile)

