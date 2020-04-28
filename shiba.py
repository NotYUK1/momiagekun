import discord
from discord.ext import commands
import random
import sqlite3
import numpy as np
import setting
import os
import traceback

client = commands.Bot(command_prefix='.')
token = os.environ['DISCORD_BOT_TOKEN']

w = t = m = pn = multi = 0
shp = php = 200
cost = 50
logs = smode = user = ''
conn = sqlite3.connect('shiba.db')

tlist = [0,20]
serifu = ['こんにちは！しばです！','っざけんなまじでー','gg']
p_list = ['しば','TR','T2']
w_word = ['\nおっやるやん','\nいや勝てるわけないやん！','\n信じてましたよ']
l_word = ['\ngg','\nセンスないよ笑','\nまだまだだね']
ns_word = ['\n相打ちだな','\n相打ちだな','\n相打ちだな']
w_list = ['師匠，お願いします！\nT2「やっちゃいますかー」','TRさん，やりましょう\nTR「は？！」','やるか']

pattern = ['🍒','🔵','🍉','🔔','🥺','💩']

@clien.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)

@client.command()
async def shelp(ctx):
    await ctx.message.channel.send(""">>> コマンド一覧
.status    自分のステータスを表示します
.slot      50GG消費してスロットを回します
.roll      500GG消費してスロットを10回転します
.jackpot   現在のJackPotを表示します
.ranking   ランキングを表示します
**タイマンしよう**　タイマンを開始します，以下を使用可能です
**ポンプ**　　　　　ショットガンでダメージを与え合います
**ツルハシ**　　　　ツルハシでダメージを与え合います
**やっぱいいや**　　タイマンを終了します
チャットに"！"が含まれている場合文字数に応じてGPが貯まります""")

@client.command()
async def status(ctx):
    gg = conn.execute("SELECT * FROM GG_Table WHERE id=?", (ctx.message.author.id,)).fetchone()
    if gg:
        sta ='>>> {}は{}GG持ってるやで\nGPは{}やで'.format(ctx.message.author.name,gg[1],gg[2])
    else:
        sta ='>>> タイマンしてGGを貯めるやで'
    await ctx.message.channel.send(sta)

@client.command()
async def slot(ctx):
    global w
    w = 0
    jp = conn.execute("SELECT jackpot FROM JP_Table WHERE id=1").fetchone()
    bet = conn.execute("SELECT gg FROM GG_Table WHERE id=?", (ctx.message.author.id,)).fetchone()
    if bet:
        if bet[0] < cost:
            await ctx.message.channel.send('>>> GGが足りないやで')
        else:
            res = get_slot(jp[0])
            await ctx.message.channel.send(res[0] + '\n>>> {}GG獲得'.format(res[1]))
            conn.execute("UPDATE GG_Table SET gg=? WHERE id=?", (bet[0] - cost + res[1],ctx.message.author.id,))
            if w == 1:
                hit = conn.execute("SELECT jackpot FROM JP_Table WHERE id=?", (ctx.message.author.id,)).fetchone()
                if hit:
                    conn.execute("UPDATE JP_Table SET jackpot=? WHERE id=?", (hit + jp[0],ctx.message.author.id,))
                else:
                    conn.execute("INSERT INTO JP_Table VALUES(?,?)", (ctx.message.author.id, jp[0],))
                conn.execute("UPDATE JP_Table SET jackpot=0 WHERE id=1")
            else:
                conn.execute("UPDATE JP_Table SET jackpot=? WHERE id=1", (jp[0] + cost/2,))
            conn.commit()
    else:
        await ctx.message.channel.send('>>> タイマンしてGGを貯めるやで')

