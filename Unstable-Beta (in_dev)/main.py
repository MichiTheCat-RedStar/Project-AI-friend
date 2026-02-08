# Импорт библиотек
print('Импортирвоание библиотек...')
import ollama
import json
import os
from datetime import datetime
from time import sleep, time
import requests
import wikipedia
from bs4 import BeautifulSoup
import search_web
from websearch import WebSearch
log_dir = None # Нужно, дабы не создавалось сто лог-файлов, а всё было в том, с которого всё началось
print('импортрование библиотек завершено')


# НАСТРОЙКИ
CPU = 4         # Количество используемых ядер процессора                               |   По стандарту 4, но просто поделите количество своих ядер на два
CW = 8192       # Размер максимальной длины ответа                                      |   По стандарту 8192, но можете сократить до значения, кратного степени двух для более короткого ответа
LOOPS = 10      # Сколько раз ИИ может вызывать повторно инструменты при нужде          |   По стандарту 5 (10 в новой версии), но можете уменьшить, если ИИ много думает напрасно
NEW = False     # Не загружать историю чата и каждый запуск начинать с нуля?            |   По станарту False, но можете отключить, чтобы история чата не загружалась и не сохранялась
LOG = True      # Сохранять в логи сами логи?                                           |   По стандарту True, но если вам не нужны логи, то можно выключить
MODS = True     # Активирует поддержку модов                                            |   По стандарту True, но если вам не нужны моды, то можно выключить
VL = True       # Включить визуальную модель                                            |   По стандарту True, но если у вас нет визуальной модели, то лучше выключить
KA = 20         # Сколько секунд после ответа модель будет в памяти                     |   По стандарту 20 секунд, но если вам нужна оперативная память между ответами модели, то ставьте на 0, а при фокусированном общении с ИИ - наоборот ставьте больше, чтобы каждый раз снова не загружать ИИ в память
WS = True       # Позволяет ассистенту открыть вкладку в браузере с запросом            |   По стандарту True, но если не нужна работа с браузером, то ставьте False


# Загрузка из файлов
print('Загрузка из файлов...')
try:
    with open("Settings/model.txt", "r", encoding="UTF-8") as f:
        f = f.read()
        MODEL = (f.split("\n"))[1]
        print('Используемая модель:', MODEL)
except: print('Ошибка загрузки модели! Проверьте "Settings/model.txt"')
try:
    with open("Settings/prompt.txt", "r", encoding="UTF-8") as f:
        PROMPT = f.read()
        print(f'Используемый промпт: {PROMPT.split("\n")[0]}')
except: print('Ошибка загрузки промпта! Проверьте "Settings/prompt.txt"')
print('Загрузка данных из файлов завершена')


# Функции
def get_time(): # Вернуть время в формате {часов:минут дней.месяцев.лет}
    now = datetime.now()
    return f"{now.hour:02d}:{now.minute:02d} {now.day:02d}.{now.month:02d}.{now.year}"

def loging(role='None', text=str): # Добавить в логи событие
    if LOG:
        global log_dir
        now = datetime.now()
        if log_dir:
            with open(log_dir, 'a', encoding='UTF-8') as f:
                f.write(f'<{now.hour:02d}:{now.minute:02d}:{now.second:02d} {now.day:02d}.{now.month:02d}.{now.year}>\n<{role}> {text}\n\n')
        else:
            log_dir = f'Logs/session_{now.year}Y-{now.month:02d}M-{now.day:02d}D_{now.hour:02d}h-{now.minute:02d}m-{now.second:02d}s.txt'
            with open(log_dir, 'a', encoding='UTF-8') as f:
                f.write(f'<{now.hour:02d}:{now.minute:02d}:{now.second:02d} {now.day:02d}.{now.month:02d}.{now.year}>\n<{role}> {text}\n\n')
loging('Система', f'Загружены функции и создан лог-файл\n{CPU=}\n{CW=}\n{LOOPS=}\n{NEW=}\n{LOG=}\n{MODS=}\n{VL=}\n{KA=}\n{WS=}')


# Инструменты для ИИ
def show_files(): # Показать все файлы в AI files
    return f'Вот все файлы в рабочем пространстве: {os.listdir("./AI files")}'

def read_file(file_name=str): # Прочитать файл
    try:
        with open("AI files/"+file_name, "r", encoding="UTF-8") as f:
            return f'Вот текст из файла "{file_name}":\n{f.read()}'
    except:
        return "Ошибка."
    
