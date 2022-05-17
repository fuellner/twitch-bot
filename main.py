import os
import random
import socket
import ssl
from dotenv import load_dotenv

load_dotenv()

def send(irc: ssl.SSLSocket, message: str):
    # \r\n => CR + LF als Indikator, dass message zuende ist
    irc.send(bytes(f'{message}\r\n', 'UTF-8'))  # type: ignore

def send_pong(irc: ssl.SSLSocket):
    print('PONG')
    send(irc, 'PONG :tmi.twitch.tv')

def send_chatmessage(irc: ssl.SSLSocket, message: str, channel: str):
    send(irc, f'PRIVMSG {channel} :{message}')

def handle_chat(irc: ssl.SSLSocket, raw_message: str):
    components = raw_message.split()
    user, host = components[0].split('!')[1].split('@')
    channel = components[2]
    message = ' '.join(components[3:])[1:]
    if message.startswith('!'):
        message_components = message.split()
        command = message_components[0][1:].lower()
        
        if command == 'würfel':
            nummer = random.randint(1, 6)
            send_chatmessage(irc, f'{user} deine Würfelzahl ist: {nummer}', channel)
        if command == 'grüße':
            nutzer = ' '.join(message_components[1:])
            send_chatmessage(irc, f'Hallo und herzlich willkommen {nutzer}', channel)

if __name__ == '__main__':
    bot_username = os.environ["BOT_NICK"]
    channel_name = os.environ["CHANNEL"]
    oauth_token = os.environ["TMI_TOKEN"]

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    irc = context.wrap_socket(socket)

    # connect to twitch irc server
    irc.connect(('irc.chat.twitch.tv', 6697))

    send(irc, f'PASS oauth:{oauth_token}')
    send(irc, f'NICK {bot_username}')
    send(irc, f'JOIN {channel_name}')

    while True:
        data = irc.recv(1024)
        raw_message = data.decode('UTF-8')

        for line in raw_message.splitlines():
            if line.startswith('PING :tmi.twitch.tv'):
                send_pong(irc)
            else:
                components = line.split()
                command = components[1]

                if command == 'PRIVMSG':
                    handle_chat(irc, line)

                print(line)
