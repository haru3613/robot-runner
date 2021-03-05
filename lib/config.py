import os
from lib import message


def fetch_config(rootPath):
    import json

    with open(os.path.join(rootPath, '.robot-runner', 'config.json')) as data_file:
        data = json.load(data_file)
    return data


def check_test_status(include_tag, exclude_tag, sub_project):
    should_do_testing = True
    if include_tag is not None:
        if sub_project['tag'] not in include_tag:
            should_do_testing = False
    if exclude_tag is not None:
        if sub_project['tag'] in exclude_tag:
            should_do_testing = False
    if should_do_testing:
        message.info_message("Found the {} tag, preparing {} test".format(
            include_tag[0], sub_project['name']))
    return should_do_testing


# {
#     "sub_project": [{
#         "testing_type": "web",
#         "name": "web",
#         "path": "web/integration",
#         "tag": "web",
#         "type": "robot"
#     }
# }
