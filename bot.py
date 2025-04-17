import discord
from discord.ext import commands, tasks
from itertools import cycle
import os
from dotenv import load_dotenv

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='+', intents=intents)

# Список кастомных статусов — можешь дополнять или менять!
STATUS_LIST = cycle([
    "❤️ t.me/rematch_cis",
    "🧡 discord.gg/rematch-cis",
    "💛 vk.com/rematch_cis",
    "💚 tiktok.com/@rematchcis",
    "🩵 youtube.com/@rachillbl",
])

# Цикл для обновления статуса
@tasks.loop(seconds=15)
async def update_status():
    current_status = next(STATUS_LIST)

    # Обновляем статус с кастомным текстом (без префикса "играет")
    activity = discord.CustomActivity(name=current_status)
    
    # Обновляем статус
    await bot.change_presence(activity=activity, status=discord.Status.online)
    print(f"Статус обновлен: {current_status}")  # Подтверждаем, что статус обновлен

# Укажи здесь ID голосового канала
VOICE_CHANNEL_ID = 1356026013078786108  # Замени на актуальный ID

@tasks.loop(seconds=30)
async def update_voice_channel_name():
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel is None:
        print("❌ Канал не найден. Проверь VOICE_CHANNEL_ID.")
        return

    if not isinstance(channel, discord.VoiceChannel):
        print("❌ Указанный канал не является голосовым.")
        return

    guild = channel.guild
    member_count = len([member for member in guild.members if not member.bot])
    new_name = f"⚽・Рематчеры: {member_count}"

    try:
        await channel.edit(name=new_name)
        print(f"✅ Название голосового канала обновлено: {new_name}")
    except discord.Forbidden:
        print("❌ У бота нет прав на изменение канала.")
    except Exception as e:
        print(f"❌ Произошла ошибка при изменении названия канала: {e}")


# ===== Команды модерации =====
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Без причины"):
    await member.ban(reason=reason)
    await ctx.send(f"{member} забанен. Причина: {reason}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Без причины"):
    await member.kick(reason=reason)
    await ctx.send(f"{member} кикнут. Причина: {reason}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason="Без причины"):
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await ctx.guild.create_role(name="Muted")
        for ch in ctx.guild.channels:
            await ch.set_permissions(mute_role, speak=False, send_messages=False)
    await member.add_roles(mute_role, reason=reason)
    await ctx.send(f"{member} замучен. Причина: {reason}")

@bot.event
async def on_ready():
    print(f"🟢 Бот {bot.user} запущен.")
    update_status.start()  # <== Запускаем цикл статуса!
    update_voice_channel_name.start()

# Запуск бота
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
