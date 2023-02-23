# A very simple web server - good for running on a raspberry pi pico W

# Imports
import time
import network
import socket
import sys
import os
import wifi_info     # The SSID and WIFI password, create your own wifi_info.py file that has two variables, ssid and wifi_password, stored as strings
    
# Replace with your own SSID and WIFI password
ssid = wifi_info.ssid
wifi_password = wifi_info.wifi_password
my_ip_addr = '192.168.0.22'  # I find a fixed IP address easier for testing...

# Please see https://docs.micropython.org/en/latest/library/network.WLAN.html
# Try to connect to WIFI
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Specify the IP address and the other numbers - if these are not correct, then the pico won't connect
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
print('listening on ', addr)

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
        # Need this small sleep statement so that the pico can respond to a keyboard break, or the "stop" button on Thonny
        time.sleep(0.5)
        
    if accept_worked == 1:
        try:
            print('client connected from', addr)
            request = cl.recv(1024)
            print("request:")
            print(request)
            request = str(request)
            
            # Default response is error message - TODO - make a better HTML response                        
            response = """<HTML><HEAD><TITLE>Error</TITLE></HEAD><BODY>Not found...</BODY></HTML>"""
                    
            # Parse the request for the filename - in the root directory
            # Look for the "GET" text
            base_file = request.find('GET /')            
            if base_file == 2:
                # Look for the "HTTP" text
                end_name = request.find(' HTTP')
                
                if end_name != -1:
                    # Get the filename
                    f_name = request[7 : end_name]
                    
                    # Print the filename
                    print("filename: " + f_name)
                    
                    try:                    
                        # Get the file size, in bytes, for reference
                        temp = os.stat(f_name)                    
                        f_size_bytes = temp[6]
                    
                        # Open the file
                        fid = open(f_name, 'rb')
                        # Read the contents
                        response = fid.read()
                        # Echo the length
                        print(len(response))
                        # Close the file
                        fid.close()
                    except:
                        print("Issue finding file...")
                        
            # Send a response - you can add more details here if necessary                                
            cl.send('HTTP/1.0 200 OK\r\nContent-Length: ' + str(len(response)) + '\r\nConnection: Keep-Alive\r\n\r\n')
            # Send the response, either the file not found, or the file
            cl.sendall(response)
                
            # All done, close!
            cl.close()
            
        except OSError as e:
            cl.close()
            print('yikes, error, connection closed')
            

