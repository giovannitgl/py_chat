import socket
import sys
import struct
class chat_client():
	def __init__(self,addr,port):
		self.user_list = []
		self.PORT = port
		self.ADDR = addr
		self.SERVER_ID = 65535
		self.ID = 0
		self.seq_num = 0
		self.wait_confirmation = []

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

	def send_message(self,msg):

		return

	def receive_message(self,sock):
		msg_type = sock.recv(2)
		if not msg_type: return
		origin = sock.recv(2)
		destination = sock.recv(2)
		seq_num = sock.recv(2)
		m = bytes()
		m += msg_type + origin + destination + seq_num
		print(m)
		type_int = struct.unpack('!H',msg_type)[0]
		seq_int = struct.unpack('!H',seq_num)[0]
		for i in self.wait_confirmation:
			#iterates through messages waiting for confirmation
			#if it received a sequence number equal to one waiting
			#it confirms if the message is ok
			if i['seq'] == seq_int:
				#allocates ID after sucessful "OI"
				if i['type'] == 3 and type_int == 1:
					self.ID = struct.unpack('!H',destination)[0]

		return

	def run(self):
		#constants
		OK = 1; ERRO = 2; OI = 3; FLW = 4
		MSG = 5; CREQ = 6; CLIST = 7
		NO_MSG = ''

		S_ADDR = (sys.argv[1],int(sys.argv[2]))

		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		sock.connect((self.ADDR,self.PORT))
		#id message sent
		#puts in confirmation queue for allocating id
		self.wait_confirmation.append({'type':OI,'seq':self.seq_num})
		msg = self.create_message(NO_MSG,OI,self.SERVER_ID)
		print(msg)
		sock.send(msg)
		self.receive_message(sock)
		print(self.ID)
		sock.close()

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print('Wrong arg format')
		sys.exit(0)

	client = chat_client(sys.argv[1],int(sys.argv[2]))
	client.run()
