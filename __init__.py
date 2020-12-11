import orange_sms.sms as SMS
import os.path as path

def initialize(username=str(), password=str()):
    basedir = path.abspath(path.dirname(__file__))
    if username and password and not path.join(basedir, "orange_sms", "token.txt"):
        SMS.SMS(username, password)

    return SMS.SMS

sms = initialize(username=str(), password=str())
