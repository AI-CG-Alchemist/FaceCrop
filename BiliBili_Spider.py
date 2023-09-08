import os
import json
import subprocess
from lxml import etree
import requests
import time
import random
from argparse import ArgumentParser


# 关闭非https报错
requests.packages.urllib3.disable_warnings()

# 搜索关键词/此次视频爬取存储目录/爬取文件数量
prompt = ''
destFolder = ''
num = 0

# 反防爬取
headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3970.5 Safari/537.36',
    'Referer': 'https://search.bilibili.com',
    'Connection':'close',
    # 需要去首页寻找填一下
    'Cookie': "buvid3=C7BB5835-3168-999D-D869-00DD2070B75310927infoc; b_nut=1690463110; _uuid=E38292410-BC93-7D6A-10BA8-CD98E610A6A6310147infoc; buvid4=70A5848B-AAC5-290C-B20F-4536AE00247118866-023072721-hMsvJD35An8mLG1L9vVCPw%3D%3D; CURRENT_FNVAL=4048; i-wanna-go-back=-1; FEED_LIVE_VERSION=V8; header_theme_version=CLOSE; nostalgia_conf=-1; rpdid=|(u)YRJ)JJ|k0J'uYm|~~Jk~l; buvid_fp_plain=undefined; CURRENT_QUALITY=80; fingerprint=c0814b4a8792c3c609dfdd2c97370428; buvid_fp=d08be02950197bda1c71216e6833e5df; b_ut=5; bp_video_offset_479496467=834804585674571815; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTQyNjUzMDEsImlhdCI6MTY5NDAwNjEwMSwicGx0IjotMX0.JpmhMP0tx5G-kux0hI08fYDd5DWOs4JoClpwAFNTyZI; bili_ticket_expires=1694265301; innersign=0; b_lsid=EAD11169_18A73EF70B9; sid=pbq4lrr2; home_feed_column=4; browser_resolution=271-659; PVID=3"
}


def solve():

    # 首先获取共搜寻视频数量
    baseURL = 'https://api.bilibili.com/x/web-interface/search/type?search_type=video&duration=1&keyword='+prompt
    data = fetchData(baseURL)["data"]
    page_num = data['numPages']
    video_num = data['numResults']

    if page_num <= 0:
        print("未找到任何相关信息")
        return
    else:
        print("此次搜索共搜寻到"+str(video_num)+"条视频数据")

    page = 0
    index = 0
    # 逐页下载视频
    while page < page_num:
        page += 1
        url = baseURL+"&page="+str(page)
        data = fetchData(url)["data"]
        video_list = data["result"]
        txt = prompt
        for i, v in enumerate(video_list):
            index += 1
            link = v['arcurl']
            bv = v['bvid']
            txt=txt+' '+bv
            print("视频访问地址:"+link)  # debug
            print("视频bv号:"+bv)  # debug
            getBiliBiliVideo(link, bv, index, i)
            if index >= min(num, video_num):
                txt=txt+'\n'
                with open('./output/bilibili_videos.txt','a',encoding='utf-8') as f: 
                    f.writelines(txt)
                return
    txt=txt+'\n'
    with open('./output/videos.txt','a',encoding='utf-8') as f: 
        f.writelines(txt) 
        # 当爬取视频数量很多时开启防止频繁请求封ip
        # secs = random.normalvariate(1, 0.4)
        # if(secs <= 0):
        #     secs = 1
        # time.sleep(secs)


''' 封装请求函数'''


def fetchData(url):
    data = requests.get(url=url, headers=headers, verify=False).json()
    return data


''' 根据bv号获取某一个视频'''


def getBiliBiliVideo(link, bv, index, i):
    session = requests.session()
    headers.update({'Referer': 'https://www.bilibili.com/'})
    res = session.get(url=link, headers=headers, verify=False)
    _element = etree.HTML(res.content)

    videoPlayInfo = str(_element.xpath(
        '//head/script[3]/text()')[0].encode('utf-8').decode('utf-8'))[20:]

    videoJson = json.loads(videoPlayInfo)
    try:
        flag = 0
    except Exception:
        # videoURL = videoURL = videoJson['data']['durl'][0]['url']
        print("早期视频暂时不提供下载！")
        return

    dirName = os.path.join(destFolder, bv).encode("utf-8").decode("utf-8")
    if not os.path.exists(dirName):
        os.makedirs(dirName)
        # print("存储点创建成功") #debug

    print("正在下载第"+str(index)+"个视频："+bv+"....")
    if flag == 0:
        videoURL = videoJson['data']['dash']['video'][0]['baseUrl']
        print("视频下载地址:"+videoURL)  # debug
        videoPath = dirName + "/"+"TMP_"+str(index)+"-"+bv+"_Video.mp4"
        fileDownload(link=link, url=videoURL,
                     path=videoPath, session=session)
        audioURL = videoJson['data']['dash']['audio'][0]['baseUrl']
        print("音频下载地址:"+audioURL)  # debug
        audioPath = dirName + "/"+str(index)+"-"+bv+"_Audio.mp3"
        fileDownload(link=link, url=audioURL, path=audioPath, session=session)
        outPath = dirName + "/" + f"{bv}.mp4"
        print("文件存储地址:"+outPath)  # debug
        combineVideoAudio(videoPath, audioPath, outPath)
    print("第"+str(index)+"个视频下载完成")
    os.system(f'python face_crop.py --data {os.path.join(destFolder,bv)} --required_similarity 0.65')


'''合并视频与音频'''


def combineVideoAudio(videoPath, audioPath, outPath):
    subprocess.call(("ffmpeg -i " + videoPath +
                    " -i " + audioPath + " -c copy " + outPath).encode("utf-8").decode("utf-8"), shell=True)
    os.remove(videoPath)
    os.remove(audioPath)


''' 分段下载视频更加稳定'''


def fileDownload(link, url, path, session=requests.session()):
    headers.update({'Referer': link, "Cookie": ""})
    session.options(url=link, headers=headers, verify=False)
    begin = 0
    end = 1025*512-1
    flag = 0
    while True:
        headers.update({'Range': 'bytes=' + str(begin) + '-' + str(end)})

        # 获取视频分片
        res = session.get(url=url, headers=headers, verify=False)
        if res.status_code != 416:
            # 响应码不为为416时有数据
            begin = end + 1
            end = end + 1024*512
        else:
            headers.update({'Range': str(end + 1) + '-'})
            res = session.get(url=url, headers=headers, verify=False)
            flag = 1
        with open(path.encode("utf-8").decode("utf-8"), 'ab') as fp:
            fp.write(res.content)
            fp.flush()
        if flag == 1:
            fp.close()
            break


if __name__ == '__main__':
    # 爬取时运行这个
    # destFolder = input("请输入视频集存储点(如result/dest):")
    # prompt = input("请输入搜索关键词:")
    # num = input("请输入下载文件数量:")

    # 测试用
    # destFolder = "data"
    # prompt = "街头采访穿搭"
    # num = 3
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

    prompt = args.prompt
    destFolder = args.destFolder
    num = args.num

    solve()
