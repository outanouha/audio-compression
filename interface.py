# interface.py
# Interface graphique avec affichage du rapport

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
import sys
import threading

sys.path.append(os.path.dirname(__file__))

from orchestrateur import Orchestrateur

class InterfaceAudio:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Compression Audio")
        self.root.geometry("700x600")
        
        self.orchestrateur = Orchestrateur()
        self.fichier = None
        
        self.creer_widgets()
    
    def creer_widgets(self):
        # Cadre superieur
        cadre = tk.Frame(self.root)
        cadre.pack(pady=10)
        
        tk.Button(cadre, text="Choisir un fichier", 
                  command=self.choisir, width=20).pack(side=tk.LEFT, padx=5)
        
        self.label_fichier = tk.Label(cadre, text="Aucun fichier", fg="gray", width=40)
        self.label_fichier.pack(side=tk.LEFT, padx=5)
        
        tk.Button(cadre, text="Lancer", 
                  command=self.lancer, width=15).pack(side=tk.LEFT, padx=5)
        
        # Zone texte pour le rapport
        self.texte = scrolledtext.ScrolledText(self.root, height=30, width=85)
        self.texte.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Tags pour les couleurs
        self.texte.tag_config("titre", foreground="blue", font=("Arial", 12, "bold"))
        self.texte.tag_config("section", foreground="purple", font=("Arial", 10, "bold"))
        self.texte.tag_config("valeur", foreground="green")
        self.texte.tag_config("erreur", foreground="red")
    
    def choisir(self):
        self.fichier = filedialog.askopenfilename(
            filetypes=[("Audio", "*.wav *.mp3 *.flac *.ogg")]
        )
        if self.fichier:
            self.label_fichier.config(text=os.path.basename(self.fichier), fg="green")
    
    def ajouter_ligne(self, texte, tag=None):
        """Ajoute une ligne dans le rapport"""
        self.texte.insert(tk.END, texte + "\n")
        if tag:
            ligne = self.texte.index("end-2c linestart")
            self.texte.tag_add(tag, ligne, "end-1c")
        self.texte.see(tk.END)
        self.root.update()
    
    def afficher_rapport(self, rapport_path):
        """Affiche le contenu du rapport texte"""
        try:
            with open(rapport_path, 'r', encoding='utf-8') as f:
                contenu = f.read()
            
            self.texte.delete(1.0, tk.END)
            
            # Colorer le rapport
            for ligne in contenu.split('\n'):
                if ligne.startswith('='):
                    self.ajouter_ligne(ligne, "titre")
                elif ligne.startswith(('1.', '2.', '3.', '4.')):
                    self.ajouter_ligne(ligne, "section")
                elif ':' in ligne and not ligne.startswith(' '):
                    self.ajouter_ligne(ligne, "valeur")
                else:
                    self.ajouter_ligne(ligne)
                    
        except Exception as e:
            self.ajouter_ligne(f"Erreur lecture rapport: {e}", "erreur")
    
    def lancer(self):
        if not self.fichier:
            messagebox.showwarning("Attention", "Choisissez un fichier d'abord")
            return
        
        self.texte.delete(1.0, tk.END)
        self.ajouter_ligne("Traitement en cours...", "titre")
        self.root.update()
        
        threading.Thread(target=self.traiter).start()
    
    def traiter(self):
        try:
            # Lancer le traitement
            resultat = self.orchestrateur.traiter(self.fichier)
            
            if resultat:
                # Trouver le rapport
                nom_base = os.path.splitext(os.path.basename(self.fichier))[0]
                rapport_path = os.path.join("rapports", f"{nom_base}.txt")
                
                # Afficher le rapport
                self.afficher_rapport(rapport_path)
            else:
                self.ajouter_ligne("Erreur lors du traitement", "erreur")
                
        except Exception as e:
            self.ajouter_ligne(f"Erreur: {str(e)}", "erreur")


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceAudio(root)
    root.mainloop()