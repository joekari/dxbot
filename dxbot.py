#!/usr/bin/env python

#TODO--------------TODO#
#----------------------#

#Strip nicks from quotes when saving
#Create function to connect to a page and get source instead of repeating every time
#Integrate with pastebin for dumping quotes

#----------------------#
#TODO--------------TODO#


import socket, random, sys, time, string, urllib2, re, HTMLParser, urllib, socket
import dicewords
from quotes import *
from reminders import *
from time import strftime

#Connection and login information
HOST = ""
PORT = 6667
NICK = "dx_bot"
USERNAME = "dx_bot"
REALNAME = "dx_bot"
CHAN = ""
PASS = ""

#Global storage variables
read=""
lastNick = ""
lastMessage = ""
names = ""

""" Gets configuration info from a config file """
def getConfig() :
	global HOST
	global PORT
	global NICK
	global USERNAME
	global REALNAME
	global CHAN
	global PASS
	with open('config.txt') as fo:
		for line in fo:
			config = line.split(', ')
			HOST 		= config[0]
			PORT 		= int(config[1])
			NICK 		= config[2]
			USERNAME 	= config[3]
			REALNAME 	= config[4]
			CHAN 		= config[5]
			PASS 		= config[6]
	fo.close()

""" Connects to the server, identifies, then connects to channel """
def connect():
	irc.connect((HOST,PORT))
	time.sleep(1)
	irc.send("PASS :%s\r\n" % PASS)
	irc.send("NICK :%s\r\n" % NICK)
	irc.send("USER :%s * * :%s\r\n" % (USERNAME, REALNAME))
	irc.send("JOIN :%s\r\n" % CHAN)

""" Helper function to determine whether a value is an integer """
def isInt(s):
	try:
		int(s)
		return True
	except ValueError:
		return False

""" Used for generic printing to console. Adds timestamp. """
def log(output):
	time = strftime("%H:%M:%S")
	print ''.join([time," - ",output,"\r\n"])

