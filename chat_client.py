import socket
import sys

def frame_message(msg,msgtype):
	'''
	Header (in bytes):
	[MSG TYPE] [ORIGIN ID] [DESTINY ID] [SEQ_NUM]
	0        1 2         3 4          5 6       8
	MSG TYPES:
	|1 OK	: Msgs are answered with ok	|5 MSG*  : Text being sent to another |
	|		  when accepted				|			client, appends to header |
	|2 ERRO	: Same as ok, but			|			2 bytes of its size       |
	|		  message wasnt accepted	|6 CREQ  : Ask for list of clients    |
	|3 OI	: Client sends as identifier|		   Server answer with Clist   |
	|		  when it firsts connect	|7 CLIST : Appends 2 bytes to header, |
	|4 FLW	: Client sends when			|          containing the number N of |
	|		  disconnecting				|		   clients, and 2*N more bytes|| 

	* MSG has various types
	TODO: define msg types
	'''
	return

def send_message(msg):

	return

def receive_message():

	return

def main():
	if len(sys.argv) != 3:
		print('Wrong arg format')
		sys.exit(0)
	
	messages = ['This is the message. ',
				'It will be sent ',
				'in parts.']
	S_ADDR = (sys.argv[1],int(sys.argv[2]))

	# Create a TCP/IP socket
	socks = [socket.socket(socket.AF_INET, socket.SOCK_STREAM),
			 socket.socket(socket.AF_INET, socket.SOCK_STREAM)]

	# Connect the socket to the port where the server is listening
	for s in socks:
		    s.connect(S_ADDR)
	
	for m in messages:
		for s in socks:
			print('sent',s.getsockname(),m,file=sys.stderr)
			s.send(m.encode())
		for s in socks:
			data = s.recv(1024)
			print('received',s.getsockname(),data,file=sys.stderr)
			if not data:
				s.close()




if __name__ == '__main__':
	main()