def write_file(file_name=str, content=''): # Создать файл
    try:
        with open("AI files/"+file_name, "w", encoding="UTF-8") as f:
            f.write(content)
            return f'Создан файл "{file_name}" с текстом "{content}".'
    except:
        return "Ошибка."
    
def wiki_search(title=str): # Поиск в соепедии
    wikipedia.set_lang("ru")
    try:
        result = wikipedia.summary(title, sentences=10)
        return result[:1024]
    except:
        return 'Ошибка. Вероятно страница не найдена.'
    
def web_search(search=str, link=bool): # Поиск в интернет   # TODO ПЕРЕДЕЛАТЬ
    try:
        if not link:
            result = 'Найдено: '
            for page in WebSearch(search).pages[:10]:
                print(page)
                result += f'< {page} >; '
            if result == 'Найдено: ': result = 'Похоже ничего не найдено'
        else: # можно проще сделать, но я перепишу, когда полностью буду переписывать веб-поиск
            response = requests.get({search}, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            soup = soup.get_text()
            result = soup.replace('\n', ' ')
    except Exception as e:
        result = f'Ошибка: {e}'
    return result[:512]


def get_processes(): # Запущенные процессы
    out = ''
    result = os.popen('tasklist').read()
    result = result.split('\n')
    for line in result:
        word = line.split(' ')
        try:
            out += f'{word[0]} {word[1]} {word[2]} {word[3]}'
        except: pass
    out = out.split(' ')
    out = out[14:]
    out = filter(bool, out)
    out = list(set(out))
    out = ' '.join(out)
    return f'Вот все процессы: {out}'
loging('Система', 'Загружены инструменты')


# tools для ИИ
tools = [
    {   "type": "function",
        "function": {
            "name": "show_files",
            "description": "Показывает все файлы в рабочем пространстве - используется чтобы узнать какие есть файлы в доступной тебе директории вместе с расширениями",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []}}
    },
    {   "type": "function",
        "function": {
            "name": "read_file", 
            "description": "Прочитать указанный файл из рабочего пространства с учётом расширения",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "Имя файла для чтения вместе с расширением, например 'notes.txt'"}},
                "required": ["file_name"]}}
    },
    {   "type": "function", 
        "function": {
            "name": "write_file",
            "description": "Записать файл в рабочее пространство с учётом расширения и контента внутри",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "Имя файла для записи вместе с расширением, например 'output.py'"},
                    "content": {
                        "type": "string",
                        "description": "Содержимое файла, например 'print(\"Hello World!\")'"}},
                "required": ["file_name", "content"]}}
    },
    {   "type": "function", 
        "function": {
            "name": "wiki_search",
            "description": "Парсинг Wikipedia по запросу страницы, выдаёт первые 10 предложений",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Название страницы"}},
                "required": ["title"]}}
    },
    {   "type": "function", # TODO Перепиши это ради боба, я уже не могу [ВОТ НЕПРУХА]
        "function": {
            "name": "web_search",
            "description": "Для поиска информации о чём-то лучше использовать wiki_search\nДанная функция является очень нестабильной!\nИскать что-то в интернете по названию или ссылке",
            "parameters": {
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Прямая ссылка или тема для поиска в интернете"},
                    "link": {
                        "type": "boolean",
                        "description": "Поиск по теме, но если ложно - по прямой ссылке"}},
                "required": ["search", "link"]}}
    },
    {   "type": "function",
        "function": {
            "name": "get_processes",
            "description": "Показывает запущенные процессы на компьютере на данный момент",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []}}
    }
]
loging('Система', 'Загружены tools для ИИ')


# Работа с изображениями
if VL:
    print('Загрузка работы с изображениями...')
    try:
        with open("Settings/model.txt", "r", encoding="UTF-8") as f:
            f = f.read()
            vl_model = (f.split("\n"))[4]
            print('Используемая визуальная модель:', vl_model)

        def photo_analysis(file_name=str):
            global CPU
            response = ollama.chat(model=vl_model, messages=[{'role': 'user', 'content': 'У тебя ограничение на 1024 символа'}, {'role': 'user', 'content': 'Кратко проанализируй изображение и опиши его', 'images': [f'AI files/{file_name}']}], options={'num_thread': CPU, 'num_predict': 1024})
            return ('Описание: '+response['message']['content'])
        
        tools.append(
        {   "type": "function", 
            "function": {
                "name": "photo_analysis",
                "description": "Анализирует изображения, используя внешнюю модель, если указать название файла",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {
                            "type": "string",
                            "description": "Название файла-изображения"}},
                    "required": ["file_name"]}}})
        print('Загрузка работы с изображениями завершена')
        loging('Система', 'Загружена работа с изображениями')
    except:
        print('Ошибка загрузки работы с изображениями! Проверьте "Settings/model.txt"')
        loging('Система', 'Ошибка загрузки работы с изображениями')


