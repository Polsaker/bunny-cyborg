#!/usr/bin/env python3

from irc import client
from chatterbot import ChatBot
import re
import time
import logging
import random
logging.getLogger(None).setLevel(logging.DEBUG)
logging.basicConfig()


class Bunny(object):
    def __init__(self):
        self.irc = client.IRCClient("rabbit")
        self.irc.configure(server = "iota.hira.io",
                           nick = "conejo--",
                           ident = "conejo--",
                           gecos = "Soy amigable")
                           
        self.irc.addhandler("pubmsg", self.on_msg)
#        self.irc.addhandler("privmsg", self.on_msg)
        self.irc.addhandler("welcome", self.autojoin)
        self.mc = ChatBot("Conejo")
        self.irc.connect()

    
    def autojoin(self, cli, ev):
        self.irc.join("#main")
    
    def on_msg(self, cli, ev):
        if ev.arguments[0][0] == "!" or ev.arguments[0][0] == "." or ev.arguments[0][0] == "$":
            return
        nicks = []
        for i in cli.channels[ev.target].users:
            nicks.append(i)
        big_regex = re.compile("(?i)" + '|'.join(map(re.escape, nicks)))
        text = big_regex.sub("#nick", ev.arguments[0])
        text = text.replace(self.irc.nickname, "#nick")
        output = self.mc.get_response(text)[0]['text']
        output = output.replace("#nick", ev.source)
        if output == "No possible replies could be determined.":
            return
#        if self.irc.nickname not in ev.arguments[0] and random.randint(0, 99) < 94:
#            cli.privmsg(ev.target, output)
#        if random.randint(0, 99) < 5:
        cli.privmsg(ev.target, output)
        
rabbit =  Bunny()

while rabbit.irc.connected == True:
    time.sleep(1) # Infinite loop of awesomeness
