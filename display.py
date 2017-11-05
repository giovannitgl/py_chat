from tkinter import *
import io
import chat_client
import queue
import threading
msg_queue = queue.Queue()

class Chat(Frame):
	def __init__(self,addr,master=None,verbose=False):
		super().__init__(master)
		ip = addr[0]
		port = addr[1]
		self.frame = Frame(self)
		self.frame.pack()
		self.client = chat_client.Client(ip,port,verbose)
		global msg_queue
		t = threading.Thread(target=self.client.listen,args=(msg_queue,))
		t.start()
		# Botões para o usuário
		leftframe = Frame(self.frame)
		leftframe.pack(side=LEFT, fill=Y)
		seachContact = Button(leftframe, text='Send\nMessage\nto...', height=3,width=5)
		broadcast = Button(leftframe, text='Broadcast', height=1,width=5)
		seachContact.pack()
		broadcast.pack()

		# Parte aonde armazana a conversa + scroll
		self.topframe = Frame(self.frame)
		self.topframe.pack(expand=True, fill=Y)
		self.textarea = Text(self.topframe, state=DISABLED)
		self.scroll = Scrollbar(self.topframe, takefocus=0, command=self.textarea.yview)
		self.scroll.pack(side=RIGHT, fill=Y)
		self.textarea.pack(side=RIGHT, expand=YES, fill=BOTH)
		self.textarea["yscrollcommand"]=self.scroll.set

		# Parte onde escreve a mensagem (input) + botão de enviar
		bottomframe = Frame(self.frame)
		bottomframe.pack(side=BOTTOM)
		self.input_user = StringVar()
		self.input_field = Entry(bottomframe, text=self.input_user, width=65)
		self.input_field.bind("<Return>", self.enter_pressed)
		button = Button(bottomframe, command=self.button_pressed,text='Send', height=1,width=5)
		button.pack(side=RIGHT)
		self.input_field.pack(side=LEFT)

		self.pack()
	def check_new_message(self):
		global msg_queue
		while not msg_queue.empty():
			msg = msg_queue.get_nowait()
			self.updateChat(msg)
		chat.after(300,chat.check_new_message)


	def button_pressed(self):
		input_get = self.input_field.get()
		self.updateChat('Me -> ' + input_get[1:])
		dest = int(input_get[0])
		self.client.send_message(input_get[1:],dest)

	def enter_pressed(self,event):
		self.button_pressed()

	def receiveMessage(self):
		self.updateChat("Him -> ", "oi")

	def updateChat(self, message):
		if message != "":
			message += "\n"
			relative_position_of_scrollbar = self.scroll.get()[1]
			self.textarea.config(state=NORMAL)
			self.textarea.insert(END, message)
			self.textarea.config(state=DISABLED)
			self.input_user.set('')

			if relative_position_of_scrollbar == 1:
				self.textarea.yview_moveto(1)
		return "break"


if __name__ == '__main__':
	root = Tk()
	root.title('Chat')
	argc = len(sys.argv)
	addr = (sys.argv[1],int(sys.argv[2]))
	if argc == 4:
		if sys.argv[3] == '-v':
			chat = Chat(addr,root,True)
		else:
			print('Wrong arg')
			sys.exit(0)
	elif argc == 3:
		client = Chat(addr,root)
	else:
		print('Wrong arg format')
		sys.exit(0)
	chat.after(300,chat.check_new_message)
	chat.mainloop()
