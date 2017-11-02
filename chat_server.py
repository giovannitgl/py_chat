import socket
import sys
import select
import struct
import queue

class chat_server:
	def __init__(self,port):
		self.user_list = []          #contain user ids
		self.waiting_for_accept = [] #contain user ids waiting for ok
		self.user_count = 0
		self.PORT = port
		self.next_id = 1
		self.SERVER_ID = 65535
		#socket - id map
		self.mapping = []

	def allocate_id(self):
		next_id = self.next_id
		self.next_id += 1
		self.waiting_for_accept.append(next_id)
		if self.next_id > self.SERVER_ID:
			next_id = -1
		return next_id
	def create_message(self,msg,msgtype,destination,seq):
		'''
		Header (in bytes):
		[MSG TYPE] [ORIGIN ID] [DESTINATION ID] [SEQ_NUM]
		0        1 2         3 4			  5 6       8
		MSG TYPES:
		|1 OK	: Accepted msgs |5 MSG*  : Actual chat msgs   |
		|		  sends ok      |		   have msg size in   |
		|2 ERRO	: Refused msgs  |		   header + msg bytes |
		|		  sends erro	|6 CREQ  : Ask for clients    |
		|3 OI	: Joining client|		   server sends clist |
		|		  sends oi      |7 CLIST : number n of clients|
		|4 FLW	: Leaving client|          in header + n      |
		|		  sends flw     |		   clients numbers    |

		*  MSG size are 2 bytes, length guaranteed to be < 400 chars
		** When client gets answered from msg type 3 it receives
		at destination id his allocated id
		TODO: define msg types
		'''
		frame = bytes()
		frame += struct.pack('!H',msgtype)
		frame += struct.pack('!H',self.SERVER_ID)
		frame += struct.pack('!H',destination)
		frame += struct.pack('!H',seq)
		if msgtype == 5:
			msg_len = len(msg)
			frame += struct.pack('!H',msg_len)
			frame += msg.encode()	
		if msgtype == 7:
			frame += struct.pack('!H',self.user_count)
		print(frame,'frame')
		return frame

	def send_message(self,msg):

		return

	def receive_message(self,sock):
		msg_type = sock.recv(2)
		if not msg_type: return
		origin = sock.recv(2)
		orig_int = struct.unpack('!H',origin)[0]
		destination = sock.recv(2)
		dest_int = struct.unpack('!H',destination)[0]
		seq_num = sock.recv(2)
		seq_int = struct.unpack('!H',seq_num)
		seq_int = seq_int[0]
		msg_int_type = struct.unpack('!H',msg_type)[0]
		#treats "OI" messages
		if msg_int_type == 3:
			new_id = self.allocate_id()
			for i in self.mapping:
				if sock is i['sock']:
					i['id'] = new_id
			self.message_queues[sock].put(self.create_message(
					'',1,new_id,seq_int
				))
			if sock not in self.outputs:
				self.outputs.append(sock)
			return
		elif msg_int_type == 5:
			n_size = sock.recv(2)
			n_int = struct.unpack('!H',n_size)[0]
			received_msg = sock.recv(n_int)
			str_msg = received_msg.decode()
			print(str_msg,'str')
			print(received_msg,'bytes')
			#forwarding of messages
			if dest_int != 0:
				for i in self.mapping:
					if i['id'] == dest_int:
						dest_sock = i['sock']
				self.message_queues[dest_sock].put(self.create_message(
					str_msg,5,dest_int,seq_int
					))
				if dest_sock not in self.outputs:
					self.outputs.append(dest_sock)
				self.message_queues[sock].put(self.create_message(
					'',1,orig_int,seq_int))
				if sock not in self.outputs:
					self.outputs.append(sock)
				return 
		return

	def run(self):
		# TODO change input output message queue to object variables
		# TODO change receive msg to be able to send answer msgs
		S_ADDR = ('localhost',PORT)
		MAX_CON = 65534
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
		server.setblocking(0)

		server.bind(S_ADDR)
		server.listen(MAX_CON)	

		#messages lists
		self.inputs = [ server ]
		self.outputs = []
		self.message_queues = {}

		self.mapping.append({'sock':server,'id':self.SERVER_ID})

		while self.inputs:
			readable, writable, exceptional =  select.select(self.inputs,self.outputs,self.inputs)
			#Handling inputs	
			for s in readable:
				if s is server:
					#Accepts new connections
					connection, addr = s.accept()
					connection.setblocking(0)
					self.inputs.append(connection)
					self.mapping.append({'sock':connection,'id':0})
					#creates queue for message
					self.message_queues[connection] = queue.Queue()
				else:
					#Receives data
					aswr = self.receive_message(s)
					if aswr:
						print(aswr)
						# message_queues[s].put(aswr)
						# if s not in outputs:
						# 	self.outputs.append(s)
					# else:
					# 	#interprets lack of message as lost connection
					# 	if s in outputs:
					# 		outputs.remove(s)
					# 	inputs.remove(s)
					# 	s.close()
					# 	del message_queues[s]

			#Handling outputs
			#TODO implement msg answering
			for s in writable:		
				try:
					next_msg = self.message_queues[s].get_nowait()
				except queue.Empty:
					self.outputs.remove(s)
				else:
					s.send(next_msg)
						
			for s in exceptional:
				self.inputs.remove(s)
				if s in outputs:
					self.outputs.remove(s)
				s.close()
				del self.message_queues[s]

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print('Wrong arg format')
		sys.exit(0)
	#connection config
	PORT = int(sys.argv[1])
	server = chat_server(PORT)
	server.run()
