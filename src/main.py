import click
from pathlib import Path
from task_manager import process_files
import os

@click.command()
@click.option("--input", "-i", required=True, type=click.Path(exists=True), help="输入目录")
@click.option("--output", "-o", required=True, type=click.Path(), help="输出目录")
@click.option("--trim-start", default=0, type=float, help="剪切开始位置（秒）")
@click.option("--trim-end", default=0, type=float, help="剪切结束位置（秒）")
@click.option("--gain", default=0, type=float, help="增益（dB）")
@click.option("--format", default="wav", type=str, help="输出格式（如：wav/mp3）")
@click.option("--workers", default=os.cpu_count(), type=int, help="处理并行线程数")
def cli(input, output, trim_start, trim_end, gain, format, workers):
    """
    轻量音频批处理工具
    示例: python main.py -i ./raw -o ./out --trim-start 0 --trim-end 3 --gain 2
    """
    input_path = Path(input)
    output_path = Path(output)

    if not output_path.exists():
        output_path.mkdir(parents=True)

    process_files(
        input_path,
        output_path,
        trim_start,
        trim_end,
        gain,
        format,
        workers
    )


if __name__ == "__main__":
    os.environ["PYTHONUTF8"] = "1"
    cli()
