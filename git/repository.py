import abc
import re


def search_version(content):
    pattern_version_major = r'def versionMajor'
    pattern_version_minor = r'def versionMinor'

    version_major = ""
    version_minor = ""
    for line in content.splitlines():
        if line.__contains__(pattern_version_major):
            version_major = re.findall(r'\d+', line)[0]
        if line.__contains__(pattern_version_minor):
            version_minor = re.findall(r'\d+', line)[0]

    return [version_major, version_minor]


class Repository(metaclass=abc.ABCMeta):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_pr_list(self, keyword):
        pass

    @abc.abstractmethod
    def get_all(self):
        pass

    @abc.abstractmethod
    def print_repo_info(self):
        pass

    @abc.abstractmethod
    def new_branch(self, base_branch):
        pass

    @abc.abstractmethod
    def upgrade_gradle_version_with_pull_request(self, branch_name):
        pass
