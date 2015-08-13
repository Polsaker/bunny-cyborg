#!/usr/bin/env python3

from irc import client
import pyborg
import re
import time
import logging
import random
import json
import base64
from queue import Queue
from threading import Thread
import traceback

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
                           gecos = self.config['gecos'],
                           sasl = self.config['sasl'],
                           if sasl = True:
                               sasl_username = self.config['sasl_username']
                               sasl_password = self.config['sasl_password']
                           else:
                               pass
                           
        self.irc.addhandler("pubmsg", self.on_msg)
        self.irc.addhandler("welcome", self.autojoin)
        self.irc.addhandler("invite", self.invited)
        self.irc.addhandler("join", self.joining)
        self.mc = pyborg.pyborg()
        logging.info("Connecting")
        
        # Hack to send the server password. This gets queued but not sent until we connect
        if sasl = True:
            self.irc.send("CAP REQ :sasl")
            self.irc.send("AUTHENTICATE PLAIN")
            sasldatastr= "%s\0%s\0%s" % (account_username, account_username, account_password)
            self.irc.send("AUTHENTICATE " + base64.b64encode(datastr.encode()).decode())
            self.irc.send("CAP END")
        else:
            pass
        if len(self.config['password']) != 0:
            self.irc.send("PASS " + self.config['password'])
        else:
            pass
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
        ev.target = ev.target.lower()
        if ev.source2.host not in self.config['owners']:
            owner = 0
        else:
            owner = 1
        if ev.arguments[0][0] == "!" and owner == 1:
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
                del self.config['channels'][ev.splitd[1]]
                cli.part(ev.splitd[1])
            elif ev.splitd[0] == "!quit":
                cli.disconnect("Bye :-(")
            elif ev.splitd[0] == "!channels":
                cli.privmsg(ev.target, ", ".join(list(cli.channels)))
                    
            
            json.dump(self.config, open("config.json", 'w'), indent=2)
            
        #if ev.arguments[0][0] == "!" or ev.arguments[0][0] == "." or ev.arguments[0][0] == "$":
        #    return
        
        nicks = []
        for i in cli.channels[ev.target].users:
            nicks.append(i)
        big_regex = re.compile("(?i)" + '|'.join(map(re.escape, nicks)))
        
        text = big_regex.sub("#nick", ev.arguments[0])
        text = text.replace(self.irc.nickname, "#nick")
        
        replyrate = self.config['channels'][ev.target]['replyrate'] if cli.nickname not in ev.arguments[0] else 99
        
        self.mc.process_msg(self, text, 
                    replyrate,
                    1,  # TODO (learn argument)!
                    (text, ev.source, ev.target, None, None),
                    owner, 
                    self.config['talk'] or self.config['channels'][ev.target]['talk'])

    
    def output(self, message, args):
        self.irc.privmsg(args[2], message.replace("#nick", args[1]))
        
rabbit =  Bunny()



while rabbit.irc.connected == True:
    time.sleep(1) # Infinite loop of awesomeness
