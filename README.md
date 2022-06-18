
     _____ _            _   _ _ _   _                 _         _                      _      ___  ___                                  
    |_   _| |          | | | | | | (_)               | |       | |                    | |     |  \/  |                                  
      | | | |__   ___  | | | | | |_ _ _ __ ___   __ _| |_ ___  | |    _   _ _ __   ___| |__   | .  . | __ _ _ __   __ _  __ _  ___ _ __ 
      | | | '_ \ / _ \ | | | | | __| | '_ ` _ \ / _` | __/ _ \ | |   | | | | '_ \ / __| '_ \  | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
      | | | | | |  __/ | |_| | | |_| | | | | | | (_| | ||  __/ | |___| |_| | | | | (__| | | | | |  | | (_| | | | | (_| | (_| |  __/ |   
      \_/ |_| |_|\___|  \___/|_|\__|_|_| |_| |_|\__,_|\__\___| \_____/\__,_|_| |_|\___|_| |_| \_|  |_/\__,_|_| |_|\__,_|\__, |\___|_|   
                                                                                                                     __/ |          
                                                                                                                    |___/


# WIP

![GitHub](https://img.shields.io/github/license/morry98/ultimate-lunch-manager)
![GitHub top language](https://img.shields.io/github/languages/top/morry98/ultimate-lunch-manager)
![GitHub issues](https://img.shields.io/github/issues/morry98/ultimate-lunch-manager)

[![Coverage Status](https://coveralls.io/repos/github/Morry98/ultimate-lunch-manager/badge.svg?branch=master)](
https://coveralls.io/github/Morry98/ultimate-lunch-manager?branch=master)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=Morry98_ultimate-lunch-manager&metric=bugs)](
https://sonarcloud.io/summary/new_code?id=Morry98_ultimate-lunch-manager)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=Morry98_ultimate-lunch-manager&metric=vulnerabilities)](
https://sonarcloud.io/summary/new_code?id=Morry98_ultimate-lunch-manager)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Morry98_ultimate-lunch-manager&metric=code_smells)](
https://sonarcloud.io/summary/new_code?id=Morry98_ultimate-lunch-manager)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Morry98_ultimate-lunch-manager&metric=alert_status)](
https://sonarcloud.io/summary/new_code?id=Morry98_ultimate-lunch-manager)

[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=Morry98_ultimate-lunch-manager&metric=ncloc)](
https://sonarcloud.io/summary/new_code?id=Morry98_ultimate-lunch-manager)
![GitHub stars](https://img.shields.io/github/stars/morry98/ultimate-lunch-manager)
![GitHub pull requests](https://img.shields.io/github/issues-pr/morry98/ultimate-lunch-manager)

An advanced slack bot for lunch managing.

You need to set only the token for slack, when you start it you can set
all the configurations directly inside the chat.

Every day it will send a message in the channel, and directly to all the people enable direct notification, 
taking the count of how many people are participating.  
After n hours/minutes it will start writing directly to each person asking the possible hours and places to go.  
At a certain hour it will write in the channel the result, the best hour, the best place and people count.  
If there are conflicts it tries to fi them writing directly to interested people.  
You need only to book the place it writes and then press the booked button, if there are problem you can press 
booking problems. In case of booking problems it will automatically change the place, if it's possible.


# Quickstart
Tested only on python 3.10, it probably works with lower versions.


## Installation

Create a Python virtual environment, activate it and install the
requirements.  
For local development, you can install the requirements using the
scripts `requirements-dev-install.bat` or `requirements-dev-install.sh`,
depending on your platform.


## Create slack bot

Create a Slack App starting from [https://api.slack.com/apps](https://api.slack.com/apps).  
Give your app a name, and a workspace you will develop the app in.

## Slack permissions

Todo

## Get Slack token

Go to App-Level Tokens and generate a new token for the app, adding the
`connections:write` scope.  
Copy the generated token and use it for the `SLACK_APP_TOKEN` env
variable.

Go to Socket Mode page and enable it.

Go to OAuth & Permissions page and add the needed OAuth scopes under Bot
Token Scopes.

Go to Install App page and install the app to your workspace. Copy the
generated Bot User OAuth Token and use it for the `SLACK_TOKEN_SOCKET`
env variable.

## Start Python bot

Set the Slack tokens in the config, run ```python main.py``` and Enjoy!

# Usage

Todo

