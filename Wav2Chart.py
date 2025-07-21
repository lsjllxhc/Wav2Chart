import wave
import numpy as np
import argparse
import sys

def load_1bit_wav(file_path):
    """加载 WAV 文件，并返回归一化的音频数据和采样率"""
    try:
        with wave.open(file_path, 'rb') as wav_file:
            n_channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_rate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            frames = wav_file.readframes(n_frames)
            
            if sample_width == 1:  # 8-bit unsigned (0-255)
                data = np.frombuffer(frames, dtype=np.uint8)
                data = data.astype(np.int16) - 128  # 转换为有符号 (-128~127)
            elif sample_width == 2:  # 16-bit signed (-32768~32767)
                data = np.frombuffer(frames, dtype=np.int16)
            else:
                raise ValueError("仅支持8位或16位WAV文件")
            
            # 归一化到 [-1, 1]
            data = data / np.max(np.abs(data))
            
            if n_channels > 1:  # 如果是多声道，只取左声道
                data = data[::n_channels]
            
            return data, frame_rate
    except Exception as e:
        print(f"加载WAV文件失败: {str(e)}")
        sys.exit(1)

def generate_chart(audio_data, sample_rate, output_file):
    """
    生成Phigros谱面文件
    - audio_data: 归一化的音频数据（-1到1）
    - sample_rate: 音频采样率
    - output_file: 输出文件名
    """
    bpm = int(sample_rate * 60)
    duration = len(audio_data) / sample_rate
    beats_per_second = bpm / 60
    total_beats = duration * beats_per_second
    
    beat_positions = np.linspace(0, total_beats, len(audio_data))
    
    chart_content = [
        "0",
        f"bp 0 {bpm}",
        ""
    ]
    
    note_id = 1
    for value, beat in zip(audio_data, beat_positions):
        beat_float = float(beat)
        amplitude = abs(value)
        num_notes = int(amplitude * 10)  # 根据幅度生成0-10个音符
        
        if num_notes <= 0:
            continue  # 跳过静音
            
        # 确定音符类型（Tap或Drag）
        note_type = "n1" if value > 0 else "n4"
        
        # 在拍数附近均匀生成多个音符
        for i in range(num_notes):
            current_beat = int(beat_float)
            chart_content.extend([
                f"{note_type} 1 {current_beat} 0 1 0",
                "# 1.00",
                "& 1.00",
            ])
            note_id += 1

    chart_content.extend([
	"",
	"cv 0 0.000 700.000",
	"",
	"cp 0 0.000 512.000 0.000",
	"",
	"cd 0 0.000 0.000",
	"",
	"ca 0 0.000 0",
	"",
	"",
	"",
	"cv 1 0.000 700.000",
	"",
	"cp 1 0.000 768.000 0.000",
	"",
	"cd 1 0.000 0.000",
	"",
	"ca 1 0.000 0",
	"",
	"",
	"",
	"cv 2 0.000 700.000",
	"",
	"cp 2 0.000 1024.000 0.000",
	"",
	"cd 2 0.000 0.000",
	"",
	"ca 2 0.000 0",
	"",
	"",
	"",
	"cv 3 0.000 700.000",
	"",
	"cp 3 0.000 1280.000 0.000",
	"",
	"cd 3 0.000 0.000",
	"",
	"ca 3 0.000 0",
	"",
	"",
	"",
	"cv 4 0.000 700.000",
	"",
	"cp 4 0.000 1536.000 0.000",
	"",
	"cd 4 0.000 0.000",
	"",
	"ca 4 0.000 0",
	"",
    ])
    # 写入文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(chart_content))
        print(f"谱面已生成: {output_file}")
        print(f"BPM: {bpm}, 总拍数: {int(total_beats)}, 总音符数: {note_id-1}")
    except IOError as e:
        print(f"写入文件失败: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='1bit音频转Phigros谱面生成器')
    parser.add_argument('input_file', help='输入WAV音频文件')
    parser.add_argument('output_file', help='输出谱面文件')
    
    args = parser.parse_args()
    
    # 加载音频
    audio_data, sample_rate = load_1bit_wav(args.input_file)
    print(f"音频加载成功: {args.input_file}")
    print(f"采样率: {sample_rate}Hz, 将使用BPM: {sample_rate*60}")
    
    # 生成谱面
    generate_chart(
        audio_data,
        sample_rate,
        args.output_file
    )

if __name__ == "__main__":
    main()
