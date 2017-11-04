import socket
import sys
import struct
import select

class chat_client():
	def __init__(self,addr,port,verbose=False):
		self.user_list = []
		self.PORT = port
		self.ADDR = addr
		self.SERVER_ID = 65535
		self.ID = 0
		self.verbose=verbose
		self.seq_num = 0
		self.wait_confirmation = []
		self.sock = self.create_socket()
		self.get_id()
		self.run()

	def create_message(self,msg,msgtype,destination):
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
		frame += struct.pack('!H',self.ID)
		frame += struct.pack('!H',destination)
		frame += struct.pack('!H',self.seq_num)
		self.seq_num += 1
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

	def receive_message(self):
		#receive bytes from socket
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
		seq_int = struct.unpack('!H',seq_num)[0]
		if type_int == 5:
			n_size = self.sock.recv(2)
			n_int = struct.unpack('!H',n_size)[0]
			received_msg = self.sock.recv(n_int)
			packet += n_size + received_msg
			msg_str = 'User' + str(orig_int) + ':' + received_msg.decode()
			if self.verbose:
				print('Received',packet,'from socket')
			return msg_str
		for i in self.wait_confirmation:
			#iterates through messages waiting for confirmation
			#if it received a sequence number equal to one waiting
			#it confirms if the message is ok
			if i['seq'] == seq_int:
				#allocates ID after sucessful "OI"
				if type_int == 1:
					if i['type'] == 5:
						self.wait_confirmation.pop()
					if i['type'] == 3:
						self.ID = struct.unpack('!H',destination)[0]
						self.wait_confirmation.remove(i)
				#retrives id list
				if i['type'] == 6 and type_int == 7:
					#retrieves size of id list
					n_size = self.sock.recv(2)
					n_int = struct.unpack('!H',n_size)[0]
					#retrieves list
					users = self.sock.recv(n_int*2)
					packet += n_size + users
					users_tuple = struct.unpack(
						'!' + str(n_int) + 'H', users
						)
					msg_users = str()
					#creates string with users ids
					for i in users_tuple:
						msg_users += str(i)
						msg_users += ' '
					if self.verbose:
						print('Received',packet,'from socket')
					self.wait_confirmation.pop()
					return msg_users
		return
	def close_conn(self):
		msg = self.create_message('',4,self.SERVER_ID)
		self.sock.send(msg)
		self.sock.close()

	def create_socket(self):

		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		sock.connect((self.ADDR,self.PORT))
		return sock

	def get_id(self):
		OK = 1;
		self.wait_confirmation.append({'type':OI,'seq':self.seq_num})
		msg = self.create_message(NO_MSG,OI,self.SERVER_ID)
		self.sock.send(msg)
		self.receive_message()
		print("Your ID: " + str(self.ID))
		
	def run(self):
		inputs = [self.sock,sys.stdin]
		while(True):
			inputready,outputready,exceptready =  select.select(inputs,[],[])
			for s in inputready:
				if s == self.sock:
					msg = self.receive_message()
					if msg : print(msg)
				elif s == sys.stdin:
					msg = sys.stdin.readline()
					if msg:
						# print('msg',msg,len(msg),msg[0]=='*')
						if self.verbose:
							print('Received \"%s\" from stdin' % msg)
						if msg[0].isdigit():
							dest = int(msg[0])
							self.send_message(msg[1:],dest)
						elif msg[0] == '*' and len(msg) == 2:
							self.request_list()

if __name__ == '__main__':
	argc = len(sys.argv)
	if argc == 4:
		if sys.argv[3] == '-v':
			client = chat_client(sys.argv[1],int(sys.argv[2]),verbose=True)
		else:
			print('Wrong arg')
			sys.exit(0)
	elif argc == 3:
		client = chat_client(sys.argv[1],int(sys.argv[2]))
	else:
		print('Wrong arg format')
		sys.exit(0)
		
	# if len(sys.argv) != 3 or len(sys.argv) != 4:

	client = chat_client(sys.argv[1],int(sys.argv[2]))