from tkinter import *

class Chat(Frame):
	def __init__(self,master=None):
		super().__init__(master)

		frame = Frame(self)
		frame.pack()
		leftframe = Frame(frame)
		leftframe.pack(side=LEFT)
		bottomframe = Frame(frame)
		bottomframe.pack(side=BOTTOM)

		self.input_user = StringVar()
		self.input_field = Entry(bottomframe, text=self.input_user, width=80)
		self.input_field.bind("<Return>", self.enter_pressed)

		user_text = Text(leftframe,height=25,width=16)
		user_text.configure(state=DISABLED)
		self.chat_text = Text(frame,height=23,width=100)
		self.chat_text.configure(state=DISABLED)
		button = Button(bottomframe, command=self.button_pressed,text='send', height=1,width=5)

		user_text.pack(side=LEFT)
		self.chat_text.pack(side=TOP)
		self.input_field.pack(side=LEFT)
		button.pack(side=RIGHT)
		self.pack()

	def button_pressed(self):
		input_get = self.input_field.get()
		if input_get != "":
			print (input_get)	
			label = Label(self.chat_text, text=input_get)
			self.input_user.set('')
			label.pack()
		return "break"

	def enter_pressed(self,event):
		self.button_pressed()
		return


if __name__ == '__main__':
	root = Tk()
	root.title('Chat')
	chat = Chat(master=root)
	chat.mainloop()