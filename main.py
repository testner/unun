import json
import time
import configparser
import requests
import schedule
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapy.selector import Selector
import pymysql
from collections import defaultdict


class PackageDetail(object):
    def __init__(self):
        self.header = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjRkN2FjMGUyMTdlZWI0OGZjODcxNzQ2NDAyMThlNjc0MjRmZWEyNDE4MmQ4ZThkZDJhYTI5MGE2ZDkwZjNlOWJhYjdhNzlkZjJlOWM4NjAzIn0.eyJhdWQiOiI3IiwianRpIjoiNGQ3YWMwZTIxN2VlYjQ4ZmM4NzE3NDY0MDIxOGU2NzQyNGZlYTI0MTgyZDhlOGRkMmFhMjkwYTZkOTBmM2U5YmFiN2E3OWRmMmU5Yzg2MDMiLCJpYXQiOjE1MjAzMTg1MzgsIm5iZiI6MTUyMDMxODUzOCwiZXhwIjoxNTUxODU0NTM4LCJzdWIiOiIiLCJzY29wZXMiOltdfQ.iJ3-dYOqtfMgCfc_N9v2iDjV4BD4FYQrT2JUVlQlWKcLMBDOHcNrWC7hnw_rL8s7fuHWZ38iZLu0uBqbV8OYqyUpanPQ_nyvY-UgrUY5_R4UBftSo_DxsLp9dOueIyc_1at3lE246Z2aRsIb7iWbxvPPV8uEBNOefQexYdchp1a1P_1aPFBbW1sfyAK5cQbA6mt8ygMFDy47K69RhF-aonrs1v3MISeHYL5d5fPHwT50_KGHVOAsNdx8A1mp6aP3oa_WDpw-UFSn0imHQtXVnb-UlVvKPUfhTc7JYDywtbdFDFua4UWPMdwoAXva4bi4lydQoPx5jvu9ETs061oL4ENav6l8t_saCLUOoUoUKEU7TVI3Y3eN54rXJpqxiIztQk1VwAfz7MkKdI8ZodDfdqy_qY7O5joP8uoNKpW27ygk_Mga2b16BwabuyXl7GeYpw2LRF7F2I5yJ5tPpGCdCYo13lXTULk3_YZoIb6FGDv_8fpr7bBPknG1y9BrhBfsBP_tmeP902HoJ-c32Ywaskrs23hJGGu-a7a9BaJU1wOk4KJwsi9S5I_-QU6keMw91Zt9jTRVYn8nwuWk0eTZz6-WdS122B0xkHaYqHSkdCobbPu-bkJK5pV6CrPnm0kYRNZhDtdsGJ_sFEXO1kHBR43gpGB69ue8PFiEYtBms1k'}
        self.j = None
        self.L = []
        self.conn = pymysql.connect('127.0.0.1', 'root', 'Lovesong9', 'prod_shop_info', charset='utf8',
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    def insert_sql(self, order_id, express_id, trade_result, task_id, express_name):
        insert = """
            INSERT INTO package_detail(order_id, express_id, trade_result, task_id, express_name) VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE order_id=VALUES(order_id), express_id=VALUES(express_id), trade_result=VALUES(trade_result), task_id=VALUES(task_id), express_name=VALUES(express_name) 
        """
        self.cursor.execute(insert, (order_id, express_id, trade_result, task_id, express_name))
        self.conn.commit()

    def get_detail(self):
        data = json.loads(requests.get('https://erp.kydev.org/api/fetch-waybill', headers=self.header).text)
        if data['message'] == 'ok':
            task_id = data['data']['task_id']
            callback_url = 'https://erp.kydev.org/api/fetch-waybill/callback'
            taobao_account = data['data']['platform_account']
            order_ids = data['data']['ps_order_ids']
            types = data['data']['platform_type']

            # task_id, callback_url, taobao_account, order_ids, types = 11, 'http://httpbin.org/post', 'test', [
            #     119866911175363233,
            #     100117951414363233,
            #     120059992920685018,
            #     115446187536363233,
            #     120060496187685018,
            #     105814885277363233,
            #     120060496187685018,
            #     120059992920685018,
            #     120059992920685018,
            #     120060496187685018,
            #     120049828038685018,
            #     104824283339069793,
            #
            #     104840635835069793,
            #     113292759222363233,
            #     95463588653363233,
            #     104491155949363233,
            #     113162865150363233,
            #     97552613986363233,
            #     95692491737363233,
            #     94854031851363233], 'tbtm'

            browser = webdriver.Chrome(executable_path='.\chromedriver.exe')
            if types == 'tbtm':
                browser.get('https://login.taobao.com/')
                browser.implicitly_wait(2)
                browser.maximize_window()
                # browser.switch_to.frame(0)
                browser.find_element_by_css_selector('#J_Quick2Static').click()
                browser.find_element_by_css_selector('#TPL_username_1').send_keys(taobao_account)
                locator = (By.CSS_SELECTOR, '#J_SiteNavMytaobao .site-nav-menu-hd a span')
                WebDriverWait(browser, 20000, 0.5).until(EC.presence_of_element_located(locator))
                browser.find_element_by_css_selector('#J_SiteNavMytaobao .site-nav-menu-hd a span').click()
                browser.find_element_by_css_selector('#bought').click()
                main_window = browser.window_handles
                for i in order_ids:
                    order_id = i
                    dic = defaultdict()
                    try:
                        browser.find_element_by_css_selector('.search-mod__order-search-input___29Ui1').clear()
                        browser.find_element_by_css_selector('.search-mod__order-search-input___29Ui1').send_keys(i)
                        time.sleep(0.5)
                        browser.find_element_by_css_selector('.search-mod__order-search-button___1q3E0').click()
                        time.sleep(0.8)
                        browser.switch_to.window(main_window[0])
                        slc = Selector(text=browser.page_source)
                        # if slc.css('.sufei-dialog-content').extract_first():
                        #     time.sleep(300)

                        if slc.css('#viewDetail').extract_first() and slc.css(
                                '.index-mod__empty-list___3CaW2 span::text').extract_first() != '没有符合条件的宝贝，请尝试其他搜索条件。':
                            try:
                                browser.find_element_by_css_selector('#viewDetail').click()
                                windows = browser.window_handles
                                browser.switch_to.window(windows[-1])
                                browser.execute_script("window.scrollTo(0, 200)")
                                slct = Selector(text=browser.page_source)

                                # tmall
                                if slct.css('.trade-detail-logistic span:nth-child(3)::text').extract_first():
                                    express_id = slct.css(
                                        '.trade-detail-logistic span:nth-child(3)::text').extract_first().strip()
                                elif slct.css(
                                        '.logistics-info-mod__container___39ogG table tbody tr:nth-child(3) td::text').extract_first():
                                    express_id = slct.css(
                                        '.logistics-info-mod__container___39ogG table tbody tr:nth-child(3) td::text').extract_first().strip()
                                elif slct.css(
                                        '.partial-ship-mod__box-body___py2jk div:nth-child(1) div:nth-child(2) div:nth-child(1) div:nth-child(4) .item-value::text').extract_first():
                                    express_id = slct.css(
                                        '.partial-ship-mod__box-body___py2jk div:nth-child(1) div:nth-child(2) div:nth-child(1) div:nth-child(4) .item-value::text').extract_first().strip()
                                elif slct.css(
                                        '.simple-list.logistics-list tbody tr:nth-child(6) td:nth-child(2)::text').extract_first():
                                    express_id = slct.css(
                                        '.simple-list.logistics-list tbody tr:nth-child(6) td:nth-child(2)::text').extract_first().strip()
                                else:
                                    express_id = ''

                                if slct.css('.imfor-title h3::text').extract_first():
                                    trade_result = slct.css('.imfor-title h3::text').extract_first().strip()
                                elif slct.css('.status-desc-mod__status-desc___2Vi38 h3::text').extract_first():
                                    trade_result = slct.css(
                                        '.status-desc-mod__status-desc___2Vi38 h3::text').extract_first().strip()
                                elif slct.css('.trade-status .wait::text').extract_first():
                                    trade_result = slct.css('.trade-status .wait::text').extract_first().strip()
                                else:
                                    trade_result = ''

                                if slct.css('.trade-detail-logistic span:nth-child(1)::text').extract_first():
                                    express_name = slct.css(
                                        '.trade-detail-logistic span:nth-child(1)::text').extract_first().strip()
                                elif slct.css(
                                        '.logistics-info-mod__container___39ogG table tbody tr:nth-child(2) td::text').extract_first():
                                    express_name = slct.css(
                                        '.logistics-info-mod__container___39ogG table tbody tr:nth-child(2) td::text').extract_first().strip()
                                elif slct.css(
                                        '.partial-ship-mod__box-body___py2jk div:nth-child(1) div:nth-child(2) div:nth-child(1) div:nth-child(3) .item-value::text').extract_first():
                                    express_name = slct.css(
                                        '.partial-ship-mod__box-body___py2jk div:nth-child(1) div:nth-child(2) div:nth-child(1) div:nth-child(3) .item-value::text').extract_first().strip()
                                elif slct.css(
                                        '.simple-list.logistics-list tbody tr:nth-child(5) td:nth-child(2)::text').extract_first():
                                    express_name = slct.css(
                                        '.simple-list.logistics-list tbody tr:nth-child(5) td:nth-child(2)::text').extract_first().strip()

                                else:
                                    express_name = ''

                                self.insert_sql(order_id, express_id, trade_result, task_id, express_name)
                                # print(slct.css('.info div:nth-child(1) span:nth-child(4)::text').extract_first().strip()) #物流名称

                                dic['ps_order_id'] = order_id
                                dic['express_id'] = express_id
                                dic['trade_result'] = trade_result
                                dic['task_id'] = task_id
                                dic['express_name'] = express_name
                                # j = json.dumps(dic)
                                print('===', dic, '===')
                                r = requests.post(callback_url, data=dic, headers=self.header)
                                print('post返回:', r.text)
                                print('dic:', dic)
                            except Exception as e:
                                print(e)
                                continue
                            finally:
                                for handle in windows:
                                    if handle != main_window[0]:
                                        browser.switch_to.window(handle)
                                        browser.close()
                                browser.switch_to.window(windows[0])
                        else:
                            dic['ps_order_id'] = order_id
                            dic['express_id'] = ''
                            dic['trade_result'] = ''
                            dic['task_id'] = task_id
                            dic['express_name'] = ''
                            r = requests.post(callback_url, data=dic, headers=self.header)
                            print('post返回:', r.text)
                            print('dic:', dic)
                    except Exception as e:
                        print(e)
                        continue

            if types == '1688':
                browser.get('https://login.taobao.com/')
                browser.implicitly_wait(2)
                browser.maximize_window()
                # browser.switch_to.frame(0)
                browser.find_element_by_css_selector('#J_Quick2Static').click()
                browser.find_element_by_css_selector('#TPL_username_1').send_keys(taobao_account)
                locator = (By.CSS_SELECTOR, '#J_SiteNavMytaobao .site-nav-menu-hd a span')
                WebDriverWait(browser, 20000, 0.5).until(EC.presence_of_element_located(locator))

                browser.get('https://work.1688.com/')
                # browser.implicitly_wait(2)
                # browser.maximize_window()
                # browser.switch_to.frame(0)
                # browser.find_element_by_css_selector('#J_Quick2Static').click()
                # browser.find_element_by_css_selector('#TPL_username_1').send_keys(taobao_account)
                # time.sleep(1)
                locator = (By.CSS_SELECTOR, '.context.quickentry li:nth-child(1) a')
                WebDriverWait(browser, 20000, 0.5).until(EC.presence_of_element_located(locator))
                s = Selector(text=browser.page_source)
                if s.css('.mask .close').extract_first():
                    browser.find_element_by_css_selector('.mask .close').click()
                if s.css('.btn.close.iconfont').extract_first():
                    browser.find_element_by_css_selector('.btn.close.iconfont').click()
                # if browser.find_element_by_css_selector('.mask .close'):
                #     browser.find_element_by_css_selector('.mask .close').click()
                browser.find_element_by_css_selector('.context.quickentry li:nth-child(1) a').click()

                for i in order_ids:
                    order_id = i
                    dic = defaultdict()
                    try:
                        browser.switch_to.default_content()
                        browser.switch_to.frame(browser.find_element_by_css_selector('.work-iframe'))
                        slt = Selector(text=browser.page_source)
                        # if slt.css('#orderlist-no-items-warn::text').extract_first() == '没有符合条件的订单，请尝试其它搜索条件。':
                        #     browser.switch_to.default_content()
                        browser.find_element_by_css_selector('#keywords').clear()
                        browser.find_element_by_css_selector('#keywords').send_keys(i)
                        time.sleep(0.5)
                        browser.find_element_by_css_selector('.button.lang-button.submit-button-box').click()
                        time.sleep(0.8)
                        slc = Selector(text=browser.page_source)
                        # if slc.css('.sufei-dialog-content').extract_first():
                        #     time.sleep(300)

                        if slc.css('.bannerOrderDetail').extract_first():
                            try:
                                browser.find_element_by_css_selector('.bannerOrderDetail').click()
                                windows = browser.window_handles
                                browser.switch_to.window(windows[-1])
                                browser.execute_script("window.scrollTo(0, 200)")
                                slcr = Selector(text=browser.page_source)
                                if slcr.css('#logisticsTabTitle a').extract_first():
                                    browser.find_element_by_css_selector('#logisticsTabTitle a').click()
                                slct = Selector(text=browser.page_source)

                                if slct.css('.item-list dl:nth-child(3) dd::text').extract_first():
                                    express_id = slct.css(
                                        '.item-list dl:nth-child(3) dd::text').extract_first().strip()
                                    express_name = slct.css(
                                        '.item-list dl:nth-child(2) dd::text').extract_first().strip()
                                else:
                                    express_id, express_name = '', ''

                                if slct.css('.step-detail-header .stress::text').extract_first():
                                    trade_result = slct.css(
                                        '.step-detail-header .stress::text').extract_first().strip()
                                else:
                                    trade_result = ''
                                self.insert_sql(order_id, express_id, trade_result, task_id, express_name)
                                dic['ps_order_id'] = order_id
                                dic['express_id'] = express_id
                                dic['trade_result'] = trade_result
                                dic['task_id'] = task_id
                                dic['express_name'] = express_name
                                print('===', dic, '===')
                                r = requests.post(callback_url, data=dic, headers=self.header)
                                print('post返回:', r.text)
                                print('dic:', dic)
                            except Exception as e:
                                print(e)
                                continue
                            finally:
                                browser.close()
                                browser.switch_to.window(windows[0])
                        else:
                            dic['ps_order_id'] = order_id
                            dic['express_id'] = ''
                            dic['trade_result'] = ''
                            dic['task_id'] = task_id
                            dic['express_name'] = ''
                            r = requests.post(callback_url, data=dic, headers=self.header)
                            print('post返回:', r.text)
                            print('dic:', dic)
                    except Exception as e:
                        print(e)
                        continue
            else:
                pass
            browser.close()


if __name__ == '__main__':
    pd = PackageDetail()
    # pd.get_detail()
    schedule.every(1).second.do(pd.get_detail)
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except:
            continue
