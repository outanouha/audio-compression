# compression_utils.py
# Module des fonctions de compression - Version finale

def compress_mp3(input_file, output_file, bitrate="128k"):
    """Compresse un fichier audio au format MP3"""
    from pydub import AudioSegment
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format="mp3", bitrate=bitrate)


def compress_aac(input_file, output_file, bitrate="128k"):
    """Compresse un fichier audio au format AAC"""
    from pydub import AudioSegment
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format="adts", bitrate=bitrate)


def compress_opus(input_file, output_file, bitrate="64k"):
    """Compresse un fichier audio au format Opus"""
    from pydub import AudioSegment
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format="opus", bitrate=bitrate)


def compress_ogg(input_file, output_file, bitrate="128k"):
    """Compresse un fichier audio au format OGG Vorbis"""
    from pydub import AudioSegment
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format="ogg", bitrate=bitrate)


def compress_flac(input_file, output_file):
    """Compresse un fichier audio au format FLAC (sans perte)"""
    from pydub import AudioSegment
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format="flac")
