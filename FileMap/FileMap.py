import os
import threading
import queue
import time
import re

class FileMap():
    file_path_dict = {} # 文件路径字典
    root_path_list = [] # 根目录列表
    def __init__(self,rood_path):
        self.root_path_list = rood_path
        pass

    # 控制线程
    def task_center(self):
        thread_dict = self.create_thread()  # 创建线程
        self.start_thread(thread_dict)  # 启动线程
        # 添加任务
        for rood in self.root_path_list:
            thread_dict["task_queue"]["in_queue"].put(rood)
        self.stop_thread(thread_dict)  # 停止线程

    def create_thread(self):
        # 消息队列创建
        task_queue_in_q = queue.Queue(maxsize=5)
        search_file_in_q = queue.Queue(maxsize=5)
        # 线程创建
        task_queue_thread = threading.Thread(target=self.task_queue, args=(task_queue_in_q, search_file_in_q))
        search_file_thread = threading.Thread(target=self.search_file, args=(search_file_in_q,task_queue_in_q))
        # 字典元素组合
        task_queue_comb = {
    "name": "task_queue",
    "in_queue": task_queue_in_q,
     "threading": task_queue_thread}

        search_file_comb = {
    "name": "search_file",
    "in_queue": search_file_in_q,
     "threading": search_file_thread}
        # 线程字典
        thread_dict = {
    "task_queue": task_queue_comb,
     "search_file": search_file_comb}
        return thread_dict

    def start_thread(self, thread_dict):
        #  启动线程
        for thread_comb in thread_dict.values():
            thread_comb["threading"].start()

    def stop_thread(self, thread_dict):
        task_count=len(thread_dict)# 任务计数
        # 观察线程状态
        while task_count>0:
            task_count=0
            for thread_comb in thread_dict.values():
                # 统计剩余任务数
                task_count=task_count+thread_comb["in_queue"].qsize()
            time.sleep(1)
        # 关闭线程
        for thread_comb in thread_dict.values():
            thread_comb["in_queue"].put("stop")
            thread_comb["threading"].join()

    # 搜索文件线程
    def search_file(self, in_queue,out_queue):
        while True:
            # 获取任务
            task = in_queue.get()
            print("搜索文件线程任务：", task)
            if task == "stop":
                break
            else:
                # 获取文件路径与正则表达式
                task=task.split("@re_")
                # 搜索文件、目录
                for root, dirs, files in os.walk(task[0]):
                    # 正则表达搜索文件
                    for file in files:
                        if re.search(task[1], file):
                            self.file_path_dict[file] = os.path.join(root, file)
                    # 搜索目录
                    for dir in dirs:
                        # 返回子目录
                        out_queue.put(os.path.join(root, dir,'@re_',task[1]))

    # 任务队列线程
    def task_queue(self, in_queue, out_queue):
        while True:
            # 获取任务
            task = in_queue.get()
            print("任务队列线程任务：", task)
            if task == "stop":
                break
            else:
                # 发布任务
                if not re.search(r"@re_", task):
                    task=task+"@re_.*"
                out_queue.put(task)

    # 测试用例
if __name__ == '__main__':
    f = FileMap(["D:\小迪安全", ]) #实例化
    f.task_center() # 启动程序
    # 修改文件名
    files = f.file_path_dict
    print("搜索结果为：", files)
    for file in files.values():
        dcd = re.search("【.*】", file)
        newfile = file[0:dcd.span()[0]] + file[dcd.span()[1]:]
        os.rename(file, newfile)

