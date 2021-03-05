import click
import os
from constants import *
import subprocess
from lib import message
from lib import robot_parser


class Runner(object):
    def __init__(self, root_path, project_name, test_outputdir, test_folder, retest_count=0, retesttimes=2, robotoption=[], NoStatusRC=False, docker_port=None, browser="chrome", testing_type="web"):
        self.root_path = root_path
        self.project_name = project_name
        self.robotoption = robotoption
        self.retesttimes = retesttimes
        self.test_outputdir = test_outputdir
        self.test_folder = test_folder
        self.robot_report = robot_parser.RobotReportParser()
        self.message = message
        self.retest_count = retest_count
        self.NoStatusRC = NoStatusRC
        self.docker_port = docker_port
        self.browser = browser
        self.testing_type = testing_type

    def robot_test_init(self, retest=False, retesting_file=None):
        cmd = []
        cmd.append('robot')
        cmd.append('--outputdir')
        cmd.append(self.test_outputdir)

        if not retesting_file:
            cmd.extend(['--output', 'output.xml'])
        else:
            cmd.extend(['--output', 'retest{}.xml'.format(self.retest_count),
                        '--rerunfailed', os.path.join(self.test_outputdir, retesting_file)])
        if not self.NoStatusRC:
            cmd.extend(['--NoStatusRC'])

        for option in self.robotoption:
            if not retest:
                cmd.extend([str(option['option']), str(option['value'])])
            else:
                if str(option['option']) not in ('-t', '-s', '--test', '--suite'):
                    cmd.extend([str(option['option']), str(option['value'])])

        if self.docker_port != None:
            cmd.extend(['--variable', 'BROWSER_PORT:{}'.format(self.docker_port)])
        
        if self.testing_type == 'web' and self.browser in ('firefox', 'chrome', 'ie'):
            cmd.extend(['--variable', 'DEFAULT_BROWSER:{}'.format(self.browser)])
        
        cmd.append(self.test_folder)

        return cmd

    def robot_test(self, retest=False, retesting_file=None):
        cmd = self.robot_test_init(retest, retesting_file)
        self.message.show_cmd(cmd)
        returncode = self.run_cmd(cmd)
        return returncode

    def run(self):
        self.message.test_start()
        returncode = self.robot_test()
        if returncode == 252:
            return returncode
        result_outputdir = os.path.join(self.test_outputdir, 'output.xml')
        try:
            self.robot_report.parser(result_outputdir)
            return self.robot_report.is_allpass
        except Exception as e:
            print(e)
            return True

    def run_cmd(self, cmd):
        try:
            if OS == "Windows":
                subprocess.check_call(cmd, shell=True)
            else:
                subprocess.check_call(cmd)
        except Exception as e:
            print(str(e))
            return e

    def retry(self, is_allpass):
        if is_allpass == False:
            self.retest()

        if self.retest_count >= 1:
            self.report_merge()

    def retest(self):
        if self.retest_count < self.retesttimes:
            retesting_file = 'output.xml'
            if self.retest_count != 0:
                retesting_file = 'retest{}.xml'.format(self.retest_count)

            self.message.retest(self.retest_count)
            self.retest_count += 1
            self.robot_test(retest=True, retesting_file=retesting_file)

            try:
                result_outputdir = os.path.join(
                    self.test_outputdir, 'retest{}.xml'.format(self.retest_count))
                self.robot_report.parser(result_outputdir)
            except Exception as e:
                return True

            if self.robot_report.is_allpass == False:
                self.retest()
        else:
            print('over retesttimes, exit retest process')

    def report_merge(self):
        self.message.report_merge()

        for i in range(1, self.retest_count + 1):
            try:
                subprocess.check_call(['rebot', '--outputdir', '%s' % self.test_outputdir, '--output', 'output.xml',
                                       '--merge', os.path.join(self.test_outputdir, 'output.xml'), os.path.join(self.test_outputdir, 'retest%d.xml' % i)])
            except Exception as e:
                print(str(e))
            i = i + 1
