import os

import json
from time import sleep

import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup as bs


class SMS:
    """
    Simple object to send an SMS using the Orange SMS API.
    """

    def __init__(self):
        if os.path.isfile('cookies.ck'):
            with open('cookies.ck','r') as f:
                wassup = f.read()
                self.cookies = {"wassup":wassup}
        else: # no cookie stored
            if os.path.isfile('credentials.json'):
                with open("credentials.json","r") as f:
                    credentials = str()
                    for i in f:
                        credentials += i
                    credentials = json.loads(credentials)
                    self.login = credentials["username"]
                    self.password = credentials["password"]
                if self.login == "" or self.password == "":
                    raise Exception("Please fill in your username and password in credentials.json accordingly.")
            else:
                raise FileNotFoundError("No credentials.json file found.")

            # Creation of the cookie file after a check of credentials.json.
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
        """
        Generation of the cookie that unables authentification into the API.
        The function creates a file named cookies.ck containing the cookie.

        Returns:
            cookie (dict): The cookie in order to authenticate.
        """

        print("Beginning authentification...")

        # Webdriver initialization
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.get("https://login.orange.fr/?return_url=https%3A%2F%2Fsmsmms.orange.fr&redirect=false")
        sleep(2)

        # TODO
        # if "captcha" in driver.page_source:
        #     input()
        #     driver.close()
        #     driver = webdriver.Firefox()
        #     print("Complete the captcha.")
        #     while "captcha" in driver.current_url: pass

        driver.find_element_by_id("login").send_keys(self.login)
        driver.find_element_by_id("btnSubmit").click()

        # check the username
        sleep(1)
        soup = bs(driver.page_source,"lxml")
        error = soup.find("h6",{"role":"alert"}).text
        if error:
            raise Exception("Wrong username.")
        sleep(2)

        driver.find_element_by_id("password").send_keys(self.password)
        driver.find_element_by_id("btnSubmit").click()

        # check the password
        sleep(2)
        if "alert" in driver.page_source:
            raise Exception("Wrong password.")

        print("Finishing authentification...")
        done = False
        while not done:
            cookies = driver.get_cookies()
            for i in cookies:
                if "wassup" == i['name']:
                    wassup = i['value']
                    done = True
                    break

        driver.close()
        print("Done!")

        with open("cookies.ck","w") as f:
            f.write(wassup)

        return {"wassup":wassup}

    def check_phone_number(self,num):
        """Converts the phone number.
        
        Args:
            num (str): the french phone number.

        Returns:
            num (str): the phone number formatted.

        Todo:
            Support for phone numbers outside of France.
        """

        return "+33" + num[1:]


    def send(self,phone_number,message):
        """Send a text message to phone_number.

        Args:
            phone_number (str): the phone number
            message (str): the content of the SMS.

        Returns:
            success (bool): has the sms been sent?
        """

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
