# Use the package we installed
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from git.repository import Repository


class BuildMaster:
    # 設定環境變數
    SLACK_BOT_TOKEN = "xoxb-3184753415-5050441132624-Vuc5DxV1Fiy9ZiXp2gBBVlp7"
    # signing secrete for verifying the incoming request are coming from Slack
    SLACK_SIGNING_SECRET = "af070c2d7337a8c304036d9022a49951"
    SLACK_APP_TOKEN = "xapp-1-A050V33LZN0-5026080724214" \
                      "-dd472481c43e1254f3a9ef15769105729c196282d6634550ebae51dd2adb702a "

    # 訊息內容與要發送的頻道
    code_freeze_reminder_message = "<!here> 大大們日安\n" \
                                   "今天是 {release_version} code freeze 的日子\n" \
                                   "請把握最後進 develop branch 的時光，並請大大們幫忙\n" \
                                   "1. 儘早完成 PR review\n" \
                                   "2. 確認 branch name 符合 CircleCI run auto test 的觸發規則\n" \
                                   "\n_*{trash_talk}*_\n" \
                                   "\n感謝所有為了 Whoscall Android 努力的大大們 :pray:\n"
    release_note_message = "*Release Note* {release_note}\n"
    error_message = "*不是 build master 不要亂 build !!!!*"
    channel_id_core_android_dev = "G0197TMFQEM"
    channel_id_test = "C050ZCNCDC3"
    channel_id_android_code_review = "G2AVCDR7B"
    authenticated_user_id = ['U6YR0399D', 'U6L1E3STZ']
    github_slack_dict = {
        'christclin': 'U6L1E3STZ',
        'MichaelChangGogolook': 'U01GK3WFEP2',
        'jason-gogolook': 'U6YR0399D',
        'hmwu-gogolook': 'U9P2HTE8N',
        'WillyZhan': 'U02R2C2PV9V',
        'Hardcorevincent': 'U01JDJBBVFX',
        'EdenYuLai': 'U03QPUP1C9E',
        'carlosyanggogolook': 'U4846G01G',
    }

    def __init__(self, repo: Repository):
        self.repo = repo
        self.repo.print_repo_info()
        # self.repo.get_all()

        # Initializes your app with your bot token and signing secret
        self.slack_app = App(token=self.SLACK_BOT_TOKEN, signing_secret=self.SLACK_SIGNING_SECRET)
        self.slack_app.command("/code-freeze-notice")(self.send_code_freeze_notice)
        self.slack_app.command("/build-rc")(self.build_rc)
        self.slack_app.action("trigger_release_note")(self.prepare_release_note)
        self.slack_app.action("trigger_lokalise_link")(self.respond_lokalise_button)

        SocketModeHandler(self.slack_app, self.SLACK_APP_TOKEN).start()

    def send_code_freeze_notice(self, ack, body, logger):
        param = body['text']
        user_id = body['user_id']

        if param != "":
            # 確認收到了指令
            ack("receive /code-freeze-notice command")
            params = param.split('#')

            # 發送訊息到指定頻道
            if user_id in self.authenticated_user_id:
                msg = self.code_freeze_reminder_message.format(release_version=params[0], trash_talk=params[1])
            else:
                msg = self.error_message

            self.slack_app.client.chat_postMessage(channel=self.channel_id_test, text=msg)
        else:
            ack("No version and trash talk !!!!")

    def build_rc(self, ack, body, logger):
        ack("receive /build-rc command")
        logger.info(body)

        # create new rc branch
        rc_version = self.repo.new_branch("test_gradle_file")
        self.show_new_branch_info(rc_version)

        # fire a pr request to update version to develop branch
        pr_link = self.repo.upgrade_gradle_version_with_pull_request("test_gradle_file")
        self.show_pr_link(pr_link)

        # edit release note
        pr_list = self.repo.get_pr_list("v" + rc_version[0] + "." + rc_version[1])
        self.edit_release_note('\n'.join(pr_list))

    # TODO show branch url in the future
    def show_new_branch_info(self, version):
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "New branch created - " + "*rc_v" + version[0] + "." + version[1] + "*"
                }
            }
        ]
        self.slack_app.client.chat_postMessage(channel=self.channel_id_test, blocks=blocks)

    def show_pr_link(self, link):
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "upgrade version PR link - " + link
                }
            }
        ]
        self.slack_app.client.chat_postMessage(channel=self.channel_id_test, blocks=blocks)

    def edit_release_note(self, note):
        blocks = [
            {
                "type": "input",
                "block_id": "release_note_block",
                "label": {
                    "type": "plain_text",
                    "text": "Release Note"
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "plain_input",
                    "multiline": True,
                    "initial_value": note,
                    "focus_on_load": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Placeholder text for single-line input"
                    }
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "trigger_release_note",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Approve"
                        },
                        "style": "primary"
                    },
                ]
            }
        ]
        self.slack_app.client.chat_postMessage(channel=self.channel_id_test, blocks=blocks, link_names=1)

    def prepare_release_note(self, ack, body, logger):
        param = body['state']['values']['release_note_block']['plain_input']['value']
        user_id = body['user']['id']

        if param != "":
            # 這邊要先更新訊息，不然會出現錯誤
            self.slack_app.client.chat_update(channel=body['container']['channel_id'],
                                              ts=body['container']['message_ts'],
                                              token=self.SLACK_BOT_TOKEN,
                                              blocks=[
                                                  {"type": "section",
                                                   "text": {
                                                       "type": "plain_text",
                                                       "text": "Start preparing release note and send to #android-code-review"}
                                                   }
                                              ])

            # 確認收到了指令
            ack("receive /send-release-note command")

            # 將 github 的 author 轉換成 slack 的 user id
            for github_author in self.github_slack_dict:
                param = param.replace('@' + github_author, '<@' + self.github_slack_dict[github_author] + '>')

            if user_id in self.authenticated_user_id:
                msg = self.release_note_message.format(release_note=param)
            else:
                msg = self.error_message

            self.slack_app.client.chat_postMessage(channel=self.channel_id_test, link_names=1, text=msg)
            self.create_lokalise_link_button()
        else:
            ack("Please fill in the release note")

    def create_lokalise_link_button(self):
        blocks = [
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "trigger_lokalise_link",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Edit repo on Lokalise"
                        },
                        "style": "primary",
                        "url": "https://app.lokalise.com/apps/2040831962fb898204d2d7.07443301/github"
                    },
                ]
            }
        ]
        self.slack_app.client.chat_postMessage(channel=self.channel_id_test, blocks=blocks)

    def respond_lokalise_button(self, ack, body, logger):
        ack()
        self.slack_app.client.chat_update(channel=body['container']['channel_id'],
                                          ts=body['container']['message_ts'],
                                          token=self.SLACK_BOT_TOKEN,
                                          blocks=[
                                              {"type": "section",
                                               "text": {
                                                   "type": "plain_text",
                                                   "text": "Done!"}
                                               }
                                          ])
