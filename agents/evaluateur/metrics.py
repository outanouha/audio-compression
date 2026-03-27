# metrics.py
# Module des métriques pour l'agent évaluateur - Version finale

import numpy as np
import librosa
import os

# ============================================================
# 1. TAUX DE COMPRESSION
# ============================================================

def taux_compression(original_path, compressed_path):
    """
    Calcule le pourcentage de réduction de taille du fichier
    Formule : τ = (1 - taille_c / taille_o) × 100
    """
    taille_o = os.path.getsize(original_path)
    taille_c = os.path.getsize(compressed_path)
    taux = (1 - taille_c / taille_o) * 100
    return round(taux, 2)


# ============================================================
# 2. MSE - ERREUR QUADRATIQUE MOYENNE
# ============================================================

def mse(original, compresse):
    """
    Calcule l'erreur quadratique moyenne (Mean Square Error)
    Formule : MSE = moyenne((original - compressé)²)
    """
    difference = original - compresse
    return np.mean(difference ** 2)


# ============================================================
# 3. SNR - RAPPORT SIGNAL/BRUIT
# ============================================================

def snr(original, valeur_mse):
    """
    Calcule le rapport signal sur bruit (Signal-to-Noise Ratio)
    Formule : SNR = 10 × log10(V / MSE) où V = moyenne(original²)
    """
    puissance_signal = np.mean(original ** 2)
    if valeur_mse == 0:
        return 100.0
    return round(10 * np.log10(puissance_signal / valeur_mse), 2)


# ============================================================
# 4. PSNR - RAPPORT SIGNAL/BRUIT DE CRÊTE
# ============================================================

def psnr(valeur_mse, max_val=1.0):
    """
    Calcule le rapport signal sur bruit de crête (Peak SNR)
    Formule : PSNR = 10 × log10(max² / MSE)
    
    Note: max_val = 1.0 car librosa retourne des signaux entre -1 et 1
    """
    if valeur_mse == 0:
        return 100.0
    return round(10 * np.log10((max_val ** 2) / valeur_mse), 2)


# ============================================================
# 5. CHARGEMENT ET ALIGNEMENT
# ============================================================

def charger_et_aligner(original_path, compressed_path, target_sr=None):
    """
    Charge deux fichiers audio et les aligne à la même longueur et fréquence.
    Si les fréquences d'échantillonnage sont différentes, resample automatiquement.
    """
    
    # Charger les fichiers avec leur fréquence native
    y_orig, sr_orig = librosa.load(original_path, sr=None)
    y_comp, sr_comp = librosa.load(compressed_path, sr=None)
    
    # Vérifier si les fréquences sont différentes
    if sr_orig != sr_comp:
        print(f"[metrics] Fréquences différentes: {sr_orig}Hz vs {sr_comp}Hz")
        
        if target_sr is None:
            target_sr = max(sr_orig, sr_comp)
        
        print(f"[metrics] Resampling vers {target_sr}Hz")
        
        if sr_orig != target_sr:
            y_orig = librosa.resample(y_orig, orig_sr=sr_orig, target_sr=target_sr)
        if sr_comp != target_sr:
            y_comp = librosa.resample(y_comp, orig_sr=sr_comp, target_sr=target_sr)
    
    # Aligner les longueurs
    min_len = min(len(y_orig), len(y_comp))
    y_orig = y_orig[:min_len]
    y_comp = y_comp[:min_len]
    
    return y_orig, y_comp


# ============================================================
# 6. INTERPRÉTATION OPTIMALE (basée sur SNR)
# ============================================================

def interpretation_optimale(taux, val_snr, val_psnr):
    """
    Interprétation combinée des 3 métriques
    Priorité au SNR pour la qualité perçue
    """
    
    # ============================================================
    # 1. ÉVALUATION DE LA QUALITÉ (basée sur SNR)
    # ============================================================
    
    if val_snr < 15:
        qualite = "Mauvaise"
        niveau = 0
        commentaire = "Qualité médiocre, compression trop agressive"
        recommandation = "Augmenter le bitrate ou changer de codec"
        
    elif val_snr < 20:
        qualite = "Passable"
        niveau = 1
        commentaire = "Perte nettement audible, son dégradé"
        recommandation = "Limite acceptable pour stockage de masse"
        
    elif val_snr < 25:
        qualite = "Moyenne"
        niveau = 2
        commentaire = "Perte audible sur équipement haute fidélité"
        recommandation = "Acceptable pour podcasts, audiobooks"
        
    elif val_snr < 30:
        qualite = "Bonne"
        niveau = 3
        commentaire = "Qualité acceptable, perte non perceptible sur équipement standard"
        recommandation = "Idéal pour diffusion web, streaming et usage mobile"
        
    elif val_snr < 35:
        qualite = "Très bonne"
        niveau = 4
        commentaire = "Perte à peine perceptible, excellente fidélité"
        recommandation = "Parfait pour écoute sur équipement haut de gamme"
        
    else:
        qualite = "Excellente"
        niveau = 5
        commentaire = "Qualité parfaite, aucune perte perceptible"
        recommandation = "Compression idéale pour l'archivage"
    
    # ============================================================
    # 2. ÉVALUATION DE L'EFFICACITÉ (taux de compression)
    # ============================================================
    
    if taux >= 90:
        efficacite = "Maximale"
        facteur = round(100/(100-taux), 1)
        gain = f"Réduction de {taux}% : le fichier est {facteur}x plus petit"
    elif taux >= 75:
        efficacite = "Très élevée"
        facteur = round(100/(100-taux), 1)
        gain = f"Réduction de {taux}% : le fichier est {facteur}x plus petit"
    elif taux >= 50:
        efficacite = "Élevée"
        facteur = round(100/(100-taux), 1)
        gain = f"Réduction de {taux}% : le fichier est {facteur}x plus petit"
    elif taux >= 25:
        efficacite = "Modérée"
        gain = f"Réduction de {taux}% : gain de stockage limité"
    else:
        efficacite = "Faible"
        gain = f"Réduction de {taux}% : compression presque inexistante"
    
    # ============================================================
    # 3. CONCLUSION (basée sur le SNR)
    # ============================================================
    
    if val_snr < 15:
        conclusion = "Compression trop agressive - Qualité médiocre, à éviter"
    elif val_snr < 20:
        conclusion = "Compression agressive - Qualité passable, acceptable pour usage occasionnel"
    elif val_snr < 25:
        conclusion = "Compression acceptable - Qualité moyenne, convient pour contenus parlés"
    elif val_snr < 30:
        conclusion = "Bon compromis - Qualité bonne pour diffusion web"
    elif val_snr < 35:
        conclusion = "Très bon compromis - Qualité élevée, recommandée"
    else:
        conclusion = "Compression optimale - Qualité excellente, aucune perte perceptible"
    
    return {
        "qualite": qualite,
        "niveau": niveau,
        "commentaire": commentaire,
        "recommandation": recommandation,
        "efficacite": efficacite,
        "gain": gain,
        "conclusion": conclusion
    }
