from aiogram import types, Dispatcher
import sqlite3 as sq
import re

from handlers import addSite, showSpisok
from aiogram.dispatcher.filters import Text
from createBot import dp, bot
from sqlite3 import SQLITE_PRAGMA

# Функция создания базы данных с тремя таблицами
class sql_start_tables():
    #global DataBase, cur
    DataBase = sq.connect('Database.db', timeout=10)
    cur = DataBase.cursor()
    if DataBase:
        print('DataBase opened')
    cur.execute('PRAGMA foreign_keys = on')
    DataBase.execute('CREATE TABLE IF NOT EXISTS Users(tg_user_id TEXT, ID TEXT PRIMARY KEY)')
    DataBase.execute('CREATE TABLE IF NOT EXISTS Sites(ID TEXT PRIMARY KEY, Site_url TEXT, Status TEXT, Ping TEXT, Check_Date TEXT)')
    DataBase.execute('CREATE TABLE IF NOT EXISTS Connections(ID TEXT, UID_User TEXT, UID_Site TEXT, FOREIGN KEY(UID_Site) REFERENCES Sites(ID) ON DELETE CASCADE, FOREIGN KEY(UID_User) REFERENCES Users(ID) ON DELETE CASCADE)')
    DataBase.execute('CREATE TABLE IF NOT EXISTS Log(ID TEXT, Site_url TEXT, Status TEXT, Ping TEXT, Check_Date TEXT)') ##########
    DataBase.commit()

# Функция добавления пользователя в таблицу Users
async def sql_add_user():
    sql_start_tables.cur.execute('INSERT INTO Users(tg_user_id, ID) VALUES (?, ?)', (addSite.users_db.tg_user_id, addSite.users_db.UID_user))
    sql_start_tables.DataBase.commit()

# Функция добавления сайта в таблицу Sites
async def sql_add_site():
    sql_start_tables.cur.execute('INSERT INTO Sites(ID, Site_url, Status, Ping, Check_Date) VALUES (?, ?, ?, ?, ?)', (addSite.sites_db.id, addSite.sites_db.site_url, addSite.sites_db.status, addSite.sites_db.ping, addSite.sites_db.check_date))
    sql_start_tables.cur.execute('INSERT INTO Log(ID, Site_url, Status, Ping, Check_Date) VALUES (?, ?, ?, ?, ?)', (addSite.sites_db.id, addSite.sites_db.site_url, addSite.sites_db.status, addSite.sites_db.ping, addSite.sites_db.check_date))
    sql_start_tables.DataBase.commit()

async def sql_update_site(uid: str):
    sql_start_tables.cur.execute('UPDATE Sites SET Status=?, Ping=?, Check_Date=? WHERE ID=?', (showSpisok.sites_db.status, showSpisok.sites_db.ping, showSpisok.sites_db.check_date, uid))
    sql_start_tables.DataBase.commit()

# Функция добавления сайта в таблицу Log ##########
async def sql_add_sitelog():
    sql_start_tables.cur.execute('INSERT INTO Log(ID, Site_url, Status, Ping, Check_Date) VALUES (?, ?, ?, ?, ?)', (addSite.sites_db.id, showSpisok.sites_db.site_url, showSpisok.sites_db.status, showSpisok.sites_db.ping, showSpisok.sites_db.check_date))
    sql_start_tables.DataBase.commit()

# Функция добавления связей в таблицу Connections
async def sql_add_conns():
    sql_start_tables.cur.execute('PRAGMA foreign_keys = on')
    sql_start_tables.cur.execute('INSERT INTO Connections(ID, UID_User, UID_Site) VALUES (?, ?, ?)', (addSite.users_db.tg_user_id,addSite.users_db.UID_user,addSite.sites_db.id))
    sql_start_tables.DataBase.commit()

