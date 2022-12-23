Take Photo
=======================

You can use Raspberry Pi to take a photo and 
store it in ``/home/pi/Pictures/vilib/photos``.


**Run the Code**

.. raw:: html

    <run></run>

.. code-block::

    cd /home/pi/vilib/examples
    sudo python3 take_photo.py

After the program runs:
1. You can enter ``http://<Your Raspberry Pi IP>:9000/mjpg`` in the browser (such as chrome) to view the viewfinder screen.
2. Type ``q`` in Terminal and press Enter to take a photo.

**Code**

.. code-block:: python

    import time
    from vilib import Vilib

    def main():
        Vilib.camera_start(vflip=False,hflip=False)
        Vilib.display(local=True,web=True)

        path = "/home/pi/Pictures/vilib/photos"
    
        while True:
            if input() == 'q': 
                _time = time.strftime("%y-%m-%d_%H-%M-%S", time.localtime())
                Vilib.take_photo(str(_time),path)
                print("The photo save as:%s/%s.jpg"%(path, _time))
                time.sleep(0.1)


    if __name__ == "__main__":
        main()

**How it works?**

What you need to focus on is the following:

.. code-block:: python

   Vilib.take_photo(photo_name=str(_time),path=path)

As the name suggests, this function takes pictures. The first parameter is the name of the generated image file, and the second parameter is the path where the file is located. They can all be customized.