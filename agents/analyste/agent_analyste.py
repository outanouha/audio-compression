import librosa
import numpy as np
import os
import soundfile as sf  # Pour lire les métadonnées (nombre de canaux)

class AnalyzerAgent:
    """
    Agent 1 : Analyse les caractéristiques d'un fichier audio.
    Entrée  : chemin vers un fichier audio
    Sortie  : dictionnaire JSON avec toutes les caractéristiques
    """

    def analyze(self, file_path: str) -> dict:
        print(f"[AnalyzerAgent] Analyse de : {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier introuvable : {file_path}")

        # Récupérer le nombre de canaux avec soundfile (sans charger tout l'audio)
        try:
            info = sf.info(file_path)
            channels = info.channels
        except:
            # Fallback : charger avec librosa pour avoir une estimation
            y_test, sr_test = librosa.load(file_path, sr=None, mono=False)
            channels = y_test.shape[0] if len(y_test.shape) > 1 else 1
        
        # Charger l'audio en mono pour l'analyse spectrale
        y, sr = librosa.load(file_path, sr=None, mono=True)

        # --- Métadonnées de base ---
        duration = librosa.get_duration(y=y, sr=sr)
        file_size_mb = os.path.getsize(file_path) / 1_000_000

        # --- Caractéristiques temporelles ---
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))
        rms = float(np.mean(librosa.feature.rms(y=y)))

        # Tempo
        try:
            tempo_array = librosa.feature.rhythm.tempo(y=y, sr=sr)
            tempo = float(tempo_array[0]) if len(tempo_array) > 0 else 0.0
        except Exception:
            tempo = 0.0

        # --- Analyse spectrale ---
        spectral_centroid = float(np.mean(
            librosa.feature.spectral_centroid(y=y, sr=sr)
        ))
        spectral_bandwidth = float(np.mean(
            librosa.feature.spectral_bandwidth(y=y, sr=sr)
        ))
        spectral_rolloff = float(np.mean(
            librosa.feature.spectral_rolloff(y=y, sr=sr)
        ))

        # --- Entropie spectrale (complexité) ---
        stft = np.abs(librosa.stft(y))
        stft_normalized = stft / (np.sum(stft) + 1e-10)
        spectral_entropy = float(-np.sum(
            stft_normalized * np.log2(stft_normalized + 1e-10)
        ))

        # --- Détection voix vs musique ---
        if zcr > 0.1 and tempo < 60:
            content_hint = "voice"
        elif tempo > 80 and spectral_centroid > 2000:
            content_hint = "music"
        elif rms < 0.01:
            content_hint = "ambient"
        else:
            content_hint = "mixed"

        # --- Dynamique ---
        amplitude_range = float(np.max(np.abs(y)) - np.min(np.abs(y)))

        result = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size_mb": round(file_size_mb, 3),
            "duration_seconds": round(duration, 2),
            "sample_rate_hz": sr,
            "channels": channels,  # ✅ AJOUT : nombre de canaux (1 = mono, 2 = stéréo)
            "zero_crossing_rate": round(zcr, 5),
            "rms_energy": round(rms, 5),
            "tempo_bpm": round(tempo, 1),
            "spectral_centroid_hz": round(spectral_centroid, 1),
            "spectral_bandwidth_hz": round(spectral_bandwidth, 1),
            "spectral_rolloff_hz": round(spectral_rolloff, 1),
            "spectral_entropy": round(spectral_entropy, 3),
            "amplitude_range": round(amplitude_range, 4),
            "content_hint": content_hint
        }

        print(f"[AnalyzerAgent] Analyse terminee : {content_hint} "
              f"({duration:.1f}s, {file_size_mb:.2f}MB, {channels} canaux)")
        return result
