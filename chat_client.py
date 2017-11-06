import socket
import sys
import struct
import select
import queue
import os

class Client():
	def __init__(self,addr,port,verbose=False,gui=False,read_file=None,write_file=None):
		self.user_list = []
		self.PORT = port
		self.ADDR = addr
		self.SERVER_ID = 65535
		self.ID = 0
		self.verbose=verbose
		self.seq_num = 0
		self.read_file=read_file
		self.write_file=write_file
		self.gui=gui
		#list waiting for msg confirmations
		#{'type':int with message type,'seq':sequence number of msg}
		self.wait_confirmation = []
		self.sock = self.create_socket()
		self.get_id()

	def create_message(self,msg,msgtype,destination,seq=None):
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
		frame += struct.pack('!H',self.ID)
		frame += struct.pack('!H',destination)
		if not seq:
			frame += struct.pack('!H',self.seq_num)
			self.seq_num += 1
		else:
			frame += struct.pack('!H',seq)
		if msgtype == 5:
			msg_len = len(msg)
			frame += struct.pack('!H',msg_len)
			frame += msg.encode()	
		return frame

	def send_message(self,msg,client):
		self.wait_confirmation.append({'type':5,'seq':self.seq_num})
		byte_msg = self.create_message(msg,5,client)
		if self.verbose:
			print('Sending',byte_msg,'to socket')
		self.sock.sendall(byte_msg)
		return

	def request_list(self):
		self.wait_confirmation.append(
				{'type':6,'seq':self.seq_num}
			)
		msg = self.create_message('',6,self.SERVER_ID)
		if self.verbose:
			print('Sending',msg,'to socket')
		self.sock.send(msg)

	def receive_message(self,files=None):
		#receive bytes from so cket
		msg_type = self.sock.recv(2)
		if not msg_type: return
		origin = self.sock.recv(2)
		destination = self.sock.recv(2)
		seq_num = self.sock.recv(2)
		#appending packet for verbose printing
		packet = bytes()
		packet += msg_type + origin + destination + seq_num
		#convertion from bytes to unsigned shorts
		type_int = struct.unpack('!H',msg_type)[0]
		orig_int = struct.unpack('!H',origin)[0]
		dest_int = struct.unpack('!H',destination)[0]
		seq_int = struct.unpack('!H',seq_num)[0]
		if type_int == 5:
			n_size = self.sock.recv(2)
			n_int = struct.unpack('!H',n_size)[0]
			received_msg = self.sock.recv(n_int)
			packet += n_size + received_msg
			msg_str = 'User ' + str(orig_int)
			if dest_int == 0:
				msg_str += ' [broadcast] '
			msg_str += '-> ' + received_msg.decode()
			ok_frame = self.create_message('',1,self.SERVER_ID)
			if self.verbose:
				print('Received',packet,'from socket')
				print('Sending', ok_frame, 'to socket')
			self.sock.send(ok_frame)
			return msg_str
		if self.verbose and msg_type != 7:
			print('Received',packet,'from socket')
		for i in self.wait_confirmation[:]:
			#iterates through messages waiting for confirmation
			#if it received a sequence number equal to one waiting
			#it confirms if the message is ok
			if i['seq'] == seq_int:
				#allocates ID after sucessful "OI"
				if type_int == 1:
					if i['type'] == 5:
						self.wait_confirmation.remove(i)
						ok_frame = self.create_message('',1,self.SERVER_ID,seq_int)
						self.sock.send(ok_frame)
					elif i['type'] == 3:
						self.ID = struct.unpack('!H',destination)[0]
						self.wait_confirmation.remove(i)
					elif i['type'] == 4:
						self.wait_confirmation.remove(i)
						for i in files:
							i.close()
						self.sock.close()
						sys.exit()
				elif type_int == 2:
					if i['type'] == 5:
						self.wait_confirmation.remove(i)
						return "ERROR: could not send message\n"
				#retrives id list
				elif (i['type'] == 6 and type_int == 7):
					#retrieves size of id list
					n_size = self.sock.recv(2)
					print('nsize')
					print(n_size)
					n_int = struct.unpack('!H',n_size)[0]
					#retrieves list
					users = self.sock.recv(n_int*2)
					print('users')
					print(users)
					print(len(users))
					packet += n_size + users
					users_tuple = struct.unpack(
						'!' + str(n_int) + 'H', users
						)
					msg_users = str()
					msg_users += "Online users: "
					#creates string with users ids
					for j in users_tuple:
						msg_users += str(j)
						msg_users += ' '
					msg_users += '\n'
					if self.verbose:
						print('Received',packet,'from socket')
					self.wait_confirmation.remove(i)
					return msg_users
		return
	def close_connection(self):
		self.wait_confirmation.append({'type':4,'seq':self.seq_num})
		msg = self.create_message('',4,self.SERVER_ID)
		if self.verbose:
			print('Sending',msg,'to socket')
		self.sock.send(msg)

	def create_socket(self):
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		sock.connect((self.ADDR,self.PORT))
		return sock

	def get_id(self):
		OI = 3; NO_MSG = ''
		self.wait_confirmation.append({'type':OI,'seq':self.seq_num})
		msg = self.create_message(NO_MSG,OI,self.SERVER_ID)
		self.sock.send(msg)
		self.receive_message()
		print("Your ID: " + str(self.ID))
		
	def listen(self,msg_list):
		while(True):
			msg = self.receive_message()
			if msg:
				msg_list.put(msg)
			
	def run(self):
		input_stream = sys.stdin.fileno()
		output_stream = sys.stdout.fileno()
		message_queue = queue.Queue()
		if self.gui: 
			input_stream = self.read_file
			output_stream = self.write_file
		r = os.fdopen(input_stream,'r')
		w = os.fdopen(output_stream,'w')
		# print(r.fileno(),w.fileno())
		inputs = [self.sock,input_stream]
		# print(w)
		outputs = []
		while inputs:
			try:
				readable,writable,exceptional = select.select(inputs,outputs,[])
				for s in readable:
					if s == self.sock:
						msg = self.receive_message((r,w))
						if msg : 
							message_queue.put(msg)
							if output_stream not in outputs:
								outputs.append(output_stream)
					elif s == input_stream:
						msg = r.readline()
						if msg:
							msg = msg
							# print('msg',msg,len(msg),msg[0]=='*')
							if self.verbose:
								print('Received \"%s\" from input' % msg)
							#treats msg commands
							if msg[0] == '/':
								#gets the command (separated by whitespace)
								#checks if it's a message
								#and checks its destiny
								if msg.find('/msg') == 0:
									space_index = msg.index(' ')
									command = msg[:space_index]
									if command[4:].isdigit:
										dest_id = int(command[4:])
										#checks message body
										body = msg[(space_index+1):]
										if body:
											self.send_message(body,dest_id)
										#no message body
										else:
											#error
											message_queue.put('ERROR: no message body')
											if output_stream not in outputs:
												outputs.append(output_stream)
									#char in id
									else:
										#error	
										message_queue.put('ERROR: not a valid user id')
										if output_stream not in outputs:
											outputs.append(output_stream)
								#request user list
								elif msg.find('/list') == 0:
									self.request_list()
								#quit
								elif msg.find('/quit') == 0:
									# r.close()
									# w.close()
									self.close_connection()
								else:
									#error
									message_queue.put('ERROR: not a valid command')
									if output_stream not in outputs:
										outputs.append(output_stream)
							else:
								self.send_message(msg,0)
							# if msg[0].isdigit():
							# 	dest = int(msg[0])
							# 	self.send_message(msg[1:],dest)
							# elif msg[0] == '*' and len(msg) == 2:
							# 	self.request_list()
							# elif msg[0] == '-' and len(msg) == 2:
							# 	r.close()
							# 	w.close()
							# 	self.close_connection()
				for s in writable:
					try:
						next_msg = message_queue.get_nowait()
					except queue.Empty:
						outputs.remove(s)
					else:
						if self.verbose:
							print('Sending \"%s\" to output' % next_msg)
						w.write(next_msg)
						w.flush()
			except KeyboardInterrupt:
				self.close_connection()
				r.close()
				w.close()
				self.sock.close()
				sys.exit(1)

if __name__ == '__main__':
	argc = len(sys.argv)
	if argc == 4:
		if sys.argv[3] == '-v':
			client = Client(sys.argv[1],int(sys.argv[2]),verbose=True)
		else:
			print('Wrong arg')
			sys.exit(0)
	elif argc == 3:
		client = Client(sys.argv[1],int(sys.argv[2]))
	else:
		print('Wrong arg format')
		sys.exit(0)
		
	# if len(sys.argv) != 3 or len(sys.argv) != 4:
	client.run()
