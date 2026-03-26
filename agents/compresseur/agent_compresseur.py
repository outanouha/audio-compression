# agent_compresseur.py
# Agent Compresseur

import os
from agents.compresseur.compression_utils import compress_mp3, compress_aac, compress_opus, compress_ogg, compress_flac

class CompressorAgent:
    
    def compresser(self, audio_path, output_path, codec, bitrate=None):
        print(f"[CompressorAgent] Compression de: {os.path.basename(audio_path)}")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Fichier introuvable: {audio_path}")
        
        taille_originale = os.path.getsize(audio_path)
        
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
        elif codec == "ogg":
            if not bitrate:
                bitrate = "128k"
            compress_ogg(audio_path, output_path, bitrate)
        elif codec == "flac":
            compress_flac(audio_path, output_path)
        else:
            raise ValueError(f"Format non supporte: {codec}")
        
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
        
        print(f"[CompressorAgent] Compression terminee: {round(taux, 2)}%")
        return resultat