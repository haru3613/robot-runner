from lib import testrailAPI
import re

class TestRail(object):
    def __init__(self, url, user, password):
        self.client = testrailAPI.APIClient(url)
        self.client.user = user
        self.client.password = password

    def add_project(self, project_name, description=None, condition=False, mode=1):
        resp = self.client.send_post(
            'add_project',
            {
                'name': project_name,
                'announcement': description,
                'show_announcement': condition,
                'suite_mode': mode
            }
        )
        return resp

    def add_milestone(self, project_id, name, description=None, due_on=None, parent_id=None, refs=None, start_on=None):
        resp = self.client.send_post(
            'add_milestone/{}'.format(project_id),
            {
                'name': name,
                'description': description,
                'due_on': due_on,
                'parent_id': parent_id,
                'refs': refs,
                'start_on': start_on
            }
        )
        return resp

    def add_run(self, project_id, name, description=None, milestone_id=None, assignedto_id=None, include_all=None, case_ids=None, refs=None):
        resp = self.client.send_post(
            'add_run/{}'.format(project_id),
            {
                'name': name,
                'description': description,
                'milestone_id': milestone_id,
                'assignedto_id': assignedto_id,
                'include_all': include_all,
                'case_ids': case_ids,
                'refs': refs
            }
        )
        return resp

    def add_result_for_case(self, run_id, case_id, status_id=None, comment=None, version=None, elapsed=None, defects=None, assignedto_id=None):
        resp = self.client.send_post(
            'add_result_for_case/{}/{}'.format(run_id, case_id),
            {
                'status_id': status_id,
                'comment': comment,
                'version': version,
                'elapsed': elapsed,
                'defects': defects,
                'assignedto_id': assignedto_id
            }
        )
        return resp

    def add_section(self, project_id, name, description=None, suite_id=None, parent_id=None):
        resp = self.client.send_post(
            'add_section/{}'.format(project_id),
            {
                'description': description,
                'suite_id': suite_id,
                'parent_id': parent_id,
                'name': name
            }
        )
        return resp

    def add_case(self, section_id, title, template_id=None, type_id=None, priority_id=None, estimate=None, milestone_id=None, refs=None):
        resp = self.client.send_post(
            'add_case/{}'.format(section_id),
            {
                'title': title,
                'template_id': template_id,
                'type_id': type_id,
                'priority_id': priority_id,
                'estimate': estimate,
                'milestone_id': milestone_id,
                'refs': refs
            }
        )
        return resp

    def get_specific_case_id(self, project_id, case_name, section_id):
        resp = self.client.send_get(
            'get_cases/{}&filter={}'.format(project_id, case_name)
        )
        if not resp:
            resp = self.add_case(section_id, case_name)
            return resp['id']
        else:
            return resp[0]['id']

    def get_specific_project(self, project_name):
        resp = self.client.send_get(
            'get_projects'
        )
        result = list(filter((lambda x: re.search(project_name, str(x['name']))), resp))
        
        if result:
            return result[0]
        else:
            result = self.add_project(project_name)
            return result
    
    def get_specific_milestone(self, project_id, milestone_name):
        resp = self.client.send_get(
            'get_milestones/{}'.format(project_id)
        )
        result = list(filter((lambda x: re.search(milestone_name, str(x['name']))), resp))

        if result:
            return result[0]
        else:
            result = self.add_milestone(project_id, milestone_name)
            return result

    def get_specific_section(self, project_id, section_name):
        resp = self.client.send_get(
            'get_sections/{}'.format(project_id)
        )
        result = list(filter((lambda x: re.search(section_name, str(x['name']))), resp))
        
        if result:
            return result[0]
        else:
            result = self.add_section(project_id, section_name)
            return result

    def close_run(self, run_id):
        resp = self.client.send_post(
            'close_run/{}'.format(run_id),
            {}
        )
        return resp