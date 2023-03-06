#!/usr/bin/python3

from tkinter import *
from tkinter import filedialog
import time

fileOut = ""
fileIn = ""
def file_open():
   global fileIn
   path = filedialog.askopenfilename(initialdir='~')
   print(path)
   fileIn = path
   op = open(path, 'r')
   read = op.read()
   
   


def folder_open():
   global fileOut
   path = filedialog.askdirectory(initialdir='~')
   print(path)
   fileOut = path

def file_save():
   files = []
   if(var_text_option.get()) :
      
      files.append(('Text File', '*.txt'))
   if (var_xml_option.get() ):
     
      files.append(('XML File','*.xml'))
   if(len(files)==0):
      my_label.config(text="Veuillez cocher ue case pour sauvegarder",foreground="#FF0000")
   else:
      my_label.config(text="")
      file = filedialog.asksaveasfilename(filetypes=files,defaultextension=files)
   
# Créer une fenêtre Tkinter
window = Tk()

# En haut : un bouton "Open file", deux checkbutton "Text Option" et "XML Option"
frame_top = Frame(window)
frame_top.pack(side='top', padx=10, pady=10)

button_open = Button(frame_top, text='Open file', command=file_open)
button_open.pack(side='left', padx=10)

var_text_option = BooleanVar()
var_text_option.set(True) 
checkbox_text_option = Checkbutton(frame_top, text='Text Option', variable=var_text_option)
checkbox_text_option.pack(side='left', padx=10)

var_xml_option = BooleanVar()
var_xml_option.set(False)
checkbox_xml_option = Checkbutton(frame_top, text='XML Option', variable=var_xml_option)
checkbox_xml_option.pack(side='left', padx=10)

# Au milieu : une zone de texte "preview" désactivée
frame_middle = Frame(window)
frame_middle.pack(padx=10, pady=10)

text_preview = Text(frame_middle, width=50, height=10, state='disabled')
text_preview.pack()

# En bas : à gauche un bouton "Choose path", au milieu une zone de texte "outName", à droite un bouton "Save"
frame_bottom = Frame(window)
frame_bottom.pack(side='bottom', padx=10, pady=10)

button_choose_path = Button(frame_bottom, text='Choose path', command=folder_open)
button_choose_path.pack(side='left', padx=10)

entry_out_name = Entry(frame_bottom, width=30)
entry_out_name.pack(side='left', padx=10)

button_save = Button(frame_bottom, text='Save', command=file_save)
button_save.pack(side='right', padx=10)

my_label = Label(window, text="")
my_label.pack()
# Démarrer la boucle principale Tkinter
window.mainloop()



'''1 demander le fichier pdf avec file open
   2 lancer le processus de conversion
   3 afficher processus en cours
   4 afficher que le processus est termine
   5 le fichier est sauvegarde au meme endroit que la source pdf'''
