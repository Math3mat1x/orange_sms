import os

import json
from time import sleep
import time
import datetime

import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup as bs

class CredentialsException(Exception):
    """A (useless?) exception class."""

class SMS():
    """
    Simple object to send an SMS using the Orange SMS API.
    """

    def __init__(self):

        self.headers = {
                "x-xms-service-id":"OMI",
                "content-type":"application/json"
                }

        self.default_message = '''
        {
            "content":"message",
            "recipients": ["phone_numbre"],
            "replyType": "mobile",
            "messageId": "0"
        }
        '''

        self.login_page_url = "https://login.orange.fr/?return_url=https%3A%2F%2Fsmsmms.orange.fr&redirect=false"

        if os.path.isfile('token.txt'):
            with open('token.txt','r') as rows:
                token, self.expires = [i if e != 0 else i[:-1] for e,i in enumerate(rows)]
                self.headers.update({"authorization":"Bearer " + token})
        else: # token not stored
            if os.path.isfile('credentials.json'):
                with open("credentials.json","r") as parts:
                    credentials = json.loads("\n".join(parts))
                    self.login = credentials["username"]
                    self.password = credentials["password"]
                if self.login == "" or self.password == "":
                    error = "Please fill in your username and password in\
                            credentials.json accordingly."
                    raise CredentialsException(error)
            else:
                raise FileNotFoundError("No credentials.json file found.")

            # Creation of the cookie file after a check of credentials.json.
            self.headers.update(self._authenticate())


    def _authenticate(self):
        """
        Generation of the cookie that unables authentification into the API.
        The function creates a file named token.txt containing the token and its expiracy timestamp.

        Returns:
            header (dict): The token in order to authenticate.
        """

        print("Beginning authentification...")

        # Webdriver initialization
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.get(self.login_page_url)
        sleep(2)

        soup = bs(driver.page_source,"lxml")
        if soup.find("div",{"id":"captchaRow"}):
            driver.close()
            driver = webdriver.Firefox()
            driver.get(self.login_page_url)
            input("Press enter when you completed the captcha")
            sleep(2)

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
        soup = bs(driver.page_source,"lxml")
        if soup.find("input",{"id":"password"}):
            raise Exception("Wrong password.")

        print("Finishing authentification...")

        done = False
        while not done:
            cookies = driver.get_cookies()
            for i in cookies:
                if i["name"] == "wassup":
                    wassup = i["value"]
                    done = True
                    break

        driver.close()

        token = requests.get("https://api.webxms.orange.fr/api/v8/token",\
                             cookies={"wassup":wassup},headers=self.headers)
        token = json.loads(token.text)
        print("Done!")

        with open("token.txt","w") as f:
            f.write(token["token"] + "\n")
            # Date conversion to timestamp
            date = token["expires"]
            date = [int(i) for i in date.split("T")[0].split("-")]
            f.write(str(time.mktime(datetime.datetime(\
                    date[0], date[1], date[2]-1).timetuple())))

        self.expires = token["expires"]
        return {"authorization":"Bearer " + token["token"]}

    def send(self, phone_number, message):
        """Send a text message to phone_number.

        Args:
            phone_number (str): the phone number
            message (str): the content of the SMS.

        Returns:
            success (bool): has the sms been sent?
        """

        phone_number = "+33" + phone_number[1:]
        to_send = json.loads(self.default_message)
        to_send['content'] = str(message)
        to_send['recipients'] = [phone_number]
        message = json.dumps(to_send)
        api_url = "https://api.webxms.orange.fr/api/v8/users/me/messages"

        res = requests.post(api_url, data=message, headers=self.headers)

        return bool(res.ok)
