#! /usr/bin/env python3

import socket
import threading
import select
import signal
import sys
import time

#basis for both classes acquired on 
#http://www.tutorialspoint.com/python/python_multithreading.htm
#and site found with help from SPC Primm
class myThread (threading.Thread):
	def __init__(self, sock):
		threading.Thread.__init__(self)
		self.sock = sock
		self.running = [1]
	def run(self):
		poller(self.sock, self.running)

#structure foudn with help from SPC Primm
class status:
	def __init__(self):
		self.channel = None
		self.sock = None
		self.worker = None

def poller(sock, running):
	#copied from https://pymotw.com/2/select/ and with help of SPC Primm
	READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
	TIMEOUT = 200
	poller = select.poll()
	poller.register(sock, READ_ONLY)
	fd_to_socket = { sock.fileno(): sock,}
	while running[0]:
	# Wait for at least one of the sockets to be ready for processing
		events = poller.poll(TIMEOUT)
		for fd, flag in events:
		# Retrieve the actual socket from its file descriptor
			s = fd_to_socket[fd]
			if flag & (select.POLLIN | select.POLLPRI):
				pong_handle(sock)

def user_create(sock):
	user = "user stephen james iracane reed\n"
	nick = "nick samuels\n"
	sock.send(bytes(user, 'utf-8'))
	sock.send(bytes(nick, 'utf-8'))
	x = sock.recv(1024)
	print(x.decode('utf-8'))

#ping response found with the help of SPC Primm
def pong_handle(sock):
	x = sock.recv(1024)
	x = x.decode("utf-8")
	if "PING" in x and ":Supports" not in x:
		sock.send(bytes("PONG " + x[6:] + '\n', 'utf-8'))
	else:
		print("\n" + x + "\nEnter a command: ", end="")
			
#basic outline for how to send message acquired from 
#https://github.com/dsprimm/uct/blob/master/uct.py

#handles the message sending	
def send_msg(session, message):
	message = message.split(" ", 1)
	session.sock.send(bytes("privmsg " + message[0] + " : " + message[1] + "\n", "utf-8"))
	print("\nEnter a command: ", end="")

#handles help
def send_help(session, void):
	session.sock.send(bytes("help\n", "utf-8"))

#handles quit
def send_quit(session, void):
	session.worker.running[0] = 0
	session.worker.join()
	session.sock.close()
	exit(0)

#logic and structure found from working with
#SPC Primm
#start
#handles switching channels
def channel_switch(session, channel):
	if channel[0] != "#":
		channel = "#" + channel
	if session.channel:
		leave(session, session.channel)
	session.channel = channel
	session.sock.send(bytes("join " + channel + "\n", "utf-8"))

#handles going afk in a channel
def away(session, message):
	if message:
		command = message.split(" ", 1)
		if len(command) > 1:
			command[1] = ":" + command[1]
			message = command[0] + " " + command[1]
		session.sock.send(bytes("away "+ message + "\n", "utf-8"))
	else:
		session.sock.send(bytes("away\n", "utf-8"))

#handles who is on
def ison(session, person):
	session.sock.send(bytes("ison "+person+"\n", "utf-8"))	

#handles leaving a channel
def leave(session, message):
	if message[0] != "#":
		message = "#" + message
	command = message.split(" ", 1)
	if len(command) > 1:
		command[1] = ":" + command[1]
		message = command[0] + " " + command[1]
	session.sock.send(bytes("part " + message + "\n", "utf-8"))
#end

#handles the who command to the server
def who(session, channel):
	session.sock.send(bytes("who " + channel + "\n", "utf-8"))

#handles chaning a nickname
def change_name(session, new_name):
	if new_name:
		if len(new_name) > 0 and len(new_name) <= 9:
			session.sock.send(bytes("nick " + new_name + "\n", "utf-8"))
		else:
			print("The length of the new username must be less than 9 characters long.\n")
	else:
		print("\nEnter a command: ", end="")

#handles pong			
def pong(session, void):
	print("\nEnter a command: ", end="")
	pass

#handles sending ping
def ping(session, target):
	if target:
		if len(target) <= 9:
			session.sock.send(bytes("ping " + target + "\n", "utf-8"))
		else:
			print("Invalid target given")
	else:
		print("\nEnter a command: ", end="")

#handles querying a nickname			
def who_is(session, name):
	if name:
		if len(name) > 0 and len(name) <= 9:
			session.sock.send(bytes("whois " + name + "\n", "utf-8"))
		else:
			print("Incorrect input given.\n")
	else:
		print("\nEnter a command: ", end="")

#handles giving the user the message of the day			
def motd(session, void):
	session.sock.send(bytes("motd\n", "utf-8"))	
	
#handles giving the user a list of other users
def lusers(session, void):
	session.sock.send(bytes("lusers\n", "utf-8"))

#handles listing who is in a channel	
def list1(session, channel):
	if channel:
		if channel[0] != "#":
			channel = "#" + channel
		session.sock.send(bytes("list "+ channel + "\n", "utf-8"))
	else:
		session.sock.send(bytes("list\n", "utf-8"))
		
#handles changing or seeing a topic of a channel		
def topic(session, channel):
	if channel:
		if channel[0] != "#":
			channel = "#" + channel
		channel = channel.split(" ", 1)
		
		if len(channel) > 1:
			channel[1] = ":" + channel[1]
			channel = channel[0] + " " + channel[1]
		else:
			channel = channel[0]
		
		session.sock.send(bytes("topic "+ channel + "\n", "utf-8"))
	else:
		print("\nEnter a command: ", end="")
	
#handles broadcasting a message	
def broadcast(session, message):
	if message[0] != ":":
		message = ":" + message
	session.sock.send(bytes("wallops "+ message + "\n", "utf-8"))
	
def main():
	commands = {
		"AWAY":away, "ISON":ison, "HELP":send_help, "INFO":send_help,
		"JOIN":channel_switch, "LIST":list1, "LUSERS":lusers, "MOTD":motd, "NICK":change_name, 
		"NOTICE":send_msg, "PART":leave, "PING":ping, "PONG":pong, "PRIVMSG":send_msg, "QUIT":send_quit, 
		"TOPIC":topic, "WALLOPS":broadcast, "WHO":who, "WHOIS":who_is
	}

	#sets up my socket connection and thread
	#start
	sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sd.connect(("127.0.0.1", 6667))
	session = status()
	session.sock = sd
	user_create(sd)
	session.worker = myThread(sd)
	session.worker.start()
	#end
	print("Enter a command: ", end="")
	while True:
		try:
			#takes input and makes sure there is input
			x = input()
			if len(x) > 0:
				#makes sure input starts with '/'
				if x[0] == '/':
					c = x.split(" ", 1)
					c[0] = c[0][1:].upper()
					command = c[0]
					#sends command based on length of given input
					if(len(c) > 1):
						if command in commands.keys():
							commands[command](session, c[1])
						else:
							print("Enter a command: ", end="")
					else:
						if command in commands.keys():
							commands[command](session, None)
						else:
							print("Enter a command: ", end="")
				elif session.channel:
					commands["NOTICE"](session, (session.channel + " " + x))
			else:
				print("Please enter something valid")
		except KeyboardInterrupt:
			#catches keyboard interrupt and closes gracefully
			print("\nKeyboard Interrupt caught..")
			session.worker.running[0] = 0
			session.worker.join()
			session.sock.close()
			break


if __name__ == "__main__":
	main()   
