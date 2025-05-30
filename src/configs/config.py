"""
Author: reisen7 (reisen7@foxmail.com)
-----
Date: Friday, 11th April 2025 6:00:52 pm
-------------------------------------

-------------------------------------
HISTORY:
Date      	By  	Comments
----------	------	------------------
"""

import os
import re
import time
import requests
from datetime import datetime
from fake_useragent import UserAgent
import json


class BilibiliHelper:
    bv = ""
    oid = ""
    cid = ""
    cookie = ""  # 类属性，存储Cookie
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Origin': 'https://www.bilibili.com',
        'Referer': 'https://www.bilibili.com/',
    }

    @classmethod
    def get_cookie(cls) -> str:
        return cls.cookie

    @classmethod
    def set_cookie(cls, cookie):
        cls.cookie = cookie  # 存储在 cookie 属性
        cls.headers['Cookie'] = cookie
        print(f"[调试] Cookie已设置: {cookie[:20]}...")

    @staticmethod
    def save_cookie(cookie_str: str):
        """保存Cookie到文件"""
        try:
            with open("cookies.json", "w") as f:
                json.dump({"cookie": cookie_str}, f)
            print("Cookie保存成功")
        except Exception as e:
            print(f"保存Cookie失败: {e}")

    @staticmethod
    def load_cookie() -> str:
        """从文件加载Cookie"""
        try:
            if os.path.exists("cookies.json"):
                with open("cookies.json", "r") as f:
                    data = json.load(f)
                    return data.get("cookie", "")
            return ""
        except Exception as e:
            print(f"加载Cookie失败: {e}")
            return ""


    @classmethod
    def get_bv(cls) -> str:
        return cls.bv

    @classmethod
    def set_bv(cls, url):
        bv_pattern = re.compile(r'(BV[0-9A-Za-z]{10})')
        match = bv_pattern.search(url)
        if match:
            cls.bv = match.group(1)
            print(f"[调试] 成功从URL中提取BV号: {cls.bv}")
            cls._get_oid_and_cid()
        else:
            print("[错误] 未能从URL中提取有效的BV号")
            cls.bv = ""

    @classmethod
    def _get_oid_and_cid(cls):
        try:
            cls.oid = cls.get_oid()
            cls.cid = cls.get_cid()
            print(f"[调试] 成功获取OID: {cls.oid}，CID: {cls.cid}")
        except ValueError as e:
            print(f"[错误] 获取OID或CID时出错: {e}")

    def __init__(self):
        self.ua = UserAgent()

    @classmethod
    def get_oid(cls) -> str:
        resp = requests.get(
            f"https://www.bilibili.com/video/{cls.bv}",
            headers=cls.get_headers(),
        )
        obj = re.compile(r'<div id="(?P<id>\d+)" bvid="{}"'.format(cls.bv))
        obj1 = re.compile(r'"aid":(?P<id>\d+),"bvid":"{}"'.format(cls.bv))
        match = obj.search(resp.text)
        if not match:
            match = obj1.search(resp.text)
        if match:
            oid = match.group("id")
            return oid
        else:
            raise ValueError("Could not find OID")

    @classmethod
    def get_cid(cls) -> str:
        cid_url = (
            f"https://api.bilibili.com/x/player/pagelist?bvid={cls.bv}"
        )
        resp2 = requests.get(cid_url, headers=cls.get_headers())
        data = resp2.json().get("data", [])
        if data:
            cid = data[0].get("cid")
            return cid
        else:
            raise ValueError("Could not find CID")

    @classmethod
    def get_headers(cls):
        headers = cls.headers.copy()
        headers['User-Agent'] = UserAgent().random  # 使用随机用户代理
        if cls.cookie:  # 修改此处：使用 cls.cookie
            headers['Cookie'] = cls.cookie
        return headers


# 设置初始值（可以放在其他地方，比如配置文件加载后）


def create_file_if_not_exists(file_path):
    file_dir = os.path.dirname(file_path)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    with open(file_path, "w", encoding="utf-8") as f:
        if os.path.exists(file_path):
            f.truncate(0)  # 清空文件内容
        else:
            pass  # 创建空文件


def get_months_between(start_timestamp, end_timestamp=None):
    # 如果未提供结束时间戳，则使用当前时间
    if end_timestamp is None:
        end_time = datetime.now()
    else:
        end_time = datetime.fromtimestamp(end_timestamp)

    start_time = datetime.fromtimestamp(start_timestamp)

    # 确保开始时间不大于结束时间
    if start_time > end_time:
        return []

    months = []
    current = start_time

    while current <= end_time:
        month_str = current.strftime("%Y-%m")
        if not months or months[-1] != month_str:  # 避免添加重复的月份
            months.append(month_str)
        # 增加到下一个月
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)

    # 如果开始和结束时间在同一月份，确保这个月份被包含
    if start_time.strftime("%Y-%m") == end_time.strftime("%Y-%m") and not months:
        months.append(start_time.strftime("%Y-%m"))

    return months


def datetime_to_timestamp_in_milliseconds():
    return int(round(time.time() * 1000))


if __name__ == "__main__":
    helper = BilibiliHelper()
    helper.set_bv("https://www.bilibili.com/video/BV1234567890")  # 设置 BV 号
    print(helper.get_oid())

