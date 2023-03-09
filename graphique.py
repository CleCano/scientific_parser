#!/usr/bin/python3
import os
import argparse
from ScientificParser import *
from tkinter import *
from tkinter import filedialog
import time

fileIn = ""
def file_open():
   global fileIn
   path = filedialog.askopenfilename(initialdir='~')
   fileIn = path
   exeCommand(fileIn,boolTextXml)
   
def exeCommand(fileIn,textOrXml):
   param = ""
   args = argparse.Namespace()
   args.t = textOrXml.get()
   args.x = not textOrXml.get()
   args.filename = fileIn
   args.out = None
   print(args)

   text_preview.config(state=NORMAL)
   text_preview.delete(1.0,END)
   text_preview.insert(END,launchExtraction(args))
   text_preview.config(state=DISABLED)
   
   
 
   




def file_save():

   if (boolTextXml.get()):files = [("Text File", ".txt")]
   else : files = files = [("XML File", ".xml")]
   file = filedialog.asksaveasfilename(filetypes=files,defaultextension=files)

def on_select():
   if(fileIn!= ""):
      exeCommand(fileIn,boolTextXml)
   

# Créer une fenêtre Tkinter
window = Tk()

# En haut : un bouton "Open file", deux checkbutton "Text Option" et "XML Option"
frame_top = Frame(window)
frame_top.pack(side='top', padx=10, pady=10)

button_open = Button(frame_top, text='Open file', command=file_open)
button_open.pack(side='left', padx=10)

boolTextXml = BooleanVar()
boolTextXml.set(True)
radButton_text_option = Radiobutton(frame_top, text='Text Option', variable=boolTextXml,value=True,command=on_select)
radButton_xml_option = Radiobutton(frame_top, text='XML Option', variable=boolTextXml,value=False,command=on_select)

radButton_text_option.pack(side='left', padx=10)



radButton_xml_option.pack(side='left', padx=10)

# Au milieu : une zone de texte "preview" désactivée
frame_middle = Frame(window)
frame_middle.pack(padx=10, pady=10)


text_preview = Text(frame_middle,wrap='none')
scrollbar = Scrollbar(frame_middle, orient='horizontal', command=text_preview.xview)

# Lier la barre de défilement à la zone de texte
text_preview.configure(xscrollcommand=scrollbar.set)
text_preview.pack(side='top', fill='both', expand=True)
scrollbar.pack(side='bottom', fill='x')

# En bas : à gauche un bouton "Choose path", au milieu une zone de texte "outName", à droite un bouton "Save"
frame_bottom = Frame(window)
frame_bottom.pack(side='bottom', padx=10, pady=10)



button_save = Button(frame_bottom, text='Save', command=file_save)
button_save.pack(padx=10)

my_label = Label(window, text="")
my_label.pack()

# Démarrer la boucle principale Tkinter
window.mainloop()



'''1 demander le fichier pdf avec file open
   2 lancer le processus de conversion
   3 afficher processus en cours
   4 afficher que le processus est termine
   5 le fichier est sauvegarde au meme endroit que la source pdf'''
