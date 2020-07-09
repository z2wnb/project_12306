# -*- codeing = utf-8 -*-
# @Time : 2020/7/5 21:47
# @Author : loadding...
# @File : query_ticket.py
# @Software : PyCharm

from lxml import etree
import re
import requests
import prettytable as pt
from selenium import webdriver
import json

# 根据车站名字获取code
def get_station_code(station_name):
    url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9151'
    response = requests.get(url)
    try:
        station_code = re.findall(r'' + station_name + '\|([A-Z]+)', response.text)[0]
    except:
        print('输入车站不存在')
        exit()
    return station_code


def get_station_list(station_info):
    # 构造获取停靠车站信息的url
    url = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=' + station_info[0] + '&from_station_telecode=' + \
          station_info[1] + '&to_station_telecode=' + station_info[2] + '&depart_date=' + station_info[3][:4] + '-' + \
          station_info[3][4:6] + '-' + station_info[3][6:8]
    response = requests.get(url)
    html = json.loads(response.text)
    station_list = []
    for i in html['data']['data']:
        station_list.append(i['station_name'])
    return station_list


# 标准查询
def get_standard_query(src_station_name, dst_station_name, date):
    src_station_code = get_station_code(src_station_name)
    dst_station_code = get_station_code(dst_station_name)
    url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=' + src_station_name + ',' + src_station_code + '&ts=' + dst_station_name + ',' + dst_station_code + '&date=' + date + '&flag=N,N,Y'
    # 创建一个浏览器对象
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # 获取网页源码，动态js执行后的结果与审查元素一样
    page_text = driver.page_source
    tree = etree.HTML(page_text)
    tb = pt.PrettyTable()
    tb.field_names = ['车次', '出发站/到达站', '出发时间/到达时间', '历时', '硬卧/二等卧', '软座', '硬座', '无座']
    # 车次数量,因为一个车次信息包括2个tr（另一个是价格信息）
    number = int(len(tree.xpath('//*[@id="queryLeftTable"]/tr')) / 2)
    for i in range(number):
        tbody = []
        tbody.append(tree.xpath('//*[@id="queryLeftTable"]/tr[' + str(2 * i + 1) + ']/td[1]/div/div[1]/div/a')[0].text)
        tbody.append(tree.xpath('//*[@id="queryLeftTable"]/tr[' + str(2 * i + 1) + ']/td[1]/div/div[2]/strong[1]')[
                         0].text + '/' +
                     tree.xpath('//*[@id="queryLeftTable"]/tr[' + str(2 * i + 1) + ']/td[1]/div/div[2]/strong[2]')[
                         0].text)
        tbody.append(tree.xpath('//*[@id="queryLeftTable"]/tr[' + str(2 * i + 1) + ']/td[1]/div/div[3]/strong[1]')[
                         0].text + '/' +
                     tree.xpath('//*[@id="queryLeftTable"]/tr[' + str(2 * i + 1) + ']/td[1]/div/div[3]/strong[2]')[
                         0].text)
        tbody.append(
            tree.xpath('//*[@id="queryLeftTable"]/tr[' + str(2 * i + 1) + ']/td[1]/div/div[4]/strong')[0].text + '/' +
            tree.xpath('//*[@id="queryLeftTable"]/tr[' + str(2 * i + 1) + ']/td[1]/div/div[4]/span')[0].text)
        tbody.append(tree.xpath('//*[@id="queryLeftTable"]/tr[' + str(2 * i + 1) + ']/td[8]')[0].text)
        tbody.append(tree.xpath('//*[@id="queryLeftTable"]/tr[' + str(2 * i + 1) + ']/td[9]')[0].text)
        tbody.append(tree.xpath('//*[@id="queryLeftTable"]/tr[' + str(2 * i + 1) + ']/td[10]')[0].text)
        tbody.append(tree.xpath('//*[@id="queryLeftTable"]/tr[' + str(2 * i + 1) + ']/td[11]')[0].text)
        tb.add_row(tbody)
    print('------------------------------------------------- Tickets Info ------------------------------------------')
    print(tb)


