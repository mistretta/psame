#!/bin/bash

/usr/bin/sqlite3 /home/pi/psame/modem_sms.db "INSERT INTO sms (id,stat,oa,scts,message) VALUES (1, 'REC UNREAD', '+33612341234', '`/bin/date +%y/%m/%d,%T+04`', '1234 ?' );" >/var/tmp/modem.out 2>&1

