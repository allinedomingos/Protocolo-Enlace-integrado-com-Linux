import enum
from enum import Enum
import Enq
import select
import poller
from tun import Tun
import os
import time

class Estado(Enum):
	Estado0 = 1 # Ocioso
	Estado1 = 2 # Espera Confirmacao
class TipoEvento(Enum):
	Payload = 1 # notificado quando chama o metodo envia do protocolo
	Quadro = 2 # notificado pelo enquadramento pelo metodo recebe
	Timeout = 3 # notificado de alguma forma

class ARQ:
		
	def __init__(self, enq):
		self.Tipo = TipoEvento.Timeout
		self.byte = b''
		self.buffer = b''
		self.data = b'\x08'
		#FORMATO DO QUADRO
		self.IDcontroll = b'\x00' # 0(Dado) e 1(ACK) 
		self.IDsessao = b'\x06'
		self.mensagem = b''
		self.IDproto = b'\x00'
		###############
		self.estado = Estado.Estado0
		self.evento = None
		self.enq = enq
		self.tentativa = 0
		self.tentativa_receb = 0
		
			
	# Maquina Estado do ARQ	
	def handle(self,evento):
		#print('Estado', self.estado)
		#Estado Ocioso#
		if (self.estado == Estado.Estado0): 
			self.estado = self.estado0(evento)
			#return self.estado
		#Espera Comunicacao#
		elif (self.estado == Estado.Estado1): 
			self.estado = self.estado1(evento)
			#return self.estado
					

	def estado0(self, evento):
		if (self.evento == TipoEvento.Payload):
				#criar um quadro
				self.mensagem = b''
				#self.mensagem = self.IDcontroll + self.IDsessao + self.IDproto + self.data
				self.mensagem = self.IDcontroll + self.IDsessao + self.data
				self.buffer = self.mensagem
				self.enq.envia(self.mensagem)
				return Estado.Estado1
				
		elif(self.evento == TipoEvento.Quadro):
			if(self.buffer[0] == 8): # Verifica DATA1
				#self.enq.envia(b'\x88' + self.IDsessao + self.IDproto) #Ack1
				self.enq.envia(b'\x88' + self.IDsessao) #Ack1
				print("passei aqui8")
				return Estado.Estado0
			elif(self.buffer[0] == 0): # Verifica DATA0
				#print('IDsessao:{}', self.IDsessao)
				#print('IDproto: {}', self.IDproto)
				#self.enq.envia(b'\x80' + self.IDsessao + self.IDproto) #Ack0
				self.enq.envia(b'\x80' + self.IDsessao) #Ack0
				print("passei aqui9")
				return Estado.Estado0
		return self.estado
				
	def estado1(self, evento):
		#print("passei aqui10" , self.data)
		if(self.evento == TipoEvento.Quadro):
			#print("passei aqui11")
		# Verificar ACK ou DATA
			#if(self.data[0].to_bytes(1, 'big') == b'\x88'):
			if(self.buffer[0:1] == b'\x88'):
				print("passei aqui3")
				if(self.IDcontroll == b'\x08'):
					self.IDcontroll = b'\x00'
					print("passei aqui4")
					return Estado.Estado0
				else:
					self.enq.envia(self.mensagem)
					#print("passei aqui5")
					return Estado.Estado1
			#elif(self.data[0].to_bytes(1, 'big') == b'\x80'): 
			elif(self.buffer[0:1] == b'\x80'): 
				print("passei aqui")
				if(self.IDcontroll == b'\x00'):
					print("passei aqui2")
					self.IDcontroll = b'\x08'
					return Estado.Estado0
				else:
					#print("passei aqui")
					self.enq.envia(self.mensagem)
					return Estado.Estado1
			#evento ACK
			elif(self.buffer[0] == 8): 
				#self.enq.envia(b'\x88'+ self.IDsessao + self.IDproto)
				self.enq.envia(b'\x88'+ self.IDsessao)
				print("passei aqui6")
				return Estado.Estado0
			elif(self.buffer[0] == 0): 
				#self.enq.envia(b'\x80'+ self.IDsessao + self.IDproto)
				self.enq.envia(b'\x80'+ self.IDsessao)
				print("passei aqui7")
				return Estado.Estado0
		
		#tratar evento de payload
		elif(self.evento == TipoEvento.Payload):
			#self.buffer = self.enq.recebe()
				
			if(self.buffer[0] == 8): 
				#self.enq.envia(b'\x88' + self.IDsessao + self.IDproto) #Ack1
				self.enq.envia(b'\x88' + self.IDsessao) #Ack1
				print("passei aqui38")
				return Estado.Estado0
				
			elif(self.buffer[0] == 0):
				#self.enq.envia(b'\x80' + self.IDsessao + self.IDproto) #Ack0
				self.enq.envia(b'\x80' + self.IDsessao) #Ack0
				print("passei aqui39")
				return Estado.Estado0
			else:
				self.mensagem = b''
				#self.mensagem = self.IDcontroll + self.IDsessao + self.IDproto + self.data
				self.mensagem = self.IDcontroll + self.IDsessao + self.data
				self.buffer = self.mensagem
				self.enq.envia(self.mensagem)
				return Estado.Estado1
		#tratar evento timeout
		elif(self.evento == TipoEvento.Timeout):
			print("Retransmitindo Quadro")
			self.enq.envia(self.mensagem)
			self.tentativa += 1
			if(self.tentativa == 4):
				print('\n---------------------------\n')
				print("Tentativas de retransmissao finalizadas...")
				print('\n---------------------------\n')
				exit()
			return Estado.Estado1
		return self.estado
		
			
	def envia(self, data):
		
		self.evento = TipoEvento.Payload
		self.data = data
		self.handle(self.evento)
		
				
	def recebe(self,quadro):
		#while(True):
			
		self.buffer = quadro #self.enq.recebe()
		
		if(self.buffer == b''):	
			return b''
		else:	
			self.evento = TipoEvento.Quadro
		print('passei aqui40')
		self.handle(self.estado)
		if(self.estado == Estado.Estado0):
			print('passei aqui41')
			return self.buffer
		return b''
	
	
				
		
