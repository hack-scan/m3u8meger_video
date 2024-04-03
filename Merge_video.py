import os
import subprocess
import tempfile
#   
def merge_ts_files_from_result_txt(result_txt_path, base_directory, ts_files_location, output_file, ffmpeg_path='D:/FFMEPG/bin/ffmpeg.exe'):
    # 根据result_txt_path中的文件顺序读取.ts文件路径，并附加ts_files_location的基础目录路径
    with open(result_txt_path, 'r') as result_file:
        ts_files = [os.path.join(ts_files_location, line.strip()) for line in result_file.readlines()]

    # 确保每个路径都是绝对路径且为.ts文件
    ts_files_absolute = [filename for filename in ts_files if filename.endswith('.ts') and os.path.exists(filename)]

    # 创建临时文件存储文件列表
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        for filename in ts_files_absolute:
            temp_file.write(f"file '{filename}'\n")
        temp_file.flush()

    # 构建FFmpeg命令行参数，从临时文件中读取文件列表
    command = [
        ffmpeg_path,
        '-f', 'concat',
        '-safe', '0',
        '-i', temp_file.name,
        '-c', 'copy',
        output_file
    ]

    try:
        # 执行FFmpeg命令
        subprocess.run(command, check=True)
    finally:
        # 在成功或失败后删除临时文件
        os.remove(temp_file.name)

# 调用函数进行合并，使用result.txt中的文件顺序
base_directory = "./"  # 这里填写result.txt所在的基础目录
ts_files_location = "C:/Users/safex/Downloads/m3u8/"  # 这里填写.ts文件的实际存放位置
output_file = 'output_correct_order.mp4'
merge_ts_files_from_result_txt('urls.txt', base_directory, ts_files_location, output_file)
