#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import json
import hashlib
import os
import pprint
import re
import subprocess
import random
import time
import sys

from urllib.parse import urljoin

def import_or_install(import_package_name, install_package_name=None):
    if install_package_name is None:
        install_package_name = import_package_name
    try:
        importlib.import_module(import_package_name)
    except ImportError:
        try:
            subprocess.call(f"pip install --user {install_package_name}")
            globals()[package] = importlib.import_module(import_package_name)
        except:
            pass
        

import_or_install("bs4", "beautifulsoup4")    
import_or_install("requests")
import_or_install("selenium")
import_or_install("xpinyin")

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from xpinyin import Pinyin

p = Pinyin()

# chrome_driver_file_path = './bin/chromedriver.exe'
# chrome_driver = webdriver.Chrome(executable_path=chrome_driver_file_path)

book_url = "https://ctext.org/sanguozhi/zh"

# chrome_driver.get(book_url)

# chrome_driver.find_element_by_link_text("五帝本紀").click()

header = {"Referer": book_url,
          "User-Agent": "sanguozhilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}

def get_main_text(article_name, article_url):
    final_tex = ""
    print(article_url)
    bs_obj = BeautifulSoup(requests.get(article_url, headers=header).text)
    content_div = bs_obj.find("div", {"id": "content3"})

    for td_tag in content_div.find_all("td", {"class": "opt"}):
        td_tag.replace_with("")
    for td_tag in content_div.find_all("td", {"class": "ctext"}):
        text = td_tag.get_text().strip()
        final_tex += text + "\n\n"
    if len(final_tex.strip()) < 10:
        print(f"final_tex: {final_tex}.")
        sys.exit()
    print(final_tex)
    with open("./sanguozhi/" + p.get_pinyin(article_name).strip() + ".tex", "w", encoding="utf-8") as f:
        f.write("\\article{" + article_name + "}\n\n" + "\\begin{pinyinscope}\n" + final_tex + "\n\\end{pinyinscope}")
    with open("./sanguozhi/sanguozhi.tex", "a", encoding="utf-8") as f:
        f.write("\\input{sanguozhi/" + p.get_pinyin(article_name).strip() + ".tex}\n")
    t = random.uniform(3, 6)
    print(f"{article_name} Done!\n\nSleeping for {t} seconds...")
    time.sleep(t)
    

def get_article_links(toc_url):
    articles_info = ""
    bs_obj = BeautifulSoup(requests.get(toc_url, headers=header).text)
    content_div = bs_obj.find("div", {"id": "content2"})
    for div_tag in content_div.find("div", recursive=False):
        div_tag.replace_with("")
    for a_tag in content_div.find_all("a", recursive=False):
        article_name = a_tag.get_text().strip()
        article_url = urljoin("https://ctext.org/", a_tag.attrs["href"])
        articles_info += article_name + "\t" + article_url + "\n"
    print(articles_info)
    with open("./toc.txt", "w", encoding="utf-8") as f:
        f.write(articles_info)

# get_article_links(book_url)

with open("./toc.txt", "r", encoding="utf-8") as f:
    for line in f:
        article, url = line.split('\t')
        get_main_text(article, url)

# chrome_driver.close()
