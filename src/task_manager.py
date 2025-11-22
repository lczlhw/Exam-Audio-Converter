from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from tqdm import tqdm
from audio_processor import process_audio

def process_single(file, input_path, output_path, fmt):
    input_file = (input_path / file).resolve()
    output_file = (output_path / f"{file.stem}_processed.{fmt}").resolve()
    return process_audio(input_file, output_file, fmt)

class Worker:
    def __init__(self, input_path, output_path, fmt):
        self.input_path = input_path
        self.output_path = output_path
        self.fmt = fmt

    def __call__(self, file):
        return process_single(file, self.input_path, self.output_path, self.fmt)

def process_files(input_path: Path, output_path: Path, trim_start, trim_end, gain, fmt, workers):
    audio_files = [f for f in input_path.iterdir() if f.suffix.lower() in [".mp3", ".wav", ".flac"]]

    if not audio_files:
        print("未找到支持的音频文件 (*.mp3/*.wav/*.flac)")
        return

    print(f"\n开始处理 {len(audio_files)} 个音频文件，使用 {workers} 个进程...\n")

    # worker = Worker(input_path, output_path, trim_start, trim_end, gain, fmt)
    worker = Worker(input_path, output_path, fmt)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        # 使用 map 让任务顺序输出，使 tqdm 更新更流畅
        results = executor.map(worker, audio_files)

        # tqdm 进度监控
        for success, message in tqdm(results, total=len(audio_files), desc="处理进度"):
            tqdm.write(f"{'✔' if success else '✘'} {message}")
