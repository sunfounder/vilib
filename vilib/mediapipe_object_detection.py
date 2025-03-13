# https://ai.google.dev/edge/mediapipe/solutions/vision/object_detector/python

import cv2
import numpy as np
import mediapipe as mp
import time


class MediapipeObjectDetection:

    # wget -q -O efficientdet.tflite -q https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/int8/1/efficientdet_lite0.tflite
    DEFAULT_MODEL = '/opt/vilib/efficientdet_lite0.tflite'
    
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480

    colors = [(0,255,255),(255,0,0),(0,255,64),(255,255,0),
        (255,128,64),(128,128,255),(255,128,255),(255,128,128)]

    def __init__(self, 
                 model:str=DEFAULT_MODEL,
                 max_results:int=10,
                 score_threshold:float=0.3,
                 width:int=CAMERA_WIDTH,
                 height:int=CAMERA_HEIGHT,
                 ):
        """
        Args:
            img: The input image.
            max_results: Max number of detection results.
            score_threshold: The score threshold of detection results.
            model: Name of the TFLite object detection model.
            width: The width of the frame captured from the camera.
            height: The height of the frame captured from the camera.
        """

        # Initialize the object detection model

        BaseOptions = mp.tasks.BaseOptions
        ObjectDetector = mp.tasks.vision.ObjectDetector
        ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = ObjectDetectorOptions(
            base_options=BaseOptions(model_asset_path=model),
            max_results=max_results,
            score_threshold=score_threshold,
            running_mode=VisionRunningMode.IMAGE)

        self.detector = ObjectDetector.create_from_options(options)


    def detect(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        result = self.detector.detect(mp_image)
        return result

    def draw(self, image, detection_result, x_boom:int=1, y_boom:int=1):
        for i, detection in enumerate(detection_result.detections):
            # Draw bounding_box
            bbox = detection.bounding_box
            start_point = int(bbox.origin_x*x_boom), int(bbox.origin_y*y_boom)
            end_point = int(bbox.origin_x*x_boom) + int(bbox.width*x_boom), int(bbox.origin_y*y_boom) + int(bbox.height*y_boom)
            # Use the orange color for high visibility.
            cv2.rectangle(image, 
                          start_point, 
                          end_point, 
                          self.colors[i%7], 
                          2
                          )

            # Draw label and score
            category = detection.categories[0]
            category_name = category.category_name
            probability = round(category.score, 2)
            result_text = category_name + ' (' + str(probability) + ')'
            text_location = (10 + int(bbox.origin_x*x_boom),
                            18 + int(bbox.origin_y*y_boom))
            cv2.putText(image, 
                        result_text, 
                        text_location, 
                        cv2.FONT_HERSHEY_DUPLEX,
                        0.8, 
                        self.colors[i%7],
                        1, 
                        cv2.LINE_AA)

        return image  



if __name__ == '__main__':
    from picamera2 import MappedArray, Picamera2, Preview
    import libcamera
    import time
    import cv2

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
                                main={"size": (640, 480), "format": "RGB888"},
                                transform=libcamera.Transform(hflip=True, vflip=True)
                                )
    picam2.configure(config)
    picam2.start()

    detector = MediapipeObjectDetection()
    framecount = 0
    fps = 0.0
    start_time = time.time()
    while True:
        img = picam2.capture_array()
        result = detector.detect(img)
        img = detector.draw(img, result, x_boom=1, y_boom=1)

        # calculate fps
        framecount += 1
        elapsed_time = float(time.time() - start_time)
        if (elapsed_time > 1):
            fps = round(framecount/elapsed_time, 1)
            framecount = 0
            start_time = time.time()

        cv2.putText(
                img, # image
                f"FPS: {fps}", # text
                (520, 20), # origin
                cv2.FONT_HERSHEY_SIMPLEX, # font
                0.6, # font_scale
                (255, 255, 255), # font_color
                1, # thickness
                cv2.LINE_AA, # line_type: LINE_8 (default), LINE_4, LINE_AA
            )            

        cv2.imshow('image', img)
        cv2.waitKey(1)

