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
    # 需要去首页寻找填一下
    'Cookie': "buvid3=FCAD8A5A-9F75-E526-A52C-7BA4EDB2A5E177734infoc; i-wanna-go-back=-1; b_ut=7; _uuid=1BDF9A9C-A5F1-EA16-F2AC-254693E2A2101078215infoc; FEED_LIVE_VERSION=V8; buvid_fp=fdd45430966fff07b5c9e1a8d1af0076; b_nut=1690704778; CURRENT_FNVAL=4048; rpdid=|(u)YRJ)J|~J0J'uYm|~|R~)~; buvid4=E06F4432-D323-B57D-6971-F3DB5F92553E01005-023073016-hMsvJD35An8mLG1L9vVCPw%3D%3D; SESSDATA=8eb1f935%2C1706256801%2Cdcc8c%2A71Q4YST0y47zS-1I5Nhibb67HpZrrlgyXiW1sZqqBo9guk3j_e-JnCIWaLQ8VGl2BmtPYJygAAQwA; bili_jct=496d2a8b08a92222009d5271e63be66f; DedeUserID=479496467; DedeUserID__ckMd5=08b57da3bdbc65d8; header_theme_version=CLOSE; PVID=1; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTQ2MTQ3NjYsImlhdCI6MTY5NDM1NTU2NiwicGx0IjotMX0.vv16ozh_cuOO8pLw0ukkTCjQkE5RS3vMNiiiatAvtB8; bili_ticket_expires=1694614766; bp_video_offset_479496467=839737815150362630; innersign=0; b_lsid=554E2596_18A88DB5104; sid=ftqco90j; home_feed_column=4; browser_resolution=988-996"
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
        for i, v in enumerate(video_list):
            try:
                txt = prompt
                index += 1
                link = v['arcurl']
                bv = v['bvid']
                txt=txt+' '+bv+'\n'
                print("视频访问地址:"+link)  # debug
                print("视频bv号:"+bv)  # debug
                getBiliBiliVideo(link, bv, index, i)
                with open('./output/bilibili_videos.txt','a',encoding='utf-8') as f: 
                    f.writelines(txt) 
                if index >= min(num, video_num):
                    return
                # 当爬取视频数量很多时开启防止频繁请求封ip
                secs = random.normalvariate(1, 0.4)
                if(secs <= 0):
                    secs = 1
                time.sleep(secs)
            except Exception as e:
                print(e)
                pass


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

    # 9.12:改成4，之前是3突然跑不通了
    videoPlayInfo = str(_element.xpath(
        '//head/script[4]/text()')[0].encode('utf-8').decode('utf-8'))[20:]

    videoJson = json.loads(videoPlayInfo)
    try:
         # videoURL = videoURL = videoJson['data']['durl'][0]['url']
        flag = 0
    except Exception:
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
