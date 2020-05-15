# -*- coding: utf-8 -*-
# File Name：     get_date
# Author :        wjh
# date：          2020/5/14

import datetime
from dateutil.relativedelta import relativedelta

import cost_record
from .bill_manage import MouthCost
from .config import *


def get_date(year='null', month='null', day=1):
    """
    这里的逻辑比较个性化：
        因为本人15号发工资，所以做的账单是从15号开始到次月15号结束
        所以直接查看数据时，默认今天的时候会判断日期，15号之前去上个月的账单，之后就取当月的账单
        手动选择的话，就没有逻辑
    :return: Dict
    """
    eat_month_data = {}
    other_month_data = {}
    if  year in ('null', None) or  month in ('null', None):
        year = str(datetime.date.today().year)[2:]
        month = datetime.date.today().month
        if datetime.date.today().day < PAY_SALARY_DAY:
            month = str((datetime.date(datetime.date.today().year, int(month), day) - relativedelta(months=1)).month)
        else:
            month = str(month)
    else:
        year = year[2:]
        month = month
    eat_month = 'eat_month' + '_' + year + '_' + month
    other_month = 'other_month' + '_' + year + '_' + month
    if hasattr(cost_record, eat_month):
        eat_month_data = getattr(cost_record, eat_month)
    if hasattr(cost_record, other_month):
        other_month_data = getattr(cost_record, other_month)
    return eat_month_data, other_month_data


def manager(year=None, month=None):
    eat_month_data, other_month_data = get_date(year=year, month=month)
    if eat_month_data or other_month_data:
        record = MouthCost(
            eat_month=eat_month_data,
            other_month=other_month_data
        )
        return record
    return None