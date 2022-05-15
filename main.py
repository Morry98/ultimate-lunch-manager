from loguru import logger as log
import os
import re

from dotenv import load_dotenv
import pyjokes
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

log.start(__file__, level="INFO")

load_dotenv()

SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')
SLACK_TOKEN_SOCKET = os.getenv('SLACK_TOKEN_SOCKET')

app = App(token=SLACK_APP_TOKEN, name="The Ultimate Lunch Manager")

CHANNEL_ID = None
CHANNEL_NAME = None
POSSIBLE_TIME = []


@app.message(re.compile(".*"))
def show_random_joke(message, say):
    log.info("Received message: {}".format(message))
    channel_type = message["channel_type"]
    if channel_type != "im":
        log.info(f"{message['user']} tried to use joke command in {message['channel']}")
        return

    dm_channel = message["channel"]
    user_id = message["user"]

    joke = pyjokes.get_joke()

    say(text=joke, channel=dm_channel)


@app.event("message")
def handle_message_events(message, say):
    log.info("Received message: {}".format(message))

    dm_channel = message["channel"]
    user_id = message["user"]

    say(text="Invalid command", channel=dm_channel)


@app.command("/start")
def repeat_text(ack, respond, command):
    global CHANNEL_ID
    global CHANNEL_NAME
    ack()
    if CHANNEL_ID is None:
        CHANNEL_ID = command["channel_id"]
        CHANNEL_NAME = command["channel_name"]
        user_name = command["user_name"]
        respond(text=f"Bot is started in this channel by {user_name}", response_type="in_channel")
        respond(text={
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Configurations :gear:",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*These are the times already entered:*\n- 12:45\n- 01:00"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Add new value",
                                "emoji": True
                            },
                            "value": "time_config",
                            "action_id": "add_new"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Delete a value",
                                "emoji": True
                            },
                            "value": "time_config",
                            "action_id": "delete"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Delete all",
                                "emoji": True
                            },
                            "style": "danger",
                            "value": "time_config",
                            "action_id": "delete_all"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Confirm values",
                                "emoji": True
                            },
                            "style": "primary",
                            "value": "time_config",
                            "action_id": "confirm"
                        }
                    ]
                }
            ]
        }, response_type="ephemeral")
    elif CHANNEL_ID == command["channel_id"]:
        respond(text="Already running in this channel!\nIf you want to stop use /stop", response_type="ephemeral")
    else:
        respond(text=f"Already running in another channel: {CHANNEL_NAME}\nIf you want to move it use /move", response_type="ephemeral")


@app.action("update_configs")
def handle_some_action(ack, body, logger):
    ack()
    log.info(body)


def main():
    handler = SocketModeHandler(app, SLACK_TOKEN_SOCKET)
    handler.start()


if __name__ == "__main__":
    main()
