import os
import json
import requests
from argparse import ArgumentParser


headers = {
    'Connection':'close',
    "referer": "https://www.douyin.com/search/%E5%84%BF%E5%AD%90?aid=165d20aa-17b3-4b63-b831-645b2eb7f064&publish_time=0&sort_type=0&source=normal_search&type=general",
    "User-Agent": "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
}

sun_s = 0
videoKeywords = ''
search = ''
num = 0
count = 0
destFolder = ''

requests.packages.urllib3.disable_warnings()


def fecthData(url):
    res = requests.get(url, headers=headers, verify=False)
    return res


def download_video(url, videoname, dv):
    res = requests.get(url)
    videoFolder = os.path.join(destFolder,dv)
    if not os.path.exists(videoFolder):
        os.mkdir(videoFolder)
    video_path = os.path.join(videoFolder, f'{dv}.mp4')
    with open(video_path, 'wb') as open_file:
        open_file.write(res.content)

    return True

# 需要手动区分是视频链接还是该视频的音频的链接，甚至有一些搜索结果是纯音频文件，用这个方法去掉那些音频


def search_videourl(temp):
    for i in temp:
        if i.find('v26') == 7:
            return i
        else:
            continue


if __name__ == '__main__':
    if not os.path.exists('./data'):
        os.mkdir('./data')

    if not os.path.exists('./output'):
        os.mkdir('./output')

    parser = ArgumentParser()
    parser.add_argument("--prompt", default="李健采访",
                        type=str, help="获取本次爬取视频的关键词")
    parser.add_argument("--num", default=10, type=int, help="爬取视频数量")
    parser.add_argument("--destFolder", default="data",
                        type=str, help="视频存储目录")
    args = parser.parse_args()
    videoKeywords = args.prompt.split()
    search = '+'.join(videoKeywords)

    destFolder = args.destFolder
    num = args.num

    while count < num:
        baseUrl = f'https://www.douyin.com/aweme/v1/web/general/search/single/?device_platform=webapp&aid=6383&channel=channel_pc_web&search_channel=aweme_general&sort_type=0&publish_time=0&keyword={search}&search_source=normal_search&query_correct_type=1&is_filter_search=0&from_group_id=&offset={sun_s * 10}&count=10&search_id=202209151332480101402051633D0E8650&pc_client_type=1&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=2560&screen_height=1080&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=105.0.0.0&browser_online=true&engine_name=Blink&engine_version=105.0.0.0&os_name=Windows&os_version=10&cpu_core_num=12&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=100&webid=7129806389195458082&msToken=20jBGIfrrkKSgtlRmqkkoaFZIj-hQEwWI2LVMn4kASh_Jg_VAJCVGW9q5gwmCLXQnEFn8KdqlEJxrjF7geVghbpbUDCgZS5GJhVjGsTSrXE382FG5H-sKFM=&X-Bogus=DFSzswVLF50ANydASsRgAKXAIQ-S'
        Info = json.loads(fecthData(baseUrl).text)
        for i in Info['data'][:-1]:
            pass_url = 0

            # 一些抖音搜索结果为图片，未确定是否包含所使用的字段('aweme_info'、'video'等字段都可能不存在)
            try:
                dv = 'DV'+i['aweme_info']['aweme_id']
                # 找出符合条件的视频链接
                url = search_videourl(
                    i['aweme_info']['video']['play_addr']['url_list'])

                if url == None:
                    continue

                # 检测搜索出的视频的标签中是否包含所需的关键字，一般是有的，如果没有，跳过这条搜索结果
                for keyword in videoKeywords:
                    if keyword not in i['aweme_info']['desc']:
                        pass_url = 1
                        break
                if pass_url:
                    continue

                # 记录符合条件的视频链接，保存在douyin_videos.txt中
                douyin_videos_path = os.path.join(
                    './output', 'douyin_videos.txt').replace("\\", "/")
                # 下载视频
                print(f'正在下载第{count + 1}个视频,视频下载链接为{url}')
                if download_video(url, i['aweme_info']['desc'], dv):
                    count += 1
                    with open(douyin_videos_path, 'a', encoding='utf-8') as open_file:
                        open_file.write(args.prompt+" "+dv + '\n')
                        open_file.close()
                print(f'第{count}个视频下载完毕')
                os.system(f'python face_crop.py --data {os.path.join(destFolder,dv)} --required_similarity 0.6')
            except:
                pass
        sun_s += 1
