import streamlit as st
import subprocess
import tempfile
import os

st.title("🎥 Ajustador de Vídeo para OOH")

def get_video_duration(path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        st.error("❌ Não foi possível determinar a duração do vídeo.")
        return None

def ajustar_video(input_path, output_path, duration):
    fator = 10.0 / duration
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f"setpts={fator}*PTS,scale=1080:-1",
        "-an", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

uploaded_file = st.file_uploader("Envie um vídeo (formato MP4)", type=["mp4"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
        temp.write(uploaded_file.read())
        temp_path = temp.name

    duration = get_video_duration(temp_path)

    if duration:
        st.success(f"Duração original: {duration:.2f} segundos")
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        ajustar_video(temp_path, output_path, duration)

        with open(output_path, "rb") as out_file:
            st.download_button(
                label="📥 Baixar vídeo ajustado",
                data=out_file,
                file_name="video-ajustado.mp4",
                mime="video/mp4"
            )
    else:
        st.error("Falha ao processar o vídeo. Envie outro arquivo válido.")
