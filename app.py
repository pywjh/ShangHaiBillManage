import os
import json
from datetime import datetime
from werkzeug.utils import redirect
from flask import Flask, render_template, url_for, request, jsonify

from api import draw
from api.get_bill_record import data_aggregation, add_record
from api.bill_manage import MouthCost

app = Flask(__name__)

other_record = MouthCost.read_other_record(os.path.dirname(__file__))


@app.route("/")
@app.route("/index")
def index():
    record, year, month = data_aggregation()
    record = MouthCost(record, year, month)
    status, columns = record.to_table()
    return render_template("index.html",
                           chart_url=url_for('get_current_month_bar'),
                           usage_chart=url_for("get_month_usage"),
                           data=status, columns=columns)


@app.route("/current_month")
def get_current_month_bar():
    """
    首页条形统计图
    :return: Bar
    """
    record, year, month = data_aggregation()
    record = MouthCost(record, year, month)
    x, y = record.web_index_bar()
    bar = draw.draw_balance_bar(xaxis=x, yaxis=y)
    return bar.dump_options()


@app.route("/current_usage")
def get_month_usage():
    """
    首页饼状图
    :return: Pie
    """
    budget = float(MouthCost.current_fix_data(other_record)['budget'])
    record, year, month = data_aggregation()
    record = MouthCost(record, year, month)
    data = record.web_index_pie()
    pie =  draw.draw_usage_pie(payout=data, budget=[('预算', budget)], title="本月结余")
    return pie.dump_options()


@app.route("/details", methods=['GET', 'POST'])
def details():
    name = 'select_month'
    if request.method == 'GET':
        year = 'null'
        month = 'null'
    else:
        month = request.form.get(name) # 获取界面选择的日期
        try:
            t: datetime = datetime.strptime(month, '%Y-%m')
        except ValueError:
            t = datetime.now()
        finally:
            year = t.year
            month = t.month

    return redirect(url_for('get_details', year=year, month=month))


@app.route("/details/year=<year>&month=<month>")
def get_details(year, month):
    name = 'select_month'
    record, year, month = data_aggregation(year, month)
    record = MouthCost(record, year, month)
    data, columns = [], []
    if record:
        data, columns = record.to_detail_table()

    return render_template("details.html",
                           chart_url=url_for('get_bar_chart', year=year, month=month),
                           name=name, data=data, columns=columns)


@app.route("/barChart/year=<year>&month=<month>")
def get_bar_chart(year, month):
    record, year, month = data_aggregation(year, month)
    record = MouthCost(record, year, month)
    if record:
        x, y = record.web_index_bar()
    else:
        x = ['无数据']
        y = []
    bar = draw.draw_balance_bar(xaxis=x, yaxis=y)
    return bar.dump_options()


@app.route("/update", methods=['GET', 'POST'])
def update():
    name = 'select_month'
    if request.method == 'GET':
        year = 'null'
        month = 'null'
    else:
        month = request.form.get(name) # 获取界面选择的日期
        try:
            t: datetime = datetime.strptime(month, '%Y-%m')
        except ValueError:
            t = datetime.now()
        finally:
            year = t.year
            month = t.month
    return redirect(url_for('get_update', year=year, month=month))


@app.route("/update/year=<year>&month=<month>")
def get_update(year, month):
    name = 'select_month'
    record, year, month = data_aggregation(year, month)
    record = MouthCost(record, year, month)
    data, columns = [], []
    if record:
        data, columns = record.to_detail_table(update=True)
    return render_template("update.html",date_f=(year, month),
        year=year,month=month,name=name,data=data,columns=columns,dt=datetime.now())


@app.route('/add', methods=['POST'])
def add_bill():
    params = json.loads(request.data)
    code, message = add_record(params)
    return jsonify({'code': code, 'message': message})


@app.route("/category_statistics", methods=['GET', 'POST'])
def category_statistics():
    name = 'select_month'
    if request.method == 'GET':
        year = 'null'
        month = 'null'
    else:
        month = request.form.get(name) # 获取界面选择的日期
        try:
            t: datetime = datetime.strptime(month, '%Y-%m')
        except ValueError:
            t = datetime.now()
        finally:
            year = t.year
            month = t.month
    return redirect(url_for('get_category', year=year, month=month))


@app.route("/category_statistics/year=<year>&month=<month>")
def get_category(year, month):
    name = 'select_month'
    record, year, month = data_aggregation(year, month)
    record = MouthCost(record, year, month)
    data, columns = record.to_table(category=True)
    return render_template(
        "category.html",
        usage_chart=url_for('get_category_pie', year=year, month=month),
        name=name,
        data=data,
        columns=columns)


@app.route("/PieChart/Category/year=<year>&month=<month>")
def get_category_pie(year, month):
    record, year, month = data_aggregation(year, month)
    record = MouthCost(record, year, month)
    eat, other = record.web_category_pie()
    if year == 'null' or month == 'null':
        year = str(datetime.now().year)
        month = str(datetime.now().month)
    pie = draw.draw_category_pie(
        inner=eat,
        outside=other,
        inner_title=f'{year}年{month}饮食报表',
        outer_title=f'{year}年{month}其他报表')
    return pie.dump_options()


@app.route('/annual', methods=['GET', 'POST'])
def annual():
    name = 'select_month'
    if request.method == 'GET':
        year = 'null'
    else:
        month = request.form.get(name) # 获取界面选择的日期
        try:
            t: datetime = datetime.strptime(month, '%Y-%m')
        except ValueError:
            t = datetime.now()
        finally:
            year = t.year
    return redirect(url_for('annual_with_year', year=year))


@app.route('/annual/year=<year>')
def annual_with_year(year):
    name = 'select_year'

    # status, columns = to_table(api.account_status_per_year(year, prefix="{}年".format(year)))
    return render_template("annual.html", name=name,
                           chart_url=url_for('get_annual_bar', year=year),
                           # pie_url=url_for('get_annual_pie', year=year),
                           # data=status, columns=columns
                           )


@app.route("/barChart/year=<year>")
def get_annual_bar(year):
    record, year, month = data_aggregation()
    record = MouthCost(record, year, month)
    a = 1
    c = api.draw_balance_bar_per_month(year=year)
    return c.dump_options()


if __name__ == "__main__":
    app.run(debug=True, port=8000)
