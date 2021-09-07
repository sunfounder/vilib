from vilib import Vilib
from picrawler import Picrawler
from time import sleep

def main():


    crawler = Picrawler([10,11,12,4,5,6,1,2,3,7,8,9]) 

    Vilib.camera_start()
    Vilib.display()
    Vilib.color_detect("red")

    # Vilib.detect_obj_parameter['color_x'] = int(x + w/2)   # 色块中心坐标 x
    # Vilib.detect_obj_parameter['color_y'] = int(y + h/2)   # 中心坐标 y
    # Vilib.detect_obj_parameter['color_w'] = w              # 宽
    # Vilib.detect_obj_parameter['color_h'] = h              # 高
    # Vilib.detect_obj_parameter['color_n'] = 0              # 色块个数

    while True:
        if Vilib.detect_obj_parameter['color_n'] != 0:
            w = Vilib.detect_obj_parameter['color_w']
            h = Vilib.detect_obj_parameter['color_h']
            
            if w*h > 100*100: 
                crawler.do_action('backward',2,speed=100) 

        sleep(0.2)



if __name__ == "__main__":
    main()