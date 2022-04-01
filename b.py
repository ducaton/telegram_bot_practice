from requests import get
from requests import post
from time import sleep
from threading import Timer

url = "https://api.telegram.org/bot<Api Token from @BotFather>/"

def get_updates_json(request, offset):
    params = {'timeout': 100, 'offset': offset}
    response = get(request + 'getUpdates', data=params)
    return response.json()
    
def get_chat_text(data_source):
    global result_id
    try:
        message_text = data_source['result'][result_id]['message']['text']
    except:
        try:
            message_text = data_source['result'][result_id]['callback_query']['data']
        except:
            return ''
    return message_text

def send_mess(data_source, text):
    global result_id
    kill_callback_query = False
    try:
        chat_id = data_source['result'][result_id]['message']['chat']['id']
    except KeyError:
        chat_id = data_source['result'][result_id]['callback_query']['message']['chat']['id']
        params = {'callback_query_id': data_source['result'][result_id]['callback_query']['id']}
        post(url + 'answerCallbackQuery', data=params)
        kill_callback_query = True
    params = {'chat_id': chat_id, 'text': text}
    post(url + 'sendMessage', data=params)
    return kill_callback_query
    
def send_mess_with_buttons(data_source, buttons, text):
    global result_id
    kill_callback_query = False
    try:
        chat_id = data_source['result'][result_id]['message']['chat']['id']
    except KeyError:
        chat_id = data_source['result'][result_id]['callback_query']['message']['chat']['id']
        params = {'callback_query_id': data_source['result'][result_id]['callback_query']['id']}
        post(url + 'answerCallbackQuery', data=params)
        kill_callback_query = True
    params = {'chat_id': chat_id, 'text': text, 'reply_markup': buttons}
    post(url + 'sendMessage', data=params)
    return kill_callback_query

def edit_mess_with_buttons(data_source, buttons, text):
    global result_id
    kill_callback_query = False
    try:
        chat_id = data_source['result'][result_id]['message']['chat']['id']
    except KeyError:
        chat_id = data_source['result'][result_id]['callback_query']['message']['chat']['id']
        params = {'callback_query_id': data_source['result'][result_id]['callback_query']['id']}
        post(url + 'answerCallbackQuery', data=params)
        kill_callback_query = True
    message_id = data_source['result'][result_id]['callback_query']['message']['message_id']
    params = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'reply_markup': buttons}
    post(url + 'editMessageText', data=params)
    return kill_callback_query
    
def result_id_decr ():
    global result_id
    result_id -= 1
    
def threads_clr ():
    global threads
    for timer in threads:
        timer.cancel()
        timer.join()
    threads.clear()

def threads_inc ():
    global threads
    timer=Timer(151.0, result_id_decr)
    threads.append(timer)
    timer.start()

def main():
    global result_id
    full_log = get_updates_json(url, -1)
    if not 'result' in full_log or len(full_log['result']) == 0:
        raise Exception('В списке нет сообщений')
    result_id = 0
    curr_upd_id = full_log['result'][result_id]['update_id']
    while True:
        full_log = get_updates_json(url, curr_upd_id)
        if not 'result' in full_log or len(full_log['result']) == 0:
            raise Exception('В списке нет сообщений')
        if result_id < (len(full_log['result']) - 1):
            result_id += 1
            message_text = get_chat_text(full_log).lower()
            if message_text in {'привет', 'ку'}:
                if send_mess(full_log, 'Здарова)'):
                    threads_inc()
            elif message_text in {'пока', 'бб'}:
                if send_mess(full_log, 'Пока('):
                    threads_inc()
            elif message_text in {'влад', 'vlad'}:
                if send_mess(full_log, ')))))'):
                    threads_inc()
            elif message_text in {'команды', 'помощь', 'помоги', '/help'}:
                if send_mess(full_log, 'Команды: \"Привет\", \"Пока\", \"Помощь\" и \"Темы\"'):
                    threads_inc()
            elif message_text in {'темы', '/topics'}:
                buttons = '{"inline_keyboard":\
                [[{"text":"Тема1","callback_data":"Тема1"},\
                  {"text":"Прощание","callback_data":"бб"}],\
                 [{"text":"Влад","callback_data":"влад"},\
                  {"text":"Помощь","callback_data":"/help"}\
                ]]}'
                if send_mess_with_buttons(full_log, buttons, 'Выберите тему'):
                    threads_inc()
            elif message_text == 'тема1':
                buttons = '{"inline_keyboard":\
                [[{"text":"Прощание","callback_data":"бб"}],\
                 [{"text":"Помощь","callback_data":"/help"}\
                ]]}'
                if edit_mess_with_buttons(full_log, buttons, 'Тема 2. Кошка села у окошка.'):
                    threads_inc()
        if result_id >= 50:
            curr_upd_id = full_log['result'][result_id]['update_id']
            result_id = 0
            threads_clr()
        sleep(0.1)

if __name__ == '__main__':
    global threads
    threads = []
    while True:
        try:
            main()
        except KeyboardInterrupt:
            threads_clr()
            exit()
        except Exception as e:
            print('Ошибка:\n', e)
            threads_clr()
            sleep(0.1)
            continue
