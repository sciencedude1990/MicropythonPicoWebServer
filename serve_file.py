# Web server
# If you call up the IP address, it will serve up the usage

# Imports
import time
import network
import socket
import machine
from machine import Pin
import sys
import os
import wifi_info     # The SSID and WIFI password

# Define the pin variable
led = Pin("LED", Pin.OUT)
    
# Replace with your own SSID and WIFI password
ssid = wifi_info.ssid
wifi_password = wifi_info.wifi_password
my_ip_addr = '192.168.0.31'

# Please see https://docs.micropython.org/en/latest/library/network.WLAN.html
# Try to connect to WIFI
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Specify the IP address
wlan.ifconfig((my_ip_addr, '255.255.255.0', '192.168.0.1', '8.8.8.8'))

# Connect
wlan.connect(ssid, wifi_password)

# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')    
    time.sleep(1)
    
# Handle connection error
if wlan.status() != 3:
    # Connection to wireless LAN failed
    print('Connection failed')    
    sys.exit()
    
else:
    print('Connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    
# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Try to bind the socket
try:
    s.bind(addr)
        
except:
    print('Bind Failed - you might need to wait a minute for things to clear up');    
    sys.exit()
    
# Listen
s.listen(4)
print('listening on', addr)

# Timeout for the socket accept, i.e., s.accept()
s.settimeout(5)

# Listen for connections, serve up web page
while True:
    
    # Handle connection error
    if wlan.status() != 3:
        # Connection to wireless LAN failed
        print('Connection failed during regular operation')
        sys.exit()
        
    # Main loop
    accept_worked = 0
    
    try:
        print("Run s.accept()")
        cl, addr = s.accept()
        accept_worked = 1
    except:
        print('Timeout waiting on accept - reset the pico if you want to break out of this')
        time.sleep(0.3)
        
    if accept_worked == 1:
        try:
            print('client connected from', addr)
            request = cl.recv(1024)
            print("request:")
            print(request)
            request = str(request)
                        
            # Default response is error message                        
            response = """<HTML><HEAD><TITLE>Error</TITLE></HEAD><BODY>Not found...</BODY></HTML>"""
            
            # Parse the request for the set or get
            done_parse = 0
            
            # Look for LED get
            led_get = request.find('?LED=?')
            if led_get != -1:
                response = str(led.value())
                done_parse = 1
            
            # Look for LED set to 0
            led_set = request.find('?LED=0')
            if led_set != -1:
                led.value(0)
                done_parse = 1
                response = """<HTML><HEAD><TITLE>LED</TITLE></HEAD><BODY>LED 0</BODY></HTML>"""
            
            # Look for LED set to 1
            led_set = request.find('?LED=1')
            if led_set != -1:
                led.value(1)
                done_parse = 1
                response = """<HTML><HEAD><TITLE>LED</TITLE></HEAD><BODY>LED 1</BODY></HTML>"""
                
            # Parse the request for a filename
            # Look for the "GET" text
            base_file = request.find('GET /')            
            if (base_file == 2) & (done_parse == 0):
                # Look for the "HTTP" text
                end_name = request.find(' HTTP')
                
                if end_name != -1:
                    # Get the filename
                    f_name = request[7 : end_name]
                    
                    # Print the filename
                    print("filename: " + f_name)
                    
                    found_file = 0
                    try:                    
                        # Get the file size, in bytes
                        temp = os.stat(f_name)
                        found_file = 1
                        
                    except OSError as error:
                        # Likely the file was not found
                        print(error)
                        print("Likely, bad filename...")
                                                
                    if found_file == 1:
                        try:
                            f_size_bytes = temp[6]
                            fid = open(f_name, 'rb')
                            response = fid.read()
                            print(len(response))
                            fid.close()
                        except OSError as error:
                            print(error)
                            print("Likely, file too big to open and send...")
                                                        
            cl.send('HTTP/1.0 200 OK\r\nContent-Length: ' + str(len(response)) + '\r\nConnection: Keep-Alive\r\n\r\n')
            cl.sendall(response)
                        
            # Send the response
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()
            
        except OSError as e:
            print(e)
            cl.close()
            print('connection closed')
            
