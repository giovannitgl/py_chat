import socket
import sys
import select
import queue

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
	if len(sys.argv) != 2:
		print('Wrong arg format')
		sys.exit(0)
	PORT = int(sys.argv[1])
	S_ADDR = ('localhost',PORT)
	MAX_CON = 65534
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
	server.setblocking(0)

	server.bind(S_ADDR)
	server.listen(MAX_CON)	

	inputs = [ server ]
	outputs = []
	message_queues = {}

	while inputs:
		readable, writable, exceptional =  select.select(inputs,outputs,inputs)
		#Handling inputs	
		for s in readable:
			if s is server:
				#Accepts new connections
				connection, addr = s.accept()
				connection.setblocking(0)
				inputs.append(connection)

				#creates queue for message
				message_queues[connection] = queue.Queue()
			else:
				#Receives data
				#TODO receive actual framed messages 
				data = s.recv(1024)
				if data:
					print(data)
					message_queues[s].put(data)
					if s not in outputs:
						outputs.append(s)
				else:
					#interprets lack of message as lost connection
					if s in outputs:
						outputs.remove(s)
					inputs.remove(s)
					s.close()
					del message_queues[s]

		#Handling outputs
		#TODO implement msg answering
		for s in writable:		
			try:
				next_msg = message_queues[s].get_nowait()
			except queue.Empty:
				outputs.remove(s)
			else:
				s.send(next_msg)
					
		for s in exceptional:
			inputs.remove(s)
			if s in outputs:
				outputs.remove(s)
			s.close()
			del message_queues[s]

if __name__ == '__main__':
	main()
