# agent_compresseur.py
# Agent Compresseur - Version finale

import os
from agents.compresseur.compression_utils import compress_mp3, compress_aac, compress_opus, compress_ogg, compress_flac

class CompressorAgent:
    """
    Agent 3 : Compresse un fichier audio selon les paramètres choisis.
    Entrée  : fichier original + codec + bitrate (optionnel)
    Sortie  : dictionnaire avec les métriques de compression
    """
    
    def compresser(self, audio_path, output_path, codec, bitrate=None):
        """
        Compresse un fichier audio
        
        Paramètres:
            audio_path : chemin du fichier original
            output_path : chemin du fichier compressé
            codec : format de compression (mp3, aac, opus, ogg, flac)
            bitrate : débit binaire (ex: "128k") - optionnel pour flac
        
        Retourne:
            dict avec taux_compression, tailles, codec, bitrate, chemins
        """
        print(f"[CompressorAgent] Compression de: {os.path.basename(audio_path)}")
        
        # Vérifier que le fichier existe
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Fichier introuvable: {audio_path}")
        
        # Créer le dossier de sortie si nécessaire
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Taille originale
        taille_originale = os.path.getsize(audio_path)
        
        # Normaliser le codec
        codec = codec.lower()
        
        # Sélection de la méthode de compression
        if codec == "mp3":
            if not bitrate:
                bitrate = "128k"
            compress_mp3(audio_path, output_path, bitrate)
            
        elif codec == "aac":
            if not bitrate:
                bitrate = "128k"
            compress_aac(audio_path, output_path, bitrate)
            
        elif codec == "opus":
            if not bitrate:
                bitrate = "64k"
            compress_opus(audio_path, output_path, bitrate)
            
        elif codec == "ogg" or codec == "vorbis" or codec == "ogg_vorbis":
            if not bitrate:
                bitrate = "128k"
            compress_ogg(audio_path, output_path, bitrate)
            
        elif codec == "flac":
            compress_flac(audio_path, output_path)
            bitrate = "sans perte"
            
        else:
            raise ValueError(f"Format non supporté: {codec}")
        
        # Calculer les métriques
        taille_compressée = os.path.getsize(output_path)
        taux = (1 - taille_compressée / taille_originale) * 100
        
        resultat = {
            "taux_compression": round(taux, 2),
            "taille_originale_ko": round(taille_originale / 1024, 2),
            "taille_compressée_ko": round(taille_compressée / 1024, 2),
            "codec": codec,
            "bitrate": bitrate if bitrate else "N/A",
            "fichier_original": audio_path,
            "fichier_compressé": output_path
        }
        
        print(f"[CompressorAgent] Compression terminée: {round(taux, 2)}%")
        return resultat
