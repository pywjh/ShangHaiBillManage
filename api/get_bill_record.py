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


def get_date(year='null', month='null', day=1):
    """
    这里的逻辑比较个性化：
        因为本人15号发工资，所以做的账单是从15号开始到次月15号结束
        所以直接查看数据时，默认今天的时候会判断日期，15号之前去上个月的账单，之后就取当月的账单
        手动选择的话，就没有逻辑
    :return: Dict
    """
    if  year in ('null', None) or  month in ('null', None):
        year = str(dt.date.today().year)
        month = dt.date.today().month
        current_fix_data = MouthCost.current_fix_data(other_record)
        if dt.date.today().day < int(current_fix_data['salary_day']):
            month = str((dt.date(dt.date.today().year, int(month),
                                day) - relativedelta(months=1)).month)
        else:
            month = str(month)
    else:
        year = year
        month = month
    path = '{}/cost_record/{}_{}.csv'.format(base_dir[:-4], year, month)
    record = MouthCost._read_csv(path)
    if record:
        record.sort(key=lambda date: datetime(
                    year=int(year),
                    month=int(date['date'].split('_')[0]),
                    day=int(date['date'].split('_')[-1])
                ))
        return record


def data_aggregation(year=None, month=None):
    """数据汇总"""
    records = get_date(year=year, month=month)
    return records, year, month


def add_record(params):
    try:
        date = params.get('date')
        name = params.get('name')
        payment = params.get('payment')
        type = params.get('type')
        note = params.get('note')
        year, month = eval(params.get('date_f'))
        if year == 'null' and month == 'null':
            year = datetime.now().year
            month = datetime.now().month
        path = '{}/cost_record/{}_{}.csv'.format(base_dir[:-4], year, month)
        content = f'\n{date},{name},{payment},{type},{note}'
        # csv文件每两行中间都有一行空白行，解决办法就是写入后面加上newline=''
        with open(path, 'a+', encoding='GBK', newline='') as csv_file:
            csv_file.write(content)
        return (0, '新增成功！')
    except Exception as e:
        return (1, e)


def annual(year):
    """
    年度统计数据汇总
    :return x_date x轴  y轴工资  cost_list 总消费列表
    """
    salary_path = '{}/cost_record/other_record.csv'.format(base_dir[:-4])
    salary_result = _read_csv(salary_path)

    x_date = [f"{row['date'].split('_')[0]}年{row['date'].split('_')[1]}月" for row in salary_result if row]
    y_salary = []
    y_salary.append(('收入', [eval(row['salary']) for row in salary_result if row]))

    csv_files = os.listdir('{}/cost_record'.format(base_dir[:-4]))
    csv_files = filter(lambda l: year in l, csv_files)

    cost_list = []
    for file in csv_files:
        cost_path = '{}/cost_record/{}'.format(base_dir[:-4], file)
        cost_list.append(_read_csv(cost_path))
    return x_date, y_salary, cost_list, csv_files


if __name__ == '__main__':
    annual('2020')