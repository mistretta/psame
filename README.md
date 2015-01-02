psame
=====

pellet stove almost modem emulator

This python script as been writen as a proof of concept, to interact with my RIKA ROCO pellet stove
by using gsm modem option of the stove but without the modem, and emulate the needed Hayes Command 
with psame.

psame is running on a raspberry pi for size convenience and easy integration around the stove.
However, to start playing you can try it on your laptop.

Note: I didn't have myself a siemens GSM Modem to spy at the RS232 exchange, the program has been 
written according to the documentation found on Internet.
Useful documentation are:
 - TC35i AT commands set
 - http://www.developershome.com/sms/smsIntro.asp

hardware requirements

You needed to buy or build cable in order to plug the rapsberry serial interface to the stove motherboard

On my stoove there is a D-sub DA-15 connector 

        pin 2 -> Rx
        pin 3 -> Tx
        pin 5 -> Ground


Enjoy !!!

For more informations, see my Blog

