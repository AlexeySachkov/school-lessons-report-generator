import urllib.request
import json
import datetime
import codecs
import time
import re
import pyquery
import hashlib
import os

with open('data.json') as f:
    base_data = json.load(f)
    homeworks = base_data['homeworks']
    for homework in homeworks:
        d, m, y = homework['from']
        homework['from'] = datetime.date(y, m, d)
        d, m, y = homework['to']
        homework['to'] = datetime.date(y, m, d)

    handles = base_data['handles']

def next_date_timestamp(date):
    current = datetime.datetime.strptime(date.strftime("%d/%m/%Y"), "%d/%m/%Y")
    next = current + datetime.timedelta(days=1)
    return time.mktime(next.timetuple())

HEADER = '<!DOCTYPE html><html>' \
         '<head><title>Отчёт о решении задач на codeforces</title>' \
         '<meta charset="UTF-8" />' \
         '<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">' \
         '<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>' \
         '<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>' \
         '<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>' \
         '<style type="text/css">' \
         'body { padding-top: 50px; }' \
         '</style>' \
         '</head><body>'

now = datetime.datetime.now()

FOOTER = '<div class="container"><div class="row"><div class="col-md-12"><hr />' \
         '<p>Последнее обновление: {}' \
         '<p>Все вопросы, пожелания, найденные ошибки и неточности можно сообщить <a href="https://github.com/AlexeySachkov/AlexeySachkov.github.io/issues/new">создав issue</a>' \
         '<p>Generated by <a href="https://github.com/AlexeySachkov/AlexeySachkov.github.io/blob/master/38.10.2018/main.py">python script</a>. Big thanks <a href="https://codeforces.com/">Codeforces</a> for the <a href="http://codeforces.com/api/help">API</a>' \
         '<p>Powered by <a href="https://pages.github.com/">Github Pages</a> and <a href="https://getbootstrap.com/">Bootstrap</a>'\
         '</div></div></div></body></html>'.format(now.strftime("%d.%m.%Y %H:%M"))

# Generate index page

with codecs.open('reports/index.html', 'w', "utf-8") as file:
    file.write(HEADER)
    file.write('<div class="container"><div class="row"><div class="col-md-12">')
    file.write('<h1>Отчёт о решении задач на codeforces</h1><hr />')
    file.write('<h2>Домашние задания</h2>')
    file.write('<div class="card-group">')
    index = 0
    for homework in homeworks:
        index = index + 1
        file.write('<div class="card"><div class="card-header">')
        file.write('Домашняя работа №{}</div>'.format(index))
        file.write('<ul class="list-group list-group-flush">')
        file.write('<li class="list-group-item">Задана: {}</li>'.format(homework['from'].strftime("%d.%m.%Y")))
        file.write('<li class="list-group-item">Сдать до: {}</li>'.format(homework['to'].strftime("%d.%m.%Y")))
        file.write('<li class="list-group-item">Список задач: ')

        total = len(homework['problems'])
        current = 0
        for problem in homework['problems']:
            current = current + 1
            matches = re.match(r'(\d+)([A-E]+)', problem)
            if matches is None:
                file.write(problem)
            else:
                file.write('<a href="https://codeforces.com/contest/{}/problem/{}" target="_blank">{}</a>'.format(matches[1], matches[2], problem))
            if current != total:
                file.write(', ')
        file.write('</li></ul></div>')

    file.write("</div>")
    file.write('<h2>Список индивидуальных отчётов</h2>')
    file.write('<ul>')
    for handle in handles:
        file.write('<li><a href="https://alexeysachkov.github.io/38.10.2018/reports/{}.html">{}</a></li>'.format(handle, handle))
    file.write('</ul>')
    file.write('<h2>Итоговые оценки</h2>')
    file.write('<p><a href=2018.final.html>1 семестр</a>')
    file.write('</div></div></div>')
    file.write(FOOTER)


BASE_URL = 'https://codeforces.com/api/user.status'

homework_scores = {}

too_fast_submissions = {}

all_one_shot_submissions = []

