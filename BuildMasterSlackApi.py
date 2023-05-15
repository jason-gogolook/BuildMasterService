# encoding: utf-8
import os

# Use the package we installed
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from git.repository import Repository

# 設定環境變數
os.environ["SLACK_BOT_TOKEN"] = "xoxb-3184753415-5050441132624-lCPxgaz0XkhdvJxgMda7DLSc"
# signing secrete for verifying the incoming request are coming from Slack
os.environ["SLACK_SIGNING_SECRET"] = "af070c2d7337a8c304036d9022a49951"
os.environ["SLACK_APP_TOKEN"] = "xapp-1-A050V33LZN0-5026080724214" \
                                "-dd472481c43e1254f3a9ef15769105729c196282d6634550ebae51dd2adb702a "

# Initializes your app with your bot token and signing secret
slack_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Add functionality here
# @app.event("app_home_opened") etc

# 訊息內容與要發送的頻道
code_freeze_reminder_message = "<!here> 大大們日安\n" \
                               "今天是 {release_version} code freeze 的日子\n" \
                               "請把握最後進 develop branch 的時光，並請大大們幫忙\n" \
                               "1. 儘早完成 PR review\n" \
                               "2. 確認 branch name 符合 CircleCI run auto test 的觸發規則\n" \
                               "\n_*{trash_talk}*_\n" \
                               "\n感謝所有為了 Whoscall Android 努力的大大們 :pray:\n"
error_message = "*不是 build master 不要亂 build !!!!*"
channel_id_core_android_dev = "G0197TMFQEM"
channel_id_test = "C050ZCNCDC3"
channel_id_android_code_review = "G2AVCDR7B"
authenticated_user_id = ['U6YR0399D', 'U6L1E3STZ']


# 定義一個 slash command 的處理函數
@slack_app.command("/build-rc")
def build_rc(ack, body, logger):
    ack("receive /build-rc command")
    logger.info(body)

    # if body['user_id'] in authenticated_user_id:
    #     create_rc_branch()


# create a rc branch by using GitPython
# def create_rc_branch():
#     # git clone
#     # git checkout -b
#     # git push
#     pass


@slack_app.command("/send-release-note")
def send_release_note(ack, body, logger):
    # 確認收到了指令
    send_code_freeze_notice(ack, body['user_id'], body['text'])


def send_code_freeze_notice(ack, user_id, param):
    if param != "":
        ack("receive /send-release-note command")
        params = param.split('#')

        # 發送訊息到指定頻道
        if user_id in authenticated_user_id:
            msg = code_freeze_reminder_message.format(release_version=params[0], trash_talk=params[1])
        else:
            msg = error_message

        slack_app.client.chat_postMessage(
            channel=channel_id_android_code_review,
            text=msg
        )
    else:
        ack("No version and trash talk !!!!")


def init(repo: Repository):
    print("init BuildMasterSlackApi")
    repo.print_repo_info()
    SocketModeHandler(slack_app, os.environ["SLACK_APP_TOKEN"]).start()
