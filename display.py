import tkinter as tk

class Chat(tk.Frame):
	def __init__(self,master=None):
		super().__init__(master)
		frame = tk.Frame(self)
		frame.pack()
		leftframe = tk.Frame(frame)
		leftframe.pack(side=tk.LEFT)
		bottomframe = tk.Frame(frame)
		bottomframe.pack(side=tk.BOTTOM)
		user_text = tk.Text(leftframe,height=25,width=16)
		chat_text = tk.Text(frame,height=20,width=100)
		entry = tk.Text(bottomframe, height=3, width=90)
		button = tk.Button(bottomframe,text='send',height=3,width=5)
		user_text.pack(side=tk.LEFT)
		chat_text.pack(side=tk.TOP)
		entry.pack(side=tk.LEFT)
		button.pack(side=tk.RIGHT)
		self.pack()

if __name__ == '__main__':
	root = tk.Tk()
	root.title('Chat')
	chat = Chat(master=root)
	chat.mainloop()

