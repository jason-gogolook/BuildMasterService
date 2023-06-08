from dotenv import load_dotenv
from github import Github
from git.repository import Repository, search_version

import os
import requests


class TestRepository(Repository):
    REPO_NAME = "jason-gogolook/gogo_design_pattern"

    def __init__(self):
        load_dotenv()
        self.GITHUB_ACCESS_TOKEN = os.getenv('BUILD_MASTER_GITHUB_ACCESS_TOKEN')

        print("Init TestRepository")
        self.repository = Github(self.GITHUB_ACCESS_TOKEN).get_repo(self.REPO_NAME)

    def get_pr_list(self, keyword):
        url = "https://api.github.com/search/issues" \
              "?q=repo:Gogolook-Inc/WhosCall_Android" \
              "+type:pr" \
              "+state:closed" \
              "+{}+in:title".format(keyword)
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + self.GITHUB_ACCESS_TOKEN,
            "X-GitHub-Api-Version": "2022-11-28"
        }
        pr_list = [keyword]
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            for item in response.json()["items"]:
                title = item["title"]
                author = item["user"]["login"]
                pr_list.append("- " + title + " @" + author)
        else:
            print(f'Error: {response.status_code} - {response.text}')
        return pr_list

    def new_branch(self, base_branch_name):
        base_branch_name = "test_gradle_file"
        base_branch = self.repository.get_branch(base_branch_name)
        gradle_file = self.repository.get_contents("GogoMind/build.gradle", base_branch.commit.sha)
        gradle_file_content = gradle_file.decoded_content.decode("utf-8")
        current_version = search_version(gradle_file_content)
        print("current_version:", current_version)

        new_branch_name = "rc_v" + current_version[0] + "." + current_version[1]
        print("new_branch_name:", new_branch_name)
        self.repository.create_git_ref(ref="refs/heads/" + new_branch_name, sha=base_branch.commit.sha)
        return current_version

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

    def upgrade_gradle_version_with_pull_request(self, branch_name):
        branch_name = "test_gradle_file"
        base_branch = self.repository.get_branch(branch_name)
        gradle_file = self.repository.get_contents("GogoMind/build.gradle", base_branch.commit.sha)
        gradle_file_content = gradle_file.decoded_content.decode("utf-8")

        current_version_major = ""
        current_version_minor = ""
        line_major = ""
        line_minor = ""
        for line in gradle_file_content.splitlines():
            if "def versionMajor" in line:
                current_version_major = line.split(" = ")[1]
                line_major = line
            if "def versionMinor" in line:
                current_version_minor = line.split(" = ")[1]
                line_minor = line

        if current_version_minor == "99":
            new_version_major = str(int(current_version_major) + 1)
            new_version_minor = "0"
        else:
            new_version_major = current_version_major
            new_version_minor = str(int(current_version_minor) + 1)

        gradle_content = gradle_file_content
        gradle_content = gradle_content.replace(line_major, "    def versionMajor = " + new_version_major)
        gradle_content = gradle_content.replace(line_minor, "    def versionMinor = " + new_version_minor)

        new_branch_name = "develop_v" + new_version_major + "." + new_version_minor + "_update_app_ver"
        self.repository.create_git_ref(ref="refs/heads/" + new_branch_name, sha=base_branch.commit.sha)

        new_branch = self.repository.get_branch(new_branch_name)
        self.repository.update_file(gradle_file.path,
                                    "Update app version",
                                    gradle_content,
                                    gradle_file.sha,
                                    branch=new_branch.name)

        pull_request = self.repository.create_pull(title="Update app version",
                                                   body="Update app version to " + new_version_major + "." + new_version_minor,
                                                   base=base_branch.name,
                                                   head=new_branch.name)

        print(f"Pull Request created: {pull_request.html_url}")
        return pull_request.html_url
