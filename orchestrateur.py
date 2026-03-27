# orchestrateur.py
# Coordonne tous les agents pour traiter un fichier audio - Version finale

import os
import sys

# Ajouter le chemin du projet pour pouvoir importer les agents
sys.path.append(os.path.dirname(__file__))

# Importer les 4 agents
from agents.analyste.agent_analyste import AnalyzerAgent
from agents.decisionnaire.agent_decisionnaire import DecisionAgent
from agents.compresseur.agent_compresseur import CompressorAgent
from agents.evaluateur.agent_evaluateur import EvaluatorAgent


class Orchestrateur:
    """
    Orchestrateur central qui coordonne les 4 agents :
    Analyseur → Décisionnaire → Compresseur → Évaluateur
    """
    
    def __init__(self):
        # Initialiser les 4 agents
        self.analyste = AnalyzerAgent()
        self.decisionnaire = DecisionAgent()
        self.compresseur = CompressorAgent()
        self.evaluateur = EvaluatorAgent()
        
        # Creer les dossiers de sortie s'ils n'existent pas
        os.makedirs("rapports", exist_ok=True)
        os.makedirs("audio_compresse", exist_ok=True)
    
    def traiter(self, fichier_original):
        """
        Traite un fichier audio:
        1. Analyse → 2. Décision → 3. Compression → 4. Évaluation
        
        Retourne un dictionnaire avec les résultats principaux
        """
        print(f"\n" + "="*60)
        print(f"Traitement: {os.path.basename(fichier_original)}")
        print("="*60)
        
        # Vérifier que le fichier existe
        if not os.path.exists(fichier_original):
            print(f"  Erreur: fichier non trouvé")
            return None
        
        # ÉTAPE 1: ANALYSE
        print("\n[1/4] Analyse du fichier audio...")
        analyse = self.analyste.analyze(fichier_original)
        
        # ÉTAPE 2: DÉCISION
        print("\n[2/4] Décision des paramètres de compression...")
        decision = self.decisionnaire.decider(analyse)
        
        # ÉTAPE 3: COMPRESSION
        print("\n[3/4] Compression du fichier...")
        nom_base = os.path.splitext(os.path.basename(fichier_original))[0]
        fichier_sortie = os.path.join("audio_compresse", f"{nom_base}.{decision['codec']}")
        
        compression = self.compresseur.compresser(
            fichier_original, 
            fichier_sortie, 
            decision['codec'], 
            decision['bitrate']
        )
        
        # ÉTAPE 4: ÉVALUATION
        print("\n[4/4] Évaluation de la qualité...")
        evaluation = self.evaluateur.evaluer(fichier_original, fichier_sortie)
        
        # SAUVEGARDER LE RAPPORT
        self._sauvegarder_rapport(nom_base, analyse, decision, compression, evaluation)
        
        # Afficher le résumé
        self._afficher_resume(analyse, decision, compression, evaluation)
        
        # Retourner les résultats principaux
        return {
            "fichier": fichier_original,
            "type": analyse.get("content_hint", "N/A"),
            "codec": decision.get("codec", "N/A"),
            "bitrate": decision.get("bitrate", "N/A"),
            "taux_compression": compression.get("taux_compression", 0),
            "qualite": evaluation.get("qualite", "N/A")
        }
    
    def _sauvegarder_rapport(self, nom_base, analyse, decision, compression, evaluation):
        """
        Sauvegarde un rapport complet au format texte
        Conforme au cahier des charges
        """
        chemin = os.path.join("rapports", f"{nom_base}.txt")
        
        with open(chemin, 'w', encoding='utf-8') as f:
            # ============================================================
            # EN-TÊTE
            # ============================================================
            f.write("=" * 70 + "\n")
            f.write(f"RAPPORT DE TRAITEMENT AUDIO\n")
            f.write(f"Fichier : {nom_base}\n")
            f.write("=" * 70 + "\n\n")
            
            # ============================================================
            # 1. ANALYSE DU FICHIER AUDIO
            # ============================================================
            f.write("1. ANALYSE DU FICHIER AUDIO\n")
            f.write("-" * 50 + "\n")
            f.write(f"   Type de contenu      : {analyse.get('content_hint', 'N/A')}\n")
            f.write(f"   Durée                : {analyse.get('duration_seconds', 0)} secondes\n")
            f.write(f"   Fréquence d'échantillon : {analyse.get('sample_rate_hz', 0)} Hz\n")
            f.write(f"   Canaux               : {analyse.get('channels', 'N/A')}\n")
            f.write(f"   Taille               : {analyse.get('file_size_mb', 0)} MB\n")
            f.write(f"   Tempo                : {analyse.get('tempo_bpm', 0)} BPM\n")
            f.write(f"   Amplitude dynamique  : {analyse.get('amplitude_range', 0)}\n")
            f.write(f"   Centroïde spectral   : {analyse.get('spectral_centroid_hz', 0)} Hz\n")
            f.write(f"   Entropie spectrale   : {analyse.get('spectral_entropy', 0)}\n\n")
            
            # ============================================================
            # 2. PARAMÈTRES DE COMPRESSION (avec justification)
            # ============================================================
            f.write("2. PARAMÈTRES DE COMPRESSION\n")
            f.write("-" * 50 + "\n")
            f.write(f"   Codec choisi         : {decision.get('codec', 'N/A').upper()}\n")
            f.write(f"   Débit binaire        : {decision.get('bitrate', 'N/A')}\n")
            f.write(f"\n   Justification :\n")
            f.write(f"   {decision.get('justification', 'N/A')}\n\n")
            
            # ============================================================
            # 3. MÉTRIQUES DE COMPRESSION
            # ============================================================
            f.write("3. MÉTRIQUES DE COMPRESSION\n")
            f.write("-" * 50 + "\n")
            f.write(f"   Taille originale      : {compression.get('taille_originale_ko', 0)} Ko\n")
            
            # Gérer les deux orthographes possibles de la clé
            taille_comp = compression.get('taille_compressée_ko', compression.get('taille_compressee_ko', 0))
            f.write(f"   Taille compressée     : {taille_comp} Ko\n")
            f.write(f"   Taux de compression   : {compression.get('taux_compression', 0)} %\n\n")
            
            # ============================================================
            # 4. MÉTRIQUES DE QUALITÉ
            # ============================================================
            f.write("4. MÉTRIQUES DE QUALITÉ\n")
            f.write("-" * 50 + "\n")
            f.write(f"   SNR  (Signal/Bruit)  : {evaluation.get('snr', 0)} dB\n")
            f.write(f"   PSNR (Signal/Bruit de crête) : {evaluation.get('psnr', 0)} dB\n")
            f.write(f"   MSE  (Erreur quadratique)    : {evaluation.get('mse', 0)}\n\n")
            
            # ============================================================
            # 5. ÉVALUATION ET RECOMMANDATION
            # ============================================================
            f.write("5. ÉVALUATION ET RECOMMANDATION\n")
            f.write("-" * 50 + "\n")
            f.write(f"   Qualité perçue        : {evaluation.get('qualite', 'N/A')} (niveau {evaluation.get('niveau', 0)}/5)\n")
            f.write(f"   Commentaire           : {evaluation.get('commentaire', 'N/A')}\n")
            f.write(f"   Recommandation        : {evaluation.get('recommandation', 'N/A')}\n")
            f.write(f"   Efficacité            : {evaluation.get('efficacite', 'N/A')}\n")
            f.write(f"   {evaluation.get('gain', 'N/A')}\n\n")
            
            # ============================================================
            # 6. CONCLUSION
            # ============================================================
            f.write("6. CONCLUSION\n")
            f.write("-" * 50 + "\n")
            f.write(f"   {evaluation.get('conclusion', 'N/A')}\n")
            
            # ============================================================
            # FIN DU RAPPORT
            # ============================================================
            f.write("\n" + "=" * 70 + "\n")
            f.write("Fin du rapport\n")
            f.write("=" * 70 + "\n")
        
        print(f"\n  Rapport sauvegardé : {chemin}")
    
    def _afficher_resume(self, analyse, decision, compression, evaluation):
        """
        Affiche un résumé du traitement dans la console
        """
        print("\n" + "="*60)
        print("RÉSUMÉ DU TRAITEMENT")
        print("="*60)
        print(f"  Type de contenu : {analyse.get('content_hint', 'N/A')}")
        print(f"  Codec           : {decision.get('codec', 'N/A').upper()}")
        print(f"  Débit           : {decision.get('bitrate', 'N/A')}")
        print(f"  Compression     : {compression.get('taux_compression', 0)}%")
        print(f"  Qualité         : {evaluation.get('qualite', 'N/A')} (niveau {evaluation.get('niveau', 0)}/5)")
        print("="*60 + "\n")


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    # Test avec un fichier audio
    orchestrateur = Orchestrateur()
    
    # À remplacer par un vrai fichier
    fichier_test = "test.wav"
    
    if os.path.exists(fichier_test):
        resultat = orchestrateur.traiter(fichier_test)
        if resultat:
            print("Traitement terminé avec succès !")
        else:
            print("Erreur lors du traitement")
    else:
        print(f"Fichier {fichier_test} non trouvé")
