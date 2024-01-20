# MicropythonPicoWebServer
A simple web server using just micropython

Using only MicroPython code, a webserver using a raspberry pi pico W.

It will serve up HTML with images!

You need to create wifi_info.py.  The file has two string variables, ssid and wifi_password with the ssid and wifi password.

I also included a simple html and image file, so that you can see that the pico w and Micropython can serve up a simple webpage with an image.

I included a .png favicon.ico in case you need one.  :)

Lastly, check out led_website.html - you can set the status of the pico w led, and it will automatically query and display the status of the led without refreshing the page using XMLHttpRequest.


https://hackaday.io/project/189675-raspberry-pi-pico-w-super-simple-webserver
