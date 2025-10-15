#!/usr/bin/python3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import heapq
import subprocess
import uvicorn
from typing import Optional
import threading
import time
import logging
from datetime import datetime

LOG = r'/root/code/rclone_uvicorn_service.log'

DISK = '/root/mnt'
UPLOADED = '动漫-更新中'

# 配置日志
# 创建文件处理器，保留完整格式
file_handler = logging.FileHandler(LOG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                          datefmt='%Y-%m-%d %H:%M:%S'))

# 创建控制台处理器，简化格式
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))

# 配置根日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 防止日志重复
logger.propagate = False

class CommandService:
    def __init__(self):
        # 硬编码多条命令
        self.commands = [
            f"rclone sync {DISK}/{UPLOADED} pikpak:/forShare/动漫-更新中 --pikpak-encoding Slash,Del",
            f"rclone copy {DISK}/{UPLOADED}/readme.md r2-forshare:forshare/forShare/动漫-更新中/ --pikpak-encoding Slash,Del"
        ]
        self.current_command_index = 0
        self.execution_heap = []  # 小顶堆
        self.lock = threading.Lock()  # 线程锁，用于同步访问堆
        self._running = True
        
        # 启动执行线程
        self.executor_thread = threading.Thread(target=self._execution_loop)
        self.executor_thread.daemon = True
        self.executor_thread.start()
    
    def add_execution(self, priority: int) -> bool:
        with self.lock:
            heapq.heappush(self.execution_heap, priority)
        return True
    
    def _execution_loop(self):
        while self._running:
            current_priority = None
            
            with self.lock:
                if self.execution_heap:
                    current_priority = heapq.heappop(self.execution_heap)
            
            if current_priority is not None:
                max_retries = 3  # 最大重试次数
                retry_count = 0
                success = False
                
                while retry_count < max_retries and not success:
                    try:
                        # 执行所有命令
                        all_commands_success = True
                        for i, command in enumerate(self.commands):
                            logger.info(f"开始执行命令 {i + 1}/{len(self.commands)} - 优先级: {current_priority} - 第{retry_count + 1}次尝试")
                            if "copy" in command:
                                result = subprocess.run(command, shell=True, check=False, timeout=60)
                            else:
                                result = subprocess.run(command, shell=True, check=False)
                            
                            if result.returncode == 0:
                                logger.info(f"命令 {i + 1} 执行成功")
                            else:
                                logger.warning(f"命令 {i + 1} 执行返回非零状态码: {result.returncode}")
                                all_commands_success = False
                                break
                        
                        if all_commands_success:
                            logger.info("所有命令执行成功")
                            success = True
                        else:
                            retry_count += 1
                            logger.warning(f"部分命令执行失败，重试中... ({retry_count}/{max_retries})")
                            time.sleep(5)  # 重试前等待5秒
                    except Exception as e:
                        retry_count += 1
                        logger.error(f"命令执行出现异常: {e}, 重试中... ({retry_count}/{max_retries})")
                        time.sleep(5)  # 重试前等待5秒
                
                if not success:
                    logger.error(f"命令执行失败，已达到最大重试次数 {max_retries}")
            else:
                time.sleep(1)
    
    def stop(self):
        self._running = False

# FastAPI应用实例
app = FastAPI()

# 命令服务实例（在实际使用时替换为你的命令）
command_service = CommandService()

class ExecutionRequest(BaseModel):
    priority: int

@app.post("/add_execution")
async def add_execution(request: ExecutionRequest):
    """
    添加新的执行请求到优先队列
    """
    try:
        success = command_service.add_execution(request.priority)
        if success:
            logger.info(f"收到新的执行请求 - 优先级: {request.priority}")
            return {"status": "success", "message": "执行请求已添加到队列"}
        else:
            logger.error("添加执行请求失败")
            raise HTTPException(status_code=500, message="添加执行请求失败")
    except Exception as e:
        logger.error(f"处理执行请求时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queue_size")
async def get_queue_size():
    """
    获取当前队列大小
    """
    with command_service.lock:
        queue_size = len(command_service.execution_heap)
        logger.info(f"查询队列大小 - 当前大小: {queue_size}")
        return {"queue_size": queue_size}

if __name__ == "__main__":
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8000) 
