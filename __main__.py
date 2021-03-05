import click
import os
import sys
from lib import config
from lib.run import Runner
from lib import robot_parser
from lib import conn_testrail
from lib import message
import time
import pytz
import datetime
from lib.request import Skype_API
from lib.owasp_zap_runner import owasp_zap_runner

__dirname = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(__dirname, '../'))
from constants import *

@click.group()
def cli():
    """Robot Runner"""


@cli.command('run', short_help='run robot test')
@click.option('-R', '--rootpath', default=os.getcwd())
@click.option('-P', '--project_name', help='Test project name')
@click.option('-r', '--retesttimes', default=2, help='Retest times when case fail')
@click.option('-O', '--robotoption', help='Setup robot option', multiple=True)
@click.option('-i', '--include_tag', multiple=True, help="Add test case of tag")
@click.option('-e', '--exclude_tag', help="Exclude test tag")
@click.option('-o', '--outputdir', is_flag=True, default=None, help="Set output directory")
@click.option('-n', '--no_status_rc',is_flag=True, default=False, help="Don't return error code")
@click.option('-m', '--milestone_name', help="Testrail milestone name (e.g. round4, regression)", default="Regression")
@click.option('-v', '--version', default=None, help="Deploy version")
@click.option('-p', '--docker_port', default=None, help="Docker port")
@click.option('-b', '--browser', default=None, help="Set different browser")
def run_cli(rootpath, project_name, retesttimes, robotoption, include_tag, exclude_tag, milestone_name, outputdir, no_status_rc, version, docker_port, browser):
    """Run Test"""

    # Check project existing
    path_parent = os.path.dirname(rootpath)
    os.chdir(path_parent)
    projects = os.listdir(os.getcwd())
    if project_name not in projects:
        print('%s is not in directory' % project_name)
        exit()

    project_config = config.fetch_config(rootpath)

    for sub_project in project_config['sub_project']:

        should_do_testing = config.check_test_status(
            include_tag, exclude_tag, sub_project)

        if should_do_testing == True:
            if outputdir==None:
                test_outputdir = os.path.join(
                    os.getcwd(), 'report', project_name, sub_project['name'])
            else:
                test_outputdir = os.path.join(rootpath, 'vendor', project_name, sub_project['name'])
            test_folder = os.path.join(
                rootpath, sub_project['path'])

            # Convert robot option data
            robotoption_array = []
            for option in robotoption:
                robotoption_array.append(
                    {'option': option.split("=")[0], 'value': option.split("=")[1]})

            test = Runner(rootpath, project_name, test_outputdir, test_folder,
                          retesttimes=retesttimes, robotoption=robotoption_array, NoStatusRC=no_status_rc, docker_port=docker_port, browser=browser, testing_type=include_tag[0])

            is_allpass = test.run()
            if is_allpass != 252:
                test.retry(is_allpass)
            result_outputdir = os.path.join(test_outputdir, 'output.xml')
            robot_report = robot_parser.RobotReportParser()
            if version != None:
                try:
                    robot_report.parser(result_outputdir)
                    message.info_message("Start report to TestRail, please wait...")
                    test_rail_url = 'https://talfin.testrail.io'
                    testrail = conn_testrail.TestRail(test_rail_url,'awsadm@talfin.ai','supporttest')

                    project = testrail.get_specific_project(project_name)

                    new_milestone = testrail.get_specific_milestone(project['id'], milestone_name)
                    tw = pytz.timezone('Asia/Taipei')
                    unique_name = str(datetime.datetime.now(tw).strftime("%Y%m%d%H%M%S%f"))
                    pass_list = []
                    fail_list = []
                    for case in robot_report.pass_list:
                        suite_name = case.suite.split("\\")[-1][:-6]
                        new_section = testrail.get_specific_section(project['id'], suite_name)
                        case_id = testrail.get_specific_case_id(project['id'], case.case_name, new_section['id'])
                        pass_list.append(case_id)

                    for case in robot_report.fail_list:
                        suite_name = case.suite.split("\\")[-1][:-6]
                        new_section = testrail.get_specific_section(project['id'], suite_name)
                        case_id = testrail.get_specific_case_id(project['id'], case.case_name, new_section['id'])
                        fail_list.append(case_id)
                        
                    total_list = pass_list + fail_list
                    new_run = testrail.add_run(project['id'], "{}_{}".format(include_tag[0], version + "_" + unique_name), include_all=False, milestone_id=new_milestone["id"], case_ids=total_list)
                    for case_id in pass_list:
                        testrail.add_result_for_case(run_id=new_run["id"], case_id=case_id, status_id=1, comment="PASS", version="1")
                    for case_id in fail_list:
                        testrail.add_result_for_case(run_id=new_run["id"], case_id=case_id, status_id=5, comment="FAIL", version="1")
                    testrail.close_run(run_id=new_run["id"])
                    rq = Skype_API()
                    if browser != None:
                        test_type = "{} {}".format(browser, include_tag[0])
                    else:
                        test_type = include_tag[0]
                    payload = {"text":"{} 版本 {} regression test 完成\n{}項 Pass, {}項 Fail\n請查看 TestRail Report\n{}".format(version, test_type, len(pass_list), len(fail_list), test_rail_url + "/index.php?/runs/view/{}".format(new_run["id"]))}
                    resp = rq.request('POST', json=payload)
                

                    message.info_message("Done")
                except Exception as e:
                    print(e)


@cli.command('zap', short_help='run zap sercurity test')
@click.option('-R', '--rootpath', default=os.getcwd())
@click.option('-P', '--project_name', help='Test project name')
@click.option('-i', '--include_tag', multiple=True, help="Add test case of tag")
@click.option('-e', '--exclude_tag', help="Exclude test tag")
def zap_cli(rootpath, project_name, include_tag, exclude_tag):
    """Create zap test"""
    path_parent = os.path.dirname(rootpath)
    os.chdir(path_parent)
    projects = os.listdir(os.getcwd())
    if project_name not in projects:
        print('%s is not in directory' % project_name)
        exit()

    project_config = config.fetch_config(rootpath)

    for sub_project in project_config['sub_project']:

        should_do_testing = config.check_test_status(
            include_tag, exclude_tag, sub_project)

        if should_do_testing == True:
            test_outputdir = os.path.join(
                os.getcwd(), 'report', project_name, sub_project['name'])
            test_folder = os.path.join(
                rootpath, sub_project['path'])
            zap_runner = owasp_zap_runner()
            zap_runner.zap_execute_test(project_name, test_folder, test_outputdir)


if __name__ == '__main__':
    cli()
