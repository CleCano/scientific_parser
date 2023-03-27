#!/usr/bin/python3

import argparse
from ScientificParser import *
from tkinter import *
from tkinter import filedialog
from customtkinter import *


fileIn = ""
"""
Fonction qui permet l'ouverture d'un fichier
"""
def clear(event=0):
    global fileIn
    fileIn = ""
    text_preview.configure(state=NORMAL)
    text_preview.delete(1.0,END)
   
    text_preview.configure(state=DISABLED)
    button_save.configure(state="disabled")

def file_open(event=0):
   global fileIn
   path = filedialog.askopenfilename(initialdir='~',filetypes=[("PDF files", ".pdf")])
   fileIn = path
   
   exeCommand(fileIn,boolTextXml)
   
"""
Fonction permetant d'executer la commande qui va extraire les informations du pdf
"""   
def exeCommand(fileIn,textOrXml):

   args = argparse.Namespace()
   args.t = textOrXml.get()
   args.x = not textOrXml.get()
   args.filename = fileIn
   args.out = None
   

   text_preview.configure(state=NORMAL)
   text_preview.delete(1.0,END)
   text_preview.insert(END,launchExtraction(args))
   text_preview.configure(state=DISABLED)

   button_save.configure(state="normal")
   
"""
Fonction de sauvegarde du fichier 
"""
def file_save(event=0):

   if boolTextXml.get():
        files = [("Text File", ".txt")]
   else:
        files = [("XML File", ".xml")]
   print(files[0])
   file = filedialog.asksaveasfile(mode='w', filetypes=files,defaultextension=files[0][1])
   file.write(text_preview.get(1.0,END))

def on_select():
   if (boolTextXml2.get()!=boolTextXml.get()):
      
      boolTextXml2.set(boolTextXml.get())
      if(not boolTextXml.get()):
             text_preview.configure(wrap='none')
      else:
             text_preview.configure(wrap='word')

      if(fileIn!= ""):
         exeCommand(fileIn,boolTextXml)


"""
Création de l'interface graphique
"""
set_default_color_theme('dark-blue')
window = CTk()
window.title('Scientific Parser')


frame_top = CTkFrame(window)
frame_top.pack(side='top', padx=10, pady=10)

button_open = CTkButton(frame_top, text='Open file', command=file_open)
button_open.pack(side='left', padx=10)

boolTextXml = BooleanVar()
boolTextXml2 = BooleanVar()
boolTextXml.set(True)
boolTextXml2.set(boolTextXml.get())
radButton_text_option = CTkRadioButton(frame_top, text='Text Option', variable=boolTextXml,value=True,command=on_select)
radButton_xml_option = CTkRadioButton(frame_top, text='XML Option', variable=boolTextXml,value=False,command=on_select)

radButton_text_option.pack(side='left', padx=10)



radButton_xml_option.pack(side='left', padx=10)


frame_middle = CTkFrame(window)
frame_middle.pack(padx=10, pady=10)


text_preview = CTkTextbox(frame_middle,wrap='word',width=900,height=600)
scrollbar = CTkScrollbar(frame_middle, orientation='horizontal', command=text_preview.xview)

# Lier la barre de défilement à la zone de texte
text_preview.configure(xscrollcommand=scrollbar.set)
text_preview.pack(side='top', fill='both', expand=True)
scrollbar.pack(side='bottom', fill='x')

# En bas : à gauche un bouton "Choose path", au milieu une zone de texte "outName", à droite un bouton "Save"
frame_bottom = CTkFrame(window)
frame_bottom.pack(side='bottom', padx=10, pady=10)



button_save = CTkButton(frame_bottom, text='Save', command=file_save)
button_save.configure(state="disabled")
button_save.pack(padx=10)


window.bind('<Control-o>', file_open)
window.bind('<Control-s>', file_save)
window.bind('<Control-x>',clear)
# Démarrer l'interface graphique
window.mainloop()



'''1 demander le fichier pdf avec file open
   2 lancer le processus de conversion
   3 afficher processus en cours
   4 afficher que le processus est termine
   5 le fichier est sauvegarde au meme endroit que la source pdf'''