# 根据出发站、到达站、出发日期、车次返回一个包含余票信息的列表
def get_single_query(src_station_name, dst_station_name, date, train_num):
    src_station_code = get_station_code(src_station_name)
    dst_station_code = get_station_code(dst_station_name)
    url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=' + src_station_name + ',' + src_station_code + '&ts=' + dst_station_name + ',' + dst_station_code + '&date=' + date + '&flag=N,N,Y'
    # 使用无界面模式，不打开浏览器
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    page_text = driver.page_source
    tree = etree.HTML(page_text)
    s = "ticket_.{5,6}" + train_num + ".{2}"
    pattern = re.compile(s)
    # 根据tr的id属性来获取指定车次余票信息
    id = pattern.findall(page_text)[0]
    tbody = []
    tbody.append(tree.xpath('//*[@id="' + id + '"]/td[1]/div/div[1]/div/a')[0].text)
    tbody.append(tree.xpath('//*[@id="' + id + '"]/td[1]/div/div[2]/strong[1]')[
                     0].text + '/' +
                 tree.xpath('//*[@id="' + id + '"]/td[1]/div/div[2]/strong[2]')[
                     0].text)
    tbody.append(tree.xpath('//*[@id="' + id + '"]/td[1]/div/div[3]/strong[1]')[
                     0].text + '/' +
                 tree.xpath('//*[@id="' + id + '"]/td[1]/div/div[3]/strong[2]')[
                     0].text)
    tbody.append(
        tree.xpath('//*[@id="' + id + '"]/td[1]/div/div[4]/strong')[0].text + '/' +
        tree.xpath('//*[@id="' + id + '"]/td[1]/div/div[4]/span')[0].text)
    tbody.append(tree.xpath('//*[@id="' + id + '"]/td[8]')[0].text)
    tbody.append(tree.xpath('//*[@id="' + id + '"]/td[9]')[0].text)
    tbody.append(tree.xpath('//*[@id="' + id + '"]/td[10]')[0].text)
    tbody.append(tree.xpath('//*[@id="' + id + '"]/td[11]')[0].text)
    return tbody


# 根据车次查询
def get_train_query(src_station_name, dst_station_name, date, train_num):
    src_station_code = get_station_code(src_station_name)
    dst_station_code = get_station_code(dst_station_name)
    url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=' + src_station_name + ',' + src_station_code + '&ts=' + dst_station_name + ',' + dst_station_code + '&date=' + date + '&flag=N,N,Y'
    # 创建一个浏览器对象
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    page_text = driver.page_source

    tb = pt.PrettyTable()
    tb.field_names = ['车次', '出发站/到达站', '出发时间/到达时间', '历时', '硬卧/二等卧', '软座', '硬座', '无座']
    tb.align['车次']='1'
    tb.padding_width=1#填充宽度
    # 正则获取停靠站信息
    s = "myStopStation.open\('[0-9]?','(.{5,6}" + train_num + ".{2})','([A-Z]*)','([A-Z]*)','([0-9]{8})'"
    pattern = re.compile(s)
    station_info = pattern.findall(page_text)[0]
    station_list = get_station_list(station_info)
    # 指定乘车区间前后扩大三站范围，范围太大也没有买票的必要了
    # 出发站和到达站的索引
    src_index = station_list.index(src_station_name)
    dst_index = station_list.index(dst_station_name)
    src_list = []  # 考虑的出发站之前的站
    dst_list = []
    # 对出发站的位置进行判断
    if src_index > 2:
        src_list.append(station_list[src_index])
        src_list.append(station_list[src_index - 1])
        src_list.append(station_list[src_index - 2])
        src_list.append(station_list[src_index - 3])
    else:
        for j in range(src_index + 1):
            src_list.append(station_list[j])
    if dst_index < len(station_list) - 2:
        dst_list.append(station_list[dst_index])
        dst_list.append(station_list[dst_index + 1])
        dst_list.append(station_list[dst_index + 2])
        dst_list.append(station_list[dst_index + 3])
    else:
        for j in range(len(station_list) - src_index):
            src_list.append(station_list[j])

    for src in src_list:
        for dst in dst_list:
            result = get_single_query(src, dst, date, train_num)
            tb.add_row(result)
    print(
        '----------------------------------------------------Tickets Info -------------------------------------------')
    print(tb)


def main():
    src_station_name = input('出发站：')
    dst_station_name = input('到达站：')
    date = input('乘车日期（yyyy-mm-dd）：')
    type = input('1、标准查询 2、车次查询\n请选择：')
    if type == '1':
        get_standard_query(src_station_name, dst_station_name, date)
    elif type == '2':
        train_num = input('输入车次：')
        get_train_query(src_station_name, dst_station_name, date, train_num)
    else:
        print('你太笨了，这都能输错!!!')
        exit()
    os.system('pause')

if __name__ == '__main__':
    main()
