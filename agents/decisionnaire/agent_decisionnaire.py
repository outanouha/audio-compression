# agent_decisionnaire.py
# Agent Décisionnaire - Version avec règles avancées

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional


# ============================================================
# STRUCTURES DE DONNÉES
# ============================================================

@dataclass(frozen=True)
class AnalyseAudio:
    """
    Structure de données pour les caractéristiques audio.
    Compatible avec la sortie de l'Agent Analyseur.
    """
    duree_s: Optional[float] = None
    taux_echantillonnage_hz: Optional[int] = None
    canaux: Optional[int] = None
    content_hint: Optional[str] = None
    tempo_bpm: Optional[float] = None
    amplitude_range: Optional[float] = None
    spectral_centroid_hz: Optional[float] = None
    spectral_entropy: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def depuis_dictionnaire(m: Dict[str, Any]) -> "AnalyseAudio":
        """Convertit le dictionnaire de l'Analyseur en objet AnalyseAudio"""
        return AnalyseAudio(
            duree_s=m.get("duration_seconds"),
            taux_echantillonnage_hz=m.get("sample_rate_hz"),
            canaux=m.get("channels"),
            content_hint=m.get("content_hint"),
            tempo_bpm=m.get("tempo_bpm"),
            amplitude_range=m.get("amplitude_range"),
            spectral_centroid_hz=m.get("spectral_centroid_hz"),
            spectral_entropy=m.get("spectral_entropy"),
            extra={k: v for k, v in m.items() 
                   if k not in ["duration_seconds", "sample_rate_hz", "channels", 
                                "content_hint", "tempo_bpm", "amplitude_range",
                                "spectral_centroid_hz", "spectral_entropy"]}
        )


@dataclass(frozen=True)
class DecisionCompression:
    codec: str
    debit_kbps: int
    mode: str
    justification: str
    raisonnement: Dict[str, Any] = field(default_factory=dict)

    def vers_json(self, *, indentation: int = 2) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=indentation)


# ============================================================
# FONCTION DE DÉCISION (AVEC RÈGLES FINES)
# ============================================================

