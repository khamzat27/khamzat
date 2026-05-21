import telebot
from telebot import types
import db as db
import status
from datetime import date
import os
 


TOKEN = 'твой токен'
bot = telebot.TeleBot(TOKEN)


user_state = {} 

def main_kb():
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.add('Записать день', 'Статистика')
    k.add('История', 'Очистить', 'Помощь')
    return k

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, 
                     'Ас салам алейкум!\n'
                     'Я твой трекер настроения и продуктивности.\n\n'
                     'Используй кнопки внизу, чтобы начать.', 
                     reply_markup=main_kb())

@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda m: m.text == 'Помощь')
def help_h(m):
    t = ("📖 **Как пользоваться:**\n\n"
         "1️⃣ *Записать день* — ввод данных за сегодня.\n"
         "2️⃣ *Статистика* — графики, средние значения и инсайты.\n"
         "3️⃣ *История* — последние 5 записей.\n"
         "4️⃣ *Очистить* — удалить все твои данные.\n\n"
         "Цель: понять, как сон и учеба влияют на настроение!")
    bot.send_message(m.chat.id, t, reply_markup=main_kb(), parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == 'Записать день')
def add_d(m):
    user_state[m.chat.id] = {'step': 'mood', 'date': date.today().isoformat()}
    
    k = types.InlineKeyboardMarkup()
    k.row(types.InlineKeyboardButton('1 😞', callback_data='m_1'),
          types.InlineKeyboardButton('2 😐', callback_data='m_2'),
          types.InlineKeyboardButton('3 🙂', callback_data='m_3'))
    k.row(types.InlineKeyboardButton('4 😊', callback_data='m_4'),
          types.InlineKeyboardButton('5 🤩', callback_data='m_5'))
          
    bot.send_message(m.chat.id, 'Оцени свое настроение сегодня (1-5):', reply_markup=k)


@bot.callback_query_handler(func=lambda c: c.data.startswith('m_'))
def callback_mood(c):
    cid = c.message.chat.id
    if cid not in user_state or user_state[cid].get('step') != 'mood':
        return
        
    mood_val = int(c.data.split('_')[1])
    user_state[cid]['mood'] = mood_val
    user_state[cid]['step'] = 'work'
    
    bot.answer_callback_query(c.id)
    
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row('0.5', '1', '2', '4', 'Другое')
    bot.send_message(cid, f'Принято: {mood_val}/5.\nСколько часов потратил на учебу/работу?', reply_markup=k)
    bot.delete_message(cid, c.message.message_id) # Удаляем сообщение с кнопками настроения для чистоты

@bot.message_handler(func=lambda m: m.chat.id in user_state and user_state[m.chat.id].get('step') == 'work')
def get_work(m):
    cid = m.chat.id
    txt = m.text.strip().replace(',', '.')
    
    if txt == 'Другое':
        user_state[cid]['step'] = 'work_input'
        bot.send_message(cid, 'Напиши число часов (например, 3.5):', reply_markup=types.ReplyKeyboardRemove())
        return
        
    try:
        hours = float(txt)
        user_state[cid]['work'] = hours
        ask_sleep(cid)
    except ValueError:
        bot.send_message(cid, 'Пожалуйста, введи число или выбери кнопку.')

@bot.message_handler(func=lambda m: m.chat.id in user_state and user_state[m.chat.id].get('step') == 'work_input')
def get_work_input(m):
    try:
        hours = float(m.text.replace(',', '.'))
        user_state[m.chat.id]['work'] = hours
        ask_sleep(m.chat.id)
    except ValueError:
        bot.send_message(m.chat.id, 'Это не число. Попробуй еще раз.')

def ask_sleep(cid):
    user_state[cid]['step'] = 'sleep'
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row('6', '7', '8', '9', 'Другое')
    bot.send_message(cid, 'Сколько часов ты спал?', reply_markup=k)

@bot.message_handler(func=lambda m: m.chat.id in user_state and user_state[m.chat.id].get('step') == 'sleep')
def get_sleep(m):
    cid = m.chat.id
    txt = m.text.strip().replace(',', '.')
    
    if txt == 'Другое':
        user_state[cid]['step'] = 'sleep_input'
        bot.send_message(cid, 'Напиши число часов сна:', reply_markup=types.ReplyKeyboardRemove())
        return
        
    try:
        hours = float(txt)
        user_state[cid]['sleep'] = hours
        ask_comment(cid)
    except ValueError:
        bot.send_message(cid, 'Пожалуйста, введи число.')

@bot.message_handler(func=lambda m: m.chat.id in user_state and user_state[m.chat.id].get('step') == 'sleep_input')
def get_sleep_input(m):
    try:
        hours = float(m.text.replace(',', '.'))
        user_state[m.chat.id]['sleep'] = hours
        ask_comment(m.chat.id)
    except ValueError:
        bot.send_message(m.chat.id, 'Не число. Попробуй снова.')

