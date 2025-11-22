from pydub import AudioSegment
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
from audio_analyzer import detect_audio_gap

def audiosegment_to_librosa(audio_segment: AudioSegment):
    """
    将 AudioSegment 转为 librosa 可处理的 numpy 数组 (float32) 和采样率
    """
    # 采样率（frame_rate）
    sr = audio_segment.frame_rate

    # 获取 PCM 原始数据
    samples = np.array(audio_segment.get_array_of_samples())

    # 如果是双声道 → 转为单声道（平均）
    if audio_segment.channels > 1:
        samples = samples.reshape((-1, audio_segment.channels))
        samples = samples.mean(axis=1)

    # 转 float32，归一化到 [-1, 1]
    y = samples.astype(np.float32) / (2 ** (8 * audio_segment.sample_width - 1))

    return y, sr


def shorten_audio(y, sr, target_duration_sec=None, speed=None):
    original_duration = len(y) / sr

    if speed is None and target_duration_sec is not None:
        speed = original_duration / target_duration_sec
        print(f"自动计算速度: {speed:.3f}（从 {original_duration:.2f}s → {target_duration_sec:.2f}s）")
    elif speed is None:
        raise ValueError("speed 和 target_duration_sec 必须至少提供一个")

    y_fast = librosa.effects.time_stretch(y, rate=speed)

    print(f"音频已缩短：原长 {original_duration:.2f}s → 现长 {len(y_fast) / sr:.2f}s")
    return y_fast, sr

def process_audio(input_file, output_file, fmt):
    """
    template_file 的时长固定为 2s

    :param input_file:
    :param output_file:
    :param template_file:
    :param fmt:
    :return:
    """

    try:
        # ⚠️ Path → str，确保为绝对路径，并保持 Unicode
        input_file = str(Path(input_file).resolve())
        output_file = str(Path(output_file).resolve())
        template_file = "assets/template.mp3"
        template_length_s = 2
        silence_duration_ms = 2000

        copy_gap = detect_audio_gap(input_file, template_file)

        audio = AudioSegment.from_file(input_file)
        audio_length_s = len(audio) / 1000

        audioes = []
        start = 0
        end = int(copy_gap[0][1] * 1000)
        # 剪切
        audioes.append(audio[:end])
        for i in range(0, 5):
            start = int(copy_gap[i][1] * 1000)
            end = int(copy_gap[i+1][0] * 1000)
            audioes.append(audio[start:end])
            start = int(copy_gap[i+1][0] * 1000)
            end = int(copy_gap[i+1][1] * 1000)
            audioes.append(audio[start:end])
        start = int(copy_gap[5][1] * 1000)
        audioes.append(audio[start:])
        # audioes.length == 12

        # 连接
        silence = AudioSegment.silent(duration=silence_duration_ms)

        output_audio = audioes[0]
        for i in range(0, 5):
            # 重复一次听力音频
            output_audio = output_audio + audioes[2*i+1] + silence + audioes[2*i+1] + audioes[2*i+2]
        output_audio = output_audio + audioes[11]

        # 加速
        y_output, sr_output = audiosegment_to_librosa(output_audio)
        y_fast, sr_fast = shorten_audio(y_output, sr_output, target_duration_sec=audio_length_s)

        sf.write(output_file, y_fast, sr_fast, format=fmt)
        return True, input_file
    except Exception as e:
        return False, f"{input_file} 处理失败: {e}"
