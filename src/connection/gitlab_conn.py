from typing import Optional

import gitlab
from gitlab.v4.objects import Project


class Connector:
    """
    GitLab connection class
    @:parameter url   full GitLab project url
    @:parameter token private GitLab token
    """

    def __init__(self, url, token):
        splitResult = url.split("/")
        self.gitLabUrl = splitResult[0] + "//" + splitResult[2]
        self.projectUrl = splitResult[3] + "/" + splitResult[4]
        self.token = token
        self.gitLab = None

    def auth(self) -> bool:
        try:
            self.gitLab = gitlab.Gitlab(url=self.gitLabUrl, private_token=self.token)
            self.gitLab.auth()
            return True
        except Exception as ex:
            print(f'Error connecting to the GitLab server, check the connection settings or site availability\n{ex}')
            return False

    def getProject(self) -> Optional[Project]:
        try:
            return self.gitLab.projects.get(self.projectUrl, lazy=True)
        except Exception as ex:
            print(f'Error connecting to the GitLab project {self.projectUrl}, check the connection settings\n{ex}')
            return None
