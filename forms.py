from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, IntegerField, SelectField
from wtforms.validators import InputRequired, DataRequired, NumberRange


class GeoIdForm(FlaskForm):
    geoId = IntegerField('Введите ID объекта', [InputRequired()])
    geoIdSubmit = SubmitField("Найти объект")


class Geo2NamesForm(FlaskForm):
    geoName1 = StringField('Введите название первого объекта', [InputRequired()])
    geoName2 = StringField('Введите название второго объекта', [InputRequired()])
    geo2NamesSubmit = SubmitField("Найти объекты")


class GeoPages(FlaskForm):
    avgGeoCount = IntegerField('Введите общее количество объектов', [DataRequired(), NumberRange(min=1)])
    pageGeoCount = IntegerField('Введите количество объектов на странице', [DataRequired(), NumberRange(min=1)])
    geoIndex = IntegerField('Введите индекс, с которого начать вывод', [DataRequired(), NumberRange(min=1)])
    geoPagesSubmit = SubmitField("Вывести объекты")


class GeoPrompt(FlaskForm):
    Prefix = StringField('Введите префикс названия объекта', [InputRequired()])
    geoPromptSubmit = SubmitField("Вывести возможные названия объектов")


