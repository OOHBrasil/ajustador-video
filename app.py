import streamlit as st
import subprocess
import os
import urllib.request
import gzip
import shutil
import tempfile

FFMPEG_URL = "https://github.com/eugeneware/ffmpeg-static/releases/download/b4.4/ffmpeg-linux-x64.gz"
FFPROBE_URL = "https://github.com/eugeneware/ffmpeg-static/releases/download/b4.4/ffprobe-linux-x64.gz"

def download_and_extract_binary(url, output_path):
    if not os.path.exists(output_path):
        gz_path = output_path + ".gz"
        st.info(f"🔽 Baixando {os.path.basename(output_path)}...")
        urllib.request.urlretrieve(url, gz_path)
        with gzip.open(gz_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.chmod(output_path, 0o755)
        os.remove(gz_path)

def ensure_binaries():
    download_and_extract_binary(FFMPEG_URL, "ffmpeg")
    download_and_extract_binary(FFPROBE_URL, "ffprobe")

def get_video_duration(path):
    try:
        result = subprocess.run(
            ["./ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True
        )
        return float(result.stdout.strip())
    except Exception:
        return None

def adjust_video(input_path, output_path):
    duration = get_video_duration(input_path)
    if duration is None:
        st.error("❌ Não foi possível determinar a duração do vídeo. Verifique se o arquivo está íntegro.")
        return

    target_duration = 10.0
    factor = round(target_duration / duration, 3)

    cmd = [
        "./ffmpeg",
        "-i", input_path,
        "-vf", f"fps=24,setpts=PTS*{factor}",
        "-af", f"atempo={1/factor:.3f}",
        "-t", str(target_duration),
        "-y", output_path
    ]
    subprocess.run(cmd)

def main():
    st.set_page_config(page_title="Ajustador de Vídeos OOH", layout="centered")
    st.title("🎬 Ajustador de Vídeos para OOH (10 segundos)")

    ensure_binaries()

    uploaded_file = st.file_uploader("📁 Envie o vídeo do cliente (qualquer duração)", type=["mp4", "mov", "mkv", "avi"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
            temp_input.write(uploaded_file.read())
            temp_input_path = temp_input.name

        temp_output_path = temp_input_path.replace(".mp4", "_ajustado.mp4")

        st.info("⏳ Processando vídeo para durar exatamente 10 segundos...")
        adjust_video(temp_input_path, temp_output_path)

        with open(temp_output_path, "rb") as f:
            st.success("✅ Vídeo ajustado com sucesso!")
            st.download_button("⬇️ Baixar vídeo ajustado", f, file_name="video_ajustado.mp4")

        os.remove(temp_input_path)
        os.remove(temp_output_path)

if __name__ == "__main__":
    main()