@client.command()
async def roll(ctx):
    global w
    w = 0
    n = 10
    jp = conn.execute("SELECT jackpot FROM JP_Table WHERE id=1").fetchone()
    have = conn.execute("SELECT gg FROM GG_Table WHERE id=?", (ctx.message.author.id,)).fetchone()
    if have:
        bet = n * cost
        pat = []
        if have[0] < bet:
            await ctx.message.channel.send('>>> GGが足りないやで')
        else:
            get = 0
            for i in range(n):
                res = get_slot(jp[0])
                pat.append(res[0])
                get = get + res[1]
            await ctx.message.channel.send("\n".join(pat) + '\n>>> {}GG獲得'.format(get))
            conn.execute("UPDATE GG_Table SET gg=? WHERE id=?", (have[0] - bet + get,ctx.message.author.id,))
            if w == 1:
                hit = conn.execute("SELECT jackpot FROM JP_Table WHERE id=?", (ctx.message.author.id,)).fetchone()
                if hit:
                    conn.execute("UPDATE JP_Table SET jackpot=? WHERE id=?", (hit + jp[0],ctx.message.author.id,))
                else:
                    conn.execute("INSERT INTO JP_Table VALUES(?,?)", (ctx.message.author.id, jp[0],))
                conn.execute("UPDATE JP_Table SET jackpot=0 WHERE id=1")
            else:
                conn.execute("UPDATE JP_Table SET jackpot=? WHERE id=1", (jp[0] + bet/2,))
            conn.commit()
    else:
        await ctx.message.channel.send('>>> タイマンしてGGを貯めるやで')

@client.command()
async def jackpot(ctx):
    jp = conn.execute("SELECT jackpot FROM JP_Table WHERE id=1").fetchone()
    winners = conn.execute("SELECT * FROM JP_Table WHERE id > 1").fetchall()
    rich = {}
    for winner in winners:
        c = client.get_user(winner[0])
        if not c: continue
        winner_id = winner[0]
        if not winner_id in rich:
            rich[winner_id] = [c.name,winner[1]]
    await ctx.message.channel.send('>>> 現在のJackPotは{}GGやで'.format(jp[0]) + "\n__過去の当選者__\n{}".format("\n".join("{} ({}GG)".format(a[0], a[1]) for a in rich.values())))


@client.command()
async def ranking(ctx):
    GG = rank(conn.execute("SELECT id,gg FROM GG_Table ORDER BY gg DESC").fetchall(),"GG")
    GP = rank(conn.execute("SELECT id,gp FROM GG_Table ORDER BY gp DESC").fetchall(),"GP")
    await ctx.message.channel.send(">>> " + GG + "\n\n" + GP)

@client.event
async def on_message(message):
    if message.author != client.user:
        global t,m,shp,php,user
        if message.content == '計算して' and t == 0:
            t = 1
            await message.channel.send('そんなんもわかんねえのか？')
        if message.content != '計算して' and t == 1:
            s = eval(message.content)
            baka = str(s + 1) + 'じゃね？'
            await message.channel.send(baka)
            t = 0

        if message.content == 'しば':
            n = random.randint(0,2)
            await message.channel.send(serifu[n])

        if message.content == 'タイマンしよう' and m == 0:
            tmode = mode()
            user = message.author.name
            await message.channel.send(tmode)
            m = 1

        if message.content == 'ポンプ' and m == 1 and user == message.author.name:
            results = result(random.randint(0,200),damage())
            if shp > 0 and php > 0:
                await message.channel.send(results[0])
            else:
                await message.channel.send(results[0] + '\n>>> {}は{}GGを得た'.format(message.author.name,results[1]))
                get_gg(message.author.id, results[1])
                conn.commit()
                m = 0
                shp = php = 200
                
        if message.content == 'ツルハシ' and m == 1 and user == message.author.name:
            results = result(tlist[random.randint(0,1)],tlist[random.randint(0,1)],)
            if shp > 0 and php > 0:
                await message.channel.send(results[0])
            else:
                await message.channel.send(results[0] + '\n>>> {}は{}GGを得た'.format(message.author.name,results[1]))
                get_gg(message.author.id, results[1])
                conn.commit()
                m = 0
                shp = php = 200
        if message.content == 'Aimbot' and m == 1 and user == message.author.name:
            results = result(200,damage())
            await message.channel.send(results[0])
            m = aim = 0
            shp = php = 200

        if message.content == 'やっぱいいや' and m == 1 and user == message.author.name:
            await message.channel.send('おい')
            m = 0
            shp = php = 200

        if '！' in message.content:
            ngp = len(message.content)
            gp = '>>> {}のGPが{}たまりました'.format(message.author.name,ngp)
            get_gp(message.author.id, ngp)
            conn.commit()
            await message.channel.send(gp)

    await client.process_commands(message)

