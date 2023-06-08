# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from build_master import BuildMaster
from git.whoscall_repo import WhoscallRepository
from git.test_repo import TestRepository

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    BuildMaster(TestRepository(), "test")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
