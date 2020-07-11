# -*- coding: utf-8 -*-
# File Name：     get_date
# Author :        wjh
# date：          2020/5/14

import os
import re

from datetime import datetime
from flask import jsonify

from api.bill_manage import MouthCost
from setting import *

base_dir = os.path.dirname(__file__)
other_record = MouthCost.read_other_record(base_dir[:-4])


def get_date(year='null', month='null', default=None):
    """
    :return: Dict
    """
    year, month = MouthCost.get_special_date(year=year, month=month,
                                             default=default)
    path = f'{base_dir[:-4]}/cost_record/{year}/{year}_{month}.csv'
    record = MouthCost._read_csv(path)
    if record:
        record.sort(key=lambda date: datetime(
                    year=int(year),
                    month=int(date['date'].split('_')[0]),
                    day=int(date['date'].split('_')[-1])
                ))
        return record


def data_aggregation(year=None, month=None, default=None):
    """数据汇总"""
    if year == 'null' or month == 'null':
        default = True
    records = get_date(year=year, month=month, default=default)
    return records, year, month


def add_record(params):
    try:
        date = params.get('date')
        name = params.get('name')
        payment = params.get('payment')
        type = params.get('type')
        note = params.get('note')
        year, month = eval(params.get('date_f'))
        month = date.split('_')[0]
        day = date.split('_')[-1]
        year, month = MouthCost.get_special_date(
            year=year,
            month=month,
            day=day,
            default=True,
        )
        path = f'{base_dir[:-4]}/cost_record/{year}/{year}_{month}.csv'
        content = f'\n{date},{name},{payment},{type},{note}'
        # csv文件每两行中间都有一行空白行，解决办法就是写入后面加上newline=''
        with open(path, 'a+', encoding='GBK', newline='') as csv_file:
            csv_file.write(content)
        return (0, '新增成功！')
    except Exception as e:
        return (1, e)


def get_all_eat_other_record(year) -> tuple:
    """将指定年分的12个月的饮食和其他消费类别总计汇总"""
    eat_list = []
    other_list = []
    months = [month for month in range(1, 13)]
    for month in months: # 将整年的所有饮食和其他消费合并
        record, year, month = data_aggregation(year=year, month=month)
        if record:
            manage = MouthCost(record, year, month)
            eat_cost, other_cost = manage.web_category_pie()
            eat_list.append(eat_cost)
            other_list.append(other_cost)
    return eat_list, other_list


def get_all_eat_other_sum_amount(eat_list, other_list):
    """将12个月的饮食和其他消费，相同的消费类别合并在一起"""
    eat_dict = {}
    other_dict = {}
    # 将饮食类的消费合并
    for eat in eat_list:
        for name, amount in eat:
            if name in eat_dict:
                eat_dict[name] = round(amount + eat_dict[name], 2)
            else:
                eat_dict[name] = amount
    # 将其他类的消费合并
    for other in other_list:
        for name, amount in other:
            if name in other_dict:
                other_dict[name] = round(amount + other_dict[name], 2)
            else:
                other_dict[name] = amount
    eat = sorted(
        [eat for eat in eat_dict.items()],
        key=lambda t: t[1], reverse=True)
    other = sorted(
        [other for other in other_dict.items()],
        key=lambda t: t[1], reverse=True)
    return eat, other


