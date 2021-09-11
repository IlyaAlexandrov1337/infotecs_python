from cyrtranslit import to_cyrillic


def is_cyrillic(symbols):
    for symbol in symbols:
        if not (u'\u0400' <= symbol <= u'\u04FF' or u'\u0500' <= symbol <= u'\u052F'):
            return False
        return True


class GeoData:
    def __init__(self):
        data = {}
        mapping = {}
        translit_data = {}
        alter_rus_data = {}
        with open('RU1.txt', 'r', encoding='utf-8') as f:
            for line in f:
                obj = line.split('\t')
                id = int(obj[0])
                data[id] = obj
                name = obj[1]
                if mapping.get(name):
                    mapping[name].append(id)
                else:
                    mapping[name] = [id]
                translit_data[to_cyrillic(name, "ru")] = name
                alter_names = obj[3].split(",")
                for alter_name in alter_names:
                    if is_cyrillic(alter_name):
                        if alter_rus_data.get(alter_name):
                            alter_rus_data[alter_name].add(name)
                        else:
                            alter_rus_data[alter_name] = set([name])
        self._data = data
        self._name_to_id = mapping
        self._translit_data = translit_data
        self._alter_rus_data = alter_rus_data

    def check_id(self, id):
        if id in self._data:
            return True
        else:
            return False

    def get_by_id(self, id):
        if self.check_id(id):
            return self._data[id]
        else:
            return None

    def get_lists_of_id(self, avg, id):
        lst = list(self._data.keys())
        index = min(enumerate(lst), key=lambda x: abs(id - x[1]))[0]
        if len(lst[index:]) < avg:
            lst = lst[index:]
        else:
            lst = lst[index: index + avg + 1]
        return lst

    def check_2_names(self, name1, name2):
        ids1 = self._name_to_id.get(name1)
        ids2 = self._name_to_id.get(name2)
        if ids1 and ids2:
            return True
        else:
            return False

    def get_by_name(self, name):
        ids = self._name_to_id.get(name)
        if not ids:
            return None
        mx = -1
        for id in ids:
            population = int(self.get_by_id(id)[14])
            if population > mx:
                mx = population
                true_id = id
        return self.get_by_id(true_id), mx


class TimeData:
    def __init__(self):
        data = {}
        with open('timeZones.txt', 'r', encoding='utf-8') as f:
            next(f)
            for line in f:
                obj = line.split('\t')
                gmt = float(obj[2])
                data[obj[1]] = gmt
        self._data = data

    def check_timezone(self, timezone):
        if timezone in self._data:
            return True
        else:
            return False

    def get_GMT_by_timezone(self, timezone):
        if self.check_timezone(timezone):
            return self._data[timezone]
        else:
            return None


class TranslitData:
    def __init__(self, geodata):
        self._geodata = geodata

    @staticmethod
    def check_cyrillic(word):
        return is_cyrillic(word)


    def try_translit_fullname(self, word):
        if not is_cyrillic(word):
            return None
        if self._geodata._alter_rus_data.get(word):
            indexes = []
            for element in self._geodata._alter_rus_data[word]:
                indexes.append(self._geodata.get_by_name(element))
            indexes.sort(key=lambda x: x[1], reverse=True)
            return indexes[0][0][1]
        if self._geodata._translit_data.get(word):
            return self._geodata._translit_data.get(word)
        return None


class PromptData:
    def __init__(self, geodata):
        data = {}
        alter_data = {}
        translit_data = {}
        for name in geodata._name_to_id.keys():
            for index in range(len(name)):
                prefix = name[:index]
                if data.get(prefix):
                    data[prefix].append(name)
                else:
                    data[prefix] = [name]
        for name in geodata._alter_rus_data.keys():
            for index in range(len(name)):
                prefix = name[:index]
                if alter_data.get(prefix):
                    alter_data[prefix].append(name)
                else:
                    alter_data[prefix] = [name]
        for name in geodata._translit_data.keys():
            for index in range(len(name)):
                prefix = name[:index]
                if translit_data.get(prefix):
                    translit_data[prefix].append(name)
                else:
                    translit_data[prefix] = [name]
        self._data = data
        self._alter_data = alter_data
        self._translit_data = translit_data

    def prompt(self, prefix):
        if is_cyrillic(prefix):
            if prefix in self._alter_data:
                return self._alter_data[prefix]
            elif prefix in self._translit_data:
                return self._translit_data[prefix]
            else:
                return None
        if prefix in self._data:
            return self._data[prefix]
        else:
            return None
