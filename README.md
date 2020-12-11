# orange_sms
![Logo](logo.png)
Easy to use Python object to send SMS using the smsmms.orange.fr tool.
## Table of contents
* [Installation](#installation)
* [Syntax](#syntax)
## Installation
Python 3 is needed.
To run this object, you will have to pip install these packages:
* json
* requests
* selenium
* bs4

You will also have to install geckodriver and firefox.  
On ArchLinux, just type:
```
sudo pacman -S firefox geckodriver
```
To download the package, just type:
```
git clone https://github.com/Math3mat1x/orange_sms.git
```
First you need to import the package, then create the object. The object only contains one function, send... to send an sms.
```
from orange_sms import sms

username = "username-or-phone-number"
password = "password"

sms = sms(username, password) # username and password arguments are only required the first time.
sent = sms.send("phone_number","Test message.")

if sent:
	print("Sent!")
```
Keep in mind that the message takes about 20 seconds to be received on a phone after being sent.
