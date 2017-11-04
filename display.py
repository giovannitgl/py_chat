from tkinter import *

class Chat(Frame):
	def __init__(self,master=None):
		super().__init__(master)

		self.frame = Frame(self)
		self.frame.pack()

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

		# Botões para o usuário
		leftframe = Frame(self.frame)
		leftframe.pack(side=LEFT, fill=Y)
		seachContact = Button(leftframe, text='Send\nMessage\nto...', height=3,width=5)
		broadcast = Button(leftframe, text='Broadcast', height=1,width=5)
		seachContact.pack()
		broadcast.pack()

		self.pack()

	def button_pressed(self):
		input_get = self.input_field.get()
		self.updateChat("Me -> ", input_get)

	def enter_pressed(self,event):
		self.button_pressed()

	def receiveMessage(self):
		self.updateChat("Him -> ", "oi")

	def updateChat(self, user, message):
		if message != "":
			message = user + message + "\n"

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
	chat = Chat(master=root)
	chat.mainloop()