def decider_compression(entree_analyse: Dict[str, Any] | AnalyseAudio) -> DecisionCompression:
    """
    Choisit le codec et le débit en fonction de l'analyse audio.
    Utilise plusieurs critères : type de contenu, dynamique, tempo, complexité spectrale.
    """
    
    # Convertir en objet AnalyseAudio si nécessaire
    if isinstance(entree_analyse, dict):
        analyse = AnalyseAudio.depuis_dictionnaire(entree_analyse)
    else:
        analyse = entree_analyse
    
    # Récupérer les informations clés
    type_contenu = analyse.content_hint or "mixed"
    canaux = analyse.canaux or 2
    duree = analyse.duree_s or 0
    tempo = analyse.tempo_bpm or 0
    amplitude = analyse.amplitude_range or 0
    spectral_centroid = analyse.spectral_centroid_hz or 0
    entropie = analyse.spectral_entropy or 0
    
    # --- DÉTERMINATION DU CODEC ---
    if type_contenu == "voice":
        codec = "opus"
        mode = "VBR"
        debit_base = 32 if canaux == 1 else 64
        justification_base = "Contenu vocal détecté. Opus offre la meilleure qualité à faible débit."
        
    elif type_contenu == "music":
        codec = "aac"
        mode = "VBR"
        debit_base = 96 if canaux == 1 else 128
        justification_base = "Contenu musical détecté. AAC offre une meilleure qualité que MP3."
        
    elif type_contenu == "ambient":
        codec = "ogg"
        mode = "VBR"
        debit_base = 64 if canaux == 1 else 96
        justification_base = "Contenu ambiant détecté. OGG offre un bon compromis."
        
    else:  # mixed ou inconnu
        codec = "mp3"
        mode = "CBR"
        debit_base = 128
        justification_base = "Type mixte ou inconnu. MP3 choisi pour sa compatibilité universelle."
    
    # --- AJUSTEMENT DU DÉBIT (RÈGLES FINES) ---
    debit = debit_base
    justifications_ajustements = []
    
    # 1. Dynamique (amplitude_range élevée = grande dynamique)
    if amplitude > 0.8:
        debit = int(debit * 1.5)
        justifications_ajustements.append("grande dynamique détectée")
    elif amplitude > 0.6:
        debit = int(debit * 1.25)
        justifications_ajustements.append("dynamique modérée détectée")
    
    # 2. Tempo (musique rapide)
    if type_contenu == "music" and tempo > 140:
        debit = int(debit * 1.25)
        justifications_ajustements.append("tempo rapide")
    elif type_contenu == "music" and tempo < 70:
        debit = int(debit * 0.9)
        justifications_ajustements.append("tempo lent")
    
    # 3. Complexité spectrale (entropie élevée = contenu riche)
    if entropie > 3.0:
        debit = int(debit * 1.3)
        justifications_ajustements.append("haute complexité spectrale")
    elif entropie > 2.0:
        debit = int(debit * 1.15)
        justifications_ajustements.append("complexité spectrale modérée")
    
    # 4. Fréquences élevées (spectral centroid haut = contenu aigu riche)
    if spectral_centroid > 5000:
        debit = int(debit * 1.2)
        justifications_ajustements.append("fréquences élevées présentes")
    elif spectral_centroid > 3000:
        debit = int(debit * 1.1)
        justifications_ajustements.append("fréquences modérément élevées")
    
    # 5. Fichiers longs (réduction du débit)
    if duree > 1800:  # plus de 30 minutes
        debit = max(32, int(debit * 0.7))
        justifications_ajustements.append("fichier long")
    
    # Bornes de sécurité
    debit = max(24, min(debit, 320))
    
    # --- CONSTRUCTION DE LA JUSTIFICATION ---
    justification = justification_base
    if justifications_ajustements:
        justification += f" Ajustements : {', '.join(justifications_ajustements)}. Débit final : {debit} kbps."
    
    # --- RAISONNEMENT DÉTAILLÉ ---
    raisonnement = {
        "type_contenu": type_contenu,
        "canaux": canaux,
        "duree_secondes": duree,
        "codec_choisi": codec,
        "debit_base_kbps": debit_base,
        "debit_final_kbps": debit,
        "mode": mode,
        "metriques_utilisees": {
            "amplitude_range": amplitude,
            "tempo_bpm": tempo,
            "spectral_centroid_hz": spectral_centroid,
            "spectral_entropy": entropie
        },
        "ajustements": justifications_ajustements
    }
    
    return DecisionCompression(
        codec=codec,
        debit_kbps=debit,
        mode=mode,
        justification=justification,
        raisonnement=raisonnement
    )


# ============================================================
# CLASSE AGENT POUR L'ORCHESTRATEUR
# ============================================================

class DecisionAgent:
    """
    Agent Décisionnaire - Interface pour l'orchestrateur.
    Compatible avec la sortie de l'Agent Analyseur.
    """
    
    def decider(self, analyse):
        """
        Reçoit le dictionnaire de l'Analyseur et retourne les paramètres de compression.
        """
        decision = decider_compression(analyse)
        
        return {
            "codec": decision.codec,
            "bitrate": f"{decision.debit_kbps}k",
            "justification": decision.justification
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    # Test 1 : Musique dynamique et rapide
    test_musique = {
        "duration_seconds": 240,
        "sample_rate_hz": 44100,
        "channels": 2,
        "content_hint": "music",
        "tempo_bpm": 150,
        "amplitude_range": 0.85,
        "spectral_centroid_hz": 4800,
        "spectral_entropy": 3.2
    }
    
    # Test 2 : Voix longue
    test_voix = {
        "duration_seconds": 3600,
        "sample_rate_hz": 22050,
        "channels": 1,
        "content_hint": "voice",
        "tempo_bpm": 0,
        "amplitude_range": 0.4,
        "spectral_centroid_hz": 1800,
        "spectral_entropy": 1.5
    }
    
    agent = DecisionAgent()
    
    print("=" * 60)
    print("TEST 1 : Musique dynamique et rapide")
    print("=" * 60)
    resultat1 = agent.decider(test_musique)
    print(f"Codec   : {resultat1['codec']}")
    print(f"Débit   : {resultat1['bitrate']}")
    print(f"Justification : {resultat1['justification']}")
    
    print("\n" + "=" * 60)
    print("TEST 2 : Voix longue")
    print("=" * 60)
    resultat2 = agent.decider(test_voix)
    print(f"Codec   : {resultat2['codec']}")
    print(f"Débit   : {resultat2['bitrate']}")
    print(f"Justification : {resultat2['justification']}")
