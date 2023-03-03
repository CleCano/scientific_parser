#!/usr/bin/python3

from tkinter import *
from tkinter import filedialog

def file_open():
   path = filedialog.askopenfilename(initialdir='~')
   print(path)
   op = open(path, 'r')
   read = op.read()
   maj =  read.upper()
   textarea.insert(END,maj)

   savePath = filedialog.askopenfilename(initialdir='~')
   wr = open(savePath, 'w')
   wr.write(maj)


def folder_open():
   path = filedialog.askdirectory(initialdir='~')
   print(path)

def file_save():
   print('tkt')
window = Tk()

buttonFileIn = Button(window, text="Open File", command=file_open)
buttonFileIn.pack(pady=5,anchor='w',padx=5)
textOption = BooleanVar()
textOption.set(True)
xmlOption = BooleanVar()
option1 = Checkbutton(window, text='Text version', variable=textOption)
option2 = Checkbutton(window, text='XML version', variable=xmlOption)

# Positionner les boutons radio à l'aide de la méthode pack()
option1.pack(side='left')
option2.pack(side='left')

textarea=Text(window ,state='disabled')
textarea.pack(pady=20)
buttonFolderOut = Button(window, text="Choose path", command=folder_open)
buttonFolderOut.pack(side='left')
outName = Text(window,width=20,height=1)
outName.pack(side='left')
saveButton = Button(window, text="Save", command=(file_save))
saveButton.pack(side='left',anchor='n')
window.mainloop()


'''1 demander le fichier pdf avec file open
   2 lancer le processus de conversion
   3 afficher processus en cours
   4 afficher que le processus est termine
   5 le fichier est sauvegarde au meme endroit que la source pdf'''
