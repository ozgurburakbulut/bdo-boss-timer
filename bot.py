import datetime
import io
import asyncio
import discord
from discord.ext import commands
from os import getenv


async def print_boss_message(boss_name, role, channel, delta):
    if len(boss_name) == 1:
        await channel.send(
            '{role.mention} - {boss[0].mention} spawn olacak {delta}min'.format(role=role, boss=boss_name,
                                                                                 delta=delta))
    elif len(boss_name) == 2:
        await channel.send(
            '{role.mention} - {boss[0].mention} e {boss[1].mention} spawn olacak {delta}min'.format(role=role,
                                                                                                     boss=boss_name,
                                                                                                     delta=delta))


async def print_next_boss_message(boss_name, boss_time, channel):
    if len(boss_name) == 1:
        await channel.send('Bir sonraki boss {boss[0].mention} às {time}'.format(boss=boss_name, time=boss_time))
    elif len(boss_name) == 2:
        await channel.send(
            'Sıradaki bosslar {boss[0].mention} e {boss[1].mention} às {time}'.format(boss=boss_name,
                                                                                            time=boss_time))


file = io.open("boss_schedule.txt", "r").read()
boss_schedule = eval(file)

description = 'Bot MENA sunucusu için olan bossları gönderecek'
bot = commands.Bot(command_prefix='.', description=description)
token = getenv('BOT_TOKEN')


@bot.event
async def on_ready():
    print('Bot ID: ', bot.user.id)
    print('Bot name: ', bot.user.name)
    print('---------------')
    print('Bot kullanılmaya hazır')
    print('Bot şu serverlarda kullanılıyor: ')
    for guild in bot.guilds:
        print(guild)


@bot.command()
async def peixinho(ctx):
    await ctx.send('blup blup')


@bot.command()
async def notifyme(ctx):
    user = ctx.message.author
    role = discord.utils.get(ctx.guild.roles, name='Boss Timer')
    await user.add_roles(role)
    await ctx.send('Boss çıktığında bilgilendirileceksiniz')


@bot.command()
async def removeme(ctx):
    user = ctx.message.author
    role = discord.utils.get(ctx.guild.roles, name='Boss Timer')
    await user.remove_roles(role)
    await ctx.send('Boss çıktığında bilgilendirilmeyeceksiniz')


@bot.command()
async def setchannel(ctx):
    channel = ctx.message.channel
    guild = ctx.message.guild
    role = discord.utils.get(ctx.guild.roles, name='Boss Timer')
    bot.bg_task = bot.loop.create_task(background_task(channel, guild, role))
    await ctx.send('Bilgiler bu kanaldan yapılacak: {0.mention}'.format(channel))


@bot.command()
async def stoppls(ctx):
    if bot.bg_task:
        bot.bg_task.cancel()
        try:
            await bot.bg_task
        except asyncio.CancelledError:
            print('Görev yapılmayacak')
        finally:
            pass
    await ctx.send('Bot durdu')


@bot.command()
async def nextboss(ctx):
    channel = ctx.message.channel
    guild = ctx.message.guild

    current_time = datetime.datetime.now()
    current_hour = datetime.datetime.strftime(current_time, "%H:%M")
    current_day = datetime.datetime.strftime(current_time, "%a")
    next_day = datetime.datetime.strftime(current_time + datetime.timedelta(days=1), "%a")

    for hour in boss_schedule.keys():
        if current_hour < hour:
            next_boss_spawn = boss_schedule[hour][current_day]
            break
        # if there is no boss to spawn on the current day
        # then it should be the first boss of the next day
        next_boss_spawn = boss_schedule['02:00'][next_day]

    boss_names = []
    for boss in next_boss_spawn:
        boss_names.append((discord.utils.get(guild.roles, name=boss)))

    await print_next_boss_message(boss_names, hour, channel)


@bot.event
async def background_task(channel, guild, role):
    await bot.wait_until_ready()
    print('Bot kullanılmaya hazır')
    while not bot.is_closed():
        current_time = datetime.datetime.now()
        current_hour = datetime.datetime.strftime(current_time, "%H:%M")
        current_hour_p5 = datetime.datetime.strftime(current_time + datetime.timedelta(minutes=5), "%H:%M")
        current_day = datetime.datetime.strftime(current_time, "%a")

        print('Current time: {current_time} | Current+5: {current_hour_p5}'.format(current_time=current_hour,
                                                                                   current_hour_p5=current_hour_p5))

        next_boss_spawn = []
        for hour in boss_schedule.keys():
            if current_hour < hour <= current_hour_p5:
                delta = datetime.datetime.strptime(hour, "%H:%M") - datetime.datetime.strptime(current_hour, "%H:%M")
                next_boss_spawn = boss_schedule[hour][current_day]
                break

        print('Sonraki bossun çıkma zamanı...')

        if next_boss_spawn:
            boss_names = []

            for boss in next_boss_spawn:
                print(boss)
                boss_names.append((discord.utils.get(guild.roles, name=boss)))

            await print_boss_message(boss_names, role, channel, int(delta.seconds / 60))

        await asyncio.sleep(60)


bot.run(token)
