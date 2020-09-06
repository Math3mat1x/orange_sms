# orange_sms
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
cd orange_sms/
```

## Syntax
First you need to import the package, then create the object. The object only contains one function, send... to send an sms.
```
from sms import SMS

sms = SMS()
result = sms.send("phone_number","Test message.")

if result:
	print("Sent!")
```
Keep in mind that the message takes about 20 seconds to be received on a phone after being sent.
