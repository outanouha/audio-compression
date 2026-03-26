# orchestrateur.py
# Coordonne tous les agents pour traiter un fichier audio

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
        1. Analyse -> 2. Decision -> 3. Compression -> 4. Evaluation
        """
        print(f"\nTraitement: {os.path.basename(fichier_original)}")
        
        # Verifier que le fichier existe
        if not os.path.exists(fichier_original):
            print(f"  Erreur: fichier non trouve")
            return None
        
        # ETAPE 1: ANALYSE
        print("  [1/4] Analyse...")
        analyse = self.analyste.analyze(fichier_original)
        
        # ETAPE 2: DECISION
        print("  [2/4] Decision...")
        decision = self.decisionnaire.decider(analyse)
        
        # ETAPE 3: COMPRESSION
        print("  [3/4] Compression...")
        # Construire le nom du fichier de sortie
        nom_base = os.path.splitext(os.path.basename(fichier_original))[0]
        fichier_sortie = os.path.join("audio_compresse", f"{nom_base}.{decision['codec']}")
        
        compression = self.compresseur.compresser(
            fichier_original, 
            fichier_sortie, 
            decision['codec'], 
            decision['bitrate']
        )
        
        # ETAPE 4: EVALUATION
        print("  [4/4] Evaluation...")
        evaluation = self.evaluateur.evaluer(fichier_original, fichier_sortie)
        
        # SAUVEGARDER LE RAPPORT
        self.sauvegarder_rapport(nom_base, analyse, decision, compression, evaluation)
        
        # Retourner les resultats
        return {
            "fichier": fichier_original,
            "type": analyse["content_hint"],
            "codec": decision["codec"],
            "bitrate": decision["bitrate"],
            "taux": compression["taux_compression"],
            "qualite": evaluation["qualite"]
        }
    
    def sauvegarder_rapport(self, nom_base, analyse, decision, compression, evaluation):
        """Sauvegarde un rapport texte avec tous les resultats"""
        
        chemin = os.path.join("rapports", f"{nom_base}.txt")
        
        with open(chemin, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write(f"RAPPORT DE TRAITEMENT: {nom_base}\n")
            f.write("="*60 + "\n\n")
            
            # Section 1: Analyse
            f.write("1. ANALYSE AUDIO\n")
            f.write("-"*40 + "\n")
            f.write(f"   Type: {analyse.get('content_hint', 'N/A')}\n")
            f.write(f"   Duree: {analyse.get('duration_seconds', 0)} secondes\n")
            f.write(f"   Sample rate: {analyse.get('sample_rate_hz', 0)} Hz\n")
            f.write(f"   Tempo: {analyse.get('tempo_bpm', 0)} BPM\n")
            f.write(f"   Taille: {analyse.get('file_size_mb', 0)} MB\n\n")
            
            # Section 2: Decision
            f.write("2. PARAMETRES DE COMPRESSION\n")
            f.write("-"*40 + "\n")
            f.write(f"   Codec: {decision.get('codec', 'N/A')}\n")
            f.write(f"   Bitrate: {decision.get('bitrate', 'N/A')}\n")
            f.write(f"   Justification: {decision.get('justification', 'N/A')}\n\n")
            
            # Section 3: Compression
            f.write("3. METRIQUES DE COMPRESSION\n")
            f.write("-"*40 + "\n")
            f.write(f"   Taux compression: {compression.get('taux_compression', 0)}%\n")
            f.write(f"   Taille originale: {compression.get('taille_originale_ko', 0)} Ko\n")
            f.write(f"   Taille compressee: {compression.get('taille_compressée_ko', 0)} Ko\n\n")
            
            # Section 4: Evaluation
            f.write("4. METRIQUES DE QUALITE\n")
            f.write("-"*40 + "\n")
            f.write(f"   Qualite: {evaluation.get('qualite', 'N/A')} (niveau {evaluation.get('niveau', 0)}/5)\n")
            f.write(f"   SNR: {evaluation.get('snr', 0)} dB\n")
            f.write(f"   PSNR: {evaluation.get('psnr', 0)} dB\n")
            f.write(f"   Commentaire: {evaluation.get('commentaire', 'N/A')}\n")
            f.write(f"   Conclusion: {evaluation.get('conclusion', 'N/A')}\n")
        
        print(f"  Rapport: {chemin}")