def mode():
    global pn,multi
    pn = random.randint(0,9)
    if pn == 2:
        multi = 5
        smode = '師匠，お願いします！\nT2「やっちゃいますかー」'
    elif pn == 1:
        multi = 2
        smode = 'TRさん，やりましょう\nTR「は？！」'
    else:
        pn = 0
        multi = 1
        smode = 'やるか'
    return smode

def damage():
    if pn == 2:
        sn = random.randint(110,220)
    elif pn == 1:
        sn = random.randint(0,100)
    else:
        sn = random.randint(90,200)
    return sn

def taiman(udmg,edmg):
    global shp,php
    n = udmg
    sn = edmg
    shp = shp - n
    shp = max(0,shp)
    php = php - sn
    php = max(0,php)
    dmg = str(n) + 'ダメージ'
    sdmg = str(sn) + 'ダメージ'
    log = '```\n' + p_list[pn] + 'に' + dmg + '\n' + p_list[pn] + 'のHP:' + str(shp) + '/200\n━━━━━━━━━━\n' + user + 'に' + sdmg + '\n' + user + 'のHP:' + str(php) + '/200\n```'
    return log


def result(udmg,edmg):
    logs = taiman(udmg,edmg)
    if shp == 0 and php > 0:
        win = logs + w_word[pn]
        result = win
        gg = php * multi + 50
    elif shp > 0 and php == 0:
        lose = logs + l_word[pn]
        result = lose
        gg = 25 * multi
    elif shp > 0 and php > 0:
        result = logs
        gg = 0
    elif shp == 0 and php == 0:
        ai = logs + ns_word[pn]
        result = ai
        gg = 50 * multi
    return result,gg

def get_gg(user_id, ugg):
    gg_count = conn.execute("SELECT gg FROM GG_Table WHERE id=?", (user_id,)).fetchone()
    if gg_count:
        conn.execute("UPDATE GG_Table SET gg=? WHERE id=?", (gg_count[0] + ugg,user_id,))
    else:
        conn.execute("INSERT INTO GG_Table VALUES(?,?,0)", (user_id, ugg,))

def get_gp(user_id, ugp):
    gp_count = conn.execute("SELECT gp FROM GG_Table WHERE id=?", (user_id,)).fetchone()
    if gp_count:
        conn.execute("UPDATE GG_Table SET gp=? WHERE id=?", (gp_count[0] + ugp,user_id,))
    else:
        conn.execute("INSERT INTO GG_Table VALUES(?,0,?)", (user_id, ugp,))


def get_slot(jp):
    global w
    left = np.random.choice(6, p=[0.24, 0.3, 0.09, 0.2, 0.1, 0.07])
    center = np.random.choice(6, p=[0.2, 0.3, 0.1, 0.15, 0.14, 0.11])
    right = np.random.choice(6, p=[0.19, 0.3, 0.25, 0.08, 0.09, 0.09])
    screan = pattern[left] + pattern[center] + pattern[right]
    if left == center == right == 5:
        coin = jp
        w = 1
    elif left == center == right == 4:
        coin = 6000
    elif left == center == right == 3:
        coin = 3000
    elif left == center == right == 2:
        coin = 1000
    elif left == center == right == 1:
        coin = cost
    elif left == center == right == 0:
        coin = 500
    elif left == center == 0:
        coin = 150
    elif left == 0:
        coin = 77
    else:
        coin = 0
    return screan,coin

def rank(players,what):
    rank = {}
    for player in players:
        c = client.get_user(player[0])
        if not c: continue
        playerid = player[0]
        if not playerid in rank:
            rank[playerid] = [c.name, player[1]]
    return "{}ランキング\n{}".format(what,"\n".join("{}位：{} ({}{})".format(i + 1, a[0], a[1],what) for i, a in enumerate(rank.values())))

client.run(token)