def ask_comment(cid):
    user_state[cid]['step'] = 'comment'
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.add('Пропустить')
    bot.send_message(cid, 'Хочешь добавить комментарий? (или нажми "Пропустить")', reply_markup=k)

@bot.message_handler(func=lambda m: m.chat.id in user_state and user_state[m.chat.id].get('step') == 'comment')
def save_record(m):
    cid = m.chat.id
    data = user_state[cid]
    
    comment = None if m.text == 'Пропустить' else m.text
    

    db.add_record(cid, data['date'], data['mood'], data['work'], data['sleep'], comment)
    

    del user_state[cid]
    
    bot.send_message(cid, 'Данные сохранены!', reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == 'Статистика')
def show_stats_menu(m):
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton('За неделю', callback_data='st_7'))
    k.add(types.InlineKeyboardButton('За месяц', callback_data='st_30'))
    k.add(types.InlineKeyboardButton('Мои инсайты', callback_data='st_ins'))
    k.add(types.InlineKeyboardButton('График', callback_data='st_chart'))
    bot.send_message(m.chat.id, 'Выбери период или тип отчета:', reply_markup=k)

@bot.callback_query_handler(func=lambda c: c.data.startswith('st_'))
def process_stats(c):
    cid = c.message.chat.id
    action = c.data
    

    if action == 'st_7': days = 7
    elif action == 'st_30': days = 30
    else: days = 365 
    
    recs = db.get_records(cid, days)
    
    if not recs:
        bot.send_message(cid, 'Нет данных за этот период. Запиши хотя бы один день!', reply_markup=main_kb())
        bot.answer_callback_query(c.id)
        return

    if action == 'st_ins':
        insight_text = status.get_insights(recs)
        bot.send_message(cid, insight_text, parse_mode='Markdown')
        
    elif action == 'st_chart':
        fname = f'chart_{cid}.png'
        status.create_chart(recs, fname)
        
        if os.path.exists(fname):
            with open(fname, 'rb') as photo:
                bot.send_photo(cid, photo, caption='Твой график активности')
            os.remove(fname) 
        else:
            bot.send_message(cid, 'Ошибка создания графика.')
            
    else:
        # Простая статистика (среднее)
        avg_mood = sum(r['mood'] for r in recs) / len(recs)
        avg_work = sum(r['work_hours'] for r in recs) / len(recs)
        avg_sleep = sum(r['sleep_hours'] for r in recs) / len(recs)
        
        text = (f"**Статистика за {days} дн.:**\n"
                f"Настроение: {avg_mood:.1f}\n"
                f"Работа: {avg_work:.1f} ч\n"
                f"Сон: {avg_sleep:.1f} ч")
        bot.send_message(cid, text, parse_mode='Markdown')

    bot.answer_callback_query(c.id)



@bot.message_handler(func=lambda m: m.text == 'История')
def show_history(m):
    recs = db.get_records(m.chat.id, 365)
    if not recs:
        bot.send_message(m.chat.id, 'История пуста.', reply_markup=main_kb())
        return
    
    txt = ' **Последние 5 записей:**\n\n'
    # Берем последние 5
    for r in recs[-5:]:
        txt += f"{r['date']}\n"
        txt += f"   Настр: {r['mood']} | Работа: {r['work_hours']}ч | Сон: {r['sleep_hours']}ч\n"
        if r['comment']:
            txt += f"    _{r['comment']}_\n"
        txt += "\n"
        
    bot.send_message(m.chat.id, txt, reply_markup=main_kb(), parse_mode='Markdown')

# --- ОЧИСТКА ---

@bot.message_handler(func=lambda m: m.text == '🗑 Очистить')
def clear_confirm(m):
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton('Да, удалить всё', callback_data='cl_yes'))
    k.add(types.InlineKeyboardButton('Нет, отмена', callback_data='cl_no'))
    bot.send_message(m.chat.id, ' Ты уверен? Это удалит всю историю навсегда.', reply_markup=k)

@bot.callback_query_handler(func=lambda c: c.data.startswith('cl_'))
def confirm_clear(c):
    cid = c.message.chat.id
    if c.data == 'cl_yes':
        db.clear_user_data(cid)
        bot.send_message(cid, '🗑 Данные удалены.', reply_markup=main_kb())
    else:
        bot.send_message(cid, 'Отмена.', reply_markup=main_kb())
    bot.answer_callback_query(c.id)

if __name__ == '__main__':
    print("База данных инициализируется...")
    db.init_db()
    print("Бот запущен! ")
    bot.polling(none_stop=True)