import os
import time
import tkinter as tk
from tkinter import scrolledtext
import importlib
import sys
import threading
import subprocess
import webbrowser  # 引入webbrowser模块
from configs.config import BilibiliHelper
import login
import utils

# 获取当前工作目录
current_path = os.getcwd()

# 自定义类，用于将标准输出重定向到Tkinter文本框
class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.last_line_start = 1  # 初始化最后一行的起始位置

    def write(self, output: str):
        self.text_widget.configure(state=tk.NORMAL)

        # 处理包含\r的进度条更新
        if output.startswith('\r'):
            output = output[1:]  # 移除\r字符
            # 删除当前行
            self.text_widget.delete(f"{self.last_line_start}.0", tk.END)
        else:
            # 记录新行的起始位置
            self.last_line_start = int(self.text_widget.index('end-1c').split('.')[0]) + 1

        self.text_widget.insert(tk.END, output)
        self.text_widget.see(tk.END)  # 自动滚动到最新内容
        self.text_widget.configure(state=tk.DISABLED)

    def flush(self):
        pass

# 登录函数
def login():
    def run():
        try:
            login_obj = BilibiliLogin()
            qrcode_url, qrcode_key = login_obj.get_qrcode()

            # 委托主线程更新日志
            def update_log(message):
                root.after(0, lambda: log_text.insert(tk.END, message + "\n"))

            update_log("正在获取二维码...")
            if qrcode_url:
                update_log("成功获取二维码，正在打开浏览器...")
                webbrowser.open(qrcode_url)
                update_log("请在浏览器中扫码登录，等待最多 180 秒...")

                for attempt in range(36):  # 36次 × 5秒 = 180秒
                    result = login_obj.check_qrcode_status()
                    if result["success"]:
                        update_log("登录成功！")
                        break
                    elif result.get("status") == 2:
                        update_log("二维码过期，请重新登录")
                        break
                    time.sleep(5)
                else:
                    update_log("登录超时，请重试")
            else:
                update_log("获取二维码失败，请检查网络或重试")
        except Exception as e:
            update_log(f"登录过程中出现异常: {str(e)}")

    # 创建守护线程，主线程退出时自动终止子线程
    thread = threading.Thread(target=run, daemon=True)
    thread.start()


    #保存cookie
    if __name__ == '__main__':
        # print(login.get_cookie().keys())
        utils.save_json_file(path="./cookie.json", data=login.get_cookie())


# 调用外部爬虫文件中的对应函数来执行爬虫任务（异步执行）
def run_spider_1():
    def run():
        try:
            log_text.delete(1.0, tk.END)
            sys.stdout = StdoutRedirector(log_text)
            spider_module = importlib.import_module('bilibiliComments')
            log_text.insert(tk.END, f"评论爬取执行完毕，文件地址: {1}\n")
            print("爬取完成")
            path = current_path + "\\doc\\comments\\评论_" + BilibiliHelper.get_bv() + ".csv"
            log_text.insert(tk.END, f"弹幕爬取执行完毕，文件地址: {path}\n")
            file_path_label_1.config(text=f"文件地址: {path}", fg="blue", cursor="hand2")
            file_path_label_1.bind("<Button-1>", lambda e: open_file_location(path))
        except Exception as e:
            log_text.insert(tk.END, f"评论爬取执行出错: {str(e)}\n")
    threading.Thread(target=run).start()

def run_spider_2():
    def run():
        try:
            log_text.delete(1.0, tk.END)
            sys.stdout = StdoutRedirector(log_text)
            spider_module = importlib.import_module('bilibiliDMhistory')
            print("爬取完成")
            path = current_path + "\\doc\\dm\\历史弹幕_" + BilibiliHelper.get_bv() + ".csv"
            log_text.insert(tk.END, f"弹幕爬取执行完毕，文件地址: {path}\n")
            file_path_label_2.config(text=f"文件地址: {path}", fg="blue", cursor="hand2")
            file_path_label_2.bind("<Button-1>", lambda e: open_file_location(path))
        except Exception as e:
            log_text.insert(tk.END, f"弹幕爬取执行出错: {str(e)}\n")
    threading.Thread(target=run).start()

def run_spider_3():
    def run():
        try:
            log_text.delete(1.0, tk.END)
            sys.stdout = StdoutRedirector(log_text)
            spider_module = importlib.import_module('bilibiliUser')
            result = spider_module.main()
            print("爬取完成")
            path = current_path + "\\doc\\user\\用户_" + BilibiliHelper.get_bv() + ".csv"
            log_text.insert(tk.END, f"用户信息爬取执行完毕，文件地址: {path}\n")
            file_path_label_3.config(text=f"文件地址: {path}", fg="blue", cursor="hand2")
            file_path_label_3.bind("<Button-1>", lambda e: open_file_location(path))
        except Exception as e:
            log_text.insert(tk.END, f"用户信息爬取执行出错: {str(e)}\n")
    threading.Thread(target=run).start()

