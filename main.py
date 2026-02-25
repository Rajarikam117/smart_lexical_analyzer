import tkinter as tk
from smart_lexer.gui.app import LexerApp


def main():
	root = tk.Tk()
	app = LexerApp(root)
	root.mainloop()


if __name__ == '__main__':
	main()
