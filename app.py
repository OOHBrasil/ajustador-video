import streamlit as st
from moviepy.editor import VideoFileClip
import tempfile
import os

st.set_page_config(page_title="Ajustador de Vídeo OOH", layout="centered")
st.title("🛠️ Ajustador de Vídeos para Painéis OOH")

uploaded_file = st.file_uploader("📁 Envie o vídeo do cliente (MP4)", type=["mp4"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    try:
        # Carrega o vídeo e ajusta a duração para 10s
        clip = VideoFileClip(temp_file_path)
        duration = clip.duration
        target_duration = 10.0

        if duration > target_duration:
            clip = clip.subclip(0, target_duration)
        elif duration < target_duration:
            clip = clip.loop(duration=target_duration)

        output_path = temp_file_path.replace(".mp4", "_ajustado.mp4")
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

        with open(output_path, "rb") as f:
            st.success("✅ Vídeo ajustado com sucesso! Faça o download abaixo.")
            st.download_button("⬇️ Baixar vídeo ajustado", f, file_name="video_ajustado.mp4")

    except Exception as e:
        st.error(f"❌ Erro ao processar o vídeo: {str(e)}")
