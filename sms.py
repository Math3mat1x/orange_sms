import pickle
import os
from time import sleep
from selenium import webdriver
import json
import requests
import credentials

class SMS:
    """Objet to interact with Orange Private API to send text messages.
    The username and password of the Orange account are to be specified in
    a seperate credentials.py file."""

    def __init__(self):
        self.login = credentials.login
        self.password = credentials.password

        if os.path.isfile('cookies.ck'):
            with open('cookies.ck','rb') as f:
                wassup = pickle.Unpickler(f).load()
                self.cookies = {"wassup":wassup}
        else:
            self.cookies = self._authenticate()

        self.headers = {
                'Host':'smsmms.orange.fr',
                'Accept':'application/json; charset=utf8',
                'Accept-Language':'en-US,en;q=0.5',
                'Accept-Encoding':'gzip, deflate, br',
                'Content-Type':'application/json',
                'Cache-Control':'no-cache',
                'Pragma':'no-cache',
                'If-None-Match':'0',
                'Content-Length':'132',
                'Origin':'https://smsmms.orange.fr',
                'Connection':'keep-alive',
                'Referer':'https://smsmms.orange.fr/',
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'
                }
        self.default_message = '''
        {
                "type": "xms",
                "messageId": 0,
                "content": "message",
                "replyType": "on_mobile",
                "recipients": ["phone_number"],
                "attachments": [],
                "mmsData": ""
        }
        '''

    def _authenticate(self):
        """Returns the cookie/token which will be later used in the API."""

        driver = webdriver.Firefox()
        driver.get("https://login.orange.fr/?return_url=https%3A%2F%2Fsmsmms.orange.fr&redirect=false")
        while "captcha" in driver.current_url: pass
        sleep(2)
        driver.find_element_by_id("login").send_keys(self.login)
        driver.find_element_by_id("btnSubmit").click()
        sleep(2)
        driver.find_element_by_id("password").send_keys(self.password)
        driver.find_element_by_id("btnSubmit").click()
        print("Veuillez utiliser la page web quelques instants...")
        done = False
        while not done:
            cookies = driver.get_cookies()
            for i in cookies:
                if "wassup" == i['name']:
                    wassup = i['value']
                    done = True
                    break
        driver.close()
        return {"wassup":wassup}

    def check_phone_number(self,num):
        """Check if the phone number in argument is valid.
        TODO: check if there is letter on the phone number, support other
        country or eventually use an external API to check if the phone
        number exists."""
        return "+33" + num[1:]


    def send(self,phone_number,message):
        """Send a text message to phone_number.
        Returns a bool indicating weither it failed or not"""
        phone_number = self.check_phone_number(phone_number)
        to_send = json.loads(self.default_message)
        to_send['content'] = str(message)
        to_send['recipients'] = [phone_number]
        message = json.dumps(to_send)

        r = requests.post("https://smsmms.orange.fr/api/v1/messages",headers=self.headers,cookies=self.cookies,data=message)
        if r.ok:
            return True
        else:
            return False
