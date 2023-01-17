import argparse
from PIL import Image, ImageEnhance, ImageOps
import preprocess
import os 
import numpy as np
import cv2

class Steganography:
    
    BLACK_PIXEL = (0, 0, 0)
    EMPTY_PIXEL = (169,169,169,0)
    RESOLUTION = (1920,1080)

    def _int_to_bin(self, rgb):
        """Convert an integer tuple to a binary (string) tuple.

        :param rgb: An integer tuple like (220, 110, 96, 220)
        :return: A string tuple like ("00101010", "11101011", "00010110", "00101010")
        """
        if len(rgb) == 3:
            r, g, b,  = rgb
            return f'{r:08b}', f'{g:08b}', f'{b:08b}'
        else:
            r, g, b, a = rgb
            return f'{r:08b}', f'{g:08b}', f'{b:08b}', f'{a:08b}'

    def _bin_to_int(self, rgb):
        """Convert a binary (string) tuple to an integer tuple.

        :param rgb: A  string tuple like ("00101010", "11101011", "00010110", "00101010")
        :return: Return an int tuple like (220, 110, 96, 220)
        """
        if len(rgb) == 3:
            r, g, b, = rgb
            return int(r, 2), int(g, 2), int(b, 2)
        else:
            r, g, b, a = rgb
            return int(r, 2), int(g, 2), int(b, 2), int(a, 2)    


    def _decode_rgb(self, rgb):
        """decode an image.

        :param rgb: An integer tuple like (220, 110, 96, 255)
        :return: An integer tuple with the two RGB values merged.
        """
        if len(rgb) == 3:
            r, g, b = self._int_to_bin(rgb)
            new_rgb = r[5:] + '0000', g[5:] + '0000', b[5:] + '0000'
            return self._bin_to_int(new_rgb)
        elif len(rgb) == 4:
            r, g, b, a = self._int_to_bin(rgb)
            #@scoop
            #account for the alpha channel that might have been added during the encoding process
            new_rgba = r[5:] + '0000', g[5:] + '0000', b[5:] + '0000', '11111111'
            return self._bin_to_int(new_rgba)

    def _decode_rgb_half(self, rgb_top, rgb_bottom):
        """decode an image.

        :param rgb: Two integer tuples like (220, 110, 96, 255),  (213, 133, 96, 255)
        :return: An integer tuple with the two RGB values merged 
        """
        if len(rgb_top) == 3:
            r1, g1, b1 = self._int_to_bin(rgb_top)
            r2, g2, b2 = self._int_to_bin(rgb_bottom)
            new_rgb = r1[6:]+r2[6:] + '0000', g1[6:]+g2[6:] + '0000', b1[6:]+b2[6:] +'0000'
            return self._bin_to_int(new_rgb)
        elif len(rgb_top) == 4:
            r1, g1, b1, a1 = self._int_to_bin(rgb_top)
            r2, g2, b2, a2 = self._int_to_bin(rgb_bottom)
            #@scoop
            #account for the alpha channel that might have been added during the encoding process
            r = r1[4:6] + r2[6:] + '0000' 
            new_rgba = r1[6:]+r2[6:] + '0000', g1[6:]+g2[6:] + '0000', b1[6:]+b2[6:]+'0000', '11111111'
            return self._bin_to_int(new_rgba)

    def crop(self, new_image, pixel_map):
         
        print(pixel_map[0,0], pixel_map[0,1], pixel_map[0,2]) 
        ww = pixel_map[0,0]
        hh = pixel_map[0,1]
        w , h = '', ''
        for i in ww:
            if i<10:
                w+=str(i) 
        for i in hh:
            if i<10:
                h+=str(i)
        w, h = int(w), int(h)
        print(w,h)

        return new_image.crop((0, 0, w, h))
 

    def decode(self, image):
        """decode an image.

        :param image: The input image.
        :return: The unmerged/extracted image.
        """
        pixel_map = image.load()

        # Create the new image and load the pixel map
        new_image = Image.new(image.mode, (self.RESOLUTION[0], int(self.RESOLUTION[1]/2))) 
        new_map = new_image.load()

        for i in range(image.size[0]): #w
            for j in range(int(np.floor(image.size[1]/2))): #h
                new_map[i, j] = self._decode_rgb_half(pixel_map[i,j],pixel_map[i,j+(self.RESOLUTION[1]/2-1)])
                # new_map[i, j] = self._decode_rgb_half(pixel_map[i, j],pixel_map[i,j+539])

        return Image.fromarray(cv2.cvtColor(np.array(self.crop(new_image, pixel_map)), cv2.COLOR_BGR2RGB))


def main():
    parser = argparse.ArgumentParser(description='Steganography')
    subparser = parser.add_subparsers(dest='command')

    #debug
    debug = subparser.add_parser('test')
    debug.add_argument('-img', required=True, help='name of the img file to test decoding. e.g. test.png')

    unmerge = subparser.add_parser('decode')
    unmerge.add_argument('--video', required=True, help='Name of the video file you want to decode. (e.g. sea.mov)')
    unmerge.add_argument('--seconds', required=True, help='Seconds in video to decode(e.g. --seconds 2) Only accepts one integer at a time.')
    unmerge.add_argument('--output', help='Desired output destination path in your computer')

    args = parser.parse_args()

    #debug
    if args.command == 'test':
        tmppath = os.path.join(os.getcwd(),args.img)
        img = Image.open(tmppath)
        Steganography().decode(img).show()


    if args.command == 'decode':
        #method1 : no save. read from numpy. cons: low quality wth
        images = preprocess.prepareFrames(args.video,args.seconds)
        
        for i in images:
            img = Image.fromarray(i)
            # img.show()
            Steganography().decode(img).show()


        #method2: save to png then read 
        # preprocess.prepareFrames_save(args.video,args.seconds)
        # path = os.listdir(os.path.join(os.getcwd(),'tmp'))
        # for i in path:
        #     if i.endswith(".png"):
        #         img = Image.open(os.path.join('tmp',i)).convert('RGBA')
        #         # img.show()
        #         Steganography().decode(img).save(args.output, subsampling=0, quality=100)
        #         Steganography().decode(img).show()



if __name__ == '__main__':
    main()