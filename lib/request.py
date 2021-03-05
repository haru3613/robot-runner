import requests

class Skype_API(object):

    def __init__(self, host="https://hook.integromat.com/adfvlg20mj2e1yirb7ubzmcsj2x95p5e"):
        self.HOST = host
        self.SESSION = requests.Session()
        self.SESSION.headers.update({
            'Content-Type': 'application/json'
        })
    
    def request(self, method, **kwargs):
        resp = self.SESSION.request(method, self.HOST, **kwargs)
        return resp