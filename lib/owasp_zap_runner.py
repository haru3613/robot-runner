import os
import sys
from constants import *
import subprocess
from lib import message


class owasp_zap_runner(object):
    def __init__(self):
        self.ZAP_PORT = '8081'

    def zap_execute_test(self, project_name, casePath, report_folder):
        """run command"""
        cmd = []
        path = os.path.dirname(__file__)

        if OS == "Windows":
            casePath = casePath.replace('/', '\\')
        cmd.extend(
            ['python', '{0}/owasp_zap.py'.format(os.path.join(project_name, path)), casePath, report_folder, self.ZAP_PORT])

        self.run_cmd(cmd)

    def run_cmd(self, cmd):
        message.show_cmd(cmd)
        try:
            if OS == "Windows":
                subprocess.check_call(cmd, shell=True)
            else:
                subprocess.check_call(cmd)
        except Exception as e:
            message.warn_msg(
                ['failed to run command, error:', e])
