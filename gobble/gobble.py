from kiwoom import Kiwoom
from dbwrapper import MongoDB
from pdreader import PDReader
from naverscraper import NaverScraper
from googlescraper import GoogleScraper
from sejongscraper import SejongScraper
from processtracker import ProcessTracker, timeit

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import os, time
import simplejson as json # simplejson for data management
import _pickle as pickle # cPickle for in-python data sorting
from pathlib import Path

TR_REQ_TIME_INTERVAL = 3.8

class Gobble(ProcessTracker):

    @timeit
    def __init__(self):
        super().__init__() # initialize ProcessTracker
        self.starting()
        self.app = QApplication(["kiwoom.py"])
        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()

    @timeit
    def start_db(self):
        pickle_in = open("db-info.pickle", "rb")
        db_info = pickle.load(pickle_in)
        user = db_info["USER"]
        pw = db_info["PW"]
        ip = db_info["IP"]
        db = db_info["DB"]
        self.connecting_db()
        self.db = MongoDB(user, pw, ip, db)
        self.connect_successful()

    @timeit
    def step_one_kiwoom(self):
        self.step_one()
        with open("log.json") as f:
            log = json.load(f)
        if log["market-dict"] != time.strftime("%Y%m%d"):
            for market_type in ["0", "10"]:
                pickle_name = "kospi-dict.pickle" if market_type == "0" else "kosdaq-dict.pickle"
                code_list = self.kiwoom.get_code_list_by_market(market_type)
                name_list = [self.kiwoom.get_master_code_name(code) for code in code_list]
                market_dict = dict(zip(code_list, name_list))
                pickle_out = open("./data/" + pickle_name, "wb")
                pickle.dump(market_dict, pickle_out)
                pickle_out.close()
                log["market-dict"] = time.strftime("%Y%m%d")
                with open("log.json", "w") as f:
                    json.dump(log, f)
            self.step_one_finish()

    @timeit
    def start_pdreader(self, start_date, end_date):
        # kospi-ohlcv
        self.starting_pdreader()
        dict_pickle = Path("./data/kospi-dict.pickle")
        if not dict_pickle.exists():
            self.step_one_skipped()
            self.step_one_kiwoom()
        self.pr = PDReader(start_date, end_date)
        self.pr.set_task()
        self.pdreader_started()

    @timeit
    def pdread_kospi_ohlcv(self):
        # task done by: pdreader.PDReader
        # roughly 35 minutes
        pr = self.pr
        self.saving_kospi_ohlcv()
        notsaved = list()
        for code, name in pr.task.items():
            try:
                self.starting_request(code, name)
                df = pr.request_df(code)
                ohlcv = pr.create_ohlcv(df)
                db_initializer = pr.get_db_initializer(code, name, ohlcv)
                with open("./data/stock/kospi-ohlcv/" + code + ".json", "w") as f:
                    json.dump(db_initializer, f)
                self.data_saved()
            except:
                self.skipped_data(code, name)
                notsaved.append(code)
        with open("log.json") as f:
            log = json.load(f)
        log["kospi-ohlcv-error"] += notsaved
        with open("log.json", "w") as f:
            json.dump(log, f)
        self.data_saved()

    def update_kospi_ohlcv(self):
        pass

    @timeit
    def start_naverscraper(self, start):
        self.ns = NaverScraper(start)
        self.ns.set_tasks()

    @timeit
    def scrape_kosdaq_ohlcv_n(self):
        ns = self.ns
        notsaved = list()
        for code, name in ns.kosdaq_task.items():
            try:
                self.starting_request(code, name)
                ohlcv = ns.scrape_ohlcv(code)
                db_initializer = ns.get_db_initializer(code, name, ohlcv)
                with open("./data/stock/kosdaq-ohlcv/" + code + ".json", "w") as f:
                    json.dump(db_initializer, f)
                self.data_saved()
            except:
                self.skipped_data(code, name)
                notsaved.append(code)
        with open("log.json") as f:
            log = json.load(f)
        log["kosdaq-ohlcv-error"] += notsaved
        with open("log.json", "w") as f:
            json.dump(log, f)
        self.data_saved()

    @timeit
    def start_googlescraper(self, start, end):
        self.gs = GoogleScraper(start, end)
        self.gs.set_tasks()

    @timeit
    def scrape_kosdaq_ohlcv_g(self):
        gs = self.gs
        notsaved = list()
        for code, name in gs.kosdaq_task.items():
            try:
                self.starting_request(code, name)
                db_initializer = gs.get_db_initializer(code, name)
                with open("./data/stock/kosdaq-ohlcv/" + code + ".json", "w") as f:
                    json.dump(db_initializer, f)
                self.data_saved()
            except:
                self.skipped_data(code, name)
                notsaved.append(code)
        with open("log.json") as f:
            log = json.load(f)
        log["kosdaq-ohlcv-error"] += notsaved
        with open("log.json", "w") as f:
            json.dump(log, f)
        self.data_saved()

    def update_kosdaq_ohlcv(self):
        pass

    def req_missing_ohlcv(self):
        pass

    @timeit
    def start_sejongscraper(self):
        self.ss = SejongScraper()
        self.ss.set_tasks()

    @timeit
    def scrape_financial_sejong(self, market_type):
        # task done by: webscraper.SejongScraper
        # do after saving kospi ohlcv
        ss = self.ss
        notsaved = list()
        task = ss.kospi_task if market_type == "kospi" else ss.kosdaq_task
        for code, name in task.items():
            try:
                value_dict = ss.create_value(code)
                file_name = "./data/stock/" + market_type + "-financial/" + code + ".json"
                data = {"code": code}
                data["annual"] = value_dict["annual"]
                data["quarter"] = value_dict["quarter"]
                with open(file_name, "w") as f:
                    json.dump(data, f)
                print(code + ", " + name + " financials added")
            except:
                print("Skipping " + code + ", " + name)
                notsaved.append(code)
        with open("log.json") as f:
            log = json.load(f)
        error_name = market_type + "-financial-error"
        log[error_name] += notsaved
        with open("log.json", "w") as f:
            json.dump(log, f)

    def update_financial_naver(self):
        pass

    def set_tasks(self):
        kospi_in = open("./data/kospi-dict.pickle", "rb")
        self.kospi_task = pickle.load(kospi_in)

        kosdaq_in = open("./data/kosdaq-dict.pickle", "rb")
        self.kosdaq_task = pickle.load(kosdaq_in)

    def _get_total_stock_num(self):
        kospi_len = len(list(self.kospi_task.keys()))
        kosdaq_len = len(list(self.kosdaq_task.keys()))
        return kospi_len + kosdaq_len

    def _buysell_skip_codes(self):
        os.chdir("./data/stock/kospi-buysell")
        kospi_list = [json.split(".")[0] for json in os.listdir()]
        os.chdir("../../../")
        os.chdir("./data/stock/kosdaq-buysell")
        kosdaq_list = [json.split(".")[0] for json in os.listdir()]
        os.chdir("../../../")
        return kospi_list + kosdaq_list

    def req_buysell(self, start):
        done_list = self._buysell_skip_codes()
        total_stock_num = self._get_total_stock_num() - len(done_list)
        code_looped = 0
        total_time = 0

        # get code list (0: KOSPI, 10: KOSDAQ)
        for market_type in [0, 10]:
            if market_type == 0:
                market = "kospi"
                task = self.kospi_task
            elif market_type == 10:
                market = "kosdaq"
                task = self.kosdaq_task

            for code, name in task.items():
                if code in done_list:
                    continue
                ts = time.time()
                try:
                    self._initialize_buysell_data(code, market, start)
                except:
                    print(code + ", " + name + " buysell save skipped due to error")
                te = time.time()
                time_took = te - ts
                total_time += time_took
                code_looped += 1
                avg_time_took = total_time/code_looped
                stocks_left = total_stock_num - code_looped
                time_left = avg_time_took * stocks_left
                print(str(stocks_left) + " stocks left to save")
                print(str(time_left) + " seconds left to finish whole request")
                print("---------------------------------------------------")

    def _initialize_buysell_data(self, code, market, start):
        global TR_REQ_TIME_INTERVAL

        kiwoom = self.kiwoom

        name = kiwoom.get_master_code_name(code)
        time.sleep(TR_REQ_TIME_INTERVAL)
        print(code + ": " + name + " buysell data initializing")
        kiwoom.prepare_data()
        print("update data dict created")

        for buysell in [1, 2]:
            if buysell == 1:
                kiwoom.set_buysell_state("buy")
            elif buysell == 2:
                kiwoom.set_buysell_state("sell")

            # opt10059 TR 요청
            kiwoom.set_input_value("일자", time.strftime('%Y%m%d'))
            kiwoom.set_input_value("종목코드", code)
            kiwoom.set_input_value("금액수량구분", 2)
            kiwoom.set_input_value("매매구분", buysell)
            kiwoom.set_input_value("단위구분", 1)
            kiwoom.comm_rq_data("opt10059_req", "opt10059", 0, "0101")
            time.sleep(TR_REQ_TIME_INTERVAL)
            print("first request sent in successfully")

            while kiwoom.remained_data == True:
                kiwoom.set_input_value("일자", time.strftime('%Y%m%d'))
                kiwoom.set_input_value("종목코드", code)
                kiwoom.set_input_value("금액수량구분", 2)
                kiwoom.set_input_value("매매구분", buysell)
                kiwoom.set_input_value("단위구분", 1)
                kiwoom.comm_rq_data("opt10059_req", "opt10059", 2, "0101")
                print("requesting...")
                current_date = kiwoom.get_date()
                print("date loop is on: ", str(current_date))
                if current_date <= int(start):
                    print("loop breaking b/c " + str(current_date) + " lower than " + start)
                    break
                time.sleep(TR_REQ_TIME_INTERVAL)
            if buysell == 1:
                print("BUY data saved, ready for DB")
            elif buysell == 2:
                print("SELL data saved, ready for DB")

        db_initializer = {"code": code, "buy": kiwoom.data["buy"], "sell": kiwoom.data["sell"]}
        file_name = "./data/stock/" + market + "-buysell/" + code + ".json"
        with open(file_name, "w") as f:
            json.dump(db_initializer, f)
        print(code + ": " + name + " buysell data successfully saved")

    def update_buysell(self):
        pass