# Работа с search_web библиотекой
if WS:
    print('Загрузка работы с браузерными запросами...')
    def open_browser(website=str, text=str):
        website = website.lower()
        if website == 'google': search_web.google_search(text); return f'Успешно открыт Google с запросом "{text}"'
        elif website == 'youtube': search_web.youtube_search(text); return f'Успешно открыт Youtube с запросом "{text}"'
        elif website == 'github': search_web.github_search(text); return f'Успешно открыт GitHub с запросом "{text}"'
        elif website == 'amazon': search_web.amazon_search(text); return f'Успешно открыт Amazon с запросом "{text}"'
        elif website == 'cnn': search_web.cnn_search(text); return f'Успешно открыт CNN с запросом "{text}"'
        elif website == 'medicalnewstoday': search_web.medicalnewstoday_search(text); return f'Успешно открыт Medical News Today с запросом "{text}"'
        elif website == 'python': search_web.python_search(text); return f'Успешно открыт Python с запросом "{text}"'
        elif website == 'pinterest': search_web.pinterest_search(text); return f'Успешно открыт Pinterest с запросом "{text}"'
        elif website == 'playstore': search_web.playstore_search(text); return f'Успешно открыт Playstore с запросом "{text}"'
        elif website == 'nytimes': search_web.nytimes_search(text); return f'Успешно открыт New York Times с запросом "{text}"'
        elif website == 'mapquest': search_web.mapquest_search(text); return f'Успешно открыт MapQuest с запросом "{text}"'
        else:  return f'Ничего не открыто, нет такого сайта в списке функции!'
    tools.append(
    {   "type": "function", 
        "function": {
            "name": "open_browser",
            "description": "Открывает пользователю браузер с конкретным запросом на конкретном сайте",
            "parameters": {
                "type": "object",
                "properties": {
                    "website": {
                        "type": "string",
                        "description": "Называние сайта из возможных:\n'google' - Google,\n'youtube' - Youtube,\n'github' - GitHub,\n'amazon' - Amazon,\n'cnn' - CNN,\n'medicalnewstoday' - Medical News Today,\n'python' - Python,\n'pinterest' - Pinterest,\n'playstore' - Playstore,\n'nytimes' - New York Times,\n'mapquest' - MapQuest"},
                    "text": {
                        "type": "string",
                        "description": "Что конкретно будет вбито в поисковую строку на этом сайте"}},
                "required": ["website", "text"]}}})
    print('Загрузка работы с браузерными запросами завершена')
    loging('Система', 'Загрузка работы с браузерными запросами завершена')


# Работа с модами
if MODS:
    ''' # TODO Доделать когда-то
    class Mods:
        def __init__(self, info, json, python):
            self.info = info
            self.json = json
            self.python = python'''
            
    print('Загрузка модов...\nПредупреждение: Моды могут быть не стабильными, так как они не являются официальными!')
    mods_dir = os.listdir("./Mods")
    for mod in mods_dir:
        print(f'Загрузка "{mod}"...')
        try:
            with open(f'Mods/{mod}/ReadMe.txt', 'r', encoding='UTF-8') as f:
                print('> Загрузка информации:')
                f = f.read()
                f = f.split('\n')
                print(f'  Мод:  \t{f[0]}\n  Версия:\t{f[1]}\n  Автор:\t{f[2]}\n  Описание:\t{f[3]}')
            with open(f'Mods/{mod}/tools.json', 'r', encoding='UTF-8') as f:
                print('> Загрузка JSON')
                f = json.load(f)
                tools.append(f)
            with open(f'Mods/{mod}/tools.py', 'r', encoding='UTF-8') as f:
                print(f'> Загрузка Python')
                exec(f.read())
            print(f'Загрузка "{mod}" завершена')
            loging('Система', f'Загрузка мода "{mod}" завершена')
        except Exception as e:
            print(f'Не удалось загрузить "{mod}"!')
            loging('Система', f'Не удалось загрузить "{mod}"\nОшибка: <{e}>')
    print('Загрузка модов завершена')
    loging('Система', 'Загрузка модов завершена')


