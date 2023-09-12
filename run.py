import os
import csv
import multiprocessing
import time
import shutil


def task_function(prompt, downloadFolder):
    print(f"任务爬取关键词'{prompt}' 相关视频并切割正在执行...")
    # 爬取视频
    if not os.path.exists(downloadFolder):
        os.mkdir(downloadFolder)
    # os.system(
    #     f'python Douyin_Spider.py --prompt {prompt} --destFolder {downloadFolder} --num 10')
    os.system(
        f'python BiliBili_Spider.py --prompt {prompt} --destFolder {downloadFolder} --num 7')
    print(f"任务爬取关键词 '{prompt}' 相关视频并切割已完成。")


if __name__ == '__main__':
    processes = []
    tasks = []
    max_processes = 5
    if not os.path.exists('./data'):
        os.mkdir('./data')

    if not os.path.exists('./output'):
        os.mkdir('./output')
    with open('celeb.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                prompt = row[0]+'采访'
                downloadFolder = os.path.join('data', prompt)
                tasks.append((prompt, downloadFolder))
                # print(prompt)
    # for prompt,downloadFolder in tasks:
    #     process = multiprocessing.Process(target=task_function, args=(prompt, downloadFolder))
    #     process.start()
    #     processes.append(process)
    pool = multiprocessing.Pool(processes=max_processes)
    for prompt, downloadFolder in tasks:
        pool.apply_async(task_function, (prompt, downloadFolder))

    # for process in processes:
    #     process.join()
    pool.close()
    pool.join()
    shutil.rmtree('./data', ignore_errors=True)
    print('所有任务已完成')


# for video in os.listdir('data'):
#     os.system(f'python crop-video.py --inp ./data/{video} --cpu')
