from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GoogleSheetAPI(object):
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']