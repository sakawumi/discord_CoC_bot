#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord # インストールした discord.py
import random
import re
import configparser
from asyncio import sleep
from collections import OrderedDict

client = discord.Client() # 接続に使用するオブジェクト
#global変数
player_data = {}
char_data = {}
init_skills = { "キック":25,
                "組み付き":25,
                "こぶし":50,
                "頭突き":10,
                "投擲":25,
                "マーシャルアーツ":1,
                "拳銃":20,
                "サブマシンガン":15,
                "ショットガン":30,
                "マシンガン":15,
                "ライフル":25,
                "応急手当":30,
                "鍵開け":1,
                "隠す":15,
                "隠れる":10,
                "聞き耳":25,
                "忍び歩き":10,
                "写真術":10,
                "精神分析":1,
                "追跡":10,
                "登攀":40,
                "図書館":25,
                "目星":25,
                "運転":20,
                "機械修理":20,
                "重機械操作":1,
                "乗馬":5,
                "水泳":25,
                "製作":5,
                "操縦":1,
                "跳躍":25,
                "電気修理":10,
                "ナビゲート":10,
                "変装":1,
                "言いくるめ":5,
                "信用":15,
                "説得":15,
                "値切り":5,
                "母国語":20,
                "医学":5,
                "オカルト":5,
                "化学":1,
                "クトゥルフ神話":0,
                "芸術":5,
                "経理":10,
                "考古学":1,
                "コンピューター":1,
                "心理学":5,
                "人類学":1,
                "生物学":1,
                "地質学":1,
                "電子工学":1,
                "天文学":1,
                "博物学":10,
                "物理学":1,
                "法律":5,
                "薬学":1,
                "歴史":20}

craziness_table = { 1 :"",
                    2 :"",
                    3 :"",
                    4 :"",
                    5 :"",
                    6 :"",
                    7 :"",
                    8 :"",
                    9 :"",
                    0 :""}

# 起動時に通知してくれる処理
@client.event
async def on_ready():
    pass
@client.event
async def on_message(message):
    try:    
        if not message.content.startswith('/'):
            return

        sleep_time = 1
        if message.content.startswith('/r'):
            use_str = re.sub(r"(/r| |　)" , "" , message.content)
            player_name = str(message.author)
            char_name = player_data[player_name]
            if re.fullmatch(r"[0-9]*d[0-9]+" , use_str):
                dice_num = dice_roll(use_str)
                send_str = f"{char_name} Roll {use_str} : {dice_num} {message.author.mention}"
                
            elif re.fullmatch(r"[0-9]*d[0-9]+\+[0-9]?d[0-9]+" , use_str):
                dire_info = re.search(r"([0-9]*d[0-9]+)\+([0-9]*d[0-9]+)" , use_str)
                dice1 = dire_info.group(1)
                dice2 = dire_info.group(2)
                dice1n = dice_roll(dice1)
                dice2n = dice_roll(dice2)
                sum_n = int(dice1n) + int(dice2n)
                send_str = f"{char_name} Roll {dice1} + {dice2} : {dice1n} + {dice2n} = {sum_n} {message.author.mention}"

            elif re.fullmatch(r"[0-9]*d[0-9]+\+[0-9]+" , use_str):
                dire_info = re.search(r"([0-9]*d[0-9]+)\+([0-9]+)" , use_str)
                dice1 = dire_info.group(1)
                num = dire_info.group(2)
                dice1n = dice_roll(dice1)
                sum_n = int(dice1n) + int(num)
                send_str = f"{char_name} Roll {dice1} + {num} : {dice1n} + {num} = {sum_n} {message.author.mention}"

            elif re.fullmatch(r"\S+" , use_str):
                status_num =  int(get_char_status(char_name , use_str))
                roll_num = dice_roll('1d100')

                if roll_num <= 5:
                    result = '**Critical!!**'
                    char_name = f"**{char_name}**"

                elif roll_num <= status_num:
                    result = 'Success!'
                    char_name = f"**{char_name}**"

                elif roll_num >= 96:
                    result = '**Fumble!!**'

                elif roll_num > status_num:
                    result = 'Failed...'

                send_str = f"{char_name} : {result} : {use_str} {roll_num:02} <= {status_num:02} {message.author.mention}"

            else:
                send_str = f"/ Bat Format {message.author.mention}"
                sleep_time = 3

            await client.send_message(message.channel, send_str)

        elif message.content.startswith('/init'):
            init_char()
            init_craziness()
            await client.send_message(message.channel, 'init Success')
            return

        elif message.content.startswith('/set'):
            info = re.search(r"/set *\[(.*)\]\s*\[(.*)\]\s*\[(.*)\]" , message.content)
            char_name = info.group(1)
            status_name = info.group(2)
            val = info.group(3)
            old_status = get_char_status(char_name , status_name)
            set_char_status(char_name , status_name , val)
            send_str = f"{char_name} {status_name} {old_status} -> {val}"
            await client.send_message(message.channel, send_str)

        elif message.content.startswith('/get'):
            info = re.search(r"/get *\[(.*)\]\s*\[(.*)\]" , message.content)
            char_name = info.group(1)
            status_name = info.group(2)
            val = get_char_status(char_name , status_name)
            send_str = f"{char_name} {status_name} : {val}"
            await client.send_message(message.channel, send_str)

        elif message.content.startswith('/cr'):
            player_name = str(message.author)
            char_name = player_data[player_name]
            dice_num = dice_roll('1d10')
            cra = craziness_table[dice_num - 1]
            send_str = f"{char_name} 1d10 = {dice_num} : {cra} {message.author.mention}"
            await client.send_message(message.channel, send_str)

        elif message.content.startswith('/save'):
            save_ini()
            await client.send_message(message.channel, 'save Success')
            return

        elif message.content.startswith('/connect'):
            info = re.search(r"/connect *\[(.*)\]\s*\[(.*)\]" , message.content)
            player_name = info.group(1)
            char_name = info.group(2)
            connect_PLtoPC(player_name , char_name)
            await client.send_message(message.channel, 'connect Success')
            return

        elif message.content.startswith('/view'):
            info = re.search(r"/view *\[(.*)\]" , message.content)
            char_name = info.group(1)
            send_str = view_char_data(char_name)
            await client.send_message(message.channel, send_str)

        elif message.content.startswith('/ Bat Format '):
            sleep_time = 5

        await sleep(sleep_time)
        await client.delete_message(message)

    except:
        send_str = f"/ Process Error {message.author.mention}"
        await client.send_message(message.channel, send_str)
        sleep_time = 3
        await sleep(sleep_time)
        await client.delete_message(message)
        return

