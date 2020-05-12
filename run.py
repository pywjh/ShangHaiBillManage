# -*- coding: utf-8 -*-
# File Name：     main
# Author :        wjh
# date：          2020/5/4

from api.purchase_history import MouthCost
from ShangHai_life_consumpyion_record import *


if __name__ == '__main__':
    record = MouthCost(
        eat_month=eat_month_20_4,
        other_month=other_month_20_4
    )
    record()