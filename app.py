import json
from datetime import datetime
from werkzeug.utils import redirect
from flask import Flask, render_template, url_for, request, jsonify

from api import draw
from api.get_bill_record import manager, add_record

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    record = manager()
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
    record = manager()
    x, y = record.web_index_bar()
    bar = draw.draw_balance_bar(xaxis=x, yaxis=y)
    return bar.dump_options()


@app.route("/current_usage")
def get_month_usage():
    """
    首页饼状图
    :return: Pie
    """
    record = manager()
    pie = record.web_index_pie()
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
    record = manager(year, month)
    data, columns = [], []
    if record:
        data, columns = record.to_detail_table()

    return render_template("details.html",
                           chart_url=url_for('get_bar_chart', year=year, month=month),
                           name=name, data=data, columns=columns)


@app.route("/barChart/year=<year>&month=<month>")
def get_bar_chart(year, month):
    record = manager(year, month)
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
    record = manager(year, month)
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


if __name__ == "__main__":
    app.run(debug=True, port=8000)
