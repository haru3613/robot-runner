import time
import sys
import os
import message
import re
from pprint import pprint
from zapv2 import ZAPv2


class owasp_zap(object):
    def __init__(self, report_folder, port):
        self.APIKEY = 'b63l3jbchossf2mut6m2jnj07q'
        self.ZAP = ZAPv2(
            proxies={
                "http": "http://127.0.0.1:" + port,
                "https": "http://127.0.0.1:" + port
            },
            apikey=self.APIKEY
        )
        self.REPORT_FOLDER = report_folder

    def main(self, cases, filename):
        if cases.addHeaders:
            self.context_scan(cases)
        else:
            map(lambda target: self.zap_scan(target), cases.targets)

        self.created_report(filename)

    def context_scan(self, cases):
        addHeaders = cases.addHeaders
        for header in addHeaders.keys():
            self.ZAP.replacer.remove_rule('Auth Header')
            self.ZAP.replacer.add_rule('Auth Header', True, 'REQ_HEADER', False, header, addHeaders[header])

        print(self.ZAP.replacer.rules)
        context = self.ZAP.context
        users = self.ZAP.users
        contextName = 'qa_context'
        sessionName = 'qa_session'
        sessionManagement = 'httpAuthSessionManagement'
        userName = 'qa_user'
        self.ZAP.core.new_session(name=sessionName, overwrite=True)
        contextId = context.new_context(contextname=contextName)

        for target in cases.targets:
            context.include_in_context(contextname=contextName, regex=target)

        self.ZAP.sessionManagement.set_session_management_method(
            contextid=contextId, methodname=sessionManagement, methodconfigparams=None)
        userId = users.new_user(contextid=contextId, name=userName)
        for target in cases.targets:
            self.core_scan_with_user(target, userId, contextId)

    def core_scan_with_user(self, target, userId, contextId):
        self.ZAP.pscan.enable_all_scanners()
        self.ZAP.core.access_url(url=target, followredirects=True)
        self.ZAP.urlopen(target)
        ascan = self.ZAP.ascan
        spider = self.ZAP.spider
        scanId = 0

        print('Starting Scans on target: {0} with User ID: {1}'.format(
            target, userId))
        scanId = spider.scan_as_user(contextid=contextId, userid=userId,
                                     url=target, maxchildren=None, recurse=True, subtreeonly=None)

        print('Start Spider scan with user ID: ' + userId +
              '. Scan ID equals: ' + scanId)
        while (int(spider.status(scanId)) < 100):
            print('Spider progress: ' + spider.status(scanId) + '%')
            time.sleep(2)
        print('Spider scan for user ID ' + userId + ' completed')

        scanId = ascan.scan_as_user(url=target, contextid=contextId,
                                    userid=userId, recurse=True,
                                    method=None, postdata=True)
        print('Start Active Scan with user ID: ' + userId +
              '. Scan ID equals: ' + scanId)

        
        while (int(ascan.status(scanId)) < 100):
            print('Active Scan progress: ' + ascan.status(scanId) + '%')
            time.sleep(2)
        print('Active Scan for user ID ' + userId + ' completed')
        pprint (self.ZAP.core.alerts())

    def zap_scan(self, target):
        message.show_msg(['Accessing target ', target])
        self.ZAP.urlopen(target)

        message.show_msg(['Spidering stats', target])
        scanId = self.ZAP.spider.scan(target)

        while (int(self.ZAP.spider.status(scanId)) < 100):
            message.show_msg(
                ['Spider progress %: ', self.ZAP.spider.status(scanId)])
            time.sleep(2)
        message.show_msg(['Spider completed'])

        message.show_msg(['Scanning target ', target])
        scanId = self.ZAP.ascan.scan(target)
        while (int(self.ZAP.ascan.status(scanId)) < 100):
            message.show_msg(
                ['Scan progress %: ', self.ZAP.ascan.status(scanId)])
            time.sleep(5)
        message.show_msg(['Scan completed'])

    def created_report(self, filename):
        html_report = self.ZAP.core.htmlreport(apikey=self.APIKEY)
        path = self.REPORT_FOLDER
        if not os.path.exists(path):
            os.makedirs(path)
        report_path = "{0}/{1}.html".format(path, filename)
        report_file = open(report_path, 'wb+')
        report_file.write(html_report.encode('utf8'))


if __name__ == '__main__':
    casePath = sys.argv[1]
    report_folder = sys.argv[2]
    port = sys.argv[3]

    sys.path.insert(0, casePath)
    files = [f for f in os.listdir(casePath) if os.path.isfile(
        os.path.join(casePath, f))]
    
    files = filter(lambda name: re.search(
        "^test_zap_.*\.py$", name) is not None, files)

    for file in files:
        file = file.replace(".py", "")
        tests_detail = __import__(file)
        owasp = owasp_zap(report_folder, port)
        owasp.main(tests_detail, file)
