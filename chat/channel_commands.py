# Commands to be used in channels

from asgiref.sync import async_to_sync

from .models import *
from .consumers import *

# Declare the list of commands. Commands are added at the end of this file
tinmi_commands = {}

#
#---COMMANDS---
# 
# Each command must have arguments: msg and consumer
# Also each command should have a one-line Docstring for the help command

# /help
async def help_cmd(msg, consumer):
    """Lists available commands"""
    for k, v in tinmi_commands.items():
        output = "<b>/{0}</b>: {1}".format(k, v[0].__doc__)
        await consumer.server_message({'message': output,})

# /ping
async def ping_cmd(msg, consumer):
    """Returns 'Pong!'"""
    await consumer.server_message({'message': "Pong!",})
# /current
async def current_cmd(msg, consumer):
    """Lists all current users in the chatroom"""
    output = ", ".join(consumer.theroom.current_users)
    await consumer.server_message({'message': "<b>users online:</b> " + output,})


# Master dictionary containing all the commands and responding calls
# '<command name>': (<command function>, <clearance level>)
# Clearance levels:
# 0: No required permissions
# 1: Room admin command
tinmi_commands =  {
        'help': (help_cmd, 0),
        'ping': (ping_cmd, 0),
        'current': (current_cmd, 0),
        }