def get_data_columns(year):
    month_total = 0
    eat_total = 0
    other_total = 0
    salary_total = 0
    rent_total = 0
    salary_list = []
    months = [month for month in range(1, 13)]
    for month in months:  # 将整年的所有饮食和其他消费合并
        record, year, month = data_aggregation(year=year, month=month)
        if record:
            manage = MouthCost(record, year, month)

            salary_list = manage.other_record
            # 吃穿总计
            month_total += manage.all_total()
            salary_info = list(filter(lambda d: d['date']==f"{year}_"
            f"{month}", salary_list))
            # 再加上房租
            if salary_info:
                month_total += float(salary_info[0].get('rent', 0))

            eat_total += sum(manage.get_eat_y())
            other_total += sum(manage.get_other_y())

    for salary in salary_list:
        salary_total += eval(salary.get('salary', 0))
        rent_total += eval(salary.get('rent', 0))

    rest_total = round(salary_total - month_total, 2)

    status = [
        {'name': f'{year}年收入金额', 'balance': round(salary_total, 2)},
        {'name': f'{year}年饮食金额', 'balance': round(eat_total, 2)},
        {'name': f'{year}年其他金额', 'balance': round(other_total, 2)},
        {'name': f'{year}年吃穿金额', 'balance': round(eat_total + other_total, 2)},
        {'name': f'{year}年租房金额', 'balance': round(rent_total, 2)},
        {'name': f'{year}年支出金额', 'balance': round(month_total, 2)},
        {
            'name': f'{year}年盈亏金额',
            'balance': f"{rest_total}" if rest_total > 0 else f""
            f"-{rest_total}"},
    ]
    columns = [
        {
            "field": "name",  # which is the field's name of data key
            "title": "名称",  # display as the table header's name
            "sortable": False,
        },
        {
            "field": "balance",
            "title": "金额 (元)",
            "sortable": False,
        },
    ]
    return status, columns


def web_statistical_bar():
    """总统计"""
    y_amount = [('支出', []), ('收入', [])]
    year_list = os.listdir(os.path.join(base_dir[:-4], 'cost_record'))
    for year in year_list:
        if not re.search(r"^\d{4}$", year):
            year_list.pop(year_list.index(year))
    for year in year_list:
        status, _ = get_data_columns(year)
        y_amount[0][1].append(list(filter(lambda d: '支出' in d['name'], status))[0]['balance'])
        y_amount[1][1].append(list(filter(lambda d: '收入' in d['name'], status))[0]['balance'])

    return year_list, y_amount


def web_statistical_line():
    """年度结余"""
    year_list, y_amount = web_statistical_bar()
    y = [('结余', [])]
    for pay, salary in zip(y_amount[0][1], y_amount[1][1]):
        y[0][1].append(round(salary - pay, 2))
    return year_list, y


def account_from_start_to_now():
    """剩余资产"""
    year_list, y = web_statistical_line()
    return round(sum(y[0][1]), 2)


def search_key(word, year=None):
    all_record = []
    if year:
        if os.path.exists(os.path.join(base_dir[:-4], f"cost_record/{year}")):
            months = [month for month in range(1, 13)]
            for month in months:  # 将整年的所有饮食和其他消费合并
                record, year, month = data_aggregation(year=year, month=month)
                if record:
                    all_record += record
                    if len(all_record) > 10000:
                        break
    else:
        cost_record_path = os.path.join(base_dir[:-4], f"cost_record/")
        year_list = os.listdir(cost_record_path)
        for year in filter(lambda l: '.csv' not in l, year_list):
            for month in [file[5:-4] for file in  os.listdir(os.path.join(cost_record_path, year))]:
                record, year, month = data_aggregation(year=year, month=month)
                if record:
                    all_record += record
                    if len(all_record) > 10000:
                        break

    search_result = filter(lambda d: word==d['name'] or word in d['name'] or word in (d['note'] or ''), all_record)

    data = [
            {
                'date': f'{year}年{i["date"].split("_")[0]}月{i["date"].split("_")[1]}日',
                'name': i['name'],
                'payment': i['payment'],
                'type': '饮食' if i['type'] == 'eat' else '其他',
                'note': i['note']
            }
        for i in sorted(search_result, key=lambda d: datetime(
                year=int(year),
                month=int(d['date'].split('_')[0]),
                day=int(d['date'].split('_')[-1])
            ))
    ]

    columns = [
        {
            "field": "date",  # which is the field's name of data key
            "title": "日期",  # display as the table header's name
            "sortable": False,
        },
        {
            "field": "name",
            "title": "用途",
            "sortable": False,
        },
        {
            "field": "payment",
            "title": "金额（元）",
            "sortable": False,
        },
        {
            "field": "type",
            "title": "类型",
            "sortable": False,
        },
        {
            "field": "note",
            "title": "备注",
            "sortable": False,
        },
    ]
    return data, columns

if __name__ == '__main__':
    # annual('2020')
    print(account_from_start_to_now())