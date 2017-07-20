from webscraper import WebScraper

import os, sys, re, random, datetime, time, abc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class NaverScraper(WebScraper):

    def __init__(self, start):
        super().__init__()
        self.start = start
        self.url = "http://finance.naver.com/item/sise_day.nhn?code="

    def scrape_ohlcv(self, code):
        browser = self.browser
        url = self.url + code + "&page="
        ohlcv = list()
        page_src_dict = {0: None}
        page = 1
        stop = False
        while not stop:
            browser.get(url + str(page))
            page_src_dict[page] = browser.page_source
            if page_src_dict[page-1] == page_src_dict[page]:
                break
            page_src_dict.pop(page-1, None)
            tables = browser.find_elements_by_tag_name('table')
            raw = tables[0].text
            data = [row.split(" ") for row in raw.split("\n")]
            for i in range(1, len(data)):
                update_data = dict()
                update_data["date"] = int(data[i][0].replace(".", ""))
                if update_data["date"] < int(self.start):
                    stop = True
                    break
                update_data["close"] = int(data[i][1].replace(",", ""))
                update_data["open"] = int(data[i][3].replace(",", ""))
                update_data["high"] = int(data[i][4].replace(",", ""))
                update_data["low"] = int(data[i][5].replace(",", ""))
                update_data["volume"] = int(data[i][6].replace(",", ""))
                ohlcv.insert(0, update_data)
            page += 1
        return ohlcv

    def get_db_initializer(self, code, name, ohlcv):
        return {"code": code, "name": name, "market": "kosdaq", "ohlcv": ohlcv}

    def _scrape_tables(self):
        pass

    def _parse_table_html(self):
        pass

    def _format_df_data(self):
        pass
