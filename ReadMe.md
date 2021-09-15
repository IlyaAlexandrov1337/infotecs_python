# Общее описание
Решение содержит набор html-страниц, конструируемых шаблонизатором, файл с названиями всех установленных библиотек requirements.txt, базы данных RU.txt и timeZones.txt и три .py файла: data.py (пользовательские классы для работы с данными), forms.py (формы) и app.py (обработка представлений). Запускаемы скрипт -- файл app.py  
**Также данное решение задеплоено на heroku, но с урезанной базой данных RU.txt (первые 119755 строчек) в виду ограничений платформы. Ссылка: ***https://infotecs-python.herokuapp.com/*****
# Описание .py файлов
В дальнейшем под id имеется в виду значение из 1-го столбца (geonameid ) базы данных RU.txt, а под name -- значение 2-го столбца (name) базы данных RU.txt.
## data.py, пользовательские классы для работы с данными

### Функция is_cyrillic(s) из модуля cyrtranslit:
Возвращает True, если есть хотя бы один символ из кириллицы в строке S. Иначе возвращает False

### Функция to_cyrillic(s) из модуля cyrtranslit:
Осуществляет транслитерацию строки S с английского на русский. 

### Класс GeoData:
При инициализации создаются атрибуты, используемые методами этого класса, класса TranslitData и класса PromptData.
- self._data --- словарь, где ключ -- id, а значение -- все данные в виде списка, соответствующие этому id (в том числе и сам id)
- self._name_to_id --- словарь, где ключ -- name, а значение -- список id тех объектов, у которых name соответствует ключу
- self._translit_data --- словарь, где ключ -- протранслитерированный name, а значение -- name
- self._alter_rus_data --- словарь, где ключ -- имя на РУССКОМ языке из 4-го столбца (alternatenames) базы данных RU.txt, а значение -- множество name'ов, соответствующих имени на русском языке

#### Метод check_id(self, id):
Возвращает True, если id есть в self._data.keys(), иначе возвращает False

#### Метод get_by_id(self, id):
Возвращает self._data[id], иначе возвращает None

#### Метод get_lists_of_id(self, avg, start_id):
Возвращает список id длиной avg (или меньший максимум, если пытаемся взять id, превышающий максимальный), начиная с id = start_id. 

#### Метод check_2_names(self, name1, name2):
Возвращает True, если name1 и name2 принимают значение из столбца name, иначе возвращает False

#### Метод get_by_name(self, only_name):
Возвращает кортеж (self.get_by_id(true_id), mx), где true_id -- id объекта с именем only_name, имеющего максимальное население mx (столбец population базы данных RU.txt), иначе возвращает None

### Класс TimeData:
При инициализации создаются атрибут, используемый только в рамках этого класса.

- self._data --- словарь, где ключ -- значение столбца timezone базы данных RU.txt, а значение -- соответствующее ключу значение GMT из базы данных timeZones.txt

#### Метод check_timezone(self, timezone):
Возвращает True, если id есть в self._data.keys(), иначе возвращает False

#### Метод get_GMT_by_timezone(self, timezone):
Возвращает GMT по значению timezone, иначе возвращает None

### Класс TranslitData:
При инициализации создаются атрибуты, которые ссылаются на атрибуты объекта класса GeoData.

- self._geodata -- объект класса GeoData
#### Метод check_cyrillic(word):
Возвращает is_cyrillic(word).


#### Метод try_translit_fullname(self, word):
Если word на латинице или его не содержится в ключах self._geodata_alter_rus_data и self._geodata._translit_data, возвращает None. Иначе возвращает self._geodata_alter_rus_data[word], если его нет, то возвращает self._geodata._translit_data[word].

### Класс PromptData:
При инициализации создаются атрибуты, которые опираются на атрибуты объекта класса GeoData.

- self._data – словарь всевозможных префиксов всех ключей атрибута-словаря ._name_to_id объекта класса GeoData
- self.alter_data – словарь всевозможных префиксов всех ключей атрибута-словаря ._alter_rus_data объекта класса GeoData
- self._data – словарь всевозможных префиксов всех ключей атрибута-словаря ._translit_data объекта класса GeoData

#### Метод prompt(self, prefix):
Если prefix содержится в одном из атрибутов self, возвращает список всех имён, в которых содержится prefix, иначе возвращает None.

## forms.py, формы 
Содержит все классы форм, используемых на главном роуте '/'

## app.py, обработка представлений

### Роут '/'
Содержит формы отправки данных для каждого из роутов:
- /get_by_id/<int:geo_id>
- /pagination/avg=<int:avg_count>&cities=<int:cities_count>&index=<int:index>&start=<int:start>
- /get_by_two_names/<name1>&<name2>
- /prompt/<prefix>

Помимо валидации на роутах, в формах также реализована дополнительная валидация. Это необходимо, если использовать GUI как интерфейс взаимодействия с сервером.

### Роут '/get_by_id/<int:geo_id>'
На этом роуте реализован метод, принимающий идентификатор id и возвращающий информацию о городе. В случае некорректного id, перенаправляет на главный роут '/'

### Роут '/pagination/avg=<int:avg_count>&cities=<int:cities_count>&index=<int:index>&start=<int:start>'
На этом роуте реализован метод, принимающий начальный идентификатор start, общее количество объектов avg_count и количество объектов на странице cities_count. Роут возвращает набор страниц. В случае некорректных параметров автоматически их исправляет.

### Роут '/get_by_two_names/<name1>&<name2>'
На этом роуте реализован метод, принимающий названия двух городов и получает информацию о найденных городах. В случае ввода названия(-ий) происходит транслитерация на латиницу двумя способами (поиском русского названия в столбце alternatenames и "настоящей" транслитирацией с помощью модуля cyrtranslit). В случае отсутсвия названий в БД, перенаправляет на главный роут '/'. Также реализовано дополнительное задание по показу численного различия временных зон.

### Роут '/prompt/<prefix>'
На этом роуте реализован дополнительный метод, в котором пользователь вводит префикс названия города и ему возвращается подсказка с возможными вариантами продолжений. Вводимый префикс может быть как на латинице, так и на кириллице.

