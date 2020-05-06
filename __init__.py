from flask import Flask, render_template, request
from datetime import datetime, timedelta
import instagram_tools as tools

app = Flask(__name__)


@app.route("/")
def home():
    # if "iPhone" in str(request.headers.get('User-Agent')) or "Android" in str(request.headers.get('User-Agent')):
    #     return render_template("m.index.html")
    return render_template("index.html")


@app.route("/insta_stat.html", methods=['GET', 'POST'])
def insta_stat():
    return render_template("insta_stat.html",
                           mockup_begin_date=datetime.now().date() - timedelta(days=1),
                           mockup_end_date=datetime.now().date())


@app.route("/result.html", methods=['GET', 'POST'])
def insta_stat_result():
    info = tools.get_statistics(str(request.form["input_for_name"]).lower(), str(request.form["input_begin_date"]), str(request.form["input_end_date"]))
    if info["error_code"] > 0:
        return render_template("error.html", acc_name=str(request.form["input_for_name"]).lower())
    return render_template("result.html",
                           avatar_img=info["avatar_url"] if info["avatar_url"] else "../static/img/avatar_alt.png",
                           is_fresh=info["is_fresh"],
                           is_verified=info["is_verified"],
                           acc_name=str(request.form["input_for_name"]).lower(),
                           begin_date=request.form["input_begin_date"],
                           end_date=request.form["input_end_date"],
                           followers_order=tools.get_number_order(info["followed_by_count"]),
                           followers_letter=tools.get_order_letter(info["followed_by_count"]),
                           followers_number='{0:,}'.format(info["followed_by_count"]).replace(',', ' '),
                           followers_word=tools.get_word_form("подписчик", info["followed_by_count"]),
                           media_order=tools.get_number_order(info["media_in_period"]),
                           media_letter=tools.get_order_letter(info["media_in_period"]),
                           media_number='{0:,}'.format(info["media_in_period"]).replace(',', ' '),
                           media_word=tools.get_word_form("пост", info["media_in_period"]),
                           likes_order=tools.get_number_order(info["likes_in_period"]),
                           likes_letter=tools.get_order_letter(info["likes_in_period"]),
                           likes_number='{0:,}'.format(info["likes_in_period"]).replace(',', ' '),
                           likes_word=tools.get_word_form("лайк", info["likes_in_period"]),
                           comments_order=tools.get_number_order(info["comments_in_period"]),
                           comments_letter=tools.get_order_letter(info["comments_in_period"]),
                           comments_number='{0:,}'.format(info["comments_in_period"]).replace(',', ' '),
                           comments_word=tools.get_word_form("комментарий", info["comments_in_period"]),
                           morning_value=info["density"]["morning"],
                           afternoon_value=info["density"]["afternoon"],
                           evening_value=info["density"]["evening"],
                           night_value=info["density"]["night"])


# if __name__ == '__main__':
#     app.run()
