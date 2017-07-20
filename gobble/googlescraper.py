from webscraper import WebScraper

import os, sys, re, random, datetime, time, abc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GoogleScraper(WebScraper):

    def __init__(self, start, end):
        super().__init__()
        self.start = start
        self.end = end
        self.url = "https://www.google.com/finance/historical?q="

    def _api_url(self, code, start):
        q = "KOSDAQ%3A" + code
        startdate = self.start
        enddate = self.end
        num = 200
        start = start
        url = self.url + q + \
              "&startdate=" + startdate + \
              "&enddate=" + enddate + \
              "&num=" + str(num) + \
              "&start=" + str(start)
        return url

    def _scrape_tables(self, code):
        browser = self.browser
        ohlcv = list()
        start = 0
        stop = False
        while not stop:
            url = self._api_url(code, start)
            browser.get(url)
            tables = browser.find_elements_by_tag_name("table")
            raw = tables[3].text
            data = [row.split(" ") for row in raw.split("\n")]
            for i in range(1, len(data)-3):
                update_data = dict()
                goog_date = data[i][0] + data[i][1] + data[i][2]
                goog_date = datetime.datetime.strptime(goog_date, "%b%d,%Y")
                date = goog_date.strftime("%Y%m%d")
                if int(date) < int(self.start):
                    stop = True
                    break
                update_data["date"] = int(date)
                update_data["open"] = int(float(data[i][3].replace(",", "")))
                update_data["high"] = int(float(data[i][4].replace(",", "")))
                update_data["low"] = int(float(data[i][5].replace(",", "")))
                update_data["close"] = int(float(data[i][6].replace(",", "")))
                update_data["volume"] = int(float(data[i][7].replace(",", "")))
                ohlcv.insert(0, update_data)
            start += 200
            if start >= int(data[-3][4]):
                stop = True
        return ohlcv

    def get_db_initializer(self, code, name):
        ohlcv = self._scrape_tables(code)
        return {"code": code, "name": name, "market": "kosdaq", "ohlcv": ohlcv}

    def _parse_table_html(self):
        pass

    def _format_df_data(self):
        pass