def getUrlContents(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.0')
	response = urllib2.urlopen(req)
	source = response.read()
	response.close()
	return source

"""
Dissects a given message into useful individual parts.
Probably doesn't need to be its own class. I think it was larger originally
"""
class IrcMessage:
	def __init__(self, msg):
		self.prefix, self.command, self.args = self.parsemsg(msg)

	def parsemsg(self, message):
		trailing = 0
		prefix = 0
		#This will be hit by non-PING messages the bot receives
		if message[0] == ":":
			#This split leaves <NICK>!<NICK>@irc.tinyspeck.com and <MESSAGE TYPE> <CHANNEL> :<MESSAGE>
			message = message[1:].split(' ', 1)
			prefix = message[0]
			message = message[1]
		#This denotes an actual message portion of a string
		if " :" in message:
			#This split leaves <MESSAGE TYPE> <CHANNEL> and <MESSAGE>
			message = message.split(" :", 1)
			trailing = message[1]
			message = message[0]
		#Splits into a list that looks like [<MESSAGE TYPE>, <CHANNEL>]
		args = message.split()
		#Pops <MESSAGE TYPE> off
		command = args.pop(0)
		#If there is actual text, add it to the end of arguments to have format [<CHANNEL>, <MESSAGE>]
		if trailing != 0:
			args.append(trailing)
		return prefix, command, args

""" Splits message into nick, channel, message, command, args """
class Privmsg:
	def __init__(self, msg) :
		try :
			#Prefix looks like this: <NICK>!<NICK>@irc.tinyspeck.com <MESSAGE TYPE> <CHANNEL> <NICK> :<MESSAGE>
			#So splitting on the !, gives the nick at the beginning
			self.nick = msg.prefix.split("!", 1)[0]
			#See IrcMessage to see how we know 0 and 1 are channel and message respectively
			self.channel = msg.args[0]
			self.message = msg.args[1]
			#In python .split(None) will split on one or more whitespace characters
			#If we split on the first whitespace and all commands are one word, then the first item should be the command
			self.command, self.args = self.message.split(None, 1)
			self.true = 1
		except :
			#This case should happen when the message is only a single string with no whitespace, so all of the message is command
			self.command = msg.args[1]
			self.args = None
			self.true = 0
		#If the current message isn't a command and isn't a PM to the bot
		if not (self.command).startswith("$") and self.channel == "#general":
			#Save to global tracking variables. This is necessary for the $grab function to save the prev message as a quote
			global lastNick
			global lastMessage
			lastNick = self.nick
			lastMessage = self.message
		#BasicCommands will check
		BasicCommands(self.nick, self.channel, self.message, self.command, self.args)

"""
Checks which (if any) commands are called and calls them
Could probably split the functions themselves to their own file to clean this up a little
"""
class BasicCommands:
	def __init__ (self, nick, channel, message, command, args) :
		#New class, so set everything in self for ease of use
		self.nick = nick
		self.channel = channel
		self.message = message
		self.command = command
		self.args = args
		if self.command == "$do" :
			self.do()
		elif self.command == "$mtg" :
			self.mtg()
		elif self.command == "$say" :
			self.say()
		elif self.command == "$commands" or self.command == "$help" :
			self.commands()
		elif self.command == "$member" :
			self.memberquery()
		elif self.command == "$quote" :
			self.quotes()
		elif self.command == "$dump" :
			self.dump()
		elif self.command == "$grab" :
			self.grab()
		elif self.command == "$remindme" :
			self.remindme()
		elif self.command == "/giphy" :
			self.giphy()
		elif self.command == "$stuff" :
			dicenum = ""
			output = ""
			#Randomly generate 6 numbers all between 0 and 5.
			for i in range(0,6):
				for j in range(0,5):
					dicenum = dicenum + str(random.randint(1, 6))
				#The dicenum references a string in the dicewords dict
				#Append the new string to whatever was there before
				output = ' '.join([output, dicewords.dicewords[dicenum]])
				dicenum = ""
			#Send the gibberish to everyone
			irc.send('PRIVMSG %s :%s\r\n' % (self.channel, output))
		#If there were no commands, check to see if the message contained a link
		elif self.channel == "#general" :
			#Jacked this from somewhere on the internet.. it's a pretty effective regex for detecting a url in a string
			pattern = re.compile('((http|https|ftp)\://|)([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&amp;%\$\-]+)*@)?((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.[a-zA-Z]{2,4})(\:[0-9]+)?(/[^/][a-zA-Z0-9\.\,\?\'\\/\+&amp;%\$#\=~_\-@]*)*')
			urls = re.findall(pattern, self.message, flags=0)
			#If there were actually any urls found
			if len(urls) != 0 :
				for u in urls :
					x = u[0]
					y = u[3]
					z = u [4]
					title = ""
					s = ""
					try :
						s = "http://" + u[4] + u[11]
						title = self.grabTitle(s)
					except :
						s = x + u[4] + u[11]
						self.grabTitle(s)
						title = self.grabTitle(s)
					self.shortenUrl(title, s)

	""" Private messages the user who sent the command a list of other commands and the format to call them """
	def commands(self) :
		if self.args == None :
			irc.send("PRIVMSG %s :$say <text> will make the bot print your text\r\n" % self.nick)
			irc.send("PRIVMSG %s :$do <text> will make the bot perform a /me of your text\r\n" % self.nick)
			irc.send("PRIVMSG %s :$skincode will message you a LoL skincode\r\n" % self.nick)
			irc.send("PRIVMSG %s :$mtg <card> will link you to a MTG card\r\n" % self.nick)
			irc.send("PRIVMSG %s :$stuff will print out a random string\r\n" % self.nick)
			# irc.send("PRIVMSG %s :$dump will message you all stored quotes\r\n" % self.nick)
			irc.send("PRIVMSG %s :$quote will print a random stored quote\r\n" % self.nick)
			irc.send("PRIVMSG %s :$quote # will print how many quotes are stored\r\n" % self.nick)
			irc.send("PRIVMSG %s :$quote <#> will print the numbered quote\r\n" % self.nick)
			irc.send("PRIVMSG %s :$quote <nickname> will print a random stored quote from that user\r\n" % self.nick)
			irc.send("PRIVMSG %s :$quote <nickname> <string> will store a new quote\r\n" % self.nick)
			irc.send("PRIVMSG %s :$grab will store the last non-command message as a quote\r\n" % self.nick)
		else :
			log("Extra args")

	""" Makes the bot do a /me of whatever is sent """
	def do(self) :
		if self.args == None :
			irc.send("PRIVMSG %s :$do <text> is the correct format\r\n" % self.nick)
		else :
			irc.send("PRIVMSG %s :\x01ACTION %s\x01\r\n" % (self.channel, self.args))

	""" Kind of a helper function to grab the title of the page that is passed in """
	def grabTitle(self, url) :
		try:
			req = urllib2.Request(url)
			req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.0')
			response = urllib2.urlopen(req)
			source = response.read()
			response.close()
			match = re.compile('<title>(.+?)</title>').findall(source)
			return match
		except:
			log("grab title except")
			return "except"

	""" Generates various links for a specfic mtg card """
	def mtg(self) :
		try:
			#Slidshocking Krow is a dumb joke card, so we of course have a special case for it
			if self.args.lower() == 'slidshocking krow' :
				irc.send("PRIVMSG %s :<Slidshocking Krow> [http://is.gd/WVZvnI] (https://i.imgur.com/AWTQ0bM.jpg)\r\n" % self.channel)
			else :
				#Gatherer always has the same start, so we really only have to worry about the actual card name being in the right format
				card_url = "http://gatherer.wizards.com/Pages/Card/Details.aspx?name=" + urllib.quote_plus(self.args)
				source = getUrlContents(card_url)
				#This is the element the card name is stored in.. this isn't the best way to do it. But it checks that element, grabs copy and if it isn't a bad match the card must exist
				match = re.compile('<span id="ctl00_ctl00_ctl00_MainContent_SubContent_SubContentHeader_subtitleDisplay"(?: style="font-size:.+?")?>(.+?)</span>').findall(source)
				if match != []:
					#If you called $mtg with no arguments it shouldn't actually get this far, but hey.. better safe than sorry
					if self.args == None :
						irc.send("PRIVMSG &s :Provide a card name\r\n", self.nick)
					else :
						try :
							#Set title so we can pass it to the shortener later
							title = self.args
							#Probably don't need temp2 to be unique, but oh well
							temp2 = self.args
							#This site is the one that has the spoiler image
							card_url2 = "http://magiccards.info/query?q=" + urllib.quote_plus(temp2)
							source = getUrlContents(card_url2)
							#Gets the link to all of the images that are on the page
							match2 = re.compile('<img src="(.+?).jpg').findall(source)
							if match != [] and self.args != None:
								#Save the link to the first image, because it should match our card the best (hopefully)
								image_url = match2[0]+".jpg"
								self.shortenUrl(title, card_url, image_url)
						except :
							log("Unable to generate card URLs")
				else:
					irc.send("PRIVMSG %s :Invalid card name, check your spelling\r\n" % (self.channel))
		except:
			log("mtg except")
			return "except"

	""" The bot will say whatever is sent after $say. Also works through private message, because why not? """
	def say(self) :
		if self.args == None :
			irc.send("PRIVMSG %s :$say <text> is the correct format\r\n" % self.nick)
		else :
			irc.send("PRIVMSG %s :%s\r\n" % (CHAN, self.args))

	""" Prints a shortened url and the title. If coming from $mtg, will also include some additional links """
	def shortenUrl(self, match, url, image=None) :
		try:
			giphy = re.compile("http://giphy");
			if giphy.match(url) == None :
				url = url.replace("https://", '').replace("http://", '').replace("ftp://", '')
				hostnme = url.split('/')[0]
				rip = socket.gethostbyname(hostnme)
				encode = urllib.quote_plus(url)
				temp = string.replace(encode, '+', '%2B')
				#is.gd is the url shortening site we use since it prints out the shortened url in an easy to grab way
				url = "http://is.gd/create.php?url=" + temp
				source = getUrlContents(url)
				#This is where the shortened url is actually contained in the page
				value = re.compile('id="short_url" value="(.+?)"').findall(source)

				html_parser = HTMLParser.HTMLParser()
				if match == self.args :
					for new_url in value :
						#If there is an image, that means the function was called from mtg
						if image != None :
							#This tries to find the first page when searching tcgplayer for the card name and returns the correct card about 95% of the time
							try :
								url = "www.google.com/search?q=site:http://tcgplayer.com+" + html_parser.unescape(match.replace("&middot;","|").lower().title()).replace(" ", "+")
							except :
								url = "www.google.com/search?q=site:http://tcgplayer.com+" + match.replace(" ", "+")
							src = getUrlContents(url)
							#This is where the link to the tcgplayer page for any returned cards are
							link = re.compile('<h3 class="r"><a href="\/url\?q=(.+?)&amp.+"').findall(src)
							try :
								#Tries to convert the title to a better format
								irc.send("PRIVMSG %s :<%s> [%s] (%s) {%s}\r\n" % (self.channel, html_parser.unescape(match.replace("&middot;","|").lower().title()), new_url, image, link[0]))
							except :
								#If that doesn't work, just use whatever is there
								irc.send("PRIVMSG %s :<%s> [%s] (%s) {%s}\r\n" % (self.channel, match, new_url, image, link[0]))
						else :
							#For everything else just send the title and the shortened url, convert if possible
							try :
								irc.send("PRIVMSG %s :<%s> [%s]\r\n" % (self.channel, html_parser.unescape(match.replace("&middot;","|").lower().title()), new_url))
							except :
								irc.send("PRIVMSG %s :<%s> [%s]\r\n" % (self.channel, match, new_url))
				else :
					#If there isn't a title we don't want a blank bar, so throw a default in
					if match == [] :
						match = ['Title not found']
					#There were a few edge cases where multiple things would be found.. the first title is always right
					match = [match[0]]
					#This should only happen once, but just in case
					for title in match :
						for new_url in value :
							try :
								#Tries to convert the title to a better format
								if image != None :
									irc.send("PRIVMSG %s :<%s> [%s] (%s) {%s}\r\n" % (self.channel, html_parser.unescape(title.replace("&middot;","|").lower.title()), new_url, image))
								else :
									irc.send("PRIVMSG %s :<%s> [%s]\r\n" % (self.channel, html_parser.unescape(title.replace("&middot;","|")), new_url))
							except :
								#Or just ust what is there
								if image != None :
									irc.send("PRIVMSG %s :<%s> [%s] (%s) {%s}\r\n" % (self.channel, title, new_url, image))
								else :
									irc.send("PRIVMSG %s :<%s> [%s]\r\n" % (self.channel, title, new_url))
		except:
			log("shortenURL except")

	""" Handles adding specific quotes, or printing specific quotes """
	def quotes(self) :
		quotesLength = len(quotesList)
		#If there are arguments we need to split (mostly relevant for adding quote)
		if self.args != None :
			split = (self.args).split()
		#If there are no args defualt behavior is to grab a random quote
		if self.args == None :
			#Only relevant when there have not been any quotes saved yet
			if quotesLength != 0:
				quotesIndex = random.randint(0, (quotesLength - 1))
				irc.send("PRIVMSG %s :%s - \"%s\"\r\n" % (self.channel, quotesList[quotesIndex][0].title(), quotesList[quotesIndex][1]))
		#$quote # is a request for the number of quotes that exist
		elif self.args == "#":
			irc.send("PRIVMSG %s :There are %s quotes saved.\r\n" % (self.channel, quotesLength))
		#$quote <NUMBER> is a request for a specific quote based on it's number
		elif isInt(self.args) :
			try:
				irc.send("PRIVMSG %s :%s - \"%s\"\r\n" % (self.channel, quotesList[int(self.args) - 1][0].title(), quotesList[int(self.args) - 1][1]))
			except:
				irc.send("PRIVMSG %s :There aren't that many quotes\r\n" % self.channel)
		#If there is an argument that isn't # or a number, then it should be a request for a quote from a specific user
		elif len(split) == 1 :
			noQuotesFoundForUser = True
			for person in userQuotes:
				if (person[0]).lower() == (self.args).lower():
					#The person list has a sublist that is [<NAME>, [<QUOTE>, <QUOTE>, ...]]
					irc.send("PRIVMSG %s :%s - \"%s\"\r\n" % (self.channel, person[0].title(), person[1][random.randint(0, (len(person[1]) - 1))]))
					noQuotesFoundForUser = False
			if noQuotesFoundForUser:
				irc.send("PRIVMSG %s :There are no quotes from that user\r\n" % self.channel)
		#If there is more than one argument, then it should be a user adding a quote
		elif len(split) > 1 :
			global names
			isUserValid = False
			#Make sure the user exists for real
			for name in names:
				if split[0].lower() == name.lower():
					isUserValid = True
			#If it is, the first string will be the name, the rest will be the quote itself
			if isUserValid:
				addQuote(split[0], split[1:])
				irc.send("PRIVMSG %s :Quote added\r\n" % self.channel)
			else:
				irc.send("PRIVMSG %s :Jordan is a dummy. Also, not a valid user.\r\n" % self.channel)

	""" Handles printing multiple quotes """
	def dump(self) :
		#Get length of the list containing quotes, to make it easier to loop
		quotesLength = len(quotesList)
		#If there are no arguments, all quotes are dumped
		if self.args == None:
			################################
			# Dump is temporarily disabled while I integrate pastebin
			################################

			# for i in range(0, quotesLength):
			# 	irc.send("PRIVMSG %s : %s - \"%s\"\r\n" % (self.nick, quotesList[i][0].title(), quotesList[i][1]))
		#The only other option is to print for a user, so do that
		else:
			for i in range(0, quotesLength):
				if quotesList[i][0].lower() == self.args.lower():
					irc.send("PRIVMSG %s : #%s %s - \"%s\"\r\n" % (self.nick, str(i + 1), quotesList[i][0].title(), quotesList[i][1]))
					sleep(0.5)

	""" Saves previous non-command message as a quote """
	def grab(self) :
		global names
		doesUserExist = False
		#Loop through the list of names and make sure the previous nick is a valid user
		for name in names:
			if lastNick.lower() == name.lower():
				doesUserExist = True
		#If the user was found, add the quote
		if doesUserExist:
			addQuote(lastNick.lower(), [lastMessage])
			irc.send("PRIVMSG %s :Quote added\r\n" % self.channel)
		else:
			irc.send("PRIVMSG %s :That is not a valid user.\r\n" % self.channel)

	def remindme(self) :
		if self.args == None :
			irc.send("PRIVMSG %s :Invalid format.\r\n" % self.channel)
		else :
			split = self.args.split(' ')
			valid = True
			if len(split) >= 3 :
				date = split[0]
				time = split[1]
				message = ' '.join(split[2:]).lstrip()
				if '/' not in date or re.match('\d\d\/\d\d', date, flags=re.IGNORECASE) == None :
					valid = False
					irc.send("PRIVMSG %s :Date format is incorrect. It should be mm/dd.\r\n" % self.channel)
				if ':' not in time or re.match('\d\d:\d\d', time) == None :
					valid = False
					irc.send("PRIVMSG %s :Time format is incorrect. It should be hh:mm in 24-hour format.\r\n" % self.channel)

				if valid :
					dateSplit = date.split('/')
					timeSplit = time.split(':')
					if int(dateSplit[0]) > 12 or int(dateSplit[0]) < 1 or int(dateSplit[1]) > 31 or int(dateSplit[1]) < 1 :
						valid = False
						irc.send("PRIVMSG %s :Invalid date.\r\n" % self.channel)
					if int(timeSplit[0]) > 24 or int(timeSplit[0]) < 0 or int(timeSplit[1]) > 59 or int(timeSplit[0]) < 0 :
						valid = False
						irc.send("PRIVMSG %s :Invalid time.\r\n" % self.channel)
				if valid :
					addReminder(self.nick, date, time, message)
					irc.send("PRIVMSG %s :Reminder added.\r\n" % self.channel)
			else :
				irc.send("PRIVMSG %s :Not enough arguments.\r\n" % self.channel)

isBotTryingToJoin = True
counter = 0
irc = socket.socket()
connect()

#requests a list of the names/nicks from the channel
irc.send("NAMES %s" % (CHAN,))

while True:
	try:
		read = read + irc.recv(1024)
	except socket.timeout, e:
		#pretty sure this block doesn't work even a little bit
		err = e.args[0]
		if err == 'timed out':
			sleep(1)
			counter = counter + 1
			if counter > 100:
				connect()
			continue
	else:
		temp = read.split("\r\n")
		#I can't figure out why this is here but it doesn't work w/o it
		#I'll worry about it later
		read = temp.pop()

		for msg in temp:
			log(msg)
			#Split message apart into useful components
			msg = IrcMessage(msg)
			#PING messages from the server require a PONG response or else the user will be timed out after a while
			if msg.command == "PING" :
				irc.send("PONG %s\r\n" % (msg.args[0],))
				reminders = checkReminders()
				if reminders != False :
					for reminder in reminders :
						irc.send("PRIVMSG %s :@%s %s\r\n" % (CHAN, reminder[1], reminder[4]))
						removeReminder(reminder[0])
				#This is for the pretty useless reconnect
				counter = 0
			#PRIVMSG are general messages to the channel and therefore we should check them for commands
			elif msg.command == "PRIVMSG" :
				Privmsg(msg)
			#JOIN triggers when the bot joins the channel..
			#Doesn't work for other users because slack doesn't fully disconnect users, just sets as away or something
			elif msg.command == "JOIN" :
				#Apparently these 2 lines make the 3rd work, but I don't have the slightest idea why
				msg.nick = msg.prefix.split("!", 1)[0]
				irc.send("PRIVMSG %s :Type $commands to see the bot's commands\r\n" % msg.nick)
				#irc.send("PRIVMSG %s :%s\r\n" % ("crypt", "Booting."))
			#This joins the channel, but I think is redundant since connect() exists
			elif isBotTryingToJoin and msg.command == "396" and msg.args[1] == "user/crypt/bot/dxbot" :
				irc.send("JOIN :%s\r\n" % (CHAN,))
				isBotTryingToJoin = False
			#353 is the response from the NAMES request from earlier.. this saves it to a variable we can use for quote stuff
			elif msg.command == "353":
				names = msg.args[3].rstrip().split()