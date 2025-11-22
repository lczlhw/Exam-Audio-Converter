import numpy as np
import librosa
from pathlib import Path
from scipy.signal import fftconvolve

def fast_cross_correlation(x, y):
    """FFT 加速互相关"""
    corr = fftconvolve(x, y[::-1], mode='valid')
    corr /= np.max(np.abs(corr)) + 1e-12
    return corr

def find_template_in_audio(source_file, target_file, sr=22050, threshold_ratio=0.8, max_sec=300):
    """
    使用 librosa 完全读取前 max_sec 秒音频进行匹配
    返回匹配时间点列表（秒）
    """
    # 1. 读目标音
    y_target, sr_target = librosa.load(target_file, sr=sr)
    y_target = (y_target - np.mean(y_target)) / (np.std(y_target) + 1e-12)
    len_target = len(y_target)

    # 2. 读长音频前 max_sec 秒
    y_source, sr_source = librosa.load(source_file, sr=sr, duration=max_sec)
    y_source = (y_source - np.mean(y_source)) / (np.std(y_source) + 1e-12)

    # 3. FFT 互相关
    corr = fast_cross_correlation(y_source, y_target)

    # 4. 找匹配峰
    idxs = np.where(corr >= threshold_ratio)[0]
    times = idxs / sr  # 转为秒

    # 5. 去重：保证相邻匹配点至少间隔目标音长度
    final_times = []
    min_gap = len_target / sr
    last_time = -min_gap
    for t in sorted(times):
        if t - last_time >= min_gap and t <= max_sec:
            final_times.append(t)
            last_time = t

    return final_times

def detect_silence_before_time(audio_file, match_time, sr=22050, frame_length=2048, hop_length=512, silence_thresh_db=-40):
    """
    检测匹配时间点 match_time 前最近的静音
    - silence_thresh_db: 静音阈值，dBFS
    返回：
        - silence_start_time: 静音开始时间（秒）
        - silence_duration: 静音时长（秒）
    """
    y, sr = librosa.load(audio_file, sr=sr)
    # 转换为帧能量（dB）
    S = np.abs(librosa.stft(y, n_fft=frame_length, hop_length=hop_length))**2
    rms = librosa.feature.rms(S=S)[0]  # 每帧 RMS 能量
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)

    # 静音帧判定
    silence_frames = rms_db < silence_thresh_db

    # 帧对应时间
    times = librosa.frames_to_time(np.arange(len(rms_db)), sr=sr, hop_length=hop_length)

    # 找 match_time 前的静音段
    pre_times = times[times <= match_time]
    pre_silence = silence_frames[:len(pre_times)]

    # 从后往前找到最后连续静音段
    if np.any(pre_silence):
        last_silence_idx = np.where(pre_silence)[0]
        # 找连续段末尾
        end_idx = last_silence_idx[-1]
        # 向前找静音开始
        start_idx = end_idx
        while start_idx > 0 and pre_silence[start_idx-1]:
            start_idx -= 1
        silence_start_time = pre_times[start_idx]
        silence_end_time = pre_times[end_idx] + (hop_length/sr)
        silence_duration = silence_end_time - silence_start_time
        return silence_start_time, silence_duration
    else:
        return None, 0  # 前面没有静音

def detect_audio_gap(source_audio, target_audio):
    # length try (waiting to finish)
    matched_times = find_template_in_audio(
        source_audio,
        target_audio,
        sr=22050,
        threshold_ratio=0.8,
        max_sec=300  # 前 5 分钟
    )

    gap_time = []
    for time in matched_times[:6]:
        start_time, silence_duration = detect_silence_before_time(source_audio, time,
                                                                  sr=22050,
                                                                  frame_length=2048,
                                                                  hop_length=1024,
                                                                  silence_thresh_db=-40)
        gap_time.append([start_time, time])
    return gap_time

if __name__ == "__main__":
    source_audio = "../../test/input_audio/template.mp3"
    target_audio = "template.mp3"

    # length try (waiting to finish)
    matched_times = find_template_in_audio(
        source_audio,
        target_audio,
        sr=22050,
        threshold_ratio=0.8,
        max_sec=300  # 前 5 分钟
    )

    print("匹配到的时间点（秒）:", matched_times)

    gap_time = []
    for time in matched_times[:6]:
        start_time, silence_duration = detect_silence_before_time(source_audio, time,
                                                             sr=22050,
                                                             frame_length=2048,
                                                             hop_length=1024,
                                                             silence_thresh_db=-40)
        gap_time.append([start_time, time])
    print("匹配到的间隔:", gap_time)
