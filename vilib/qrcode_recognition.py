import cv2
from pyzbar import pyzbar

'''Define parameters for qrcode recognition object'''
qrcode_obj_parameter = {}
qrcode_obj_parameter['x'] = 0   # the largest block center x-axis coordinate
qrcode_obj_parameter['y'] = 0   # the largest block center y-axis coordinate
qrcode_obj_parameter['w'] = 0     # the largest block pixel width
qrcode_obj_parameter['h'] = 0     # the largest block pixel height
qrcode_obj_parameter['data'] = "None" # recognition result


def qrcode_recognize(img, border_rgb=(255, 0, 0)):
    # Detect and decode QR codes
    barcodes = pyzbar.decode(img)

    if len(barcodes) > 0:
        for barcode in barcodes:
            # Return the coordinate(top left), width and height of contour
            (x, y, w, h) = barcode.rect
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            # the barcode data is a byte object, converted into a string
            barcodeData = barcode.data.decode("utf-8")
            # barcodeType = barcode.type
            text = f"{barcodeData}"

            if len(text) > 0:
                qrcode_obj_parameter['data'] = text
                qrcode_obj_parameter['h'] = h
                qrcode_obj_parameter['w'] = w
                qrcode_obj_parameter['x'] = x 
                qrcode_obj_parameter['y'] = y
                cv2.putText(
                        img, # image
                        text, # text
                        (x, y - 10), # origin
                        cv2.FONT_HERSHEY_SIMPLEX, # font
                        0.5, # font_scale
                        border_rgb, # font_color
                        1, # thickness
                        cv2.LINE_AA, # line_type: LINE_8 (default), LINE_4, LINE_AA
                    )
            else:
                qrcode_obj_parameter['data'] = "None"
                qrcode_obj_parameter['x'] = 0
                qrcode_obj_parameter['y'] = 0
                qrcode_obj_parameter['w'] = 0
                qrcode_obj_parameter['h'] = 0
        return img
    else:
        return img