def init_char():
    """
    キャラクター情報初期化
    """
    global char_data
    global ini
    char_data.clear()
    try:
        ini.read("./char.ini" , encoding='utf8')
        for section in ini.sections():
            char_data[section] = OrderedDict()
            for key in ini.options(section):
                 (char_data[section])[key] = ini.get(section, key)
    except:
        raise

def init_craziness():
    """
    狂気表初期化
    """
    global craziness_table
    global cr_ini
    try:
        cr_ini.read("./craziness.ini" , encoding='utf8')
        for i in range(10):
            craziness_table[int(i)] = cr_ini.get('craziness', str(i))
    except:
        raise

def save_ini():
    """
    キャラクター情報保存
    """
    global char_data
    global ini
    try:
        for char_name in char_data:
            for status in char_data[char_name]:


                  ini.set(char_name, status ,(char_data[char_name])[status])
        with open("./char.ini", "w", encoding='utf8') as f:
            ini.write(f)
    except:
        raise

def connect_PLtoPC(player_name , character_name):
    """
    ユーザーニックネームとキャラクター名の紐づけ

    Parameers
    ----------
    player_name : string
        プレイヤー名(ニックネーム)
    character_name : string
        キャラクター名
    """
    global player_data
    try:
        player_data[player_name] = character_name
    except:
        raise

def dice_roll(dice):
    """
    ダイスロール

    Parameters
    ----------
    dice : str
        ダイス情報
    """
    dice_info = re.search(r"([0-9]*)d([0-9]+)", dice)
    dice_num = 1
    if dice_info.group(1)  != None :
        dice_num = int(dice_info.group(1))

    dice_max = int(dice_info.group(2))
    result = 0
    i = 0
    for i in range(dice_num):
        result += int(random.randint(1 , dice_max))
    return result

def view_char_data(char_name):
    """
    キャラクター情報一括出力

    Parameters
    ----------
    char_name : string
        キャラクター名
    """
    global char_data
    try:
        send_str = f'«{char_name}»\r\n'
        for status in char_data[char_name]:
              send_str += f'{status}:{(char_data[char_name])[status]}'
              send_str += '\r\n'

        return send_str
    except:
        raise

def set_char_status(character_name , skill_name , val):
    """
    キャラクター情報設定

    Parameters
    ----------
    character_name : string
        キャラクター名
    skill_name : string
        ステータス名
    val : int
        技能値
    """
    global char_data
    try:
        (char_data[character_name])[skill_name] = val
    except:
        raise

def get_char_status(character_name , skill_name):
    """
    キャラクター情報取得
    初期値の場合は初期値テーブルから取得

    Parameters
    ----------
    player_name : string
        キャラクター名
    skill_name : string
        ステータス名
    """
    global char_data
    try:
        if skill_name in char_data[character_name]:
            return (char_data[character_name])[skill_name]
        else:
            global init_skills
            return init_skills[skill_name]
    except:
        raise


ini = configparser.SafeConfigParser()
cr_ini = configparser.SafeConfigParser()
init_char()
init_craziness()
token_ini = configparser.SafeConfigParser()
token_ini.read("./token.ini" , encoding='utf8')
tokenID = token_ini.get('general' , 'token')
client.run(tokenID)

