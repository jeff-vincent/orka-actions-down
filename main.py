import json
import os
import requests


class TearDownOrkaVM:
    def __init__(self):
        self.token = None
        self.runner_id = None
        self.vm_name = os.environ["VM_NAME"]
        orka_ip = '10.221.188.100'
        self.orka_address = f"http://{orka_ip}"
        self.orka_user = os.environ["INPUT_ORKAUSER"]
        self.orka_pass = os.environ["INPUT_ORKAPASS"]
        self.github_pat = os.environ["INPUT_GITHUBPAT"]
        repo_and_user_name = os.environ["GITHUB_REPOSITORY"].split('/')
        self.github_repo_name = repo_and_user_name[1]
        self.github_user = repo_and_user_name[0]        
        self.gh_session = requests.Session()
        self.gh_session.auth = (self.github_user, self.github_pat)

    def get_orka_auth_token(self):
        data = {
            'email': self.orka_user,
	        'password': self.orka_pass
            }
        result = requests.post(self.orka_address+'/token', data=data)
        content = json.loads(result.content.decode('utf-8'))
        self.token = content['token']

    def tear_down_vm(self):
        url = f"{self.orka_address}/resources/vm/purge"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.token}"
            }
        data = {'orka_vm_name': self.vm_name}
        requests.delete(url, data=json.dumps(data), headers=headers)
    
    def get_runner_id(self):
        url = f"https://api.github.com/repos/{self.github_user}/{self.github_repo_name}/actions/runners"
        result = self.gh_session.get(url)
        content = json.loads(result._content.decode('utf-8'))
        for item in content['runners']:
            if self.vm_name in item['name']:
                self.runner_id = item['id']

    def remove_runner_from_gh(self):
        headers = {'Accept':'application/vnd.github.v3+json'}
        url = f"https://api.github.com/repos/{self.github_user}/{self.github_repo_name}/actions/runners/{self.runner_id}"
        self.gh_session.delete(url,headers=headers)


def main(tear_down):
    tear_down.get_orka_auth_token()
    tear_down.tear_down_vm()
    tear_down.get_runner_id()
    tear_down.remove_runner_from_gh()


if __name__ == '__main__':
    tear_down = TearDownOrkaVM()
    main(tear_down)
