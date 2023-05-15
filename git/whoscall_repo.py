from github import Github
from git.repository import Repository


class WhoscallRepository(Repository):

    ACCESS_TOKEN = "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"
    REPO_NAME = "Gogolook-Inc/WhosCall_Android"

    def __init__(self):
        print("init WhoscallRepository")
        gogolook_github = Github(self.ACCESS_TOKEN)
        self.repository = gogolook_github.get_repo(self.REPO_NAME)

    def get_pr_list(self, keyword):
        pass

    def new_branch(self, branch_name):
        pass

    def upgrade_gradle_version_with_pull_request(self, branch_name):
        pass

    def get_all(self):
        self.print_all_branches()

    def print_repo_info(self):
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
              "\nrepository info : "
              "\n [name:", self.repository.name, "]"
              "\n [url:", self.repository.url, "]"
              "\n [path:", self.repository.full_name, "]"
              "\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    def print_all_branches(self):
        for branch in self.repository.get_branches():
            print(branch.name)