for handle in handles:
    url = BASE_URL + '?lang=ru&handle={}&from=1&count=1000'.format(handle)
    print(url)
    connected = False
    while not connected:
        try:
            request = urllib.request.Request(url)
            if os.environ['PROXY'] is not None:
                print('setting proxy to {}'.format(os.environ['PROXY']))
                request.set_proxy(os.environ['PROXY'], 'https')
            response = urllib.request.urlopen(request)
            content = response.read()
            connected = True
        except OSError as err:
            print("OS Error: {}".format(err))
            connected = False

    with codecs.open('reports/{}.html'.format(handle), 'w', "utf-8") as file:
        file.write(HEADER)
        file.write('<div class="container"><div class="row"><div class="col-md-12">')
        file.write('<h2 class="page-header">Отчёт о выполнении домашнего задания <a href="https://codeforces.com/profile/{}">{}</a></h2><hr />'.format(handle, handle))
        response = json.loads(content)

        if response['status'] != 'OK':
            file.write('<em>Failed to get data!</em>')
            continue

        per_problem = {}
        included_in_homework = set()
        data = sorted(response['result'], key=lambda k: k['creationTimeSeconds'])

        for submission in data:
            problem = str(submission['problem']['contestId']) + submission['problem']['index']
            if problem not in per_problem:
                per_problem[problem] = [submission]
            else:
                per_problem[problem].append(submission)

        one_shot = []
        for problem, submissions in per_problem.items():
            if len(submissions) == 1:
                one_shot.append(submissions[0]['creationTimeSeconds'])
                t = submissions[0]
                t['handle'] = handle
                all_one_shot_submissions.append(t)
            else:
                for submission in submissions:
                    if submission['verdict'] == 'OK':
                        # prolem was solved
                        t = submission
                        t['handle'] = handle
                        all_one_shot_submissions.append(t)
                        break

        if len(one_shot) > 0:
            for index in range(0, len(one_shot) - 1, 2):
                if one_shot[index + 1] - one_shot[index] < 90:
                    # less than 90 seconds to solve a problem!
                    if handle not in too_fast_submissions:
                        too_fast_submissions[handle] = 0
                    too_fast_submissions[handle] = too_fast_submissions[handle] + 1

        index = 0
        homework_scores[handle] = {}
        for homework in homeworks:
            index = index + 1
            file.write('<div class="card">')
            file.write('<div class="card-header">Домашняя работа №{}</div>'.format(index))
            file.write('<ul class="list-group list-group-flush">')
            file.write('<li class="list-group-item">Задана: {}</li>'.format(homework['from'].strftime("%d.%m.%Y")))
            file.write('<li class="list-group-item">Сдать до: {}</li>'.format(homework['to'].strftime("%d.%m.%Y")))
            file.write('</ul><div class="card-body">')

            end_timestamp = next_date_timestamp(homework['to'])

            num_in_time = 0
            num_late = 0
            for problem in homework['problems']:
                included_in_homework.add(problem)
                file.write('<h5 class="card-title">{}</h5>'.format(problem))
                if problem not in per_problem:
                    file.write('<p class="text-danger"><strong>Не было сделано ни одной попытки!</strong>')
                else:
                    got_ac = False
                    in_time = False
                    for submission in per_problem[problem]:
                        if submission['verdict'] == 'OK':
                            got_ac = True
                            if submission['creationTimeSeconds'] < end_timestamp:
                                in_time = True
                                break

                    file.write('Было сделано попыток: {}. '.format(len(per_problem[problem])))
                    if got_ac and in_time:
                        num_in_time = num_in_time + 1
                        file.write('<strong class="text-success">Задача сдана вовремя</strong>')
                    elif got_ac:
                        num_late = num_late + 1
                        file.write('<strong class="text-warning">Задача не была сдана вовремя, однако был сдана позже</strong>')
                    else:
                        file.write('<strong class="text-danger">Задача не была сдана</strong>')
                    file.write('<p><a data-toggle="collapse" href="#{}-{}">Показать все попытки</>'.format(handle, problem))
                    file.write('<ul class="collapse" id="{}-{}">'.format(handle, problem))
                    for submission in per_problem[problem]:
                        file.write('<li><a href="https://codeforces.com/contest/{}/submission/{}">{}</a> - {}</li>'.format(submission['problem']['contestId'], submission['id'], submission['id'], submission['verdict']))
                    file.write('</ul>')

            file.write('</div><div class="card-footer">')
            file.write('<p><strong>Система оценок:</strong> 1 балл за задачу, которая была сдана вовремя; 0.75 за дорешаную позже задачу')
            file.write('<p>Оценка выставляется исходя из процентного соотношения количества полученных балов к максимально возможному количеству баллов')
            file.write('<p><=25% - 2; <=50% - 3; <= 75% - 4; > 75% - 5')
            file.write('</div><div class="card-footer">')
            score = num_in_time + num_late * 0.75
            percent = int(score / len(homework['problems']) * 100)
            if percent <= 25:
                final_score = 2
            elif percent <= 50:
                final_score = 3
            elif percent <= 75:
                final_score = 4
            else:
                final_score = 5
            homework_scores[handle][index] = final_score
            file.write('<p>Всего решено задач: {}, вовремя: {}, дорешано: {}. Оценка: {} ({}/{} - {}%)'.format(num_in_time + num_late, num_in_time, num_late, final_score, score, len(homework['problems']), percent))
            file.write('</div></div><br />')

        file.write('<div class="card">')
        file.write('<div class="card-header">Дополнительнo решённые задачи</div>')
        file.write('<div class="card-body">')
        count = 0
        for problem, submissions in per_problem.items():
            if problem in included_in_homework:
                continue
            count = count + 1
            file.write('<h5 class="card-title">{}</h5>'.format(problem))
            got_ac = False
            for submission in submissions:
                if submission['verdict'] == 'OK':
                    got_ac = True
            if got_ac:
                file.write('<strong class="text-success">Задача была сдана</strong>')
            else:
                file.write('<strong class="text-warning">Задача не была сдана</strong>')
            file.write('<p><a data-toggle="collapse" href="#{}-{}">Показать все попытки</>'.format(handle, problem))
            file.write('<ul class="collapse" id="{}-{}">'.format(handle, problem))
            for submission in submissions:
                file.write('<li><a href="https://codeforces.com/contest/{}/submission/{}">{}</a> - {}</li>'.format(submission['problem']['contestId'], submission['id'], submission['id'], submission['verdict']))
            file.write('</ul>')

        if count == 0:
            file.write('<p>Ни одной попытки по другим задачам сделано не было')

        file.write('</div></div>')


        file.write('</div></div></div>')
        file.write(FOOTER)
        time.sleep(5)

