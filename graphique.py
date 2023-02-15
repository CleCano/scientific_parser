#!/usr/bin/python3

from tkinter import *
from tkinter import filedialog

def file_open():
   path = filedialog.askopenfilename(initialdir='~')
   op = open(path, 'r')
   read = op.read()
   maj =  read.upper()
   textarea.insert(END,maj)

   savePath = filedialog.askopenfilename(initialdir='~')
   wr = open(savePath, 'w')
   wr.write(maj)

	
window = Tk()

button = Button(window, text="Open File", command=file_open)
button.pack(pady=50)
textarea=Text(window)
textarea.pack(pady=20)
window.mainloop()


'''1 demander le fichier pdf avec file open
   2 lancer le processus de conversion
   3 afficher processus en cours
   4 afficher que le processus est termine
   5 le fichier est sauvegarde au meme endroit que la source pdf'''
