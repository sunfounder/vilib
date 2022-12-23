Read QR Code
=======================

The full name of QR Code is Quick Response Code, which is a coding method. It can store more information and represent more data types than the traditional Bar Code.

As a new information storage, transmission and identification technology, QR Code has attracted the attention of many countries in the world since its birth. The United States, Germany, Japan and other countries have not only applied QR Code technology to the management of various documents by public security, diplomatic, military and other departments, but also applied QR Code to the management of various reports and bills by customs, taxation and other departments , the management of commodity and cargo transportation by commercial and transportation departments, the management of postal parcels by the postal department, and the automated management of industrial production lines in the industrial production field.

.. image:: img/DTC4.png

**Run the Code**

.. raw:: html

    <run></run>

.. code-block::

    cd /home/pi/vilibt/examples
    sudo python3 qr_coder_read.py

**View the Image**

After the code runs, the terminal will display the following prompt:

.. code-block::

    No desktop !
    * Serving Flask app "vilib.vilib" (lazy loading)
    * Environment: production
    WARNING: Do not use the development server in a production environment.
    Use a production WSGI server instead.
    * Debug mode: off
    * Running on http://0.0.0.0:9000/ (Press CTRL+C to quit)

Then you can enter ``http://<your IP>:9000/mjpg`` in the browser to view the video screen. such as:  ``https://192.168.18.113:9000/mjpg``


**Code** 

.. code-block:: python

    from vilib import Vilib
    from time import sleep


    def main():
        Vilib.camera_start(vflip=False,hflip=False)
        Vilib.display(local=True,web=True)
        Vilib.qrcode_detect_switch(True)
        
        while True:
            text = Vilib.detect_obj_parameter['qr_data'] 
            print(text)
            sleep(0.5)  
                
    if __name__ == "__main__":
        main()
        



**How it works?**

Functions related to human face detection:

* ``Vilib.qrcode_detect_switch(False)`` : Switch ON/OFF QR code detection, Returns the decoded data of the QR code.
