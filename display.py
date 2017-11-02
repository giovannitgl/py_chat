''' ENTER E BOTAO FUNCIONAM
from tkinter import *

def button_pressed():
    input_get = input_field.get()
    label = Label(frame, text=input_get)
    input_user.set('')
    label.pack()
    return "break"

def enter_pressed(event):
    button_pressed()



window = Tk()
window.title('Chat')
window.geometry("600x500")

input_user = StringVar()
input_field = Entry(window, text=input_user)
input_field.pack(side=BOTTOM)

frame = Frame(window, width=300, height=300)
frame.pack_propagate(False) #
input_field.bind("<Return>", enter_pressed)
frame.pack()

b = Button(window, text="Enviar", command=button_pressed)
b.pack()

window.mainloop()

'''

from tkinter import *

def button_pressed():
    
    return "break"

class Chat(Frame):
	def __init__(self,master=None):
		super().__init__(master)

		frame = Frame(self)
		frame.pack()
		leftframe = Frame(frame)
		leftframe.pack(side=LEFT)
		bottomframe = Frame(frame)
		bottomframe.pack(side=BOTTOM)

		user_text = Text(leftframe,height=25,width=16)
		user_text.configure(state=DISABLED)
		chat_text = Text(frame,height=20,width=100)
		chat_text.configure(state=DISABLED)
		entry = Text(bottomframe, height=3, width=90)
		button = Button(bottomframe, command=button_pressed,text='send', height=3,width=5)

		user_text.pack(side=LEFT)
		chat_text.pack(side=TOP)
		entry.pack(side=LEFT)
		button.pack(side=RIGHT)
		self.pack()

if __name__ == '__main__':
	root = Tk()
	root.title('Chat')
	chat = Chat(master=root)
	chat.mainloop()