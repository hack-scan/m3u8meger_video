import os
import re
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# 定义中文日志等级别名
logging.addLevelName(logging.DEBUG, '调试')
logging.addLevelName(logging.INFO, '信息')
logging.addLevelName(logging.WARNING, '警告')
logging.addLevelName(logging.ERROR, '错误')
logging.addLevelName(logging.CRITICAL, '严重')

# 设置日志记录
LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)

def save_urls_to_file(links, file_path='urls.txt'):
    """
    将URL列表保存到文件中，每行一个URL。
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        for link in links:
            file.write(link + '\n')
def log_message_in_chinese(level, message, *args, **kwargs):
    """
    根据日志级别输出中文信息
    """
    msg = message.format(*args, **kwargs)
    if level >= logging.WARNING:
        logging.log(level, f"{logging.getLevelName(level)}: {msg}")
    else:
        logging.log(level, f"{msg}")


def download_and_save_link(line_no, link, target_directory, total_files):
    """
    下载链接并将.ts文件保存到指定目录，并将URL写入url.txt文件。
    """
    # 构建完整的URL
    url = f'https://vip.kuaikan-cdn4.com/20240319/mnsnGipD/6872kb/hls/{link}'

    filename = link.split('/')[-1]
    local_path = os.path.join(target_directory, filename)

    # 获取目标目录
    directory = os.path.dirname(local_path)

    # 创建目标目录（如果不存在）
    os.makedirs(directory, exist_ok=True)

    # 下载文件
    if not os.path.isfile(local_path):
        try:
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)


                # 将URL写入url.txt文件
                with open('url.txt', 'a', encoding='utf-8') as url_file:
                    url_file.write(url + '\n')
            else:
                log_message_in_chinese(logging.WARNING, "第{}行: 文件 '{}' 未找到。", line_no, filename)
        except requests.exceptions.RequestException as e:
            log_message_in_chinese(logging.ERROR, "第{}行: 文件 '{}' 下载过程中出现异常: {} 。", line_no, filename, e)
    global downloaded_files_count
    downloaded_files_count += 1

    # 更新下载进度条
    progress_bar.update(1)
# 主程序入口
if __name__ == '__main__':
    total_lines = sum(1 for _ in open("urls.txt", "r", encoding="utf-8"))
    downloaded_files_count = 0
    with open("video.txt", "r", encoding="utf-8") as video_input, \
         ThreadPoolExecutor(max_workers=5) as executor, \
         tqdm(total=total_lines, desc='下载进度',ncols=100,bar_format = '{l_bar}{bar}| [{n_fmt}/{total_fmt}{postfix}]') as progress_bar:

        futures = []
        for line_no, line in enumerate(video_input, start=1):
            links = re.findall(r'/20240319/mnsnGipD/6872kb/hls/(.*?\.ts)', line)
            if links:
                for link in links:
                    futures.append(executor.submit(download_and_save_link, line_no, link, 'C:/Users/safex/Downloads/m3u8/', total_lines))

        # 等待所有任务完成
        for future in as_completed(futures):
            future.result()

    # 清理并关闭进度条