# Функция чтения таблицы User - возвращает список ID по tg_user_id
def sql_read_user(tg_user_id : int):
    sql_start_tables.cur.execute('SELECT ID FROM Users WHERE tg_user_id = ?', (tg_user_id,))
    list_of_users = sql_start_tables.cur.fetchall()    
    return list_of_users

# Функция получения списка сайтов по tg_user_id - возвращает список с URL, Status, Ping из таблицы Sites
def sql_get_list_of_sites(tg_user_id : str):
    sql_start_tables.cur.execute('SELECT Sites.Site_url, Sites.Status, Sites.Ping FROM Sites INNER JOIN Connections ON Sites.ID=Connections.UID_Site INNER JOIN USERS ON Connections.UID_User=Users.ID WHERE Users.tg_user_id=?', (tg_user_id,))
    list_of_sites = sql_start_tables.cur.fetchall()
    return list_of_sites

def sql_get_url(tg_user_id : str):
    sql_start_tables.cur.execute('SELECT Sites.Site_url FROM Sites INNER JOIN Connections ON Sites.ID=Connections.UID_Site INNER JOIN USERS ON Connections.UID_User=Users.ID WHERE Users.tg_user_id=?', (tg_user_id,))
    url = sql_start_tables.cur.fetchall()
    return url

def sql_get_uid(tg_user_id : str):
    sql_start_tables.cur.execute('SELECT Sites.ID FROM Sites INNER JOIN Connections ON Sites.ID=Connections.UID_Site INNER JOIN USERS ON Connections.UID_User=Users.ID WHERE Users.tg_user_id=?', (tg_user_id,))
    uid = sql_start_tables.cur.fetchall()
    return uid

# Функция получения количества доавленных сайтов пользователем по tg_user_id - возвращает количество
def sql_get_amount(tg_user_id : int):
    sql_start_tables.cur.execute('SELECT ID FROM Users WHERE tg_user_id = ?', (tg_user_id,))
    list_of_sites = sql_start_tables.cur.fetchall()
    return len(list_of_sites)


# Функция удаления сайта по номеру из списка у определенного tg_user_id
def sql_remove_site(tg_user_id: str, number: int):
    list_of_UID_site = list()
    list_of_UID_user = list()
    for a in range(sql_get_amount(tg_user_id)):
        sql_start_tables.cur.execute('SELECT ID FROM Users WHERE tg_user_id = ?', (tg_user_id,))
        list_of_users = sql_start_tables.cur.fetchall()
        string_of_one_user = str(list_of_users[a])
        string_of_one_user = re.sub(r'[,\'\"\(\)]', '', string_of_one_user)
        list_of_UID_user.append(string_of_one_user)

    for a in range(sql_get_amount(tg_user_id)):
        sql_start_tables.cur.execute('SELECT UID_Site FROM Connections WHERE UID_User = ?', (list_of_UID_user[a],))
        string_of_one_site = str(sql_start_tables.cur.fetchone())
        string_of_one_site = re.sub(r'[,\'\"\(\)]', '', string_of_one_site)
        list_of_UID_site.append(string_of_one_site)

    sql_start_tables.cur.execute('DELETE FROM Connections WHERE UID_Site = ? and UID_User = ?', (list_of_UID_site[number - 1], list_of_UID_user[number - 1],))
    sql_start_tables.cur.execute('DELETE FROM Users WHERE ID = ?', (list_of_UID_user[number - 1],))
    sql_start_tables.cur.execute('DELETE FROM Sites WHERE ID = ?', (list_of_UID_site[number - 1],))
    sql_start_tables.DataBase.commit()


    
def sql_get_last_date(UID_Site : str):
    sql_start_tables.cur.execute('SELECT Check_Date FROM Log WHERE ID = ? ORDER BY Check_date DESC', (UID_Site,))
    check_date = str(sql_start_tables.cur.fetchone())
    check_date = re.sub(r'[,\'\"\(\)]', '', check_date)
    return check_date