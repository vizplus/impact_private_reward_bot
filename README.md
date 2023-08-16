# TG-bot-VIZ
Telegram bot for interacting with VIZ blockchain.
With the help of this bot a user (administrator of a private Telegram group) can award group members with VIZ token. It can be done by forwarding the target message to this bot in Telegram. Bot will parse administrator's name, reciever's Telegram ID and unique identifier of the group (COMMUNITY_ID) in which the message had appeared. The latter must be provided by the administrator (it's in config.py).

## Getting Started
You can clone this repository by using terminal command:
```
git clone https://github.com/David-Roklem/TG-bot-VIZ.git
```
Don't forget to create API token using @BotFather. This token must be added to .env file under API_TOKEN variable

### Dependencies
```
python = ">=3.8.1,<4.0.0"
aiogram = ">=2.25.1,<3.0.0rc1"
python-dotenv = "^0.21.0"
asyncpg = "^0.27.0"
viz-python-lib = {url = "https://github.com/VIZ-Blockchain/viz-python-lib/archive/refs/heads/master.zip"}
ecdsa = "^0.18.0"
```

### Installing
This project uses poetry as a package manager as well as virtual environment. So install poetry with the command in terminal:
```
pip install poetry
```
After that, for installing all the required dependencies, run:
```
poetry install
```
Alternatively, if you don't want to use Poetry, there is ready-to-use requirements.txt file

### PostgreSQL
The code base is adapted for utilizing PostgreSQL. If you wish to use another database, you will need to rewrite code in order to satisfy new requirements

### Executing program
As this project uses [https://pypi.org/project/python-dotenv/](python-dotenv) library, first of all you need to configure your .env with the following variables:
```
API_TOKEN=''
DB_NAME=''
DB_USER=''
DB_PASSW=''
DB_HOST=''
DB_PORT=''
```

### pip or poetry
If you want to use this bot on you local machine, you can choose either pip or poetry. With poetry usage there is the instruction above, In case you decide to use pip, you wil need this command:
```
pip install -r requirements.txt
```
Also, you will need to install viz-python-lib separately (as it is not production ready to install it from PyPI yet):
```
pip install https://github.com/VIZ-Blockchain/viz-python-lib/archive/refs/heads/master.zip
```

### Deployment
If you want to deploy the bot to a server (e.g. VPS/VDS), it is recommended to use Docker. Dockerfile and docker-compose.yml are already present in this project. Obviously, there are other options such as cloud platforms, PaaS etc. which don't require Docker.