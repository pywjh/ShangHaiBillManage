# -*- coding: utf-8 -*-
# File Name：     auto_create_cost_record
# Author :        wjh
# date：          2020/6/11
import os
import datetime


def exist_filter(year):
    year = str(year)
    file_name_list = [f"{year}_{month}.csv" for month in range(1, 13)]
    for file_name in file_name_list:
        if not os.path.exists(file_name):
            with open(file_name, 'w', encoding='GBK') as f:
                f.write('date,name,payment,type,note\n')
        print(f"{file_name}已存在")


if __name__ == '__main__':
    current_year = datetime.date.today().year
    base_path = os.path.dirname(__file__)
    path = base_path + f'/cost_record/{current_year}'
    if os.path.exists(path):
        os.chdir(path)
    exist_filter(current_year)


