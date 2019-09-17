import PIL.ImageGrab
import time


def screenshot(timestep):
    while(True):
        time.sleep(timestep)
        im = PIL.ImageGrab.grab()     
        im.show() 

def main():
    screenshot(10)

if __name__ == '__main__':
    main()