exit(0)
# Check for copy-paste

existing_hashes = set()

copy_paste = {}

index=0
total = len(all_one_shot_submissions)
for submission in all_one_shot_submissions:
    index = index + 1
    print('{}/{}'.format(index, total))
    if submission['contestId'] == '100092':
        continue  # skip trainings. source code cannot be obtained

    url = 'https://codeforces.com/contest/{}/submission/{}'.format(submission['contestId'], submission['id'])
    connected = False
    while not connected:
        try:
            d = pyquery.PyQuery(url)
            connected = True
        except TimeoutError:
            connected = False
        except OSError:
            connected = False

    html = d("#program-source-text").html()
    if html is None:
        print('cannot obtain program sources for: {}'.format(url))
        continue
    code = ''.join(html.split())
    hash_obj = hashlib.sha512(code.encode('utf-8'))
    hex = hash_obj.hexdigest()
    if hex in existing_hashes:
        handle = submission['handle']
        if handle not in copy_paste:
            copy_paste[handle] = 0
        copy_paste[handle] = copy_paste[handle] + 1

    existing_hashes.add(hex)
    time.sleep(1)

# Generate finals page

additional = {
    'Natasha_andr': {
        'test': 3,
        'b': [2, 0, 0]
    },
    'imyanark': {
        'test': 0,
        'b': [-1, 0, 0]
    },
    'andrushabausov': {
        'test': 5,
        'b': [0, 0, 0]
    },
    'MayeTusks': {
        'test': 4,
        'b': [7, 0, 0]
    },
    'matveykos': {
        'test': 4,
        'b': [-1, 0, 0]
    },
    'artenator2': {
        'test': 3,
        'b': [2, 0, 0]
    },
    'Diana.kuptsova6062003': {
        'test': 3,
        'b': [3, 0, 0]
    },
    'VladimirLevin2002': {
        'test': 3,
        'b': [3, 0, 0]
    },
    'Ulia2911': {
        'test': 3,
        'b': [0, 0, 0]
    },
    'Wolf_from_Cintra': {
        'test': 0,
        'b': [0, 0, 0]
    },
    'olga_shakh': {
        'test': 0,
        'b': [1, 0, 0]
    },
    '3.x.310': {
        'test': 2,
        'b': [-2, 0, 0]
    },
    'kristina_': {
        'test': 4,
        'b': [-1, 0, 0]
    },
    'PRofe': {
        'test': 0,
        'b': [4, 0, 0]
    },
    'systemnickname': {
        'test': 3,
        'b': [1, 0, 0]
    },
    'VialovaA': {
        'test': 5,
        'b': [7, 0, 0]
    },
    'DanissimoKuw': {
        'test': 4,
        'b': [3, 0, 0]
    },
    'Dmitry_Ddv': {
        'test': 4,
        'b': [1, 0, 0]
    },
    'isashaaaa': {
        'test': 3,
        'b': [4, 0, 0]
    },
    'Mihail.M.K': {
        'test': 3,
        'b': [1, 0, 0]
    },
    'Ar1shka': {
        'test': 3,
        'b': [2, 0, 0]
    },
    'akon1te': {
        'test': 3,
        'b': [4, 0, 0]
    },
    'Sudarikov': {
        'test': 4,
        'b': [2, 0, 0]
    },
    'leyyyn': {
        'test': 0,
        'b': [0, 0, 0]
    },
    'Hac_ker.sashko': {
        'test': 4,
        'b': [-1, 0, 0]
    },
    'Senchatay': {
        'test': 3,
        'b': [2, 0, 0]
    },
    'Gleb_Yasakov': {
        'test': 4,
        'b': [4, 0, 0]
    },
    'Vanco132': {
        'test': 3,
        'b': [4, 0, 0]
    },
    'Meow_Tory': {
        'test': 0,
        'b': [0, 0, 0]
    }
}

