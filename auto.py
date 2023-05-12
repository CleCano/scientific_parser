import os
import sys  

if  len(sys.argv) < 3 :
# Chemin du dossier contenant les fichiers PDF
    print("Erreur Commande de la forme auto commandPath FolderInPath FolderOutPath")
commandPath = sys.argv[1]
folderInPath = sys.argv[2]
folderOutPath = sys.argv[3]


# Liste des fichiers dans le dossier
files = os.listdir(folderInPath)

# Boucle pour parcourir tous les fichiers PDF
for file in files:
    # Vérifie si le fichier est un fichier PDF
    if file.endswith('.pdf'):
        # Chemin complet du fichier
        file_name = os.path.splitext(file)[0]
        file_path = (os.path.join(folderInPath, file_name))
        # Traitement à effectuer pour chaque fichier, par exemple :
        os.system("python3 " + commandPath +" "+file_path+".pdf -x --out "+folderOutPath +"/"+ file_name+".xml")
