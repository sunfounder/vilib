Display
=======================

You can view the pictures captured by the Raspberry Pi camera in the browser.

**Run the Code**

.. raw:: html

    <run></run>

.. code-block::

    cd /home/pi/vilib/examples
    sudo python3 display.py

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

Then you can enter ``http://<your IP>:9000/mjpg`` in the browser to view the video screen. such as:  ``http://192.168.18.113:9000/mjpg``

.. image:: img/display.png


**Code**

.. code-block:: python

    from vilib import Vilib

    def main():
        Vilib.camera_start(vflip=False,hflip=False) # vflip:vertical flip, hflip:horizontal Flip
        # local:local display, web:web display
        # when local=True, the image window will be displayed on the system desktop
        # when web=True, the image window will be displayed on the web browser at http://localhost:9000/mjpg
        Vilib.display(local=True,web=True) 
        print('\npress Ctrl+C to exit')
        
    if __name__ == "__main__":
        main()

**How it works?**

The content involved in this article is exactly the basic function of the ``vilib`` library. We have already :ref:`install_vilib`.

What you need to focus on is the following:

.. code-block:: python

    from vilib import Vilib

All functions related to computer vision are encapsulated in this library.

.. code-block:: python

    Vilib.camera_start(vflip=True,hflip=True) 

Let the camera module enter the working state. 
If you modify the two parameters of this function to ``False``, 
the screen will be flipped horizontally/vertically.

.. code-block:: python

    Vilib.camera_close()

Stop the camera module.

.. code-block:: python

    Vilib.display(local=True,web=True)

Allows you to see the picture taken by the camera module.

* Its parameter ``local=True`` is used to open the viewfinder in the Raspberry Pi desktop, which is suitable for remote desktop or the situation where a screen is provided for the Raspberry Pi.
* The parameter ``web=True`` allows you to view the image through the browser, which is the method suggested in this article. It is suitable for the situation where your PC and Raspberry Pi are connected to the same local area network.