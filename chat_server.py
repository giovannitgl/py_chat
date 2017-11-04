import socket
import sys
import select
import struct
import queue

class chat_server:
	def __init__(self,port,verbose=False):
		self.waiting_for_accept = [] #contain user ids waiting for ok
		self.user_count = 0
		self.PORT = port
		self.next_id = 1
		self.SERVER_ID = 65535
		self.verbose=verbose
		#socket - id map
		# {'sock':<socket object>, 'id':int}
		self.mapping = []
		self.freed_ids = []

	def allocate_id(self):
		if not self.freed_ids:
			next_id = self.next_id
			self.next_id += 1
			self.waiting_for_accept.append(next_id)
			if self.next_id > self.SERVER_ID:
				next_id = -1
			return next_id
		else:
			return self.freed_ids.pop()
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
			print(self.mapping)
			frame += struct.pack('!H',self.user_count)
			for i in self.mapping:
				id_int = i['id']
				if id_int != self.SERVER_ID:
					frame += struct.pack('!H',id_int)
		return frame

	def receive_message(self,sock):
		#retrieve socket id for verbose printing
		for i in self.mapping:
			if sock == i['sock']:
				sock_id = i['id']
		#receive bytes from socket
		msg_type = sock.recv(2)
		if not msg_type: return
		origin = sock.recv(2)
		destination = sock.recv(2)
		seq_num = sock.recv(2)
		#convertion from bytes to unsigned shorts
		orig_int = struct.unpack('!H',origin)[0]
		seq_int = struct.unpack('!H',seq_num)[0]
		dest_int = struct.unpack('!H',destination)[0]
		msg_int_type = struct.unpack('!H',msg_type)[0]
		#appending packet for verbose printing or forwading msg
		packet = bytes()
		packet += msg_type + origin + destination + seq_num
		#treats "OI" messages
		if msg_int_type == 3:
			print('3')
			new_id = self.allocate_id()
			for i in self.mapping:
				if sock is i['sock']:
					i['id'] = new_id
			self.user_count += 1
			id_alloc_frame = self.create_message('',1,new_id,seq_int)
			self.message_queues[sock].put(id_alloc_frame)
			if sock not in self.outputs:
				self.outputs.append(sock)
			if self.verbose:
				print('Received msg',packet,'from id',sock_id)
			return
		#treats "MSG" messages
		elif msg_int_type == 5:
			print('5')
			n_size = sock.recv(2)
			n_int = struct.unpack('!H',n_size)[0]
			received_msg = sock.recv(n_int)
			# str_msg = received_msg.decode()
			packet += n_size + received_msg
			#forwarding of messages
			if dest_int != 0:
				dest_sock = None
				for i in self.mapping:
					if i['id'] == dest_int:
						dest_sock = i['sock']
				if dest_sock:
					self.message_queues[dest_sock].put(packet)
					if dest_sock not in self.outputs:
						self.outputs.append(dest_sock)
					ok_frame = self.create_message('',1,orig_int,seq_int)
					self.message_queues[sock].put(ok_frame)
					if sock not in self.outputs:
						self.outputs.append(sock)
					if self.verbose:
						print('Received msg',packet,'from id',sock_id)
					return 
				else:
					error_frame = self.create_message('',2,orig_int,seq_int)
					self.message_queues[sock].put(error_frame)
					if sock not in self.outputs:
						self.outputs.append(sock)
					if self.verbose:
						print('Received msg',packet,'from id', sock_id)
					return
			#Broadcast
			else:
				for dest_int in range(1, self.user_count+1):
					if int(orig_int) != dest_int:
						for i in self.mapping:
							print (i['id'])
							if i['id'] == dest_int:
								dest_sock = i['sock']
						# str_frame = self.create_message(str_msg,5,dest_int,seq_int)
						self.message_queues[dest_sock].put(packet)
						if dest_sock not in self.outputs:
							self.outputs.append(dest_sock)
						ok_frame = self.create_message('',1,orig_int,seq_int)
						self.message_queues[sock].put(ok_frame)
						if sock not in self.outputs:
							self.outputs.append(sock)
						if self.verbose:
							print('Received msg',packet,'from id',sock_id)
				return

		#treats "CREQ" messages
		elif msg_int_type == 6:
			print('6')
			list_frame = self.create_message('',7,orig_int,seq_int)
			self.message_queues[sock].put(list_frame)
			if sock not in self.outputs:
				self.outputs.append(sock)
		#treats "FLW" messages
		elif msg_int_type == 4:
			print('4')
			self.freed_ids.append(sock_id)
			for i in self.mapping[:]:
				if i['id'] == sock_id:
					self.mapping.remove(i)
			ok_frame = self.create_message('',1,orig_int,seq_int)
			self.message_queues[sock].put(ok_frame)
			if sock not in self.outputs:
				self.outputs.append(sock)
		if self.verbose:
			print('Received msg',packet,'from id',sock_id)
		return

	def run(self):
		# TODO change input output message queue to object variables
		# TODO change receive msg to be able to send answer msgs
		S_ADDR = ('localhost',self.PORT)
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
			#Handling outputs
			for s in writable:		
				try:
					next_msg = self.message_queues[s].get_nowait()
				except queue.Empty:
					self.outputs.remove(s)
				else:
					if self.verbose:
						for i in self.mapping:
							if s == i['sock']:
								sock_id = i['id']
						print('sending',next_msg,'to id',sock_id)
					s.send(next_msg)
						
			for s in exceptional:
				self.inputs.remove(s)
				if s in outputs:
					self.outputs.remove(s)
				s.close()
				del self.message_queues[s]

if __name__ == '__main__':
	argc = len(sys.argv)
	if argc == 3:
		if sys.argv[2] == '-v':
			server = chat_server(int(sys.argv[1]),verbose=True)
		else:
			print('Wrong arg')
			sys.exit(0)
	elif argc == 2:
		server = chat_server(int(sys.argv[1]))
	else:
		print('Wrong arg format')
		sys.exit(0)
	server.run()
