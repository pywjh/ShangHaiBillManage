import ShangHai_life_consumpyion_record as slcr

def year_cost_record():

    month_records = dir(slcr)

    month_record = list(filter(lambda x: str(x)[0] != '_', month_records))

    for month in month_record:
        if hasattr(slcr, month):
            print(getattr(slcr, month))

if __name__ == '__main__':
    year_cost_record()
    