# Загрузка истории
if not NEW:
    print('Загрузка истории...')
    if os.path.exists("chat_history.json"): # Если итория есть
        with open("chat_history.json", "r", encoding="UTF-8") as f:
            history = json.load(f)
        print('История загружена')
        loging('Система', 'Загружена история переписки')
    else:                                   # Если итории нет
        history = [{"role": "system", "content": PROMPT}]
        print('История не найдена и создана пустая')
        loging('Система', 'История переписки не найдена и создана пустая')
else:
    history = [{"role": "system", "content": PROMPT}]
history.append({"role": "system", "content": f"<{get_time()}> Сессия начата."})


# Тут основной цикл в режиме вопрос-ответ
print('Запуск общения с AI...\n\n\nНапишите "!выход" для выхода\nНапишите "!очистить" для удаление истории из памяти\nНапишите "!сохранить" для сохранения истории в память')
while True:
    try:
        user_input = input("\n\n<ВЫ> ")
        loging('Пользователь', user_input)
        
        # Команды пользователя
        if user_input.lower() == "!выход": break
        elif user_input.lower() == "!очистить": history = [{"role": "system", "content": PROMPT}, {"role": "system", "content": f"<{get_time()}> Сессия начата."}]; loging('Система', 'История очищена'); continue
        elif user_input.lower() == "!сохранить":
            with open("chat_history.json", "w", encoding="UTF-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                print('История сохранена')
                loging('Система', 'История сохранена')
            continue

        history.append({"role": "user", "content": user_input})
        print('ИИ думает...', end='', flush=True)
        tool_check, step_tool = True, 0
        time_start = time()
        while tool_check and (step_tool < LOOPS): # Цикл с использованием инструментов

            if step_tool+1 < LOOPS: # Чтобы последний ответ всегда был текстовым, а не с использованием инструментов
                used_tools = tools
            else:
                used_tools = []

            response = ollama.chat(model=MODEL, messages=history, options={'num_thread': CPU, 'num_predict': CW, 'repeat_penalty': 1.0, 'keep_alive': KA}, tools=used_tools)
            answer = response['message']['content']
            loging('Искуственный Интелект', response)
            if response.get('message', {}).get('tool_calls'): # Обработка инструментов
                for tool_call in response['message']['tool_calls']:
                    function_name = tool_call['function']['name']
                    function_argument = tool_call['function']['arguments']
                    arguments, step = '', 0
                    for i in function_argument:
                        if step > 0: arguments += ', '
                        function_content = str(function_argument.get(i))
                        arguments += f'{i} = r\'\'\'{function_content}\'\'\''
                        step += 1
                    loging('Искуственный Интелект', f'{function_name}({arguments})')
                    tool_content = str(eval(f'{function_name}({arguments})'))
                    history.append({"role": "tool", "content": tool_content})
                    loging('Система', f'Вызван {function_name} с результатом <{tool_content}>')
                    step_tool += 1
            else:
                tool_check = False

        if answer: # вывод ответа
            print(('\b'*12)+(' '*12)+('\b'*12)+f'<ИИ> {answer}\n<думал {(time()-time_start):.2f} секунд>')
            history.append({"role": "assistant", "content": answer})
            loging('Искуственный Интелект', answer)
        else:
            print(('\b'*12)+'AI выполнил задание!'+f'\n<думал {(time()-time_start):02f} секунд>')

    except Exception as e:
        history.append({"role": "system", "content": f"Ошибка: {e}"})
        loging('Система', f'В цикле была возвращена ошибка <{e}>')
        print("\nУпс! Ошибочка:", e)
        sleep(2.5)


# Завершение программы с сохранением всего что нужно
print('\nОбщение с AI завершено\nСохранение истории...') # Тут история сохраняется
history.append({"role": "system", "content": f"<{get_time()}> Сессия завершена."})
if not NEW:
    with open("chat_history.json", "w", encoding="UTF-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
        print('История сохранена')
        loging('Система', 'История сохранена')
print('Программа завершена')
loging('Система', 'Программа закрыта правильно')