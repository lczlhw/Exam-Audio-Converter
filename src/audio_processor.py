from pydub import AudioSegment
from pathlib import Path

def process_audio(input_file, output_file, trim_start, trim_end, gain, fmt):
    try:
        # ⚠️ Path → str，确保为绝对路径，并保持 Unicode
        input_file = str(Path(input_file).resolve())
        output_file = str(Path(output_file).resolve())

        audio = AudioSegment.from_file(input_file)

        # 剪切
        start = int(trim_start * 1000)
        end = int(trim_end * 1000) if trim_start < trim_end <= len(audio) else len(audio)
        audio = audio[start:end]

        # 增益
        if gain != 0:
            audio = audio + gain

        audio.export(output_file, format=fmt)
        return True, input_file
    except Exception as e:
        return False, f"{input_file} 处理失败: {e}"
