import serial
import ARQ
import Enq
import poller
import sys,time,os
from tun import Tun
	
	
class Protocolo:
	
	def __init__(self, porta, tun):
		self.serial = porta
		self.enq = Enq.Enquadramento(self.serial)
		self.arq = ARQ.ARQ(self.enq)
		self.tun = tun
		self.tun.start()
		self.cbTun = CallbackTun(self.tun, self) 
		self.sched = poller.Poller()
		self.sched.adiciona(self.cbTun)
		self.cbSerial = CallbackStdin(self)
		self.sched.adiciona(self.cbSerial)
		self.sched.despache()
		
		
		
	def envia(self, data):  
		self.arq.envia(data)
		
	def recebEnq(self):
		self.enq.recebe()
			
	def recebe(self,quadro):
		data = self.arq.recebe(quadro)
		#se não recebeu um quadro completo, retorna
		if (data == b''):
			return
		self.arq.IDproto = data[1]
		print(self.arq.IDproto)
		print('Quadro send frame:', data[2:]) # descarta Idcontroll
		self.tun.send_frame(data[2:],Tun.PROTO_IPV4)
		
	
class CallbackTun(poller.Callback):
	
	def __init__(self, tun, proto):
		poller.Callback.__init__(self, tun.fd, 1000)
		self._tun = tun
		self.proto = proto
		
	def handle(self):
		idProto, quadro = self._tun.get_frame() # e uma tupla
		self.proto.envia(quadro)
		
	def handle_timeout(self):
		print('Timeout !')
	
class CallbackStdin(poller.Callback):
	
	def __init__(self, proto):
		poller.Callback.__init__(self, proto.serial, 1000)
		self.serial = proto.serial
		self.proto = proto
		
	def handle(self):
		quadro = self.proto.enq.recebe() # recebe do enquandramento
		if (quadro!= b''): # Apos finalizar recebimento
			 self.proto.recebe(quadro) # envio ele para proto que vai criar uma tun
			
	def handle_timeout(self):
		print('Timeout !')
			
			
class CallbackTimer(poller.Callback):
	
	t0 = time.time()
	
	def __init__(self, tout):
		poller.Callback.__init__(self, None, tout)
			
	def handle_timeout(self):
		
		print('Timer: t=', time.time()-CallbackTimer.t0)
