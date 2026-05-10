import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import re
import json
import os
import datetime
import copy

# ==========================================
# НАСТРОЙКИ
# ==========================================
TOKEN = os.getenv("DISCORD_TOKEN")
DATA_FILE = "characters.json"

# ==========================================
# ЗАПУСК БОТА
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# РАБОТА С ДАННЫМИ
# ==========================================
def load_characters():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_characters(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_weapons():
    if os.path.exists("weapons.json"):
        with open("weapons.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_items():
    if os.path.exists("items.json"):
        with open("items.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_attachments():
    if os.path.exists("attachments.json"):
        with open("attachments.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_armor():
    if os.path.exists("armor.json"):
        with open("armor.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_cyberware():
    if os.path.exists("cyberware.json"):
        with open("cyberware.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# ==========================================
# ХАРАКТЕРИСТИКИ
# ==========================================
SHORT_STATS = {
    "интеллект": "ИНТ", "сила воли": "ВОЛЯ", "харизма": "ХАР",
    "эмпатия": "ЭМП", "техника": "ТЕХ", "реакция": "РЕА",
    "удача": "УДЧ", "телосложение": "ТЕЛ", "ловкость": "ЛВК", "скорость": "СКО"
}

STAT_EMOJI = {
    "интеллект": "🧠", "сила воли": "💪", "харизма": "👑",
    "эмпатия": "💙", "техника": "🔧", "реакция": "⚡",
    "удача": "🍀", "телосложение": "🦾", "ловкость": "🤸", "скорость": "💨"
}

# ==========================================
# НАВЫКИ
# ==========================================
SKILLS = {
    "концентрация": {"стат": "сила воли"},
    "выносливость": {"стат": "сила воли"},
    "сопротивление пыткам": {"стат": "сила воли"},
    "сокрытие/раскрытие": {"стат": "интеллект"},
    "чтение по губам": {"стат": "интеллект"},
    "внимательность": {"стат": "интеллект"},
    "выслеживание": {"стат": "интеллект"},
    "обращение с животными": {"стат": "интеллект"},
    "бюрократия": {"стат": "интеллект"},
    "бизнес": {"стат": "интеллект"},
    "композиция": {"стат": "интеллект"},
    "криминология": {"стат": "интеллект"},
    "криптография": {"стат": "интеллект"},
    "дедукция": {"стат": "интеллект"},
    "образование": {"стат": "интеллект"},
    "язык": {"стат": "интеллект"},
    "поиск информации": {"стат": "интеллект"},
    "знание местности": {"стат": "интеллект"},
    "наука": {"стат": "интеллект"},
    "выживание в пустыне": {"стат": "интеллект"},
    "атлетика": {"стат": "ловкость"},
    "акробатика": {"стат": "ловкость"},
    "скрытность": {"стат": "ловкость"},
    "рукопашный бой": {"стат": "ловкость"},
    "уклонение": {"стат": "ловкость"},
    "оружие ближнего боя": {"стат": "ловкость"},
    "вождение": {"стат": "реакция"},
    "пилотирование": {"стат": "реакция", "цена": 2},
    "автоматический огонь": {"стат": "реакция", "цена": 2},
    "пистолеты": {"стат": "реакция"},
    "оружие крупного калибра": {"стат": "реакция", "цена": 2},
    "тактическое оружие": {"стат": "реакция"},
    "актерское мастерство": {"стат": "харизма"},
    "допрос": {"стат": "харизма"},
    "убеждение": {"стат": "харизма"},
    "знаток улиц": {"стат": "харизма"},
    "торговля": {"стат": "харизма"},
    "гардероб и стиль": {"стат": "харизма"},
    "общение": {"стат": "эмпатия"},
    "проницательность": {"стат": "эмпатия"},
    "игра на инструментах": {"стат": "техника"},
    "авиационные технологии": {"стат": "техника"},
    "знание техники": {"стат": "техника"},
    "кибернетика": {"стат": "техника"},
    "подрывник": {"стат": "техника", "цена": 2},
    "электроника/безопасность": {"стат": "техника", "цена": 2},
    "первая помощь": {"стат": "техника"},
    "фальсификация": {"стат": "техника"},
    "автомеханика": {"стат": "техника"},
    "парамедик": {"стат": "техника", "цена": 2},
    "кино-/фототехника": {"стат": "техника"},
    "взлом замков": {"стат": "техника"},
    "карманник": {"стат": "техника"},
    "оружейник": {"стат": "техника"},
}

# ==========================================
# АВТОДОПОЛНЕНИЯ
# ==========================================
async def автодополнение_навыков(interaction: discord.Interaction, current: str):
    все = list(SKILLS.keys())
    if not current:
        return [app_commands.Choice(name=n, value=n) for n in все[:25]]
    подходящие = [n for n in все if current.lower() in n.lower()]
    return [app_commands.Choice(name=n, value=n) for n in подходящие[:25]]

async def автодополнение_навыков_анкетолог(interaction: discord.Interaction, current: str):
    все = ["не указано"] + list(SKILLS.keys())
    if not current:
        return [app_commands.Choice(name=n, value=n) for n in все[:25]]
    подходящие = [n for n in все if current.lower() in n.lower()]
    return [app_commands.Choice(name=n, value=n) for n in подходящие[:25]]

async def автодополнение_оружия(interaction: discord.Interaction, current: str):
    шаблоны = load_weapons()
    все = list(шаблоны.keys())
    if not current:
        return [app_commands.Choice(name=n, value=n) for n in все[:25]]
    подходящие = [n for n in все if current.lower() in n.lower()]
    return [app_commands.Choice(name=n, value=n) for n in подходящие[:25]]

async def автодополнение_обвесов(interaction: discord.Interaction, current: str):
    шаблоны = load_attachments()
    все = list(шаблоны.keys())
    if not current:
        return [app_commands.Choice(name=n, value=n) for n in все[:25]]
    подходящие = [n for n in все if current.lower() in n.lower()]
    return [app_commands.Choice(name=n, value=n) for n in подходящие[:25]]

async def автодополнение_предметов(interaction: discord.Interaction, current: str):
    шаблоны = load_items()
    все = list(шаблоны.keys())
    if not current:
        return [app_commands.Choice(name=n, value=n) for n in все[:25]]
    подходящие = [n for n in все if current.lower() in n.lower()]
    return [app_commands.Choice(name=n, value=n) for n in подходящие[:25]]

async def автодополнение_брони(interaction: discord.Interaction, current: str):
    шаблоны = load_armor()
    все = list(шаблоны.keys())
    if not current:
        return [app_commands.Choice(name=n, value=n) for n in все[:25]]
    подходящие = [n for n in все if current.lower() in n.lower()]
    return [app_commands.Choice(name=n, value=n) for n in подходящие[:25]]

async def автодополнение_имплантов(interaction: discord.Interaction, current: str):
    шаблоны = load_cyberware()
    все = list(шаблоны.keys())
    if not current:
        return [app_commands.Choice(name=n, value=n) for n in все[:25]]
    подходящие = [n for n in все if current.lower() in n.lower()]
    return [app_commands.Choice(name=n, value=n) for n in подходящие[:25]]

# ==========================================
# СИНХРОНИЗАЦИЯ
# ==========================================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Бот {bot.user} готов к работе!")

# ==========================================
# ПЕРСОНАЖ
# ==========================================
@bot.tree.command(name="персонаж", description="Управление персонажем")
@app_commands.describe(действие="Что сделать", имя_персонажа="Имя персонажа", игрок="Игрок (@упоминание)")
@app_commands.choices(действие=[
    app_commands.Choice(name="показать", value="показать"),
    app_commands.Choice(name="создать", value="создать"),
    app_commands.Choice(name="удалить", value="удалить"),
])
async def персонаж(interaction: discord.Interaction, действие: str, имя_персонажа: str = None, игрок: discord.Member = None):
    персонажи = load_characters()

    if действие == "показать":
        цель = игрок or interaction.user
        автор_id = str(цель.id)
        if автор_id not in персонажи:
            await interaction.response.send_message(f"`[ERR]` У {цель.mention} нет персонажа!", ephemeral=True)
            return
        p = персонажи[автор_id]
        embed = discord.Embed(title=f"`[DOSSIER]` {p['имя']}", description=f"О.У.: **{p['оу']}**", color=0x00ffcc)
        статы = p['статы']
        стат_строки = []
        for full_name, short_name in SHORT_STATS.items():
            emoji = STAT_EMOJI.get(full_name, "◆")
            значение = статы.get(full_name, 1)
            if full_name == "удача":
                текущая = p.get('удача_текущая', значение)
                восстановить_удачу(p)
                текущая = p.get('удача_текущая', значение)
                стат_строки.append(f"{emoji} {short_name}: **{текущая}** / {значение}")
            elif full_name == "эмпатия":
                базовая = p.get('базовая_эмпатия', значение)
                текущая_эмп = p.get('человечность', 10) // 10
                стат_строки.append(f"{emoji} {short_name}: **{текущая_эмп}** / {базовая}")
            else:
                стат_строки.append(f"{emoji} {short_name}: **{значение}**")
        половина = len(стат_строки) // 2
        embed.add_field(name="`[CORE]` Характеристики", value='\n'.join(стат_строки[:половина]), inline=True)
        embed.add_field(name="\u200b", value='\n'.join(стат_строки[половина:]), inline=True)
        тело = статы.get('телосложение', 1)
        воля = статы.get('сила воли', 1)
        реакция = статы.get('реакция', 1)
        здоровье = 5 * ((тело + воля) // 2)
        человечность = p.get('человечность', 10)
        эмпатия = человечность // 10
        статы['эмпатия'] = эмпатия
        embed.add_field(name="`[DER]` Производные", value=(
            f"❤️ Здоровье: **{здоровье}**\n🤖 Человечность: **{человечность}**\n🎯 Инициатива: **{реакция}**\n💰 Эдди: **{p['эдди']}** €$"), inline=False)
        if p['импланты']:
            embed.add_field(name="`[IMPL]` Импланты", value='\n'.join([f"◆ {imp}" for imp in p['импланты']]), inline=True)
        else:
            embed.add_field(name="`[IMPL]` Импланты", value="Нет имплантов", inline=True)
        if p['снаряжение']:
            embed.add_field(name="`[GEAR]` Снаряжение", value='\n'.join([f"▸ {item}" for item in p['снаряжение']]), inline=True)
        else:
            embed.add_field(name="`[GEAR]` Снаряжение", value="Пусто", inline=True)
        # Броня
        надета = p.get('надето_броня', {"голова": None, "тело": None})
        броня_стр = []
        for слот, item in надета.items():
            if item:
                броня_стр.append(f"🛡️ {слот}: **{item['название'].title()}** (защита: {item['шаблон']['защита']})")
        if броня_стр:
            embed.add_field(name="`[ARM]` Броня", value='\n'.join(броня_стр), inline=True)
        # Киберимпланты
        уст_имп = p.get('установлено_импланты', {})
        имп_стр = []
        for слот, импланты in уст_имп.items():
            for имп in импланты:
                имп_стр.append(f"⚡ {слот}: **{имп['название'].title()}** — {имп['шаблон']['эффект']}")
        if имп_стр:
            embed.add_field(name="`[CYB]` Киберимпланты", value='\n'.join(имп_стр), inline=True)
        if человечность < 0:
            embed.add_field(name="`[PSY]` Статус", value="**НЕКОНТРОЛИРУЕМЫЙ КИБЕРПСИХ**\n*Управление невозможно.*", inline=False)
        elif эмпатия == 0:
            embed.add_field(name="`[PSY]` Статус", value="Киберпсихоз\n*Штраф -2 к харизме*", inline=False)
        elif эмпатия == 1:
            embed.add_field(name="`[PSY]` Статус", value="-# *Диссоциативное расстройство*\n-# *Штраф -1 к харизме*", inline=False)
        embed.set_footer(text=f"NetRunner ID: {цель.name}")
        await interaction.response.send_message(embed=embed)

    elif действие == "создать":
        if "Анкетолог" not in [р.name for р in interaction.user.roles]:
            await interaction.response.send_message("`[ERR]` Только Анкетолог!", ephemeral=True)
            return
        if not имя_персонажа or not игрок:
            await interaction.response.send_message("`[ERR]` Укажи имя и игрока!", ephemeral=True)
            return
        if len(имя_персонажа) > 30:
            await interaction.response.send_message("`[ERR]` Максимум 30 символов!", ephemeral=True)
            return
        цель_id = str(игрок.id)
        if цель_id in персонажи:
            await interaction.response.send_message(f"`[WARN]` У {игрок.mention} уже есть персонаж!", ephemeral=True)
            return
        персонажи[цель_id] = {
            "имя": имя_персонажа, "оу": 0, "эдди": 1000,
            "статы": {"интеллект": 1, "сила воли": 1, "харизма": 1, "эмпатия": 1, "техника": 1, "реакция": 1, "удача": 1, "телосложение": 1, "ловкость": 1, "скорость": 1},
            "навыки": {}, "удача_текущая": 1, "удача_последняя_трата": None, "человечность": 10, "базовая_эмпатия": 1,
            "снаряжение": [], "надетое_снаряжение": [], "оружие": [], "руки": {"правая": None, "левая": None}, "быстрый_доступ": [],
            "броня": [], "надето_броня": {"голова": None, "тело": None},
            "киберимпланты": [],
            "установлено_импланты": {
                "стилевые": [], "нейронные": [], "оптика_правая": [], "оптика_левая": [],
                "аудио": [], "внутренние": [], "внешние": [],
                "рука_правая": [], "рука_левая": [], "нога_правая": [], "нога_левая": []
            },
            "открытые_слоты": {},
        }
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` ✅ Персонаж **{имя_персонажа}** создан для {игрок.mention}!")

    elif действие == "удалить":
        if "Анкетолог" not in [р.name for р in interaction.user.roles]:
            await interaction.response.send_message("`[ERR]` Только Анкетолог!", ephemeral=True)
            return
        if not игрок:
            await interaction.response.send_message("`[ERR]` Укажи игрока!", ephemeral=True)
            return
        цель_id = str(игрок.id)
        if цель_id not in персонажи:
            await interaction.response.send_message(f"`[ERR]` У {игрок.mention} нет персонажа!", ephemeral=True)
            return
        del персонажи[цель_id]
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` Персонаж {игрок.mention} удалён.")

# ==========================================
# АНКЕТОЛОГ
# ==========================================
@bot.tree.command(name="установить_статы", description="[Анкетолог] Установить характеристики")
@app_commands.describe(игрок="Игрок", интеллект="1-8", сила_воли="1-8", харизма="1-8", эмпатия="1-8", техника="1-8", реакция="1-8", удача="1-8", телосложение="1-8", ловкость="1-8", скорость="1-8")
async def установить_статы(interaction: discord.Interaction, игрок: discord.Member, интеллект: int = 1, сила_воли: int = 1, харизма: int = 1, эмпатия: int = 1, техника: int = 1, реакция: int = 1, удача: int = 1, телосложение: int = 1, ловкость: int = 1, скорость: int = 1):
    if "Анкетолог" not in [р.name for р in interaction.user.roles]:
        await interaction.response.send_message("`[ERR]` Только Анкетолог!", ephemeral=True)
        return
    персонажи = load_characters()
    цель_id = str(игрок.id)
    if цель_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` Нет персонажа!", ephemeral=True)
        return
    статы = {"интеллект": интеллект, "сила воли": сила_воли, "харизма": харизма, "эмпатия": эмпатия, "техника": техника, "реакция": реакция, "удача": удача, "телосложение": телосложение, "ловкость": ловкость, "скорость": скорость}
    for v in статы.values():
        if v < 1 or v > 8:
            await interaction.response.send_message("`[ERR]` 1-8!", ephemeral=True)
            return
    if sum(статы.values()) > 45:
        await interaction.response.send_message("`[ERR]` Сумма > 45!", ephemeral=True)
        return
    персонажи[цель_id]['статы'] = статы
    персонажи[цель_id]['базовая_эмпатия'] = статы['эмпатия']
    персонажи[цель_id]['человечность'] = статы['эмпатия'] * 10
    save_characters(персонажи)
    await interaction.response.send_message(f"`[SYS]` Статы {игрок.mention} установлены!")

@bot.tree.command(name="установить_навыки", description="[Анкетолог] Установить навыки")
@app_commands.autocomplete(навык1=автодополнение_навыков_анкетолог, навык2=автодополнение_навыков_анкетолог, навык3=автодополнение_навыков_анкетолог, навык4=автодополнение_навыков_анкетолог, навык5=автодополнение_навыков_анкетолог)
@app_commands.describe(игрок="Игрок", навык1="Навык 1", уровень1="0-8", навык2="Навык 2", уровень2="0-8", навык3="Навык 3", уровень3="0-8", навык4="Навык 4", уровень4="0-8", навык5="Навык 5", уровень5="0-8")
async def установить_навыки(interaction: discord.Interaction, игрок: discord.Member, навык1: str = None, уровень1: int = 0, навык2: str = None, уровень2: int = 0, навык3: str = None, уровень3: int = 0, навык4: str = None, уровень4: int = 0, навык5: str = None, уровень5: int = 0):
    if "Анкетолог" not in [р.name for р in interaction.user.roles]:
        await interaction.response.send_message("`[ERR]` Только Анкетолог!", ephemeral=True)
        return
    персонажи = load_characters()
    цель_id = str(игрок.id)
    if цель_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` Нет персонажа!", ephemeral=True)
        return
    p = персонажи[цель_id]
    if 'навыки' not in p: p['навыки'] = {}
    потрачено = sum(p['навыки'].values())
    лимит = 4 if (потрачено == 0 and p['оу'] == 0) else 8
    for назв, ур in [(навык1, уровень1), (навык2, уровень2), (навык3, уровень3), (навык4, уровень4), (навык5, уровень5)]:
        if not назв or назв == "не указано": continue
        if назв not in SKILLS:
            await interaction.response.send_message(f"`[ERR]` Навык «{назв}» не найден!", ephemeral=True)
            return
        if ур < 0 or ур > лимит:
            await interaction.response.send_message(f"`[ERR]` 0-{лимит}!", ephemeral=True)
            return
        if ур == 0:
            if назв in p['навыки']: del p['навыки'][назв]
        else:
            p['навыки'][назв] = ур
    save_characters(персонажи)
    await interaction.response.send_message(f"`[SYS]` Навыки {игрок.mention} установлены!")

# ==========================================
# УДАЧА
# ==========================================
def восстановить_удачу(p):
    from datetime import datetime, timedelta
    макс = p['статы'].get('удача', 1)
    тек = p.get('удача_текущая', макс)
    посл = p.get('удача_последняя_трата')
    if тек >= макс: return тек, 0
    if not посл: return макс, макс - тек
    try:
        разница = datetime.now() - datetime.fromisoformat(посл)
        восст = int(разница.total_seconds() / 3600 // 48)
        if восст > 0:
            новая = min(макс, тек + восст)
            p['удача_текущая'] = новая
            p['удача_последняя_трата'] = (datetime.fromisoformat(посл) + timedelta(hours=48 * (новая - тек))).isoformat()
            return новая, новая - тек
    except: pass
    return тек, 0

# ==========================================
# ЧЕЛОВЕЧНОСТЬ
# ==========================================
@bot.tree.command(name="человечность", description="Изменить человечность")
@app_commands.describe(игрок="Игрок", изменение="+/-")
async def человечность(interaction: discord.Interaction, игрок: discord.Member, изменение: int):
    if "Гейммастер" not in [р.name for р in interaction.user.roles]:
        await interaction.response.send_message("`[ERR]` Только Гейммастер!", ephemeral=True)
        return
    персонажи = load_characters()
    цель_id = str(игрок.id)
    if цель_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` Нет персонажа!", ephemeral=True)
        return
    p = персонажи[цель_id]
    if 'человечность' not in p: p['человечность'] = p['статы'].get('эмпатия', 1) * 10
    старая = p['человечность']
    новая = max(0, старая + изменение)
    базовая = p.get('базовая_эмпатия', p['статы'].get('эмпатия', 1))
    if новая > базовая * 10: новая = базовая * 10
    p['человечность'] = новая
    p['статы']['эмпатия'] = новая // 10
    save_characters(персонажи)
    псих = ""
    if новая < 0: псих = "\n💀💀💀 НЕКОНТРОЛИРУЕМЫЙ КИБЕРПСИХ! 💀💀💀"
    elif новая // 10 == 0: псих = "\n⚠️ КИБЕРПСИХОЗ!"
    elif новая // 10 == 1: псих = "\n*Диссоциативное расстройство*"
    await interaction.response.send_message(f"💀 {p['имя']}: {старая} → **{новая}**\nЭмпатия: **{новая // 10}**{псих}")

# ==========================================
# СТАТ
# ==========================================
@bot.tree.command(name="стат", description="Показать характеристики")
@app_commands.describe(игрок="Чей лист")
async def стат(interaction: discord.Interaction, игрок: discord.Member = None):
    персонажи = load_characters()
    цель = игрок or interaction.user
    автор_id = str(цель.id)
    if автор_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` Нет персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    статы = p['статы']
    embed = discord.Embed(title=f"`[STAT]` {p['имя']}", description=f"О.У.: **{p['оу']}**", color=0x00ccff)
    for full_name, short_name in SHORT_STATS.items():
        emoji = STAT_EMOJI.get(full_name, "◆")
        значение = статы.get(full_name, 1)
        if full_name == "удача":
            восстановить_удачу(p)
            embed.add_field(name=f"{emoji} {full_name.upper()} [{short_name}]", value=f"**{p.get('удача_текущая', значение)}**", inline=True)
        elif full_name == "эмпатия":
            embed.add_field(name=f"{emoji} {full_name.upper()} [{short_name}]", value=f"**{p.get('базовая_эмпатия', значение)}**", inline=True)
        else:
            embed.add_field(name=f"{emoji} {full_name.upper()} [{short_name}]", value=f"**{значение}**", inline=True)
    embed.set_footer(text="Максимум: 8")
    await interaction.response.send_message(embed=embed)

# ==========================================
# НАВЫК
# ==========================================
@bot.tree.command(name="навык", description="Показать навыки")
@app_commands.choices(группа=[
    app_commands.Choice(name="ИНТ", value="инт"),
    app_commands.Choice(name="ТЕХ", value="тех"),
    app_commands.Choice(name="РЕА+ВОЛЯ", value="реа_воля"),
    app_commands.Choice(name="ЛВК+ХАР", value="лвк_хар"),
])
async def навык(interaction: discord.Interaction, группа: str = "инт"):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    статы = p['статы']
    if 'навыки' not in p: p['навыки'] = {}
    навыки_игрока = p['навыки']
    потрачено = sum(навыки_игрока.values())
    группы = {"инт": ["интеллект"], "тех": ["техника"], "реа_воля": ["реакция", "сила воли"], "лвк_хар": ["ловкость", "харизма"]}
    названия = {"инт": "Интеллект", "тех": "Техника", "реа_воля": "Реакция и Воля", "лвк_хар": "Ловкость и Харизма"}
    активные = группы.get(группа, [])
    embed = discord.Embed(title=f"`[SKILL]` {p['имя']} — {названия.get(группа, '')}", description=f"О.У.: **{p['оу']}** (потрачено: {потрачено})", color=0x00ffaa)
    строки = []
    for skill_name, skill_data in SKILLS.items():
        стат = skill_data['стат']
        if стат not in активные: continue
        ур = навыки_игрока.get(skill_name, 0)
        бонус = статы.get(стат, 1)
        строки.append(f"{skill_name}: +{ур + бонус} (ур.{ур})")
    if строки:
        embed.add_field(name="\u200b", value='\n'.join(строки), inline=False)
    embed.set_footer(text="Цена: 1-2 О.У. | /бросок")
    await interaction.response.send_message(embed=embed)

# ==========================================
# НАВЫК АП
# ==========================================
@bot.tree.command(name="навык_ап", description="Повысить навык")
@app_commands.autocomplete(навык=автодополнение_навыков)
async def навык_ап(interaction: discord.Interaction, навык: str):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    if 'навыки' not in p: p['навыки'] = {}
    if навык not in SKILLS:
        await interaction.response.send_message("`[ERR]` Не найден!", ephemeral=True)
        return
    тек = p['навыки'].get(навык, 0)
    if тек >= 8:
        await interaction.response.send_message("`[WARN]` Макс 8!", ephemeral=True)
        return
    цена = SKILLS[навык].get("цена", 1)
    if p['оу'] < цена:
        await interaction.response.send_message(f"`[ERR]` Нужно {цена} О.У.!", ephemeral=True)
        return
    p['оу'] -= цена
    p['навыки'][навык] = тек + 1
    save_characters(персонажи)
    бонус = p['статы'].get(SKILLS[навык]['стат'], 1)
    await interaction.response.send_message(f"`[SYS]` **{навык.title()}** → ур.{тек + 1} (бонус +{тек + 1 + бонус}) | О.У.: {p['оу']}")

# ==========================================
# БРОСОК
# ==========================================
@bot.tree.command(name="бросок", description="Проверить навык (D10)")
@app_commands.autocomplete(навык=автодополнение_навыков)
@app_commands.describe(навык="Навык", удача="Удача", мод="Модификатор")
async def бросок(interaction: discord.Interaction, навык: str, удача: int = 0, мод: int = 0):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    статы = p['статы']
    if навык not in SKILLS:
        await interaction.response.send_message("`[ERR]` Не найден!", ephemeral=True)
        return
    бонус_удачи = 0
    if удача > 0:
        макс = статы.get('удача', 1)
        тек = p.get('удача_текущая', макс)
        восстановить_удачу(p)
        тек = p.get('удача_текущая', макс)
        if удача > тек:
            await interaction.response.send_message(f"`[ERR]` Удачи: {тек}/{макс}", ephemeral=True)
            return
        p['удача_текущая'] = тек - удача
        p['удача_последняя_трата'] = datetime.datetime.now().isoformat()
        save_characters(персонажи)
        бонус_удачи = удача
    skill_data = SKILLS[навык]
    стат_бонус = статы.get(skill_data['стат'], 1)
    ур = p.get('навыки', {}).get(навык, 0)
    псих = 0
    эмп = p.get('человечность', 10) // 10
    if skill_data['стат'] == 'харизма':
        if эмп == 0: псих = -2
        elif эмп == 1: псих = -1
    общий = стат_бонус + ур + бонус_удачи + мод + псих
    бросок = random.randint(1, 10)
    результат = бросок + общий
    взрыв_текст = ""
    тип = ""
    if бросок == 10:
        взрыв = random.randint(1, 10)
        результат += взрыв
        тип = "🔥 КРИТИЧЕСКАЯ УДАЧА!"
        взрыв_текст = f"\n║ 💥 +{взрыв}"
    elif бросок == 1:
        взрыв = random.randint(1, 10)
        результат -= взрыв
        тип = "💀 КРИТИЧЕСКАЯ НЕУДАЧА!"
        взрыв_текст = f"\n║ 💥 -{взрыв}"
    await interaction.response.send_message(
        f"`[CHECK]` {interaction.user.mention} ▶ **{навык.title()}**\n"
        f"╔═══ D10: **{бросок}** ═══╗\n"
        f"║ Навык: +{ур}\n║ {SHORT_STATS[skill_data['стат']]}: +{стат_бонус}" +
        (f"\n║ Удача: +{бонус_удачи}" if бонус_удачи else "") +
        (f"\n║ Мод: {мод:+}" if мод else "") +
        (f"\n║ Психоз: {псих}" if псих else "") +
        f"{взрыв_текст}\n║ Итого: **{результат}**\n╚═══ {тип} ═══╝"
    )


# ==========================================
# СНАРЯЖЕНИЕ
# ==========================================
@bot.tree.command(name="снаряжение", description="Управление снаряжением")
@app_commands.autocomplete(предмет=автодополнение_предметов)
@app_commands.describe(действие="Что сделать", предмет="Номер (для продажи) или название (для покупки)")
@app_commands.choices(действие=[
    app_commands.Choice(name="список", value="список"),
    app_commands.Choice(name="купить", value="купить"),
    app_commands.Choice(name="продать", value="продать"),
])
async def снаряжение(interaction: discord.Interaction, действие: str, предмет: str = None):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    if 'надетое_снаряжение' not in p:
        p['надетое_снаряжение'] = []

    if действие == "список":
        if not p['снаряжение'] and not p['надетое_снаряжение']:
            await interaction.response.send_message("🎒 Снаряжение: пусто")
            return
        строки = ["**🎒 Снаряжение:**"]
        номер = 1
        for item in p['снаряжение']:
            строки.append(f"{номер}. ▸ {item}")
            номер += 1
        for item in p['надетое_снаряжение']:
            строки.append(f"{номер}. 👕 {item} (Надето)")
            номер += 1
        await interaction.response.send_message('\n'.join(строки))

    elif действие == "купить":
        if not предмет:
            await interaction.response.send_message("`[ERR]` Укажи название!", ephemeral=True)
            return
        шаблоны = load_items()
        if предмет not in шаблоны:
            await interaction.response.send_message(f"`[ERR]` Доступные: {', '.join(шаблоны)}", ephemeral=True)
            return
        д = шаблоны[предмет]
        if p['эдди'] < д['цена']:
            await interaction.response.send_message(f"`[ERR]` {д['цена']} эдди! У тебя {p['эдди']}.", ephemeral=True)
            return
        p['эдди'] -= д['цена']
        p['снаряжение'].append(предмет)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[€$]` **{предмет}** куплен за {д['цена']} эдди!\nЭффект: {д['эффект']} | Осталось: {p['эдди']}")

    elif действие == "продать":
        if not предмет:
            await interaction.response.send_message("`[ERR]` Укажи номер из списка!", ephemeral=True)
            return
        try:
            номер = int(предмет)
        except:
            await interaction.response.send_message("`[ERR]` Нужно число — номер из `/снаряжение список`!", ephemeral=True)
            return
        
        общий = p['снаряжение'] + p['надетое_снаряжение']
        if номер < 1 or номер > len(общий):
            await interaction.response.send_message(f"`[ERR]` №{номер} не найден! Всего: {len(общий)}.", ephemeral=True)
            return
        
        продан = общий[номер - 1]
        if продан in p['снаряжение']:
            p['снаряжение'].remove(продан)
        else:
            p['надетое_снаряжение'].remove(продан)
        
        цена = 10
        p['эдди'] += цена
        save_characters(персонажи)
        await interaction.response.send_message(f"`[€$]` **{продан}** продан за {цена} эдди. Баланс: **{p['эдди']}**")

# ==========================================
# ВЫДАТЬ СНАРЯЖЕНИЕ
# ==========================================
@bot.tree.command(name="выдать_снаряжение", description="[Гейммастер] Выдать снаряжение")
@app_commands.describe(игрок="Кому", предмет="Название")
async def выдать_снаряжение(interaction: discord.Interaction, игрок: discord.Member, предмет: str):
    if "Гейммастер" not in [р.name for р in interaction.user.roles]:
        await interaction.response.send_message("`[ERR]` Только Гейммастер!", ephemeral=True)
        return
    персонажи = load_characters()
    цель_id = str(игрок.id)
    if цель_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Нет персонажа!", ephemeral=True)
        return
    p = персонажи[цель_id]
    p['снаряжение'].append(предмет)
    save_characters(персонажи)
    await interaction.response.send_message(f"`[SYS]` {игрок.mention} получил **{предмет}**!")

# ==========================================
# ОРУЖИЕ
# ==========================================
@bot.tree.command(name="оружие", description="Управление оружием")
@app_commands.autocomplete(предмет=автодополнение_оружия)
@app_commands.describe(действие="Что сделать", номер="Номер оружия", предмет="Название (для покупки)", качество="Качество", рука="В какую руку")
@app_commands.choices(действие=[
    app_commands.Choice(name="список", value="список"),
    app_commands.Choice(name="купить", value="купить"),
    app_commands.Choice(name="продать", value="продать"),
    app_commands.Choice(name="экипировать", value="экипировать"),
    app_commands.Choice(name="убрать", value="убрать"),
    app_commands.Choice(name="в быстрый доступ", value="в_бд"),
    app_commands.Choice(name="из быстрого доступа", value="из_бд"),
])
@app_commands.choices(качество=[
    app_commands.Choice(name="низкое (-1, ×0.5)", value="низкое"),
    app_commands.Choice(name="обычное", value="обычное"),
    app_commands.Choice(name="высокое (+1, ×1.5)", value="высокое"),
])
@app_commands.choices(рука=[
    app_commands.Choice(name="правая", value="правая"),
    app_commands.Choice(name="левая", value="левая"),
    app_commands.Choice(name="обе", value="обе"),
])
async def оружие(interaction: discord.Interaction, действие: str, номер: int = None, предмет: str = None, качество: str = "обычное", рука: str = "правая"):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    моды = {"низкое": {"урон": -1, "цена": 0.5, "зн": "⬇️"}, "обычное": {"урон": 0, "цена": 1.0, "зн": "➖"}, "высокое": {"урон": 1, "цена": 1.5, "зн": "⬆️"}}
    if 'руки' not in p: p['руки'] = {"правая": None, "левая": None}
    if 'быстрый_доступ' not in p: p['быстрый_доступ'] = []
    сп = p.get('оружие', [])

    # Вспомогательная функция: индекс оружия в быстром доступе
    def индекс_в_бд(номер_оружия):
        for i, idx in enumerate(p['быстрый_доступ']):
            if idx == номер_оружия - 1:
                return i
        return -1

    if действие == "список":
        строки = ["**🔫 Оружие:**"]
        if сп:
            for i, о in enumerate(сп, 1):
                ш = о['шаблон']; к = о.get('качество', 'обычное')
                обв = о.get('обвесы', {})
                с1, с2 = обв.get('слот1'), обв.get('слот2')
                обв_стр = f" [{с1 or '—'}|{с2 or '—'}]" if (с1 or с2) else ""
                метка = ""
                if i - 1 in p['быстрый_доступ']: метка = " ⚡БД"
                if p['руки']['правая'] == i - 1 or p['руки']['левая'] == i - 1: метка = " ✋"
                строки.append(f"{i}. {моды[к]['зн']} **{о['название'].title()}** ({к}) — {ш['урон']} ({ш['тип']}){обв_стр}{метка}")
        else:
            строки.append("пусто")

        строки.append("")
        строки.append("**✋ В руках:**")
        for r in ["правая", "левая"]:
            idx = p['руки'][r]
            if idx is not None and idx < len(сп):
                строки.append(f"{r}: **{сп[idx]['название'].title()}**")
            else:
                строки.append(f"{r}: пусто")

        строки.append("")
        строки.append("**⚡ Быстрый доступ:**")
        if p['быстрый_доступ']:
            for idx in p['быстрый_доступ']:
                if idx < len(сп):
                    строки.append(f"• **{сп[idx]['название'].title()}**")
        else:
            строки.append("пусто")
        await interaction.response.send_message('\n'.join(строки))

    elif действие == "купить":
        if not предмет:
            await interaction.response.send_message("`[ERR]` Укажи название оружия!", ephemeral=True)
            return
        шаблоны = load_weapons()
        if предмет not in шаблоны:
            await interaction.response.send_message(f"`[ERR]` Доступные: {', '.join(шаблоны)}", ephemeral=True)
            return
        ш = copy.deepcopy(шаблоны[предмет])
        м = моды[качество]
        цена = int(ш['цена'] * м['цена'])
        if p['эдди'] < цена:
            await interaction.response.send_message(f"`[ERR]` {цена} эдди! У тебя {p['эдди']}.", ephemeral=True)
            return
        ч = ш['урон'].split('d')
        кубы = max(1, int(ч[0]) + м['урон'])
        ш['урон'] = f"{кубы}d{ч[1]}"
        ш['цена'] = цена
        p['эдди'] -= цена
        if 'оружие' not in p: p['оружие'] = []
        p['оружие'].append({"название": предмет, "качество": качество, "шаблон": ш, "обвесы": {"слот1": None, "слот2": None}})
        save_characters(персонажи)
        await interaction.response.send_message(f"`[€$]` {м['зн']} **{предмет.title()}** ({качество}) куплен!\nУрон: {ш['урон']} | Цена: {цена} | Осталось: {p['эдди']}")

    elif действие == "продать":
        if not номер:
            await interaction.response.send_message("`[ERR]` Укажи номер оружия из списка!", ephemeral=True)
            return
        if номер < 1 or номер > len(сп):
            await interaction.response.send_message(f"`[ERR]` Оружие №{номер} не найдено!", ephemeral=True)
            return
        о = сп[номер - 1]
        # Снимаем с рук
        for r in ["правая", "левая"]:
            if p['руки'][r] == номер - 1: p['руки'][r] = None
        # Убираем из быстрого доступа
        ибд = индекс_в_бд(номер)
        if ибд >= 0: p['быстрый_доступ'].pop(ибд)
        # Сдвигаем индексы
        for r in ["правая", "левая"]:
            if p['руки'][r] is not None and p['руки'][r] > номер - 1: p['руки'][r] -= 1
        for i in range(len(p['быстрый_доступ'])):
            if p['быстрый_доступ'][i] > номер - 1: p['быстрый_доступ'][i] -= 1
        цена_продажи = int(о['шаблон']['цена'] * 0.1)
        p['эдди'] += цена_продажи
        сп.pop(номер - 1)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[€$]` **{о['название'].title()}** продан за {цена_продажи} эдди. Баланс: **{p['эдди']}**")

    elif действие == "экипировать":
        if not сп:
            await interaction.response.send_message("Нет оружия!", ephemeral=True)
            return
        if not номер:
            await interaction.response.send_message("`[ERR]` Укажи номер оружия!", ephemeral=True)
            return
        if номер < 1 or номер > len(сп):
            await interaction.response.send_message("`[ERR]` Не найден!", ephemeral=True)
            return
        оруж = сп[номер - 1]
        рук = оруж['шаблон'].get('рук', 1)
        # Убираем из быстрого доступа если было
        ибд = индекс_в_бд(номер)
        if ибд >= 0: p['быстрый_доступ'].pop(ибд)
        if рук == 2:
            if рука != "обе":
                await interaction.response.send_message("`[ERR]` Двуручное — выбери «обе»!", ephemeral=True)
                return
            p['руки']['правая'] = номер - 1
            p['руки']['левая'] = номер - 1
        else:
            if рука == "обе":
                await interaction.response.send_message("`[ERR]` Одноручное — выбери руку!", ephemeral=True)
                return
            тек = p['руки'][рука]
            if тек is not None and тек < len(сп) and сп[тек]['шаблон'].get('рук', 1) == 2:
                p['руки']['правая'] = None
                p['руки']['левая'] = None
            p['руки'][рука] = номер - 1
        save_characters(персонажи)
        стр = []
        for r in ["правая", "левая"]:
            idx = p['руки'][r]
            стр.append(f"{r}: **{сп[idx]['название'].title()}**" if idx is not None and idx < len(сп) else f"{r}: пусто")
        await interaction.response.send_message(f"`[SYS]` {interaction.user.mention}:\n" + '\n'.join(стр))

    elif действие == "убрать":
        if not рука:
            await interaction.response.send_message("`[ERR]` Укажи руку!", ephemeral=True)
            return
        if рука == "обе":
            p['руки']['правая'] = None
            p['руки']['левая'] = None
        else:
            тек = p['руки'][рука]
            if тек is not None and тек < len(сп) and сп[тек]['шаблон'].get('рук', 1) == 2:
                p['руки']['правая'] = None
                p['руки']['левая'] = None
            else:
                p['руки'][рука] = None
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` {interaction.user.mention} убрал оружие ({рука}).")

    elif действие == "в_бд":
        if not номер:
            await interaction.response.send_message("`[ERR]` Укажи номер оружия!", ephemeral=True)
            return
        if номер < 1 or номер > len(сп):
            await interaction.response.send_message("`[ERR]` Не найден!", ephemeral=True)
            return
        # Проверяем, не в руках ли уже
        for r in ["правая", "левая"]:
            if p['руки'][r] == номер - 1:
                await interaction.response.send_message("`[ERR]` Сначала убери оружие из рук!", ephemeral=True)
                return
        # Проверяем лимит быстрого доступа
        тек_рук = sum(1 for idx in p['быстрый_доступ'] if idx < len(сп) and сп[idx]['шаблон'].get('рук', 1) == 2)
        тек_одноруч = len(p['быстрый_доступ']) - тек_рук
        рук = сп[номер - 1]['шаблон'].get('рук', 1)
        if рук == 2:
            if p['быстрый_доступ']:
                await interaction.response.send_message("`[ERR]` Быстрый доступ занят! Максимум 1 двуручное.", ephemeral=True)
                return
        else:
            if тек_рук > 0 or тек_одноруч >= 2:
                await interaction.response.send_message("`[ERR]` Быстрый доступ заполнен! Максимум: 1 двуручное или 2 одноручных.", ephemeral=True)
                return
        if номер - 1 in p['быстрый_доступ']:
            await interaction.response.send_message("`[ERR]` Уже в быстром доступе!", ephemeral=True)
            return
        p['быстрый_доступ'].append(номер - 1)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{сп[номер - 1]['название'].title()}** в быстром доступе! ⚡")

    elif действие == "из_бд":
        if not номер:
            await interaction.response.send_message("`[ERR]` Укажи номер оружия!", ephemeral=True)
            return
        ибд = индекс_в_бд(номер)
        if ибд < 0:
            await interaction.response.send_message("`[ERR]` Не в быстром доступе!", ephemeral=True)
            return
        p['быстрый_доступ'].pop(ибд)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{сп[номер - 1]['название'].title()}** убран из быстрого доступа.")

# ==========================================
# БРОНЯ
# ==========================================
@bot.tree.command(name="броня", description="Управление бронёй")
@app_commands.autocomplete(предмет=автодополнение_брони)
@app_commands.describe(действие="Что сделать", номер="Номер (для продажи/экипировки)", предмет="Название (для покупки)")
@app_commands.choices(действие=[
    app_commands.Choice(name="список", value="список"),
    app_commands.Choice(name="купить", value="купить"),
    app_commands.Choice(name="продать", value="продать"),
    app_commands.Choice(name="экипировать", value="экипировать"),
    app_commands.Choice(name="снять", value="снять"),
])
async def броня(interaction: discord.Interaction, действие: str, номер: int = None, предмет: str = None):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    if 'броня' not in p:
        p['броня'] = []
    if 'надето_броня' not in p:
        p['надето_броня'] = {"голова": None, "тело": None}

    if действие == "список":
        строки = ["**🛡️ Броня:**"]
        if not p['броня'] and not any(p['надето_броня'].values()):
            await interaction.response.send_message("🛡️ Броня: пусто")
            return
        номер_стр = 1
        for item in p['броня']:
            строки.append(f"{номер_стр}. ▸ {item['название'].title()} (защита: {item['шаблон']['защита']}, тип: {item['шаблон']['тип']})")
            номер_стр += 1
        for слот, item in p['надето_броня'].items():
            if item:
                строки.append(f"{номер_стр}. 🛡️ {item['название'].title()} (Надето: {слот})")
                номер_стр += 1
        await interaction.response.send_message('\n'.join(строки))

    elif действие == "купить":
        if not предмет:
            await interaction.response.send_message("`[ERR]` Укажи название!", ephemeral=True)
            return
        шаблоны = load_armor()
        if предмет not in шаблоны:
            await interaction.response.send_message(f"`[ERR]` Доступные: {', '.join(шаблоны)}", ephemeral=True)
            return
        ш = шаблоны[предмет]
        if p['эдди'] < ш['цена']:
            await interaction.response.send_message(f"`[ERR]` {ш['цена']} эдди! У тебя {p['эдди']}.", ephemeral=True)
            return
        p['эдди'] -= ш['цена']
        p['броня'].append({"название": предмет, "шаблон": copy.deepcopy(ш)})
        save_characters(персонажи)
        await interaction.response.send_message(f"`[€$]` **{предмет.title()}** куплен!\nЗащита: {ш['защита']} | Тип: {ш['тип']} | Осталось: {p['эдди']}")

    elif действие == "продать":
        if not номер:
            await interaction.response.send_message("`[ERR]` Укажи номер из списка!", ephemeral=True)
            return
        общий = p['броня'] + [v for v in p['надето_броня'].values() if v is not None]
        if номер < 1 or номер > len(общий):
            await interaction.response.send_message(f"`[ERR]` №{номер} не найден!", ephemeral=True)
            return
        продан = общий[номер - 1]
        if продан in p['броня']:
            p['броня'].remove(продан)
        else:
            for слот in p['надето_броня']:
                if p['надето_броня'][слот] == продан:
                    p['надето_броня'][слот] = None
                    break
        цена = int(продан['шаблон']['цена'] * 0.1)
        p['эдди'] += цена
        save_characters(персонажи)
        await interaction.response.send_message(f"`[€$]` **{продан['название'].title()}** продан за {цена} эдди. Баланс: **{p['эдди']}**")

    elif действие == "экипировать":
        if not номер:
            await interaction.response.send_message("`[ERR]` Укажи номер из списка!", ephemeral=True)
            return
        if номер < 1 or номер > len(p['броня']):
            await interaction.response.send_message(f"`[ERR]` №{номер} не найден в инвентаре!", ephemeral=True)
            return
        предмет = p['броня'][номер - 1]
        слот = предмет['шаблон']['тип']
        if p['надето_броня'][слот] is not None:
            старый = p['надето_броня'][слот]
            await interaction.response.send_message(
                f"`[ERR]` Слот «{слот}» занят **{старый['название'].title()}**!\nСначала сними его: `/броня снять`",
                ephemeral=True
            )
            return
        p['броня'].remove(предмет)
        p['надето_броня'][слот] = предмет
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{предмет['название'].title()}** надет (слот: {слот})! 🛡️")

    elif действие == "снять":
        общий = [v for v in p['надето_броня'].values() if v is not None]
        if not общий:
            await interaction.response.send_message("Нет надетой брони!", ephemeral=True)
            return
        if not номер or номер < 1 or номер > len(общий):
            await interaction.response.send_message(f"`[ERR]` Укажи номер надетой брони (1-{len(общий)})!", ephemeral=True)
            return
        предмет = общий[номер - 1]
        for слот in p['надето_броня']:
            if p['надето_броня'][слот] == предмет:
                p['надето_броня'][слот] = None
                p['броня'].append(предмет)
                save_characters(персонажи)
                await interaction.response.send_message(f"`[SYS]` **{предмет['название'].title()}** снят и возвращён в инвентарь.")
                return

# ==========================================
# КИБЕРИМПЛАНТЫ
# ==========================================
@bot.tree.command(name="кибер", description="Управление киберимплантами")
@app_commands.autocomplete(предмет=автодополнение_имплантов)
@app_commands.describe(действие="Что сделать", предмет="Номер (для продажи) или название (для покупки)")
@app_commands.choices(действие=[
    app_commands.Choice(name="список", value="список"),
    app_commands.Choice(name="купить", value="купить"),
    app_commands.Choice(name="продать", value="продать"),
])
async def кибер(interaction: discord.Interaction, действие: str, предмет: str = None):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    if 'киберимпланты' not in p: p['киберимпланты'] = []
    if 'установлено_импланты' not in p: p['установлено_импланты'] = []

    if действие == "список":
        if not p['киберимпланты'] and not p['установлено_импланты']:
            await interaction.response.send_message("🔌 Киберимпланты: пусто")
            return
        строки = ["**🔌 Киберимпланты:**"]
        номер = 1
        for item in p['киберимпланты']:
            строки.append(f"{номер}. ▸ {item['название'].title()} ({item['шаблон']['эффект']})")
            номер += 1
        for слот, импланты in p['установлено_импланты'].items():
            for item in импланты:
                строки.append(f"{номер}. ⚡ {item['название'].title()} (Установлен: {слот}) — {item['шаблон']['эффект']}")
                номер += 1
        await interaction.response.send_message('\n'.join(строки))

    elif действие == "купить":
        if not предмет:
            await interaction.response.send_message("`[ERR]` Укажи название!", ephemeral=True)
            return
        шаблоны = load_cyberware()
        if предмет not in шаблоны:
            await interaction.response.send_message(f"`[ERR]` Доступные: {', '.join(шаблоны)}", ephemeral=True)
            return
        ш = шаблоны[предмет]
        if p['эдди'] < ш['цена']:
            await interaction.response.send_message(f"`[ERR]` {ш['цена']} эдди! У тебя {p['эдди']}.", ephemeral=True)
            return
        p['эдди'] -= ш['цена']
        p['киберимпланты'].append({"название": предмет, "шаблон": copy.deepcopy(ш)})
        save_characters(персонажи)
        await interaction.response.send_message(f"`[€$]` **{предмет}** куплен за {ш['цена']} эдди!\nЭффект: {ш['эффект']} | Слот: {ш['слот']} | Осталось: {p['эдди']}")

    elif действие == "продать":
        if not предмет:
            await interaction.response.send_message("`[ERR]` Укажи номер из списка!", ephemeral=True)
            return
        try: номер = int(предмет)
        except:
            await interaction.response.send_message("`[ERR]` Нужно число!", ephemeral=True)
            return
        общий = list(p['киберимпланты'])
        for импланты in p['установлено_импланты'].values():
            общий.extend(импланты)
        if номер < 1 or номер > len(общий):
            await interaction.response.send_message(f"`[ERR]` №{номер} не найден!", ephemeral=True)
            return
        продан = общий[номер - 1]
        if продан in p['киберимпланты']:
            p['киберимпланты'].remove(продан)
        else:
            for импланты in p['установлено_импланты'].values():
                if продан in импланты:
                    импланты.remove(продан)
                    break
        цена = int(продан['шаблон']['цена'] * 0.1)
        p['эдди'] += цена
        save_characters(персонажи)
        await interaction.response.send_message(f"`[€$]` **{продан['название'].title()}** продан за {цена} эдди. Баланс: **{p['эдди']}**")


# ==========================================
# УСТАНОВИТЬ/СНЯТЬ КИБЕРИМПЛАНТ
# ==========================================
@bot.tree.command(name="установить_кибер", description="Установить или снять киберимплант")
@app_commands.describe(действие="Что сделать", номер="Номер из /кибер список")
@app_commands.choices(действие=[
    app_commands.Choice(name="установить", value="установить"),
    app_commands.Choice(name="снять", value="снять"),
])
async def установить_кибер(interaction: discord.Interaction, действие: str, номер: int):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    if 'киберимпланты' not in p: p['киберимпланты'] = []
    if 'установлено_импланты' not in p: p['установлено_импланты'] = []

    if действие == "установить":
        if номер < 1 or номер > len(p['киберимпланты']):
            await interaction.response.send_message(f"`[ERR]` №{номер} не найден в инвентаре!", ephemeral=True)
            return
        имп = p['киберимпланты'][номер - 1]
        слот = имп['шаблон']['слот']

        # Проверка: это открывающий имплант?
        if имп['шаблон'].get('открывает'):
            открывает = имп['шаблон']['открывает']
            лимит = имп['шаблон']['лимит']
            if 'открытые_слоты' not in p: p['открытые_слоты'] = {}
            if открывает in p['открытые_слоты']:
                await interaction.response.send_message(f"`[ERR]` Слот «{открывает}» уже открыт!", ephemeral=True)
                return
            p['открытые_слоты'][открывает] = лимит
            if 'установлено_импланты' not in p: p['установлено_импланты'] = {}
            if открывает not in p['установлено_импланты']:
                p['установлено_импланты'][открывает] = []
            p['киберимпланты'].remove(имп)
            save_characters(персонажи)
            await interaction.response.send_message(f"`[SYS]` **{имп['название'].title()}** активирован! Слот «{открывает}» открыт ({лимит} мест). ⚡")
            return

        # Проверка: это борг-имплант?
        if имп['шаблон'].get('борг_слота'):
            борг_слот = имп['шаблон']['борг_слота']
            if борг_слот not in p.get('открытые_слоты', {}):
                await interaction.response.send_message(f"`[ERR]` Слот «{борг_слот}» не открыт! Сначала установи открывающий имплант.", ephemeral=True)
                return
            if f"борг_{борг_слот}" in p.get('открытые_слоты', {}):
                await interaction.response.send_message(f"`[ERR]` Борг-имплант для «{борг_слот}» уже установлен!", ephemeral=True)
                return
            p['открытые_слоты'][борг_слот] += имп['шаблон']['добавляет_слотов']
            p['открытые_слоты'][f"борг_{борг_слот}"] = True
            p['киберимпланты'].remove(имп)
            save_characters(персонажи)
            await interaction.response.send_message(f"`[SYS]` **{имп['название'].title()}** активирован! Слот «{борг_слот}» расширен (+{имп['шаблон']['добавляет_слотов']} места). ⚡")
            return

        # Проверка: слот открыт?
        лимиты = {"стилевые": 3, "внутренние": 3, "внешние": 3}
        if слот in p.get('открытые_слоты', {}):
            лимит = p['открытые_слоты'][слот]
        elif слот in лимиты:
            лимит = лимиты[слот]
        else:
            await interaction.response.send_message(f"`[ERR]` Слот «{слот}» закрыт! Сначала установи открывающий имплант.", ephemeral=True)
            return

        # Проверка: не дубликат?
        for уст in p['установлено_импланты'].get(слот, []):
            if уст['название'] == имп['название']:
                await interaction.response.send_message(f"`[ERR]` **{имп['название'].title()}** уже установлен в этот слот!", ephemeral=True)
                return

        if len(p['установлено_импланты'].get(слот, [])) >= лимит:
            await interaction.response.send_message(f"`[ERR]` Слот «{слот}» заполнен (макс: {лимит})!", ephemeral=True)
            return

        p['киберимпланты'].remove(имп)
        if слот not in p['установлено_импланты']:
            p['установлено_импланты'][слот] = []
        p['установлено_импланты'][слот].append(имп)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{имп['название'].title()}** установлен в слот «{слот}»! ⚡")

    elif действие == "снять":
        # Ищем по номеру среди всех установленных
        все_уст = []
        for слот, импланты in p['установлено_импланты'].items():
            for имп in импланты:
                все_уст.append((слот, имп))
        if номер < 1 or номер > len(все_уст):
            await interaction.response.send_message(f"`[ERR]` №{номер} не найден среди установленных!", ephemeral=True)
            return
        слот, имп = все_уст[номер - 1]
        p['установлено_импланты'][слот].remove(имп)
        p['киберимпланты'].append(имп)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{имп['название'].title()}** снят и возвращён в инвентарь.")


# ==========================================
# ВЫДАТЬ КИБЕРИМПЛАНТ
# ==========================================
@bot.tree.command(name="выдать_кибер", description="[Гейммастер] Выдать киберимплант")
@app_commands.autocomplete(предмет=автодополнение_имплантов)
@app_commands.describe(игрок="Кому", предмет="Название")
async def выдать_кибер(interaction: discord.Interaction, игрок: discord.Member, предмет: str):
    if "Гейммастер" not in [р.name for р in interaction.user.roles]:
        await interaction.response.send_message("`[ERR]` Только Гейммастер!", ephemeral=True)
        return
    персонажи = load_characters()
    цель_id = str(игрок.id)
    if цель_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Нет персонажа!", ephemeral=True)
        return
    шаблоны = load_cyberware()
    if предмет not in шаблоны:
        await interaction.response.send_message(f"`[ERR]` Доступные: {', '.join(шаблоны)}", ephemeral=True)
        return
    p = персонажи[цель_id]
    if 'киберимпланты' not in p: p['киберимпланты'] = []
    p['киберимпланты'].append({"название": предмет, "шаблон": copy.deepcopy(шаблоны[предмет])})
    save_characters(персонажи)
    ш = шаблоны[предмет]
    await interaction.response.send_message(f"`[SYS]` {игрок.mention} получил **{предмет.title()}**!\nЭффект: {ш['эффект']} | Слот: {ш['слот']}")

# ==========================================
# ВЫДАТЬ БРОНЮ
# ==========================================
@bot.tree.command(name="выдать_броню", description="[Гейммастер] Выдать броню")
@app_commands.autocomplete(предмет=автодополнение_брони)
@app_commands.describe(игрок="Кому", предмет="Название")
async def выдать_броню(interaction: discord.Interaction, игрок: discord.Member, предмет: str):
    if "Гейммастер" not in [р.name for р in interaction.user.roles]:
        await interaction.response.send_message("`[ERR]` Только Гейммастер!", ephemeral=True)
        return
    персонажи = load_characters()
    цель_id = str(игрок.id)
    if цель_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Нет персонажа!", ephemeral=True)
        return
    шаблоны = load_armor()
    if предмет not in шаблоны:
        await interaction.response.send_message(f"`[ERR]` Доступные: {', '.join(шаблоны)}", ephemeral=True)
        return
    p = персонажи[цель_id]
    if 'броня' not in p: p['броня'] = []
    p['броня'].append({"название": предмет, "шаблон": copy.deepcopy(шаблоны[предмет])})
    save_characters(персонажи)
    ш = шаблоны[предмет]
    await interaction.response.send_message(f"`[SYS]` {игрок.mention} получил **{предмет.title()}**!\nЗащита: {ш['защита']} | Тип: {ш['тип']}")

# ==========================================
# ВЫДАТЬ ОРУЖИЕ
# ==========================================
@bot.tree.command(name="выдать_оружие", description="[Гейммастер] Выдать оружие")
@app_commands.autocomplete(оружие=автодополнение_оружия)
@app_commands.describe(игрок="Кому", оружие="Название", качество="Качество")
@app_commands.choices(качество=[
    app_commands.Choice(name="низкое (-1, ×0.5)", value="низкое"),
    app_commands.Choice(name="обычное", value="обычное"),
    app_commands.Choice(name="высокое (+1, ×1.5)", value="высокое"),
])
async def выдать_оружие(interaction: discord.Interaction, игрок: discord.Member, оружие: str, качество: str = "обычное"):
    if "Гейммастер" not in [р.name for р in interaction.user.roles]:
        await interaction.response.send_message("`[ERR]` Только Гейммастер!", ephemeral=True)
        return
    персонажи = load_characters()
    цель_id = str(игрок.id)
    if цель_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Нет персонажа!", ephemeral=True)
        return
    шаблоны = load_weapons()
    if оружие not in шаблоны:
        await interaction.response.send_message(f"`[ERR]` Доступные: {', '.join(шаблоны)}", ephemeral=True)
        return
    p = персонажи[цель_id]
    моды = {"низкое": {"урон": -1, "цена": 0.5, "зн": "⬇️"}, "обычное": {"урон": 0, "цена": 1.0, "зн": "➖"}, "высокое": {"урон": 1, "цена": 1.5, "зн": "⬆️"}}
    м = моды[качество]
    ш = copy.deepcopy(шаблоны[оружие])
    ч = ш['урон'].split('d')
    ш['урон'] = f"{max(1, int(ч[0]) + м['урон'])}d{ч[1]}"
    ш['цена'] = int(ш['цена'] * м['цена'])
    if 'оружие' not in p: p['оружие'] = []
    p['оружие'].append({"название": оружие, "качество": качество, "шаблон": ш, "обвесы": {"слот1": None, "слот2": None}})
    save_characters(персонажи)
    await interaction.response.send_message(f"`[SYS]` {м['зн']} {игрок.mention} получил **{оружие.title()}** ({качество})!\nУрон: {ш['урон']} | {ш['тип']} | {ш['навык']}")

# ==========================================
# ОБВЕСЫ
# ==========================================
@bot.tree.command(name="обвес", description="Управление обвесами")
@app_commands.autocomplete(обвес=автодополнение_обвесов)
@app_commands.describe(действие="Что сделать", номер="Номер обвеса (для продажи)", оружие_номер="Номер оружия", обвес="Название (для покупки/установки)", слот="Слот 1/2")
@app_commands.choices(действие=[
    app_commands.Choice(name="установить", value="установить"),
    app_commands.Choice(name="снять", value="снять"),
    app_commands.Choice(name="мой инвентарь", value="инвентарь"),
    app_commands.Choice(name="купить", value="купить"),
    app_commands.Choice(name="продать", value="продать"),
])
@app_commands.choices(слот=[
    app_commands.Choice(name="слот 1", value="1"),
    app_commands.Choice(name="слот 2", value="2"),
])
async def обвес(interaction: discord.Interaction, действие: str, номер: int = None, оружие_номер: int = 1, обвес: str = None, слот: str = "1"):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    оружие_список = p.get('оружие', [])

    if действие == "инвентарь":
        инв = p.get('инвентарь_обвесов', [])
        if not инв:
            await interaction.response.send_message("🔧 Нет обвесов.")
            return
        обвесы = load_attachments()
        строки = ["**🔧 Твои обвесы:**"]
        for i, n in enumerate(инв, 1):
            д = обвесы.get(n, {})
            строки.append(f"{i}. **{n}** — {д.get('эффект', '?')}")
        await interaction.response.send_message('\n'.join(строки))
        return

    if действие == "купить":
        if not обвес:
            await interaction.response.send_message("`[ERR]` Укажи обвес!", ephemeral=True)
            return
        обвесы = load_attachments()
        if обвес not in обвесы:
            await interaction.response.send_message(f"`[ERR]` Доступные: {', '.join(обвесы)}", ephemeral=True)
            return
        д = обвесы[обвес]
        if p['эдди'] < д['цена']:
            await interaction.response.send_message(f"`[ERR]` {д['цена']} эдди! У тебя {p['эдди']}.", ephemeral=True)
            return
        p['эдди'] -= д['цена']
        if 'инвентарь_обвесов' not in p: p['инвентарь_обвесов'] = []
        p['инвентарь_обвесов'].append(обвес)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[€$]` **{обвес}** куплен!\nЭффект: {д['эффект']} | Осталось: {p['эдди']}")
        return

    if действие == "продать":
        if not номер:
            await interaction.response.send_message("`[ERR]` Укажи номер обвеса из инвентаря!", ephemeral=True)
            return
        инв = p.get('инвентарь_обвесов', [])
        if номер < 1 or номер > len(инв):
            await interaction.response.send_message(f"`[ERR]` Обвес №{номер} не найден! Всего: {len(инв)}.", ephemeral=True)
            return
        название = инв[номер - 1]
        обвесы = load_attachments()
        цена_продажи = int(обвесы[название]['цена'] * 0.1)
        p['эдди'] += цена_продажи
        инв.pop(номер - 1)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[€$]` **{название}** продан за {цена_продажи} эдди. Баланс: **{p['эдди']}**")
        return

    if not оружие_список:
        await interaction.response.send_message("Нет оружия!", ephemeral=True)
        return
    if оружие_номер < 1 or оружие_номер > len(оружие_список):
        await interaction.response.send_message(f"`[ERR]` Оружие №{оружие_номер} не найдено!", ephemeral=True)
        return

    оруж = оружие_список[оружие_номер - 1]
    слот_ключ = f"слот{слот}"
    if 'обвесы' not in оруж: оруж['обвесы'] = {"слот1": None, "слот2": None}

    if действие == "установить":
        if not обвес:
            await interaction.response.send_message("`[ERR]` Укажи обвес!", ephemeral=True)
            return
        обвесы = load_attachments()
        if обвес not in обвесы:
            await interaction.response.send_message(f"`[ERR]` Доступные: {', '.join(обвесы)}", ephemeral=True)
            return
        инв = p.get('инвентарь_обвесов', [])
        if обвес not in инв:
            await interaction.response.send_message(f"`[ERR]` Нет **{обвес}** в инвентаре!\nТвои: {', '.join(инв) or 'пусто'}", ephemeral=True)
            return
        for ключ in ['слот1', 'слот2']:
            if оруж['обвесы'][ключ] == обвес:
                await interaction.response.send_message(f"`[ERR]` Уже стоит в слоте {ключ[-1]}!", ephemeral=True)
                return
        if оруж['обвесы'][слот_ключ]:
            await interaction.response.send_message(f"`[ERR]` Слот {слот} занят **{оруж['обвесы'][слот_ключ]}**!", ephemeral=True)
            return
        оруж['обвесы'][слот_ключ] = обвес
        инв.remove(обвес)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{обвес}** → {оруж['название'].title()} (слот {слот})!\n{обвесы[обвес]['эффект']}")

    elif действие == "снять":
        if not оруж['обвесы'][слот_ключ]:
            await interaction.response.send_message(f"`[ERR]` Слот {слот} пуст.", ephemeral=True)
            return
        ст = оруж['обвесы'][слот_ключ]
        оруж['обвесы'][слот_ключ] = None
        if 'инвентарь_обвесов' not in p: p['инвентарь_обвесов'] = []
        p['инвентарь_обвесов'].append(ст)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{ст}** снят с {оруж['название'].title()}.")

# ==========================================
# ВЫДАТЬ ОБВЕС
# ==========================================
@bot.tree.command(name="выдать_обвес", description="[Гейммастер] Выдать обвес")
@app_commands.autocomplete(обвес=автодополнение_обвесов)
@app_commands.describe(игрок="Игрок", обвес="Название")
async def выдать_обвес(interaction: discord.Interaction, игрок: discord.Member, обвес: str):
    if "Гейммастер" not in [р.name for р in interaction.user.roles]:
        await interaction.response.send_message("`[ERR]` Только Гейммастер!", ephemeral=True)
        return
    персонажи = load_characters()
    цель_id = str(игрок.id)
    if цель_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Нет персонажа!", ephemeral=True)
        return
    обвесы = load_attachments()
    if обвес not in обвесы:
        await interaction.response.send_message(f"`[ERR]` Доступные: {', '.join(обвесы)}", ephemeral=True)
        return
    p = персонажи[цель_id]
    if 'инвентарь_обвесов' not in p: p['инвентарь_обвесов'] = []
    if обвес in p['инвентарь_обвесов']:
        await interaction.response.send_message(f"`[ERR]` Уже есть!", ephemeral=True)
        return
    p['инвентарь_обвесов'].append(обвес)
    save_characters(персонажи)
    д = обвесы[обвес]
    await interaction.response.send_message(f"`[SYS]` {игрок.mention} получил **{обвес}**!\n{д['эффект']} | Цена: {д['цена']}")

# ==========================================
# НАДЕТЬ СНАРЯЖЕНИЕ
# ==========================================
@bot.tree.command(name="надеть", description="Надеть или снять предмет снаряжения")
@app_commands.describe(действие="Надеть или снять", номер="Номер предмета из /снаряжение список")
@app_commands.choices(действие=[
    app_commands.Choice(name="надеть", value="надеть"),
    app_commands.Choice(name="снять", value="снять"),
])
async def надеть(interaction: discord.Interaction, действие: str, номер: int):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    if 'надетое_снаряжение' not in p:
        p['надетое_снаряжение'] = []

    if действие == "надеть":
        # Надеть можно только из обычного инвентаря (первые N номеров)
        if номер < 1 or номер > len(p['снаряжение']):
            await interaction.response.send_message(f"`[ERR]` №{номер} не найден в инвентаре! Используй `/снаряжение список`.", ephemeral=True)
            return
        предмет = p['снаряжение'][номер - 1]
        if предмет in p['надетое_снаряжение']:
            await interaction.response.send_message(f"`[ERR]` **{предмет}** уже надет!", ephemeral=True)
            return
        p['снаряжение'].remove(предмет)
        p['надетое_снаряжение'].append(предмет)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{предмет}** надет! ✅")

    elif действие == "снять":
        общий = p['снаряжение'] + p['надетое_снаряжение']
        if номер < 1 or номер > len(общий):
            await interaction.response.send_message(f"`[ERR]` №{номер} не найден! Используй `/снаряжение список`.", ephemeral=True)
            return
        предмет = общий[номер - 1]
        if предмет not in p['надетое_снаряжение']:
            await interaction.response.send_message(f"`[ERR]` **{предмет}** не надет!", ephemeral=True)
            return
        p['надетое_снаряжение'].remove(предмет)
        p['снаряжение'].append(предмет)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{предмет}** снят и возвращён в инвентарь.")

# ==========================================
# АТАКА
# ==========================================
@bot.tree.command(name="атака", description="Атаковать экипированным оружием")
@app_commands.describe(рука="Какой рукой", удача="Удача", мод="Модификатор")
@app_commands.choices(рука=[
    app_commands.Choice(name="правая", value="правая"),
    app_commands.Choice(name="левая", value="левая"),
])
async def атака(interaction: discord.Interaction, рука: str = "правая", удача: int = 0, мод: int = 0):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    сп = p.get('оружие', [])
    руки = p.get('руки', {"правая": None, "левая": None})
    экип = руки.get(рука)
    if экип is None or экип >= len(сп):
        await interaction.response.send_message(f"`[ERR]` В {рука} руке пусто!", ephemeral=True)
        return
    оруж = сп[экип]
    ш = оруж['шаблон']
    навык = ш['навык']
    статы = p['статы']
    стат_бонус = статы.get(SKILLS[навык]['стат'], 1)
    ур = p.get('навыки', {}).get(навык, 0)
    бонус_удачи = 0
    if удача > 0:
        макс = статы.get('удача', 1)
        тек = p.get('удача_текущая', макс)
        восстановить_удачу(p)
        тек = p.get('удача_текущая', макс)
        if удача > тек:
            await interaction.response.send_message(f"`[ERR]` Удачи: {тек}/{макс}", ephemeral=True)
            return
        p['удача_текущая'] = тек - удача
        p['удача_последняя_трата'] = datetime.datetime.now().isoformat()
        save_characters(персонажи)
        бонус_удачи = удача
    общий = стат_бонус + ур + бонус_удачи + мод
    бросок = random.randint(1, 10)
    результат = бросок + общий
    взрыв_текст = ""
    тип = ""
    if бросок == 10:
        взрыв = random.randint(1, 10)
        результат += взрыв
        тип = "🔥 КРИТИЧЕСКАЯ УДАЧА!"
        взрыв_текст = f"\n║ 💥 +{взрыв}"
    elif бросок == 1:
        взрыв = random.randint(1, 10)
        результат -= взрыв
        тип = "💀 КРИТИЧЕСКАЯ НЕУДАЧА!"
        взрыв_текст = f"\n║ 💥 -{взрыв}"
    ч = ш['урон'].split('d')
    урон = sum(random.randint(1, int(ч[1])) for _ in range(int(ч[0])))
    await interaction.response.send_message(
        f"`[ATK]` {interaction.user.mention} ({рука}): **{оруж['название'].title()}**\n"
        f"╔═══ АТАКА ═══╗\n║ D10: **{бросок}**\n║ Навык: +{ур}\n║ {SHORT_STATS[SKILLS[навык]['стат']]}: +{стат_бонус}" +
        (f"\n║ Удача: +{бонус_удачи}" if бонус_удачи else "") +
        (f"\n║ Мод: {мод:+}" if мод else "") +
        f"{взрыв_текст}\n║ Итого: **{результат}**\n╠═══ УРОН ═══╣\n║ {ш['урон']}: **{урон}**\n╚═══ {тип} ═══╝"
    )

# ==========================================
# ВЫДАТЬ
# ==========================================
@bot.tree.command(name="выдать", description="[Гейммастер] Выдать ресурсы")
@app_commands.describe(игрок="Кому", тип="Что выдать", количество="Сколько")
@app_commands.choices(тип=[
    app_commands.Choice(name="О.У.", value="оу"),
    app_commands.Choice(name="Эдди", value="эдди"),
])
async def выдать(interaction: discord.Interaction, игрок: discord.Member, тип: str, количество: int):
    if "Гейммастер" not in [р.name for р in interaction.user.roles]:
        await interaction.response.send_message("`[ERR]` Только Гейммастер!", ephemeral=True)
        return
    персонажи = load_characters()
    цель_id = str(игрок.id)
    if цель_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Нет персонажа!", ephemeral=True)
        return
    p = персонажи[цель_id]
    if тип == "оу":
        p['оу'] += количество
        save_characters(персонажи)
        await interaction.response.send_message(f"`[ОУ]` +{количество} для {игрок.mention}. Всего: **{p['оу']}**")
    else:
        p['эдди'] += количество
        save_characters(персонажи)
        await interaction.response.send_message(f"`[€$]` {'+' if количество >= 0 else ''}{количество} для {игрок.mention}. Баланс: **{p['эдди']}**")

# ==========================================
# УДАЛИТЬ ВЕЩЬ (ГМ)
# ==========================================
@bot.tree.command(name="удалить_вещь", description="[Гейммастер] Удалить вещь у игрока")
@app_commands.describe(игрок="У кого", тип="Что удалить", номер="Номер")
@app_commands.choices(тип=[
    app_commands.Choice(name="снаряжение", value="снаряжение"),
    app_commands.Choice(name="оружие", value="оружие"),
    app_commands.Choice(name="обвес", value="обвес"),
    app_commands.Choice(name="броня", value="броня"),
    app_commands.Choice(name="киберимплант", value="кибер"),
])
async def удалить_вещь(interaction: discord.Interaction, игрок: discord.Member, тип: str, номер: str = None):
    if "Гейммастер" not in [р.name for р in interaction.user.roles]:
        await interaction.response.send_message("`[ERR]` Только Гейммастер!", ephemeral=True)
        return
    персонажи = load_characters()
    цель_id = str(игрок.id)
    if цель_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Нет персонажа!", ephemeral=True)
        return
    p = персонажи[цель_id]

    if тип == "снаряжение":
        if not номер:
            await interaction.response.send_message("`[ERR]` Укажи номер из списка снаряжения!", ephemeral=True)
            return
        try: n = int(номер)
        except:
            await interaction.response.send_message("`[ERR]` Нужно число!", ephemeral=True)
            return
        общий = p.get('снаряжение', []) + p.get('надетое_снаряжение', [])
        if n < 1 or n > len(общий):
            await interaction.response.send_message(f"`[ERR]` №{n} не найден!", ephemeral=True)
            return
        удалено = общий[n - 1]
        if удалено in p.get('снаряжение', []): p['снаряжение'].remove(удалено)
        else: p.get('надетое_снаряжение', []).remove(удалено)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{удалено}** удалён у {игрок.mention}.")

    elif тип == "оружие":
        if not номер:
            await interaction.response.send_message("`[ERR]` Укажи номер оружия!", ephemeral=True)
            return
        try: n = int(номер)
        except:
            await interaction.response.send_message("`[ERR]` Нужно число!", ephemeral=True)
            return
        сп = p.get('оружие', [])
        if n < 1 or n > len(сп):
            await interaction.response.send_message(f"`[ERR]` №{n} не найден!", ephemeral=True)
            return
        удалено = сп.pop(n - 1)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{удалено['название']}** удалён у {игрок.mention}.")

    elif тип == "обвес":
        if not номер:
            await interaction.response.send_message("`[ERR]` Укажи номер обвеса!", ephemeral=True)
            return
        try: n = int(номер)
        except:
            await interaction.response.send_message("`[ERR]` Нужно число!", ephemeral=True)
            return
        инв = p.get('инвентарь_обвесов', [])
        if n < 1 or n > len(инв):
            await interaction.response.send_message(f"`[ERR]` №{n} не найден!", ephemeral=True)
            return
        удалено = инв.pop(n - 1)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{удалено}** удалён у {игрок.mention}.")

    elif тип == "броня":
        if not номер:
            await interaction.response.send_message("`[ERR]` Укажи номер брони!", ephemeral=True)
            return
        try: n = int(номер)
        except:
            await interaction.response.send_message("`[ERR]` Нужно число!", ephemeral=True)
            return
        общий = p.get('броня', []) + [v for v in p.get('надето_броня', {}).values() if v is not None]
        if n < 1 or n > len(общий):
            await interaction.response.send_message(f"`[ERR]` №{n} не найден!", ephemeral=True)
            return
        удалено = общий[n - 1]
        if удалено in p.get('броня', []): p['броня'].remove(удалено)
        else:
            for слот in p.get('надето_броня', {}):
                if p['надето_броня'][слот] == удалено:
                    p['надето_броня'][слот] = None
                    break
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{удалено['название']}** удалён у {игрок.mention}.")

    elif тип == "кибер":
        if not номер:
            await interaction.response.send_message("`[ERR]` Укажи номер!", ephemeral=True)
            return
        try: n = int(номер)
        except:
            await interaction.response.send_message("`[ERR]` Нужно число!", ephemeral=True)
            return
        общий = list(p.get('киберимпланты', []))
        for импланты in p.get('установлено_импланты', {}).values():
            общий.extend(импланты)
        if n < 1 or n > len(общий):
            await interaction.response.send_message(f"`[ERR]` №{n} не найден!", ephemeral=True)
            return
        удалено = общий[n - 1]
        if удалено in p.get('киберимпланты', []):
            p['киберимпланты'].remove(удалено)
        else:
            for импланты in p.get('установлено_импланты', {}).values():
                if удалено in импланты:
                    импланты.remove(удалено)
                    break
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{удалено['название']}** удалён у {игрок.mention}.")
# ==========================================
# КУБИК
# ==========================================
@bot.tree.command(name="к", description="Бросить кубики")
@app_commands.describe(запрос="d20, 3d6, 2d6+3")
async def к(interaction: discord.Interaction, запрос: str = "d6"):
    запрос = запрос.lower().replace(' ', '')
    match = re.match(r'^(\d*)d(\d+)([+-]\d+)?$', запрос)
    if not match:
        await interaction.response.send_message("`[ERR]` d20, 3d6, 2d6+3", ephemeral=True)
        return
    к, г, м = int(match.group(1) or 1), int(match.group(2)), int(match.group(3) or 0)
    if к > 20 or г > 1000:
        await interaction.response.send_message("`[ERR]` Слишком много!", ephemeral=True)
        return
    броски = [random.randint(1, г) for _ in range(к)]
    сумма = sum(броски) + м
    if к == 1 and м == 0:
        await interaction.response.send_message(f"`[DICE]` {interaction.user.mention} ▶ D{г}: **{броски[0]}**")
    else:
        текст = f"`[DICE]` {interaction.user.mention} ▶ {к}D{г}{'+' if м > 0 else ''}{м if м else ''}\n" + \
                (f"Броски: {', '.join(map(str, броски))}\n" if к > 1 else "") + f"Результат: **{сумма}**"
        await interaction.response.send_message(текст)

# ==========================================
# ВАЙП
# ==========================================
@bot.tree.command(name="вайп", description="Удалить всех (админ)")
async def вайп(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("`[ERR]` Только админ!", ephemeral=True)
        return
    if not load_characters():
        await interaction.response.send_message("Пусто.", ephemeral=True)
        return
    save_characters({})
    await interaction.response.send_message("💀 Все удалены.")

# ==========================================
# ЗАПУСК
# ==========================================
bot.run(TOKEN)