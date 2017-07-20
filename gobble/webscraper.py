import os, sys, re, random, datetime, time, abc
import _pickle as pickle
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WebScraper:

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        self.browser = webdriver.PhantomJS(executable_path=os.getcwd() + '/phantomjs.exe')
        self.main_window = self.browser.window_handles[0]

    @abc.abstractmethod
    def set_tasks(self):
        """
        set tasks which are dictionaries of code, name values where Gobble
        later loops through (ex. SejongScraper sets both Kospi and kosdaq
        tasks, because it needs to loop through all stocks in Kospi and Kosdaq)
        """
        kospi_in = open("./data/kospi-dict.pickle", "rb")
        self.kospi_task = pickle.load(kospi_in)

        kosdaq_in = open("./data/kosdaq-dict.pickle", "rb")
        self.kosdaq_task = pickle.load(kosdaq_in)

    @abc.abstractmethod
    def _scrape_tables(self, code):
        """
        scrapes table source code
        """
        pass

    @abc.abstractmethod
    def _parse_table_html(self, table_type):
        """
        parses messy html source code into pandas DataFrame object
        """
        pass

    @abc.abstractmethod
    def _format_df_data(self, df):
        """
        formats the DataFrame object into json format later used to add to database
        """
        pass
