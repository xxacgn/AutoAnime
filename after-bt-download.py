#!/usr/bin/python3

# BT下载完成后的脚本，将文件移动到对应目录、上传到 OneDrive、更新最近更新列表
import os
import subprocess
import sys
import re
import time
import random
import urllib.parse
from enum import Enum, unique, auto

UPDATE_LIST = True
DEBUG = False
LOG = r'/root/code/script.log'

DISK = '/root/mnt'
UPLOADED = '动漫-更新中'


@unique
class Mode(Enum):
    DEFAULT = auto()
    SECOND = auto()

# write string to log file


def write_log(string):
    f = open(LOG, 'a')
    f.write(string + "\n")
    f.close()


# find dir has name end with target, if not exist then create it


def find_dir(dir_list, target):
    for dir_name in dir_list:
        if os.path.isdir('./' + UPLOADED + '/' + dir_name) and (
            dir_name.endswith(target) or dir_name.upper().endswith(target.upper())):
            if DEBUG:
                write_log('find dir: ' + dir_name)
            return dir_name
    if DEBUG:
        write_log('not find dir: ' + target)
    os.mkdir(UPLOADED + "/" + target)
    write_log('create dir: ' + target)
    return target


def judge_if_target(file_path_name, file_name):
    global mode
    if '[ANi]' in file_name:
        return
    elif '[Lilith-Raws]' in file_name and '[Baha]' in file_name:
        return
    elif '[SweetSub]' in file_name and 'Heavenly Delusion' in file_name:
        return
    elif '[BeanSub]' in file_name and 'Vinland_Saga_S2' in file_name:
        mode = Mode.SECOND
        return
    elif '[Nekomoe kissaten]' in file_name and ('U149' in file_name or 'Skip to Loafer' in file_name):
        mode = Mode.SECOND
        return
    elif '[BeanSub&FZSD]' in file_name and 'Jigokuraku' in file_name:
        mode = Mode.SECOND
        return
    else:
        write_log('exit for not target file')
        sys.exit(0)


def extract_name():
    global file_name
    if mode == Mode.DEFAULT:
        # delete any characters between [ and ]
        file_name = re.split(r'\[|\]', file_name)[2]
        # delete numbers at end
        index = len(file_name) - 1
        while file_name[index] != '-':
            index -= 1
        file_name = file_name[:index].strip()
        index = len(file_name) - 1
        while file_name[index] == '.' or file_name[index] == ' ':
            index -= 1
        file_name = file_name[:index + 1]
    elif mode == Mode.SECOND:
        file_name = re.split(r'\[|\]', file_name)[3].strip()
    if DEBUG:
        write_log('file name after scrape is : ' + file_name)


if __name__ == '__main__':
    mode = Mode.DEFAULT
    write_log('-----------------------')
    write_log(time.asctime(time.localtime(time.time())))
    argv = sys.argv
    if DEBUG:
        write_log("number of argv is :\t" + str(len(argv)))
    for i in argv:
        write_log("argv " + i)
    write_log('-----------------------')
    file_path_name = argv[2] + '"' + argv[1] + '"'
    # use / to find file name
    file_name = argv[1]

    judge_if_target(file_path_name, file_name)
    file_name_org = file_name

    extract_name()

    os.chdir(DISK)
    if DEBUG:
        write_log('chdir and current dir is : ' + os.getcwd())
    dir_list = os.listdir(UPLOADED)
    if DEBUG:
        write_log('dir list is :')
        temp = ""
        for i in dir_list:
            temp += i + "\t"
        write_log(temp)

    target = find_dir(dir_list, file_name)
    # mv file to dir
    cmd = "cp -n " + file_path_name + " " + DISK + \
        "/'" + UPLOADED + "'/'" + target + "'/"
    if DEBUG:
        write_log("execute : " + cmd)
    sta_code = os.system(cmd)
    write_log(file_path_name +
              " :\n\tcopy end with status code is : " + str(sta_code))

    # sys.exit(0)
    # update list
    if UPDATE_LIST:
        os.system("/root/code/updateList.py '" +
                  target + "' '" + file_name_org+"'")

    # sleep random time
    if DEBUG:
        write_log(file_path_name+" :\n\tbefore random sleep time:\t" +
                  time.asctime(time.localtime(time.time())))
    random_time = random.randint(0, 2000)
    time.sleep(random_time*0.001)
    if DEBUG:
        write_log(file_path_name+" :\n\tafter random sleep time:\t" +
                  time.asctime(time.localtime(time.time())))
        write_log(file_path_name+" :\n\tsleep " + str(random_time) + "ms")
    # loop sleep until rclone finish
    wait_time = 0
    while len(subprocess.getoutput('ps -x|grep -v -E "daemon|grep"|grep  rclone')) != 0:
        time.sleep(10)
        wait_time += 1
        if wait_time > 300:
            break

    write_log(file_path_name+" :\n\tstart sync after wait times: "+str(wait_time))
    sta_code = os.system("rclone sync " + DISK + "/" + "'" + UPLOADED +
                         "'" + " OneDrive:/forShare/动漫-更新中")
    write_log(file_path_name +
              " :\n\tfinish sync with status code is : " + str(sta_code))

    # title = file_name_org
    # link = "https://hackermonica.me/"+urllib.parse.quote(
    #     "动漫-更新中/"+target+"/"+file_name_org)
    # description = "Monica的动漫资源站更新,\t"+target+"\t更新:\t"+file_name_org
    # write_log("the three parameter are:\n"+title+"\n "+link+"\n "+description)
    # import rssGen_rssUp
    # rssGen_rssUp.writeRss(title, link, description)
    # write_log("finish rss with:")