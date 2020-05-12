from flask import Flask, render_template, url_for

from api.bill_manage import MouthCost
from ShangHai_life_consumpyion_record import *

from api import draw

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", chart_url=url_for('get_current_month_bar'))


@app.route("/current_month")
def get_current_month_bar():
    x = record.x_axis_zh()
    eat_y = record.get_eat_y()
    other_y = record.get_other_y()
    all_y = record.get_all_y()
    y = []
    y.append(('饮食消费', eat_y))
    y.append(('其他消费', other_y))
    y.append(('合计消费', all_y))
    bar = draw.draw_balance_bar(xaxis=x, yaxis=y)
    return bar.dump_options()


if __name__ == "__main__":
    record = MouthCost(
        eat_month=eat_month_20_4,
        other_month=other_month_20_4
    )
    app.run(debug=True, port=8000)
