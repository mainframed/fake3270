#!/usr/bin/env python


# # FAKE TN3270 by Soldier of FORTRAN
#
# This is a fake TN3270 generator. Used to make fake tn3270 streams to
# help me make art.
#
# ## Requirements:
#
# Needs tn3270 lib (https://github.com/zedsec390/tn3270lib) to run
#
# ## Notes:
#
# This is fairly barebones. Ideally you can read this guide
# (http://www.tommysprinkle.com/mvs/P3270/index.htm) to understand tn3270
# datastreams then edit fake3270.py line 72 to add your own TN3270 data.
#
# ## Usage
#
# ./fake3270.py
#
# then connect with any tn3270 client (x3270/c3270/TN3270-X/Attachmate, whatever)
#
# Copyright: GPL 3



import tn3270lib
import socket
import time
import ssl
import struct
import select
import SocketServer
import random
import os
import sys
import signal
import binascii
import argparse
from socket import *
import thread

try:
	from OpenSSL import SSL
	openssl_available = True
except ImportError:
	print "[!!] OpenSSL Library not available. SSL Disabled!"
	openssl_available = False

class c:
    BLUE = '\033[94m'
    DARKBLUE = '\033[0;34m'
    PURPLE = '\033[95m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[1;37m'
    ENDC = '\033[0m'
    DARKGREY = '\033[1;30m'
    

    def disable(self):
        self.BLUE = ''
        self.GREEN = ''
        self.YELLOW = ''
	self.DARKBLUE = ''
	self.PURPLE = ''
	seld.WHITE= ''
        self.RED = ''
        self.ENDC = ''


def send_tn(clientsock, data):
	clientsock.sendall(data)

def recv_tn(clientsock, timeout=100):
	rready,wready,err = select.select( [clientsock, ], [], [], timeout)
	#print len(rready)
	if len(rready): 
		data = clientsock.recv(1920)
	else:
		data = ''
	return data

def signal_handler(signal, frame):
        print c.ENDC+ "\nGAME OVER MAN!\n"
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


#########################################################################
# PUT YOUR FAKE TN3270 INFORMATION HERE                                 #
# Read http://www.tommysprinkle.com/mvs/P3270/index.htm for more info   #
#########################################################################

def fake_3270():
	tn3270_stuff = ( binascii.unhexlify("057A1100001D00") +
            "Here lies trouble".decode('utf-8').encode('EBCDIC-CP-BE'))
	tn3270_stuff += ("\x29\x01\x42\xF1"+"Double Trouble".decode('utf-8').encode('EBCDIC-CP-BE'))
	return tn3270_stuff

#########################################################################

def logo():
	print c.DARKBLUE
	logo = []
	logo.append("""
  _______  _______  ___   _  _______  __   __    _  __   _______  _______  _______  _______
 |       ||   _   ||   | | ||       ||  | |  |  | ||  | |       ||       ||       ||  _    |
 |    ___||  |_|  ||   |_| ||    ___||__| |   |_| ||__| |___    ||____   ||___    || | |   |
 |   |___ |       ||      _||   |___      |       |      ___|   | ____|  |    |   || | |   |
 |    ___||       ||     |_ |    ___|     |  _    |     |___    || ______|    |   || |_|   |
 |   |    |   _   ||    _  ||   |___      | | |   |      ___|   || |_____     |   ||       |
 |___|    |__| |__||___| |_||_______|     |_|  |__|     |_______||_______|    |___||_______|""")
	print logo[0], "\n"
	print c.ENDC

def printv(str):
	""" Prints str if we're in verbose mode """
	if args.verbose:
		print str

def get_all(sox):
	#terrible, I know	
	data = ''
	while True:
		d = recv_tn(sox,1)
		if not d:
			break
		else:
			data += d
	return data


def handler(clientsock,addr,tn3270, screen):
	#Begin tn3270 negotiation:
	send_tn(clientsock, tn3270lib.IAC + tn3270lib.DO + tn3270lib.options['TN3270'])
	tn3270.msg("Sending: IAC DO TN3270")
	data  = recv_tn(clientsock)
	if data == tn3270lib.IAC + tn3270lib.WILL + tn3270lib.options['TN3270']:
		tn3270.msg("Received Will TN3270, sending IAC DONT TN3270")
		send_tn(clientsock, tn3270lib.IAC + tn3270lib.DONT + tn3270lib.options['TN3270'])
		data  = recv_tn(clientsock)

	if data != tn3270lib.IAC + tn3270lib.WONT + tn3270lib.options['TN3270']:
		#We don't support 3270E and your client is messed up, exiting
		tn3270.msg("Didn't negotiate tn3270 telnet options, quitting!")
		clientsock.close()
		return

	send_tn(clientsock, tn3270lib.IAC + tn3270lib.DO + tn3270lib.options['TTYPE'])
	tn3270.msg("Sending: IAC DO TTYPE")
	data  = recv_tn(clientsock)
	send_tn(clientsock, tn3270lib.IAC  + 
		                tn3270lib.SB   + 
		                tn3270lib.options['TTYPE'] +
		                tn3270lib.SEND +
		                tn3270lib.IAC  +
		                tn3270lib.SE  )
	data  = recv_tn(clientsock)
	tn3270.msg("Sending: IAC DO EOR")
	send_tn(clientsock, tn3270lib.IAC + tn3270lib.DO + tn3270lib.options['EOR'])
	data  = recv_tn(clientsock)
	tn3270.msg("Sending: IAC WILL EOR; IAC DO BINARY; IAC WILL BINARY")
	send_tn(clientsock, tn3270lib.IAC  + 
		                tn3270lib.WILL + 
		                tn3270lib.options['EOR'] +
		                tn3270lib.IAC  +
		                tn3270lib.DO   +
		                tn3270lib.options['BINARY'] +
		                tn3270lib.IAC  +
		                tn3270lib.WILL +
		                tn3270lib.options['BINARY']  )

	data = get_all(clientsock)
	buff = list("\0" * 1920)
	buff_addr = 0
	current_screen = 0
	timing = 0
	send_tn(clientsock, screen[current_screen] + tn3270lib.IAC + tn3270lib.TN_EOR)
	# First we wait:
	data  = recv_tn(clientsock)
	data  += get_all(clientsock)
	not_done = True
	clientsock.close()
	print "[+] Connection Closed", addr



#start argument parser
parser = argparse.ArgumentParser(description='Fake\'n\'3270: A fake Tn3270 screen for testing art.')
parser.add_argument('-p','--port',help='The TN3270 server port. Default is 23', dest='port', default=23, type=int)
parser.add_argument('-v','--verbose',help='Be verbose',default=False,dest='verbose',action='store_true')
parser.add_argument('-d','--debug',help='Show debug information. Displays A LOT of information',default=False,dest='debug',action='store_true')
args = parser.parse_args()

logo()

print '[+] Starting fake\'n\'3270'

# First we need an object:
tn = tn3270lib.TN3270()

if args.debug:
	tn.set_debuglevel(1)

######################################>>>>>>>>>>>>>
print "[+] Creating fake TN3270 screen on port",
print args.port
screen = []
screen.insert(0,fake_3270())
ADDR = ('', args.port)

print "[+] Creating Plaintext Socket"
tnsock = socket(AF_INET, SOCK_STREAM)
tnsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

tnsock.bind(ADDR)
tnsock.listen(5)

print "[+] Waiting for Incomming Connections on port", 
print args.port
while 1:
	clientsock, addr = tnsock.accept()
	print '[+] Connection Recieved from:', addr
	thread.start_new_thread(handler, (clientsock, addr, tn, screen ))

#######################>>>>>>>>>>