with codecs.open('reports/2018.final.html', 'w', "utf-8") as file:
    file.write(HEADER)
    file.write('<div class="container"><div class="row"><div class="col-md-12">')
    file.write('<h1>Отчёт о решении задач на codeforces</h1><hr />')
    file.write('<h2>Итоговые оценки за 1 семестр</h2>')
    file.write('<table class="table table-bordered table-hover">')
    file.write('<thead><tr><th>Handle</th><th>HW#1</th><th>HW#2</th><th>HW#3</th><th>HW#4</th>')
    file.write('<th>Test</th>')
    file.write('<th>B#1</th>')
    file.write('<th>Sum</th>')
    file.write('<th>PrS</th>')
    file.write('<th>B#2</th>')
    file.write('<th>PrS2</th>')
    file.write('</tr></thead>')
    file.write('<tbody>')
    for handle in handles:
        file.write('<tr><td>{}</td>'.format(handle))
        sum = 0
        for index in range(1, len(homeworks)+1):
            file.write('<td>{}</td>'.format(homework_scores[handle][index]))
            sum = sum + homework_scores[handle][index]
        test = additional[handle]['test']
        sum = sum + test
        test = '-' if test == 0 else test
        b = additional[handle]['b']
        too_fast = 0 if handle not in too_fast_submissions else -too_fast_submissions[handle]
        cp = 0 if handle not in copy_paste else -copy_paste[handle]
        file.write('<td>{}</td><td>{}</td><!--<td>{}</td><td>{}</td>-->'.format(test, b[0], too_fast, cp))
        sum = sum + b[0]# + too_fast + cp
        file.write('<td>{}</td>'.format(sum))
        if sum >= 25:
            final_score = 5
        elif sum >= 20:
            final_score = 4
        elif sum >= 15:
            final_score = 3
        else:
            final_score = 2
        file.write('<td>{}</td>'.format(final_score))
        sum += cp
        if sum >= 25:
            final_score = 5
        elif sum >= 20:
            final_score = 4
        elif sum >= 15:
            final_score = 3
        else:
            final_score = 2
        file.write('<td>{}</td><td>{}</td>'.format(cp, final_score))
        file.write('</tr>')

    file.write('</tbody></table>')
    file.write('<p><strong>Легенда</strong>')
    file.write('<p> HW#X - Оценка за домашнюю работу №X')
    file.write('<p> Test - Оценка за тест 19.11.2018')
    file.write('<p> B#1 - Дополнительные баллы за ответы на лекциях и работу на практике. Может быть отрицательным числом')
    file.write('<p> Sum - Cумма полученных баллов')
    file.write('<p> PrS - Предварительная оценка. Способ подсчёта:')
    file.write('<ul>')
    file.write('<li>Минимальное количество баллов на 5: 25</li>')
    file.write('<li>Минимальное количество баллов на 4: 20</li>')
    file.write('<li>Минимальное количество баллов на 3: 15</li>')
    file.write('</ul>')
    file.write('<p> B#2 - Штрафы за копирование чужих решений')
    file.write('<p> PrS2 - Предварительная оценка с учётом штрафов за копирование чужих решений')
    file.write('<p><strong>Важно!</strong> Данная система оценивания предварительная, минимальное количество баллов для получения той или иной оценки может быть изменено. Любая оценка может быть оспорена. Для подтверждения потребуется сдать одну или несколько задач на codeforces и ответить на несколько вопросов.')
    file.write('<p><strong>Важно!</strong> Некоторые сдали все домашние работы, но полностью их скопировали у других - я добавлю дополнительную колонку, которая будет показывать штрафы за копирование чужих решений')
    file.write('<p>[18.12.2018] Информация о копировании чужих решений была добавлена.')
    file.write('<p><strong>Важно!</strong> На последних занятиях по практике я часто давал индивидуальные задания на codeforces - будет добавлена отдельная колонка с оценкой выполнения этих индивидуальных заданий')
    file.write('<p>Выполнение домашних заданий приносит баллы, даже если сроки сдачи уже прошли, однако помните про штрафы за копирование чужих работ!')
    file.write('<p>Если вы переживаете за свою оценку и заинтересованы в её повышении - напишите мне на почту (sachkov2011 at gmail dot com) для получения индивидуального задания')
    file.write('<p>Список возможных вопросов будет опубликован на этом сайте позже, с примерами ответов')
    file.write('</div></div></div>')
    file.write(FOOTER)
