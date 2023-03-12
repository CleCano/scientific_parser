# scientific_parser : Sprint 3

## Explication du système :

### Extraction du nom du fichier, du titre, des auteurs et de l'abstract

## Comment utiliser le logiciel :

### Lancement de l'interface graphique :
  
  -Ouvrir un shell  
  -Se placer dans le dossier d'installation "scientific_parser_IUTEAM"  
  -Lancer la commande : ./graphique.py  

### Utiliser l'interface graphique :

  - Une fois lancée, il est possible via l'interface graphique de charger un fichier pdf en entrée via un explorateur de fichiers
  - Vous pourrez ensuite choisir via deux boutons radio le type de sortie souhaité
  - Si jamais vous ne renseignez pas de fichier de sortie le résultat de la conversion sera affiché dans l'espace de texte au milieu de l'interface
  - Il est toujours possible de sauvegarder le contenu de cet espace après conversion via le bouton adapté


### Utiliser uniquement en ligne de commande :

  - Se placer dans le dossier scientific_parser_IUTEAM
  - Utiliser la commande python3 ScientificParser.py
  - Les différentes options de la commande sont spécifiées dans le manuel d'aide de celle-ci
  - Il est possible de spécifier le nom du fichier de sortie souhaité, s'il n'est pas renseigné le fichier de sortie prendra le même nom que celui d'entrée et l'extension sera adapté à la conversion effectuée 


## Dépendances :

### ```python3``` pour exécuter l'application. 
`sudo apt-get install python3`
`sudo apt-get install python3-pip`

---
### La librairie ```PyPdf2``` pour la conversion du pdf en texte.

`pip install PyPDF2`

---
### La librairie ```tkinter``` pour l'interface graphique de l'application.

` sudo apt-get install python3-tk`

---