def run_spider_4():
    def run():
        try:
            log_text.delete(1.0, tk.END)
            sys.stdout = StdoutRedirector(log_text)
            spider_module = importlib.import_module('bilibiliVideo')
            path = current_path + "\\doc\\video\\视频信息_" + BilibiliHelper.get_bv() + ".csv"
            log_text.insert(tk.END, f"视频互动爬取执行完毕，文件地址: {path}\n")
            print("爬取完成")
            file_path_label_4.config(text=f"文件地址: {path}", fg="blue", cursor="hand2")
            file_path_label_4.bind("<Button-1>", lambda e: open_file_location(path))
        except Exception as e:
            log_text.insert(tk.END, f"视频互动爬取执行出错: {str(e)}\n")
    threading.Thread(target=run).start()

# 用于打开文件所在位置的函数（在Windows系统下通过调用资源管理器实现）
def open_file_location(file_path):
    try:
        subprocess.Popen(f'explorer /select,"{file_path}"')
    except Exception as e:
        print(f"打开文件位置出错: {str(e)}")


#GUI设计
root = tk.Tk()
root.title("BILIBILI爬虫工具")
root.configure(bg="black")

# 获取屏幕宽度和高度
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
# 设置窗口大小
window_width = 600
window_height = 600
# 计算窗口居中的坐标
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# 视频地址输入框
url_label = tk.Label(root, text="视频地址:", bg="black", fg="green", font=("Courier", 12))
url_label.pack()
url_entry = tk.Entry(root, bg="gray", fg="black", font=("Courier", 12))
url_entry.pack()

# 视频地址确认按钮及相关变量
def confirm_video_url():
    confirmed_video_url = url_entry.get()
    BilibiliHelper.set_bv(confirmed_video_url)
    log_text.insert(tk.END, "视频地址已确认\n")

video_confirm_button = tk.Button(root, text="确认视频地址", command=confirm_video_url, bg="dark green", fg="black", font=("Courier", 12))
video_confirm_button.pack()

# Cookie值输入框
cookie_label = tk.Label(root, text="Cookie值:", bg="black", fg="green", font=("Courier", 12))
cookie_label.pack()
cookie_entry = tk.Entry(root, bg="gray", fg="black", font=("Courier", 12))
cookie_entry.pack()

def confirm_cookie_value():
    confirmed_cookie_value = cookie_entry.get()
    BilibiliHelper.set_cookie(confirmed_cookie_value)
    log_text.insert(tk.END, "Cookie值已确认\n")

cookie_confirm_button = tk.Button(root, text="确认Cookie值", command=confirm_cookie_value, bg="dark green", fg="black", font=("Courier", 12))
cookie_confirm_button.pack()

# 登录按钮
login_button = tk.Button(root, text="登录", command=login, bg="dark green", fg="black", font=("Courier", 12))
login_button.pack()

# 爬虫任务按钮
spider_buttons = []
button_1 = tk.Button(root, text="评论爬取", command=run_spider_1, bg="dark green", fg="black", font=("Courier", 12))
button_1.pack()
spider_buttons.append(button_1)
button_2 = tk.Button(root, text="弹幕爬取", command=run_spider_2, bg="dark green", fg="black", font=("Courier", 12))
button_2.pack()
spider_buttons.append(button_2)
button_3 = tk.Button(root, text="用户信息爬取", command=run_spider_3, bg="dark green", fg="black", font=("Courier", 12))
button_3.pack()
spider_buttons.append(button_3)
button_4 = tk.Button(root, text="视频互动爬取", command=run_spider_4, bg="dark green", fg="black", font=("Courier", 12))
button_4.pack()
spider_buttons.append(button_4)

# 用于显示各个爬虫文件地址的标签，初始为空
file_path_label_1 = tk.Label(root, text="", bg="black", fg="green", font=("Courier", 12))
file_path_label_1.pack()
file_path_label_2 = tk.Label(root, text="", bg="black", fg="green", font=("Courier", 12))
file_path_label_2.pack()
file_path_label_3 = tk.Label(root, text="", bg="black", fg="green", font=("Courier", 12))
file_path_label_3.pack()
file_path_label_4 = tk.Label(root, text="", bg="black", fg="green", font=("Courier", 12))
file_path_label_4.pack()

# 日志显示文本框（可滚动）
log_text = scrolledtext.ScrolledText(root, width=60, height=30, bg="black", fg="green", font=("Courier", 12))
log_text.pack()
sys.stdout = StdoutRedirector(log_text)

root.mainloop()