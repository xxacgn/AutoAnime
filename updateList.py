#!/usr/bin/python3

# 更新 readme.md 中最近更新列表的脚本
import os
import sys
import datetime
import urllib.parse
import re

ROOT_DIR = "/root/mnt/动漫-更新中"

if __name__ == '__main__':
    os.chdir(ROOT_DIR)
    file = open("readme.md", "r+")
    file_content = file.readlines()
    target = sys.argv[1]
    file_name = sys.argv[2]
    # 字串刮削
    pattern = r"(?<![0-9])[0-9]{2}(?![0-9])"
    match = re.search(pattern, file_name)
    if match:
        file_name = target + " - " + match.group(0)
    
    time = datetime.datetime.now().strftime('%m-%d %H:%M')
    start = -1
    for line in file_content:
        start += 1
        if line.startswith("-"):
            break
    end = start
    for i in range(start+1, len(file_content)):
        end += 1
        if not file_content[i].startswith("-"):
            break
    ## if "-" lines are nore than 5, delete the last one
    if end - start > 14:
        file_content.pop(end)
        end -= 1
    ## insert new line at the start
    file_content.insert(start, "- [%s]\t%s\t[跳转](%s)\n" % (time, file_name , urllib.parse.quote("动漫-更新中/"+target)))
    # write file_content to file
    file.seek(0)
    file.truncate()
    file.writelines(file_content)
    file.close()