import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSW = os.getenv('DB_PASSW')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')


# The code above supposes the use of python-dotenv library and .env file
# inside your code base (in main directory). Instead of that you can just
# create the same variables assigning your data to them. It will look like:
# API_TOKEN = ''
# DB_NAME = ''
# DB_USER = ''
# DB_PASSW = ''
# DB_HOST = ''
# DB_PORT = ''
# Inside the quotation marks should be your database data.

# Community id
# To find out an ID of a group, use @username_to_id_bot.
# After starting the bot, tap "Chat" button and provide your group.
# It's ID should begin with "minus" ("-").
# Add the ID inside the quotation marks, like this:
# COMMUNITY_ID = '-129934934922'
COMMUNITY_ID = '123'  # must be replaced to your community id
