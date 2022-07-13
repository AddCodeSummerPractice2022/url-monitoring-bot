from aiogram import types, Dispatcher
import sqlite3 as sq
import re

from handlers import addSite, showSpisok
from aiogram.dispatcher.filters import Text
from createBot import dp, bot
from sqlite3 import SQLITE_PRAGMA

# Функция создания базы данных с тремя таблицами
def sql_start_tables():
    global DataBase, cur
    DataBase = sq.connect('Database.db', timeout=10)
    cur = DataBase.cursor()
    if DataBase:
        print('DataBase opened')
    cur.execute('PRAGMA foreign_keys = on')
    DataBase.execute('CREATE TABLE IF NOT EXISTS Users(tg_user_id TEXT, ID TEXT PRIMARY KEY)')
    DataBase.execute('CREATE TABLE IF NOT EXISTS Sites(ID TEXT PRIMARY KEY, Site_url TEXT, Status TEXT, Ping TEXT, Check_Date TEXT)')
    DataBase.execute('CREATE TABLE IF NOT EXISTS Connections(ID TEXT, UID_User TEXT, UID_Site TEXT, FOREIGN KEY(UID_Site) REFERENCES Sites(ID) ON DELETE CASCADE, FOREIGN KEY(UID_User) REFERENCES Users(ID) ON DELETE CASCADE)')
    DataBase.commit()

# Функция добавления пользователя в таблицу Users
async def sql_add_user():
        cur.execute('INSERT INTO Users(tg_user_id, ID) VALUES (?, ?)', (addSite.users_db.tg_user_id, addSite.users_db.UID_user))
        DataBase.commit()

# Функция добавления сайта в таблицу Sites
async def sql_add_site():
    cur.execute('INSERT INTO Sites(ID, Site_url, Status, Ping, Check_Date) VALUES (?, ?, ?, ?, ?)', (addSite.sites_db.id, addSite.sites_db.site_url, addSite.sites_db.status, addSite.sites_db.ping, addSite.sites_db.check_date))
    DataBase.commit()

# Функция добавления связей в таблицу Connections
async def sql_add_conns():
    cur.execute('PRAGMA foreign_keys = on')
    cur.execute('INSERT INTO Connections(ID, UID_User, UID_Site) VALUES (?, ?, ?)', (addSite.users_db.tg_user_id,addSite.users_db.UID_user,addSite.sites_db.id))
    DataBase.commit()

# Функция чтения таблицы User - возвращает список ID по tg_user_id
def sql_read_user(tg_user_id : int):
    cur.execute('SELECT ID FROM Users WHERE tg_user_id = ?', (tg_user_id,))
    spisok = cur.fetchall()    
    return spisok

# Функция получения списка сайтов по tg_user_id - возвращает список с URL, Status, Ping
def sql_get_spisok(tg_user_id : str):
    cur.execute('SELECT Sites.Site_url, Sites.Status, Sites.Ping FROM Sites INNER JOIN Connections ON Sites.ID=Connections.UID_Site INNER JOIN USERS ON Connections.UID_User=Users.ID WHERE Users.tg_user_id=?', (tg_user_id,))
    spisok = cur.fetchall()
    return spisok
# Функция получения количества доавленных сайтов пользователем по tg_user_id - возвращает количество
def sql_get_amount(tg_user_id : int):
    cur.execute('SELECT ID FROM Users WHERE tg_user_id = ?', (tg_user_id,))
    spisok = cur.fetchall()
    return len(spisok)

# Функция удаления сайта по номеру из списка у определенного tg_user_id
def sql_remove_site(tg_user_id: str, number: int):
    spisok_of_UID_site = list()
    spisok_of_UID_user = list()
    for a in range(sql_get_amount(tg_user_id)):
        cur.execute('SELECT ID FROM Users WHERE tg_user_id = ?', (tg_user_id,))
        spisok = cur.fetchall()
        stroka = str(spisok[a])
        stroka = re.sub(r'[,\'\"\(\)]', '', stroka)
        spisok_of_UID_user.append(stroka)
    print(spisok_of_UID_user)

    for a in range(sql_get_amount(tg_user_id)):
        cur.execute('SELECT UID_Site FROM Connections WHERE UID_User = ?', (spisok_of_UID_user[a],))
        stroka = str(cur.fetchone())
        stroka = re.sub(r'[,\'\"\(\)]', '', stroka)
        spisok_of_UID_site.append(stroka)
    print(spisok_of_UID_site)
    cur.execute('DELETE FROM Connections WHERE UID_Site = ? and UID_User = ?', (spisok_of_UID_site[number - 1], spisok_of_UID_user[number - 1],))
    cur.execute('DELETE FROM Users WHERE ID = ?', (spisok_of_UID_user[number - 1],))
    cur.execute('DELETE FROM Sites WHERE ID = ?', (spisok_of_UID_site[number - 1],))
    DataBase.commit()