from math import ceil
from flask import Flask, render_template, request, redirect
from flask_wtf.csrf import CSRFProtect
from forms import GeoIdForm, Geo2NamesForm, GeoPages, GeoPrompt
from data import GeoData, TimeData, TranslitData, PromptData


app = Flask(__name__)
csrf = CSRFProtect(app)

SECRET_KEY = '1a0b329df51147t0a111335d2acbfd8'
app.config['SECRET_KEY'] = SECRET_KEY

data = GeoData()
timezones = TimeData()
transliterate = TranslitData(data)
prompt = PromptData(data)


@app.route("/", methods=["GET", "POST"])
def main_render():
    msg_error = ''
    first_form = GeoIdForm()
    second_form = GeoPages()
    third_form = Geo2NamesForm()
    fourth_form = GeoPrompt()
    if request.method == "POST":
        if first_form.geoIdSubmit.data and first_form.is_submitted():
            geo_id = first_form.geoId.data
            if data.check_id(geo_id):
                return redirect(f'/get_by_id/{geo_id}')
            else:
                msg_error = 'Данный ID не найден (ID должен быть числом)'
                return render_template("index.html", firstForm=first_form, secondForm=second_form,
                                       thirdForm=third_form, fourthForm=fourth_form, msg_error1=msg_error)
        if second_form.geoPagesSubmit.data and second_form.is_submitted():
            if second_form.validate():
                cities_count = second_form.pageGeoCount.data
                avg_count = second_form.avgGeoCount.data
                index = second_form.geoIndex.data
                return redirect(f'/pagination/avg={avg_count}'
                                f'&cities={cities_count}&index={index}&start={1}')
            else:
                msg_error = 'Введите положительные целые числа'
                return render_template("index.html", firstForm=first_form, secondForm=second_form,
                                       thirdForm=third_form, fourthForm=fourth_form, msg_error2=msg_error)
        if third_form.geo2NamesSubmit.data and third_form.is_submitted():
            name1 = third_form.geoName1.data
            name2 = third_form.geoName2.data
            if transliterate.check_cyrillic(name1):
                name1 = transliterate.try_translit_fullname(name1)
            if transliterate.check_cyrillic(name2):
                name2 = transliterate.try_translit_fullname(name2)
            if data.check_2_names(name1, name2):
                return redirect(f'/get_by_two_names/{name1}&{name2}')
            else:
                msg_error = 'Проверьте введённые города'
                return render_template("index.html", firstForm=first_form, secondForm=second_form,
                                       thirdForm=third_form, fourthForm=fourth_form, msg_error3=msg_error)
        if fourth_form.geoPromptSubmit.data and fourth_form.is_submitted():
            prefix = fourth_form.Prefix.data
            return redirect(f'/prompt/{prefix}')
    else:
        return render_template("index.html", firstForm=first_form, secondForm=second_form, thirdForm=third_form,
                               fourthForm=fourth_form)


@app.route("/get_by_id/<int:geo_id>")
def get_id_render(geo_id):
    if data.check_id(geo_id):
        obj = data.get_by_id(geo_id)
        return render_template("geoId.html", city=obj, id=geo_id)
    else:
        return redirect('/')


@app.route("/pagination/avg=<int:avg_count>&cities=<int:cities_count>&index=<int:index>"
           "&start=<int:start>")
def get_pages_render(avg_count, cities_count, index, start):
    if avg_count == 0 or cities_count == 0:
        return redirect(f'/pagination/avg={avg_count or 1}&cities={cities_count or 1}&index={index}&start={start}')
    if start < 1 or start > avg_count:
        return redirect(f'/pagination/avg={avg_count}&cities={cities_count}&index={index}&start={1}')
    all_ids = data.get_lists_of_id(avg_count - 1, index)
    page_ids = all_ids[start - 1: start - 1 + cities_count]
    page_count = ceil(len(all_ids) / cities_count)
    page_data = {key: data.get_by_id(key) for key in page_ids}
    return render_template("geoPages.html", cities=page_data, cities_count=cities_count,
                           page_count=page_count, index=index, avg=avg_count)


@app.route("/get_by_two_names/<name1>&<name2>")
def get_names_render(name1, name2):
    if transliterate.check_cyrillic(name1):
        name1 = transliterate.try_translit_fullname(name1)
    if transliterate.check_cyrillic(name2):
        name2 = transliterate.try_translit_fullname(name2)
    if data.check_2_names(name1, name2):
        obj1 = data.get_by_name(name1)[0]
        obj2 = data.get_by_name(name2)[0]
        if float(obj1[5]) > float(obj2[5]):
            north = obj1[1]
        elif float(obj1[5]) == float(obj2[5]):
            north = 'Это один и тот же город'
        else:
            north = obj2[1]
        if obj1[17] == obj2[17]:
            timezone = 'Одинаковая'
        else:
            dif = abs(timezones.get_GMT_by_timezone(obj1[17]) -
                      timezones.get_GMT_by_timezone(obj2[17]))
            if dif:
                if dif == 1:
                    end = ''
                elif dif in (2.0, 3.0, 4.0) or dif % 10:
                    end = 'a'
                else:
                    end = 'ов'
                timezone = f'Разная, разница составляет {dif} час{end}'
            else:
                timezone = f'Формально разная, но часовой пояс одинаковый'
        return render_template("geo2names.html", city1=obj1, city2=obj2, name1=name1, name2=name2,
                               north_city_name=north, timezone=timezone)
    else:
        return redirect('/')


@app.route("/prompt/<prefix>")
def get_prompt(prefix):
    prefix = prefix[0].upper() + prefix[1:]
    prompts = prompt.prompt(prefix)
    if prompts:
        return render_template("geoPrompt.html", prompts=prompts, word=prefix)
    else:
        error_msg = "Ничего не найдено"
        return render_template("geoPrompt.html", prompts=[], error_msg=error_msg, word=prefix)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000)
