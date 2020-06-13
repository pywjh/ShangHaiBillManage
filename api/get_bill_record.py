# -*- coding: utf-8 -*-
# File Name：     get_date
# Author :        wjh
# date：          2020/5/14

import os
import csv
import datetime as dt

from dateutil.relativedelta import relativedelta
from datetime import datetime

from api.bill_manage import MouthCost

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


def get_all_eat_other_record(year):
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
        {'name': f'{year}年支出金额', 'balance': round(month_total, 2)},
        {'name': f'{year}年饮食金额', 'balance': round(eat_total, 2)},
        {'name': f'{year}年其他金额', 'balance': round(other_total, 2)},
        {'name': f'{year}年租房金额', 'balance': round(rent_total, 2)},
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

if __name__ == '__main__':
    # annual('2020')
    pass