#!/usr/bin/python3

# 循环执行任务的脚本，将OneDrive中bts_mount目录下的文件移动到bts目录下
# 因为rclone的mount有一定延迟，所以每隔一段时间就执行一次rclone sync

import os
import time
import sys
import random
from service import Service
SRC = "/root/bts_mount"
DST = "/root/bts"
LOG = "/root/code/cp.log"

def my_task(times: int):
    if times >= 10:
        stacode = os.system("rclone sync OneDrive:/bts /root/bts")
        if stacode != 0:
            os.system("echo '"+time.asctime(time.localtime(time.time())) +
                      " : rclone sync failed \n' >> " + LOG)
    
    list = os.listdir(SRC)
    random_time = random.randint(0, 10)
    if not bool(list):
        time.sleep(random_time)
    else:
        # move files in list to DST
        os.system("mv "+SRC+"/* "+DST+"/")
        os.system("echo '"+time.asctime(time.localtime(time.time())) +
                  " : mv " + str(list) + "\n' >> " + LOG)
        time.sleep(random_time)


class TaskService(Service):
    def __init__(self, *args, **kwargs):
        super(TaskService, self).__init__(*args, **kwargs)

    def run(self):
        times = 0
        while True:
            times += 1
            my_task(times)
            if times >= 10:
                times = 0
            if self.got_sigterm():
                os.system("echo '"+time.asctime(time.localtime(time.time())) +
                    " : exit for got sigterm \n' >> " + LOG)
                return 0


if __name__ == '__main__':

    if len(sys.argv) != 2:
        sys.exit('Syntax: %s COMMAND' % sys.argv[0])

    cmd = sys.argv[1].lower()
    service = TaskService('cp_loop_daemon', pid_dir='/tmp')

    if cmd == 'start':
        service.start()
    elif cmd == 'stop':
        service.stop()
    elif cmd == 'kill':
        service.kill()
    elif cmd == 'restart':
        service.stop()
        sleeptimes = 0
        while service.is_running() and sleeptimes < 10:
            time.sleep(1)
            sleeptimes += 0.1
        if service.is_running():
            sys.exit('Service is still running and restart time out.')
        service.start()
    elif cmd == 'pid':
        print(service.get_pid())
    elif cmd == 'status':
        if service.is_running():
            print("Service is running.")
        else:
            print("Service is not running.")
    else:
        sys.exit('Unknown command "%s".' % cmd)
        