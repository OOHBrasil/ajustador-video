import streamlit as st
import subprocess
import gzip
import shutil
import os
import tempfile
from moviepy.editor import VideoFileClip

# Novos nomes dos arquivos compactados
FFMPEG_GZ = "ffmpeg-darwin-x64.gz"
FFPROBE_GZ = "ffprobe-darwin-x64.gz"
FFMPEG_BIN = "ffmpeg"
FFPROBE_BIN = "ffprobe"

def descompactar_binarios():
    if not os.path.exists(FFMPEG_BIN):
        with gzip.open(FFMPEG_GZ, 'rb') as f_in, open(FFMPEG_BIN, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.chmod(FFMPEG_BIN, 0o755)

    if not os.path.exists(FFPROBE_BIN):
        with gzip.open(FFPROBE_GZ, 'rb') as f_in, open(FFPROBE_BIN, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.chmod(FFPROBE_BIN, 0o755)

def obter_duracao(video_path):
    try:
        result = subprocess.run(
            [f"./{FFPROBE_BIN}", "-v", "error", "-show_entries",
             "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        return float(result.stdout.strip())
    except Exception:
        return None

def ajustar_video(video_path, output_path, duration):
    fator = 10.0 / duration
    subprocess.run([
        f"./{FFMPEG_BIN}", "-i", video_path, "-vf",
        f"setpts={fator}*PTS,scale=1080:-1", "-an",
        output_path
    ])

# ----------- INTERFACE DO APP -----------

st.title("🎥 Ajustador de Vídeos para OOH")
descompactar_binarios()

uploaded_file = st.file_uploader("📤 Envie um vídeo (MP4)", type=["mp4"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    duracao = obter_duracao(temp_path)

    if duracao:
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        ajustar_video(temp_path, output_path, duracao)

        with open(output_path, "rb") as f:
            st.download_button("📥 Baixar vídeo ajustado", f, file_name="video-ajustado.mp4")

    else:
        st.error("❌ Não foi possível determinar a duração do vídeo. Verifique se o arquivo está íntegro.")
