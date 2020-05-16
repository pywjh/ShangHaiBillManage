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
from api.config import *

base_dir = os.path.dirname(__file__)


def _read_csv(path, encoding_list=('GBK', 'UTF-8')):
    for endcoding in encoding_list:
        try:
            with open(path, encoding=endcoding) as csv_file:

                reader = csv.DictReader(csv_file)
                return [row for row in reader if row]

        except UnicodeDecodeError:
            print("Not Support This File Encoding!!")
        except FileNotFoundError:
            print('未找到账单文件：{}'.format(path.split('/')[-1]))
        except Exception as e:
            print(e)
    return None


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
        if dt.date.today().day < PAY_SALARY_DAY:
            month = str((dt.date(dt.date.today().year, int(month),
                                day) - relativedelta(months=1)).month)
        else:
            month = str(month)
    else:
        year = year
        month = month
    path = '{}/cost_record/{}_{}.csv'.format(base_dir[:-4], year, month)
    record = _read_csv(path)
    if record:
        record.sort(key=lambda date: datetime(
                    year=int(year),
                    month=int(date['date'].split('_')[0]),
                    day=int(date['date'].split('_')[-1])
                ))
        return record


def manager(year=None, month=None):
    records = get_date(year=year, month=month)
    if records:
        record = MouthCost(record=records, year=year, month=month)
        return record
    return None


if __name__ == '__main__':
    print(manager('2020', '4'))