#!/usr/bin/env python3

from irc import client
from chatterbot import ChatBot
import re
import time
import logging
import random
import json

logging.getLogger(None).setLevel(logging.INFO)
logging.basicConfig()


class Bunny(object):
    def __init__(self):
        logging.info("Starting")
        self.config = json.load(open("config.json"))
        
        self.irc = client.IRCClient("rabbit")
        self.irc.configure(server = self.config['server'],
                           nick = self.config['nick'],
                           ident = self.config['ident'],
                           gecos = self.config['gecos'])
                           
        self.irc.addhandler("pubmsg", self.on_msg)
        self.irc.addhandler("welcome", self.autojoin)
        self.irc.addhandler("invite", self.invited)
        self.irc.addhandler("join", self.joining)
        self.mc = ChatBot("Conejo")
        logging.info("Connecting")
        self.irc.connect()

    
    def invited(self, cli, ev):
        if self.config['followinvites']:
            cli.join(ev.arguments[0])
    
    def joining(self, cli, ev):
        if ev.source2.nick == cli.nickname:
            logging.info("Joined {0}".format(ev.target))
            ev.target = ev.target.lower()
            try:
                self.config['channels'][ev.target]
            except:
                self.config['channels'][ev.target] = {}
                self.config['channels'][ev.target]['talk'] = True
                self.config['channels'][ev.target]['replyrate'] = self.config['replyrate']
                json.dump(self.config, open("config.json", 'w'), indent=2)

    def autojoin(self, cli, ev):
        logging.info("Joining channels")
        for i in self.config['channels']:
            self.irc.join(i)
    
    def on_msg(self, cli, ev):
        ev.target2 = ev.target
        ev.target = ev.target.lower()
        if ev.arguments[0][0] == "!":
            if ev.source2.host not in self.config['owners']:
                return
            if ev.splitd[0] == "!shutup":
                self.config['channels'][ev.target]['talk'] = False
                cli.privmsg(ev.target, "Ok :-(")
            elif ev.splitd[0] == "!wakeup":
                self.config['channels'][ev.target]['talk'] = True
                cli.privmsg(ev.target, "Whoooo!")
            elif ev.splitd[0] == "!replyrate":
                self.config['channels'][ev.target]['replyrate'] = int(ev.splitd[1])
                cli.privmsg(ev.target, "Now replying to {0}% of messages".format(ev.splitd[1]))
            elif ev.splitd[0] == "!noinvite":
                self.config['followinvites'] = False
                cli.privmsg(ev.target, "Not following invites anymore")
            elif ev.splitd[0] == "!invite":
                self.config['followinvites'] = True
                cli.privmsg(ev.target, "Now following invites")
            elif ev.splitd[0] == "!join":
                cli.join(ev.splitd[1])
            elif ev.splitd[0] == "!part":
                cli.part(ev.splitd[1])
            elif ev.splitd[0] == "!quit":
                cli.disconnect("Bye :-(")
            
            json.dump(self.config, open("config.json", 'w'), indent=2)
            
        if ev.arguments[0][0] == "!" or ev.arguments[0][0] == "." or ev.arguments[0][0] == "$":
            return
        
        nicks = []
        for i in cli.channels[ev.target2].users:
            nicks.append(i)
        big_regex = re.compile("(?i)" + '|'.join(map(re.escape, nicks)))
        
        text = big_regex.sub("#nick", ev.arguments[0])
        text = text.replace(self.irc.nickname, "#nick")
        output = self.mc.get_response(text)  # This is what makes the bot actually learn!
        if self.config['talk'] is False or self.config['channels'][ev.target]['talk'] is False:
            return
        
        output = output.replace("#nick", ev.source)
        
        if output == "No possible replies could be determined.":
            return
        
        if self.irc.nickname not in ev.arguments[0] and random.randint(0, 99) < 94:
            cli.privmsg(ev.target, output)
            return
            
        if random.randint(0, 99) < self.config['channels'][ev.target]['replyrate']:
            cli.privmsg(ev.target, output)
        
rabbit =  Bunny()

while rabbit.irc.connected == True:
    time.sleep(1) # Infinite loop of awesomeness
