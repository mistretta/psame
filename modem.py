#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Module to emulate the minimum set of command needed to act like a modem 

    Adrien Mistretta

"""

import sqlite3
import serial

# WARNING: Version 0.1 is just a proof of concept. There is a lot of control
# missing
# Author take no respnsability, use at your own risk

def sendok():
    """
        function to reply OK to an hayes command send by the stove
    """
    okay = '\r\nOK\r\n'
    send(okay)

def send(sendcommand):
    """
        function to send data to the stove. 
    """
    SER.write(sendcommand)
    #print "S:"+sendcommand

def receive(lng):
    """
        function to receive data from the stove. 
    """
    text = SER.read(lng)
    while len(text) <= 0:
        text = SER.read(lng)
    #print "R:"+ "0x%s " % (text.encode('hex')) + " " + text
    return text

def echo_off():
    """
        function to turn echo off. 
    """
    global ECHO
    ECHO = 0
    sendok()

def getatcommand():
    """
        function to read a complete Hayes command from the stove. 
    """
    atcommand = ''
    char = receive(1)
    while char != '\r' and char != '\x1b':
        atcommand = atcommand + char
        char = receive(1)

    # retrieve the characer after \r. It should be \n, but for an unknown reason
    # the stoove send \x00

    char = receive(1)
    if char == '\x00' or char == '\n':
        print "COMMAND:" + atcommand
        return atcommand
    else:
        print "ERROR"
        return ''

def writesms():
    """
        function to receive an sms send by the stove. the sms is stored in the received database
    """
    message = ''
    send("> ")
    char = receive(1)
    while char != '\x1a' and char != '\x1b':
        message = message + char
        char = receive(1)
        # last '\0'
    char = receive(1)
    print "MESSAGE:" + message
    CURSOR.execute("SELECT count(id) from received")
    index = CURSOR.fetchone()

    CURSOR.execute("INSERT INTO received (message) VALUES (?)", (message,))

    CONN.commit()
    send("\r\n+CMGS: "+ str(int(index[0])+1))
    sendok()

def readsms1():
    """
        function to send an sms to the stove from memory 1. memory 1 is the first row from the sms table
    """
    readsms(1)

def readsms(slot):
    """
        function to send an sms to the stove from specified slot. However only slot 1 seems to be used
    """
    try:
        CURSOR.execute("SELECT stat,oa,scts,message FROM sms where id=(?)",
                 str(slot))
    except:
        print "erreur sql"
    row = CURSOR.fetchone()

    if row == None:
        # No SMS
        send("\r\n+CMGR: 0,,0")
    else:
        send('\r\n+CMGR: "'+row[0]+'","'+row[1]+'","'+row[2]+'"\r\n')
        send(row[3])
        # Status update
        CURSOR.execute("UPDATE sms "
                  "SET stat='REC READ' "
                  "WHERE id=(?) and stat='REC UNREAD'",
                  str(slot))
        CONN.commit()
    sendok()


def delsms1():
    """
        function to delete an sms from slot 1.
    """
    delsms(1)

def delsms2():
    """
        function to delete an sms from slot 2.
    """
    delsms(2)

def delsms3():
    """
        function to delete an sms from slot 3.
    """
    delsms(3)

def delsms(slot):
    """
        function to delete an sms from specified slot.
    """
    CURSOR.execute("DELETE FROM sms where id=(?)", str(slot))
    CONN.commit()
    sendok()


DATABASE = "modem_sms.db"
#PORT = "/dev/ttyUSB0"
PORT = "/dev/ttyAMA0"

# Set 
SER = serial.Serial(PORT, 
                    baudrate=115200,
                    timeout=None,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    xonxoff=False,
                    rtscts=False,
                    writeTimeout=None,
                    dsrdtr=False,
                    interCharTimeout=None)


ECHO = 0
 
ATDICT = { 'AT+CMGR=1': readsms1,
           'AT+CMGD=1': delsms1,
           'AT+CMGD=2': delsms2,
           'AT+CMGD=3': delsms3,
           'AT&F': sendok,
           'AT+CMGF=1': sendok,
           'AT+CNMI=0,0,0,0,1': sendok,
           'ATE0': echo_off,
           'AT+CMGS=?': sendok,
           'AT+CMGS="+33612341234"': writesms,
           'AT': sendok
}

CONN = sqlite3.connect(DATABASE)
CURSOR = CONN.cursor()

# I create tables if they doesn't exists
# for columns name, I use the name as it appears in the Siemens documentation.

CURSOR.execute('''CREATE TABLE IF NOT EXISTS sms
               (id INTEGER PRIMARY KEY ASC,
                status INTEGER,
		stat TEXT,
		oa TEXT,
		da TEXT,
		scts TEXT,
		message TEXT)''')

CURSOR.execute('''CREATE TABLE IF NOT EXISTS received
               (id INTEGER PRIMARY KEY ASC,
		dt datetime default current_timestamp,
		message TEXT)''')

CONN.commit()

while True:
    COMMAND = getatcommand()
    if (ECHO):
        send(COMMAND)
        send("\r\n")

    try:
        ATDICT[COMMAND]()
    except:
        print "AT command not found: #"+COMMAND+"#\n"
        sendok()


SER.close()
CONN.close()
