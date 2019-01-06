# Commands to be used in rooms

from asgiref.sync import async_to_sync

from .models import *
from .consumers import *

from .runtime_constants import *

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
    output = ", ".join(channel_current_users[consumer.room_id])
    await consumer.server_message({'message': "<b>users online:</b> " + output,})

# /created
async def created_cmd(msg, consumer):
    """Returns when the room was created"""
    await consumer.server_message({'message': str(consumer.theroom.date),})

# /owner
async def owner_cmd(msg, consumer):
    """Returns the owner of the room"""
    await consumer.server_message({'message': "Owner of this room: " + str(consumer.theroom.room_owner),})

# Master dictionary containing all the commands and responding calls
# '<command name>': (<command function>, <clearance level>)
# Clearance levels:
# 0: No required permissions
# 1: Room admin command
tinmi_commands =  {
        'help': (help_cmd, 0),
        'ping': (ping_cmd, 0),
        'current': (current_cmd, 0),
        'owner': (owner_cmd, 0),
        'created': (created_cmd, 0)
        }

