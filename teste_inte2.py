import serial
import Proto
import poller
import sys,time
from tun import Tun


print('Informar a porta serial')

porta = input()

client_ser = serial.Serial(porta, 9600)

tun = Tun("tun0","10.0.0.2","10.0.0.1",mask="255.255.255.252",mtu=1500,qlen=4)

Proto.Protocolo(client_ser, tun)



