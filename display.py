from tkinter import *

class Chat(Frame):
	def __init__(self,master=None):
		super().__init__(master)

		self.frame = Frame(self, height=500)
		self.frame.pack()
		leftframe = Frame(self.frame)
		leftframe.pack(side=LEFT)
		bottomframe = Frame(self.frame)
		bottomframe.pack(side=BOTTOM)

		self.input_user = StringVar()
		self.input_field = Entry(bottomframe, text=self.input_user, width=80)
		self.input_field.bind("<Return>", self.enter_pressed)

		user_text = Text(leftframe,height=200,width=16)
		user_text.configure(state=DISABLED)
		button = Button(bottomframe, command=self.button_pressed,text='send', height=1,width=5)


		seachContact = Button(leftframe, text='Send\nMessage\nto...', height=3,width=5)
		broadcast = Button(leftframe, text='Broadcast', height=1,width=5)

		seachContact.pack()
		broadcast.pack()
		self.input_field.pack(side=LEFT)
		button.pack(side=RIGHT)
		self.pack()

	def button_pressed(self):
		aux = "Me -> "
		input_get = self.input_field.get()
		if input_get != "":
			input_get = aux + input_get
			print (input_get)	
			label = Label(self.frame, text=input_get, fg="green", bg="white")
			self.input_user.set('')
			label.pack()
		return "break"

	def enter_pressed(self,event):
		self.button_pressed()
		return


if __name__ == '__main__':
	root = Tk()
	root.title('Chat')
	root.maxsize(width=850, height=600)
	chat = Chat(master=root)
	chat.mainloop()