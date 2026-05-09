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

# ==========================================
# ХАРАКТЕРИСТИКИ
# ==========================================
SHORT_STATS = {
    "интеллект": "ИНТ",
    "сила воли": "ВОЛЯ",
    "харизма": "ХАР",
    "эмпатия": "ЭМП",
    "техника": "ТЕХ",
    "реакция": "РЕА",
    "удача": "УДЧ",
    "телосложение": "ТЕЛ",
    "ловкость": "ЛВК",
    "скорость": "СКО"
}

STAT_EMOJI = {
    "интеллект": "🧠",
    "сила воли": "💪",
    "харизма": "👑",
    "эмпатия": "💙",
    "техника": "🔧",
    "реакция": "⚡",
    "удача": "🍀",
    "телосложение": "🦾",
    "ловкость": "🤸",
    "скорость": "💨"
}

# ==========================================
# НАВЫКИ
# ==========================================
SKILLS = {
    # ВОЛЯ
    "концентрация":            {"стат": "сила воли"},
    "выносливость":            {"стат": "сила воли"},
    "сопротивление пыткам":    {"стат": "сила воли"},
    # ИНТ
    "сокрытие/раскрытие":     {"стат": "интеллект"},
    "чтение по губам":         {"стат": "интеллект"},
    "внимательность":          {"стат": "интеллект"},
    "выслеживание":            {"стат": "интеллект"},
    "обращение с животными":   {"стат": "интеллект"},
    "бюрократия":              {"стат": "интеллект"},
    "бизнес":                  {"стат": "интеллект"},
    "композиция":              {"стат": "интеллект"},
    "криминология":            {"стат": "интеллект"},
    "криптография":            {"стат": "интеллект"},
    "дедукция":                {"стат": "интеллект"},
    "образование":             {"стат": "интеллект"},
    "язык":                    {"стат": "интеллект"},
    "поиск информации":        {"стат": "интеллект"},
    "знание местности":        {"стат": "интеллект"},
    "наука":                   {"стат": "интеллект"},
    "выживание в пустыне":     {"стат": "интеллект"},
    # ЛВК
    "атлетика":                {"стат": "ловкость"},
    "акробатика":              {"стат": "ловкость"},
    "скрытность":              {"стат": "ловкость"},
    "рукопашный бой":          {"стат": "ловкость"},
    "уклонение":               {"стат": "ловкость"},
    "оружие ближнего боя":     {"стат": "ловкость"},
    # РЕА
    "вождение":                {"стат": "реакция"},
    "пилотирование":           {"стат": "реакция", "цена": 2},
    "автоматический огонь":    {"стат": "реакция", "цена": 2},
    "пистолеты":               {"стат": "реакция"},
    "оружие крупного калибра": {"стат": "реакция", "цена": 2},
    "тактическое оружие":      {"стат": "реакция"},
    # ХАР
    "актерское мастерство":    {"стат": "харизма"},
    "допрос":                  {"стат": "харизма"},
    "убеждение":               {"стат": "харизма"},
    "знаток улиц":             {"стат": "харизма"},
    "торговля":                {"стат": "харизма"},
    "гардероб и стиль":        {"стат": "харизма"},
    # ЭМП
    "общение":                 {"стат": "эмпатия"},
    "проницательность":        {"стат": "эмпатия"},
    # ТЕХ
    "игра на инструментах":    {"стат": "техника"},
    "авиационные технологии":  {"стат": "техника"},
    "знание техники":          {"стат": "техника"},
    "кибернетика":             {"стат": "техника"},
    "подрывник":               {"стат": "техника", "цена": 2},
    "электроника/безопасность":{"стат": "техника", "цена": 2},
    "первая помощь":           {"стат": "техника"},
    "фальсификация":           {"стат": "техника"},
    "автомеханика":            {"стат": "техника"},
    "парамедик":               {"стат": "техника", "цена": 2},
    "кино-/фототехника":      {"стат": "техника"},
    "взлом замков":            {"стат": "техника"},
    "карманник":               {"стат": "техника"},
    "оружейник":               {"стат": "техника"},
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

# ==========================================
# СИНХРОНИЗАЦИЯ КОМАНД
# ==========================================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Бот {bot.user} готов к работе! Слэш-команды синхронизированы.")

# ==========================================
# ПЕРСОНАЖ
# ==========================================
@bot.tree.command(name="персонаж", description="Управление персонажем")
@app_commands.describe(
    действие="Что сделать",
    имя_персонажа="Имя персонажа (для создания)",
    игрок="Игрок (для создания/удаления — @упоминание)"
)
@app_commands.choices(действие=[
    app_commands.Choice(name="показать", value="показать"),
    app_commands.Choice(name="создать", value="создать"),
    app_commands.Choice(name="удалить", value="удалить"),
])
async def персонаж(interaction: discord.Interaction, действие: str, имя_персонажа: str = None, игрок: discord.Member = None):
    персонажи = load_characters()

    if действие == "показать":
        if игрок:
            цель = игрок
        else:
            цель = interaction.user
        автор_id = str(цель.id)
        if автор_id not in персонажи:
            if цель == interaction.user:
                await interaction.response.send_message(f"`[ERR]` У тебя ещё нет персонажа!", ephemeral=True)
            else:
                await interaction.response.send_message(f"`[ERR]` У {цель.mention} нет персонажа!", ephemeral=True)
            return

        p = персонажи[автор_id]
        embed = discord.Embed(
            title=f"`[DOSSIER]` {p['имя']}",
            description=f"О.У.: **{p['оу']}**",
            color=0x00ffcc
        )

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
        человечность = p.get('человечность', статы.get('эмпатия', 1) * 10)
        эмпатия = человечность // 10
        статы['эмпатия'] = эмпатия

        embed.add_field(
            name="`[DER]` Производные",
            value=(
                f"❤️ Здоровье: **{здоровье}**\n"
                f"🤖 Человечность: **{человечность}**\n"
                f"🎯 Инициатива: **{реакция}**\n"
                f"💰 Эдди: **{p['эдди']}** €$"
            ),
            inline=False
        )

        if p['импланты']:
            импланты = '\n'.join([f"◆ {imp}" for imp in p['импланты']])
        else:
            импланты = "Нет имплантов"
        embed.add_field(name="`[IMPL]` Импланты", value=импланты, inline=True)

        if p['снаряжение']:
            снаряга = '\n'.join([f"▸ {item}" for item in p['снаряжение']])
        else:
            снаряга = "Пусто"
        embed.add_field(name="`[GEAR]` Снаряжение", value=снаряга, inline=True)

        if человечность < 0:
            embed.add_field(
                name="`[PSY]` Статус",
                value="**НЕКОНТРОЛИРУЕМЫЙ КИБЕРПСИХ**\n*Персонаж полностью потерял связь с реальностью. Управление невозможно.*",
                inline=False
            )
        elif эмпатия == 0:
            embed.add_field(
                name="`[PSY]` Статус",
                value="Киберпсихоз\n*Штраф -2 к броскам харизмы*",
                inline=False
            )
        elif эмпатия == 1:
            embed.add_field(
                name="`[PSY]` Статус",
                value="-# *Диссоциативное расстройство*\n-# *Штраф -1 к броскам харизмы*",
                inline=False
            )

        embed.set_footer(text=f"NetRunner ID: {цель.name}")
        await interaction.response.send_message(embed=embed)

    elif действие == "создать":
        if "Анкетолог" not in [роль.name for роль in interaction.user.roles]:
            await interaction.response.send_message("`[ERR]` Только Анкетолог может создавать персонажей!", ephemeral=True)
            return
        if имя_персонажа is None:
            await interaction.response.send_message("`[SYS]` Укажи имя персонажа!", ephemeral=True)
            return
        if len(имя_персонажа) > 30:
            await interaction.response.send_message("`[ERR]` Имя персонажа не может быть длиннее 30 символов!", ephemeral=True)
            return
        if игрок is None:
            await interaction.response.send_message("`[SYS]` Укажи игрока через @упоминание!", ephemeral=True)
            return
        цель_id_str = str(игрок.id)
        if цель_id_str in персонажи:
            await interaction.response.send_message(f"`[WARN]` У {игрок.mention} уже есть персонаж!", ephemeral=True)
            return

        персонажи[цель_id_str] = {
            "имя": имя_персонажа,
            "оу": 0,
            "эдди": 1000,
            "статы": {
                "интеллект": 1, "сила воли": 1, "харизма": 1,
                "эмпатия": 1, "техника": 1, "реакция": 1,
                "удача": 1, "телосложение": 1, "ловкость": 1, "скорость": 1
            },
            "навыки": {},
            "удача_текущая": 1,
            "удача_последняя_трата": None,
            "человечность": 10,
            "базовая_эмпатия": 1,
            "импланты": [],
            "снаряжение": [],
            "оружие": []
        }
        save_characters(персонажи)
        await interaction.response.send_message(
            f"`[SYS]` ✅ Персонаж **{имя_персонажа}** создан для {игрок.mention}!\n"
            f"`[INFO]` Стартовые очки характеристик: **35**\n"
            f"`[INFO]` Характеристики начинаются с 1 (макс. 8)\n"
            f"`[INFO]` Навыки начинаются с 0 (макс. 8, на старте макс. 4)"
        )

    elif действие == "удалить":
        if "Анкетолог" not in [роль.name for роль in interaction.user.roles]:
            await interaction.response.send_message("`[ERR]` Только Анкетолог может удалять персонажей!", ephemeral=True)
            return
        if игрок is None:
            await interaction.response.send_message("`[SYS]` Укажи игрока через @упоминание!", ephemeral=True)
            return
        цель_id_str = str(игрок.id)
        if цель_id_str not in персонажи:
            await interaction.response.send_message(f"`[ERR]` У {игрок.mention} нет персонажа!", ephemeral=True)
            return
        del персонажи[цель_id_str]
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` Персонаж {игрок.mention} удалён. Чистый лист.")


# ==========================================
# КОМАНДЫ АНКЕТОЛОГА
# ==========================================
@bot.tree.command(name="установить_статы", description="[Анкетолог] Установить все характеристики игроку")
@app_commands.describe(
    игрок="Выбери игрока",
    интеллект="Интеллект (1-8)",
    сила_воли="Сила воли (1-8)",
    харизма="Харизма (1-8)",
    эмпатия="Эмпатия (1-8)",
    техника="Техника (1-8)",
    реакция="Реакция (1-8)",
    удача="Удача (1-8)",
    телосложение="Телосложение (1-8)",
    ловкость="Ловкость (1-8)",
    скорость="Скорость (1-8)",
)
async def установить_статы(
    interaction: discord.Interaction,
    игрок: discord.Member,
    интеллект: int = 1, сила_воли: int = 1, харизма: int = 1,
    эмпатия: int = 1, техника: int = 1, реакция: int = 1,
    удача: int = 1, телосложение: int = 1, ловкость: int = 1, скорость: int = 1,
):
    if "Анкетолог" not in [роль.name for роль in interaction.user.roles]:
        await interaction.response.send_message("`[ERR]` Только Анкетолог может это делать!", ephemeral=True)
        return
    персонажи = load_characters()
    цель_id = str(игрок.id)
    if цель_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` У {игрок.mention} нет персонажа!", ephemeral=True)
        return
    статы = {
        "интеллект": интеллект, "сила воли": сила_воли, "харизма": харизма,
        "эмпатия": эмпатия, "техника": техника, "реакция": реакция,
        "удача": удача, "телосложение": телосложение, "ловкость": ловкость, "скорость": скорость,
    }
    for name, value in статы.items():
        if value < 1 or value > 8:
            await interaction.response.send_message(f"`[ERR]` {name}: значение должно быть от 1 до 8!", ephemeral=True)
            return
    всего = sum(статы.values())
    if всего > 45:
        await interaction.response.send_message(f"`[ERR]` Слишком много! Сумма статов: {всего}, максимум 45.", ephemeral=True)
        return
    персонажи[цель_id]['статы'] = статы
    персонажи[цель_id]['базовая_эмпатия'] = статы['эмпатия']
    персонажи[цель_id]['человечность'] = статы['эмпатия'] * 10
    save_characters(персонажи)
    строки = []
    for full_name, short_name in SHORT_STATS.items():
        emoji = STAT_EMOJI.get(full_name, "◆")
        строки.append(f"{emoji} {short_name}: **{статы[full_name]}**")
    await interaction.response.send_message(
        f"`[SYS]` Характеристики {игрок.mention} установлены!\n" + '\n'.join(строки)
    )


@bot.tree.command(name="установить_навыки", description="[Анкетолог] Установить навыки игроку")
@app_commands.autocomplete(навык1=автодополнение_навыков_анкетолог, навык2=автодополнение_навыков_анкетолог, навык3=автодополнение_навыков_анкетолог, навык4=автодополнение_навыков_анкетолог, навык5=автодополнение_навыков_анкетолог)
@app_commands.describe(
    игрок="Игрок",
    навык1="Первый навык", уровень1="Уровень (0-8)",
    навык2="Второй навык", уровень2="Уровень (0-8)",
    навык3="Третий навык", уровень3="Уровень (0-8)",
    навык4="Четвёртый навык", уровень4="Уровень (0-8)",
    навык5="Пятый навык", уровень5="Уровень (0-8)",
)
async def установить_навыки(
    interaction: discord.Interaction,
    игрок: discord.Member,
    навык1: str = None, уровень1: int = 0,
    навык2: str = None, уровень2: int = 0,
    навык3: str = None, уровень3: int = 0,
    навык4: str = None, уровень4: int = 0,
    навык5: str = None, уровень5: int = 0,
):
    if "Анкетолог" not in [роль.name for роль in interaction.user.roles]:
        await interaction.response.send_message("`[ERR]` Только Анкетолог может это делать!", ephemeral=True)
        return
    персонажи = load_characters()
    цель_id = str(игрок.id)
    if цель_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` У {игрок.mention} нет персонажа!", ephemeral=True)
        return
    p = персонажи[цель_id]
    if 'навыки' not in p:
        p['навыки'] = {}
    потрачено = sum(p.get('навыки', {}).values())
    лимит = 4 if (потрачено == 0 and p['оу'] == 0) else 8
    установлено = []
    пары = [(навык1, уровень1), (навык2, уровень2), (навык3, уровень3), (навык4, уровень4), (навык5, уровень5)]
    for назв, ур in пары:
        if назв is None or назв.strip() == "" or назв == "не указано":
            continue
        if назв not in SKILLS:
            await interaction.response.send_message(f"`[ERR]` Навык «{назв}» не найден!", ephemeral=True)
            return
        if ур < 0 or ур > лимит:
            await interaction.response.send_message(f"`[ERR]` Уровень навыка должен быть 0-{лимит}!", ephemeral=True)
            return
        if ур == 0:
            if назв in p['навыки']:
                del p['навыки'][назв]
        else:
            p['навыки'][назв] = ур
        установлено.append(f"**{назв.title()}**: ур.{ур}")
    save_characters(персонажи)
    if установлено:
        await interaction.response.send_message(f"`[SYS]` Навыки {игрок.mention} установлены!\n" + '\n'.join(установлено))
    else:
        await interaction.response.send_message(f"`[SYS]` Навыки {игрок.mention} не изменены (не указаны).")


# ==========================================
# ВОССТАНОВЛЕНИЕ УДАЧИ
# ==========================================
def восстановить_удачу(p):
    from datetime import datetime, timedelta
    макс_удача = p['статы'].get('удача', 1)
    текущая = p.get('удача_текущая', макс_удача)
    последняя = p.get('удача_последняя_трата', None)
    if текущая >= макс_удача:
        return текущая, 0
    if последняя is None:
        return макс_удача, макс_удача - текущая
    try:
        время_траты = datetime.fromisoformat(последняя)
        сейчас = datetime.now()
        разница = сейчас - время_траты
        часы = разница.total_seconds() / 3600
        восстановлено = int(часы // 48)
        if восстановлено > 0:
            новая = min(макс_удача, текущая + восстановлено)
            реально_восстановлено = новая - текущая
            p['удача_текущая'] = новая
            p['удача_последняя_трата'] = (время_траты + timedelta(hours=48 * реально_восстановлено)).isoformat()
            return новая, реально_восстановлено
    except:
        pass
    return текущая, 0


# ==========================================
# ЧЕЛОВЕЧНОСТЬ
# ==========================================
@bot.tree.command(name="человечность", description="Изменить человечность персонажа")
@app_commands.describe(игрок="Игрок", изменение="На сколько изменить (отрицательное — потеря)")
async def человечность(interaction: discord.Interaction, игрок: discord.Member, изменение: int):
    персонажи = load_characters()
    цель_id = str(игрок.id)
    if цель_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` У {игрок.mention} нет персонажа!", ephemeral=True)
        return
    p = персонажи[цель_id]
    if 'человечность' not in p:
        p['человечность'] = p['статы'].get('эмпатия', 1) * 10
    старая = p['человечность']
    новая = старая + изменение
    базовая = p.get('базовая_эмпатия', p['статы'].get('эмпатия', 1))
    максимум = базовая * 10
    if новая > максимум:
        новая = максимум
    p['человечность'] = новая
    p['статы']['эмпатия'] = новая // 10
    save_characters(персонажи)
    псих_сообщение = ""
    if новая < 0:
        псих_сообщение = "\n💀💀💀 **ПЕРСОНАЖ СТАЛ НЕКОНТРОЛИРУЕМЫМ КИБЕРПСИХОМ!** 💀💀💀"
    elif новая // 10 == 0:
        псих_сообщение = "\n⚠️ **КИБЕРПСИХОЗ!** Персонаж на грани."
    elif новая // 10 == 1:
        псих_сообщение = "\n*Персонаж страдает диссоциативным расстройством.*"
    await interaction.response.send_message(
        f"💀 **{p['имя']}** — изменение человечности!\n"
        f"Человечность: {старая} → **{новая}**\n"
        f"Эмпатия: **{новая // 10}** [{SHORT_STATS['эмпатия']}]"
        f"{псих_сообщение}"
    )


# ==========================================
# СТАТ
# ==========================================
@bot.tree.command(name="стат", description="Показать характеристики персонажа")
@app_commands.describe(игрок="Чей лист показать (можно не указывать, тогда свой)")
async def стат(interaction: discord.Interaction, игрок: discord.Member = None):
    персонажи = load_characters()
    if игрок is None:
        цель = interaction.user
    else:
        цель = игрок
    автор_id = str(цель.id)
    if автор_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` У {цель.mention} нет персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    статы = p['статы']
    embed = discord.Embed(title=f"`[STAT]` {p['имя']} — Характеристики", description=f"О.У.: **{p['оу']}**", color=0x00ccff)
    for full_name, short_name in SHORT_STATS.items():
        emoji = STAT_EMOJI.get(full_name, "◆")
        значение = статы.get(full_name, 1)
        if full_name == "удача":
            текущая = p.get('удача_текущая', значение)
            восстановить_удачу(p)
            текущая = p.get('удача_текущая', значение)
            embed.add_field(name=f"{emoji} {full_name.upper()} [{short_name}]", value=f"**{текущая}**", inline=True)
        elif full_name == "эмпатия":
            базовая = p.get('базовая_эмпатия', значение)
            embed.add_field(name=f"{emoji} {full_name.upper()} [{short_name}]", value=f"**{базовая}**", inline=True)
        else:
            embed.add_field(name=f"{emoji} {full_name.upper()} [{short_name}]", value=f"**{значение}**", inline=True)
    embed.set_footer(text=f"Максимум: 8")
    await interaction.response.send_message(embed=embed)


# ==========================================
# НАВЫК (ПОКАЗ)
# ==========================================
@bot.tree.command(name="навык", description="Показать навыки персонажа")
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
        await interaction.response.send_message(f"`[ERR]` Сначала создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    статы = p['статы']
    if 'навыки' not in p:
        p['навыки'] = {}
    навыки_игрока = p['навыки']
    потрачено_оу = sum(навыки_игрока.values())
    группа_статов = {
        "инт": ["интеллект"],
        "тех": ["техника"],
        "реа_воля": ["реакция", "сила воли"],
        "лвк_хар": ["ловкость", "харизма"],
    }
    названия = {
        "инт": "Интеллект",
        "тех": "Техника",
        "реа_воля": "Реакция и Воля",
        "лвк_хар": "Ловкость и Харизма",
    }
    активные = группа_статов.get(группа, [])
    embed = discord.Embed(
        title=f"`[SKILL]` {p['имя']} — {названия.get(группа, '')}",
        description=f"О.У.: **{p['оу']}** (потрачено: {потрачено_оу})",
        color=0x00ffaa
    )
    группы = {}
    for skill_name, skill_data in SKILLS.items():
        стат = skill_data['стат']
        if стат not in активные:
            continue
        if стат not in группы:
            группы[стат] = []
        уровень_навыка = навыки_игрока.get(skill_name, 0)
        стат_бонус = статы.get(стат, 1)
        общий_бонус = уровень_навыка + стат_бонус
        группы[стат].append(f"{skill_name}: +{общий_бонус} (ур.{уровень_навыка})")
    все_строки = []
    for стат in активные:
        if стат in группы:
            короткое = SHORT_STATS[стат]
            значение = статы.get(стат, 1)
            все_строки.append(f"**[{короткое} +{значение}]**")
            все_строки.extend(группы[стат])
            все_строки.append("")
    if все_строки:
        embed.add_field(name="\u200b", value='\n'.join(все_строки), inline=False)
    embed.set_footer(text=f"Цена: 1-2 О.У. | /бросок [навык] — проверка")
    await interaction.response.send_message(embed=embed)


# ==========================================
# НАВЫК АП (ПОВЫШЕНИЕ)
# ==========================================
@bot.tree.command(name="навык_ап", description="Повысить навык (1-2 О.У. = 1 уровень)")
@app_commands.autocomplete(навык=автодополнение_навыков)
async def навык_ап(interaction: discord.Interaction, навык: str):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` Сначала создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    статы = p['статы']
    if 'навыки' not in p:
        p['навыки'] = {}
    навыки_игрока = p['навыки']
    if навык not in SKILLS:
        await interaction.response.send_message(f"`[ERR]` Навык «{навык}» не найден.", ephemeral=True)
        return
    текущий = навыки_игрока.get(навык, 0)
    if текущий >= 8:
        await interaction.response.send_message(f"`[WARN]` Максимум 8!", ephemeral=True)
        return
    цена = SKILLS[навык].get("цена", 1)
    if p['оу'] < цена:
        await interaction.response.send_message(f"`[ERR]` Нужно {цена} О.У.! Баланс: **{p['оу']}**", ephemeral=True)
        return
    p['оу'] -= цена
    навыки_игрока[навык] = текущий + 1
    save_characters(персонажи)
    бонус = статы.get(SKILLS[навык]['стат'], 1)
    новый = текущий + 1 + бонус
    await interaction.response.send_message(
        f"`[SYS]` **{навык.title()}** повышен до ур. **{текущий + 1}**!\n"
        f"Бонус: +{новый} | Потрачено О.У.: {цена} | Осталось: **{p['оу']}**"
    )


# ==========================================
# БРОСОК
# ==========================================
@bot.tree.command(name="бросок", description="Проверить навык (D10 + бонусы)")
@app_commands.autocomplete(навык=автодополнение_навыков)
@app_commands.describe(навык="Название навыка", удача="Сколько удачи потратить", мод="Доп. модификатор (+/-)")
async def бросок(interaction: discord.Interaction, навык: str, удача: int = 0, мод: int = 0):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` Сначала создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    статы = p['статы']
    if навык not in SKILLS:
        await interaction.response.send_message(f"`[ERR]` Навык «{навык}» не найден.", ephemeral=True)
        return
    бонус_удачи = 0
    if удача > 0:
        макс_удача = статы.get('удача', 1)
        текущая = p.get('удача_текущая', макс_удача)
        новая, восст = восстановить_удачу(p)
        текущая = новая
        if удача > текущая:
            await interaction.response.send_message(
                f"`[ERR]` Недостаточно удачи! Запас: **{текущая}** / {макс_удача}",
                ephemeral=True
            )
            return
        p['удача_текущая'] = текущая - удача
        p['удача_последняя_трата'] = datetime.datetime.now().isoformat()
        save_characters(персонажи)
        бонус_удачи = удача
    skill_data = SKILLS[навык]
    стат_бонус = статы.get(skill_data['стат'], 1)
    уровень_навыка = p.get('навыки', {}).get(навык, 0)
    штраф_психоза = 0
    эмпатия_тек = p.get('человечность', 10) // 10
    if skill_data['стат'] == 'харизма':
        if эмпатия_тек == 0:
            штраф_психоза = -2
        elif эмпатия_тек == 1:
            штраф_психоза = -1
    общий_бонус = стат_бонус + уровень_навыка + бонус_удачи + мод + штраф_психоза
    бросок = random.randint(1, 10)
    результат = бросок + общий_бонус
    взрыв = 0
    взрыв_текст = ""
    тип_взрыва = ""
    if бросок == 10:
        взрыв = random.randint(1, 10)
        результат += взрыв
        тип_взрыва = "🔥 КРИТИЧЕСКАЯ УДАЧА!"
        взрыв_текст = f"\n║ 💥 Взрывной бросок: +{взрыв}"
    elif бросок == 1:
        взрыв = random.randint(1, 10)
        результат -= взрыв
        тип_взрыва = "💀 КРИТИЧЕСКАЯ НЕУДАЧА!"
        взрыв_текст = f"\n║ 💥 Крит-провал: -{взрыв}"
    await interaction.response.send_message(
        f"`[CHECK]` {interaction.user.mention} ▶ **{навык.title()}**\n"
        f"╔═══ D10: **{бросок}** ═══╗\n"
        f"║ Навык: +{уровень_навыка}\n"
        f"║ {SHORT_STATS[skill_data['стат']]}: +{стат_бонус}" +
        (f"\n║ Удача: +{бонус_удачи}" if бонус_удачи > 0 else "") +
        (f"\n║ Мод: {'+' if мод >= 0 else ''}{мод}" if мод != 0 else "") +
        (f"\n║ Киберпсихоз: {штраф_психоза}" if штраф_психоза < 0 else "") +
        f"{взрыв_текст}\n"
        f"║ Итого: **{результат}**\n"
        f"╚═══ {тип_взрыва} ═══╝"
    )


# ==========================================
# ИМПЛАНТ
# ==========================================
@bot.tree.command(name="имплант", description="Управление имплантами")
@app_commands.describe(действие="Что сделать", название="Название импланта")
@app_commands.choices(действие=[
    app_commands.Choice(name="список", value="список"),
    app_commands.Choice(name="добавить", value="добавить"),
    app_commands.Choice(name="удалить", value="удалить"),
])
async def имплант(interaction: discord.Interaction, действие: str, название: str = None):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` Сначала создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    if действие == "список":
        if p['импланты']:
            список = '\n'.join([f"◆ {imp}" for imp in p['импланты']])
            await interaction.response.send_message(f"`[IMPL]` Импланты **{p['имя']}**:\n{список}")
        else:
            await interaction.response.send_message(f"`[INFO]` У **{p['имя']}** нет имплантов.")
    elif действие == "добавить":
        if название is None:
            await interaction.response.send_message("`[ERR]` Укажи название импланта!", ephemeral=True)
            return
        p['импланты'].append(название)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` Имплант **{название}** установлен! 🦾")
    elif действие == "удалить":
        if название is None:
            await interaction.response.send_message("`[ERR]` Укажи название импланта!", ephemeral=True)
            return
        if название in p['импланты']:
            p['импланты'].remove(название)
            save_characters(персонажи)
            await interaction.response.send_message(f"`[SYS]` Имплант **{название}** извлечён.")
        else:
            await interaction.response.send_message(f"`[ERR]` Имплант не найден.", ephemeral=True)


# ==========================================
# СНАРЯЖЕНИЕ (ОБЫЧНОЕ)
# ==========================================
@bot.tree.command(name="снаряжение", description="Управление обычным снаряжением")
@app_commands.describe(действие="Что сделать", предмет="Название предмета")
@app_commands.choices(действие=[
    app_commands.Choice(name="список", value="список"),
    app_commands.Choice(name="добавить", value="добавить"),
    app_commands.Choice(name="удалить", value="удалить"),
])
async def снаряжение(interaction: discord.Interaction, действие: str, предмет: str = None):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` Сначала создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    if действие == "список":
        if p['снаряжение']:
            строки = ["**🎒 Обычное снаряжение:**"]
            for item in p['снаряжение']:
                строки.append(f"▸ {item}")
            await interaction.response.send_message('\n'.join(строки))
        else:
            await interaction.response.send_message("🎒 Обычное снаряжение: пусто")
    elif действие == "добавить":
        if предмет is None:
            await interaction.response.send_message("`[ERR]` Укажи название!", ephemeral=True)
            return
        p['снаряжение'].append(предмет)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{предмет}** добавлен в инвентарь!")
    elif действие == "удалить":
        if предмет is None:
            await interaction.response.send_message("`[ERR]` Укажи название!", ephemeral=True)
            return
        if предмет in p['снаряжение']:
            p['снаряжение'].remove(предмет)
            save_characters(персонажи)
            await interaction.response.send_message(f"`[SYS]` **{предмет}** убран.")
        else:
            await interaction.response.send_message(f"`[ERR]` Предмет не найден.", ephemeral=True)


# ==========================================
# ОРУЖИЕ
# ==========================================
@bot.tree.command(name="оружие", description="Управление оружием")
@app_commands.autocomplete(предмет=автодополнение_оружия)
@app_commands.describe(действие="Что сделать", предмет="Название оружия", качество="Качество оружия")
@app_commands.choices(действие=[
    app_commands.Choice(name="список", value="список"),
    app_commands.Choice(name="добавить", value="добавить"),
    app_commands.Choice(name="удалить", value="удалить"),
])
@app_commands.choices(качество=[
    app_commands.Choice(name="низкое (урон -1, цена ×0.5)", value="низкое"),
    app_commands.Choice(name="обычное (стандарт)", value="обычное"),
    app_commands.Choice(name="высокое (урон +1, цена ×1.5)", value="высокое"),
])
async def оружие(interaction: discord.Interaction, действие: str, предмет: str = None, качество: str = "обычное"):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` Сначала создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    моды = {
        "низкое": {"урон": -1, "цена": 0.5, "знак": "⬇️"},
        "обычное": {"урон": 0, "цена": 1.0, "знак": "➖"},
        "высокое": {"урон": 1, "цена": 1.5, "знак": "⬆️"},
    }
    if действие == "список":
        оружие_список = p.get('оружие', [])
        if оружие_список:
            строки = ["**🔫 Оружие:**"]
            for i, оруж in enumerate(оружие_список, 1):
                ш = оруж['шаблон']
                кач = оруж.get('качество', 'обычное')
                знак = моды[кач]['знак']
                обвесы = оруж.get('обвесы', {})
                с1 = обвесы.get('слот1', None)
                с2 = обвесы.get('слот2', None)
                обвесы_стр = ""
                if с1 or с2:
                    обвесы_стр = f" [{с1 or '—'} | {с2 or '—'}]"
                строки.append(f"{i}. {знак} **{оруж['название'].title()}** ({кач}) — {ш['урон']} ({ш['тип']}){обвесы_стр}")
            await interaction.response.send_message('\n'.join(строки))
        else:
            await interaction.response.send_message("🔫 Оружие: пусто")
    elif действие == "добавить":
        if предмет is None:
            await interaction.response.send_message("`[ERR]` Укажи название!", ephemeral=True)
            return
        шаблоны = load_weapons()
        if предмет not in шаблоны:
            доступные = ', '.join(шаблоны.keys())
            await interaction.response.send_message(
                f"`[ERR]` Оружие не найдено!\nДоступные: {доступные}",
                ephemeral=True
            )
            return
        шаблон = copy.deepcopy(шаблоны[предмет])
        мод = моды[качество]
        if шаблон['урон']:
            части = шаблон['урон'].split('d')
            кубы = int(части[0]) + мод['урон']
            if кубы < 1:
                кубы = 1
            шаблон['урон'] = f"{кубы}d{части[1]}"
        шаблон['цена'] = int(шаблон['цена'] * мод['цена'])
        if 'оружие' not in p:
            p['оружие'] = []
        p['оружие'].append({
            "название": предмет,
            "качество": качество,
            "шаблон": шаблон,
            "обвесы": {"слот1": None, "слот2": None}
        })
        await interaction.response.send_message(
            f"`[SYS]` {мод['знак']} **{предмет.title()}** ({качество}) добавлен!\n"
            f"Урон: {шаблон['урон']} | Тип: {шаблон['тип']} | Навык: {шаблон['навык']}\n"
            f"Цена: {шаблон['цена']} эдди"
        )
        save_characters(персонажи)
    elif действие == "удалить":
        if предмет is None:
            await interaction.response.send_message("`[ERR]` Укажи название!", ephemeral=True)
            return
        оружие_список = p.get('оружие', [])
        for i, оруж in enumerate(оружие_список):
            if оруж['название'] == предмет:
                оружие_список.pop(i)
                save_characters(персонажи)
                await interaction.response.send_message(f"`[SYS]` Оружие **{предмет}** убрано.")
                return
        await interaction.response.send_message(f"`[ERR]` Оружие не найдено.", ephemeral=True)


# ==========================================
# ОБВЕСЫ
# ==========================================
@bot.tree.command(name="обвес", description="Установить или снять обвес с оружия")
@app_commands.autocomplete(обвес=автодополнение_обвесов)
@app_commands.describe(действие="Что сделать", оружие_номер="Номер оружия из списка", обвес="Название обвеса", слот="Слот (1 или 2)")
@app_commands.choices(действие=[
    app_commands.Choice(name="установить", value="установить"),
    app_commands.Choice(name="снять", value="снять"),
    app_commands.Choice(name="мой инвентарь", value="инвентарь"),
])
@app_commands.choices(слот=[
    app_commands.Choice(name="слот 1", value="1"),
    app_commands.Choice(name="слот 2", value="2"),
])
async def обвес(interaction: discord.Interaction, действие: str, оружие_номер: int = 1, обвес: str = None, слот: str = "1"):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` Сначала создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    оружие_список = p.get('оружие', [])

    if действие == "инвентарь":
        инвентарь = p.get('инвентарь_обвесов', [])
        if not инвентарь:
            await interaction.response.send_message("🔧 У тебя нет обвесов в инвентаре.")
            return
        обвесы = load_attachments()
        строки = ["**🔧 Твои обвесы:**"]
        for name in инвентарь:
            данные = обвесы.get(name, {})
            строки.append(f"• **{name}** — {данные.get('эффект', '?')}")
        await interaction.response.send_message('\n'.join(строки))
        return

    if not оружие_список:
        await interaction.response.send_message("У тебя нет оружия!", ephemeral=True)
        return
    if оружие_номер < 1 or оружие_номер > len(оружие_список):
        await interaction.response.send_message(f"`[ERR]` Оружие №{оружие_номер} не найдено! Всего: {len(оружие_список)}.", ephemeral=True)
        return

    оруж = оружие_список[оружие_номер - 1]
    слот_ключ = f"слот{слот}"
    if 'обвесы' not in оруж:
        оруж['обвесы'] = {"слот1": None, "слот2": None}

    if действие == "установить":
        if обвес is None:
            await interaction.response.send_message("`[ERR]` Укажи название обвеса!", ephemeral=True)
            return
        обвесы = load_attachments()
        if обвес not in обвесы:
            доступные = ', '.join(обвесы.keys())
            await interaction.response.send_message(f"`[ERR]` Обвес не найден! Доступные: {доступные}", ephemeral=True)
            return
        # Проверка: обвес есть в инвентаре?
        инвентарь = p.get('инвентарь_обвесов', [])
        if обвес not in инвентарь:
            await interaction.response.send_message(
                f"`[ERR]` У тебя нет **{обвес}** в инвентаре!\n"
                f"Твои обвесы: {', '.join(инвентарь) if инвентарь else 'пусто'}",
                ephemeral=True
            )
            return
        # Проверка: такой же обвес уже стоит на этом оружии?
        for ключ in ['слот1', 'слот2']:
            if оруж['обвесы'][ключ] == обвес:
                await interaction.response.send_message(
                    f"`[ERR]` **{обвес}** уже установлен на это оружие (слот {ключ[-1]})!",
                    ephemeral=True
                )
                return
        # Проверка: слот занят?
        if оруж['обвесы'][слот_ключ] is not None:
            старый = оруж['обвесы'][слот_ключ]
            await interaction.response.send_message(
                f"`[ERR]` Слот {слот} занят обвесом **{старый}**!\n"
                f"Сначала сними его: `/обвес снять {оружие_номер} {старый} слот:{слот}`",
                ephemeral=True
            )
            return
        # Устанавливаем
        оруж['обвесы'][слот_ключ] = обвес
        инвентарь.remove(обвес)
        save_characters(персонажи)
        await interaction.response.send_message(
            f"`[SYS]` **{обвес}** установлен на **{оруж['название'].title()}** (слот {слот})!\n"
            f"Эффект: {обвесы[обвес]['эффект']}"
        )

    elif действие == "снять":
        if оруж['обвесы'][слот_ключ] is None:
            await interaction.response.send_message(f"`[ERR]` Слот {слот} пуст.", ephemeral=True)
            return
        старый = оруж['обвесы'][слот_ключ]
        оруж['обвесы'][слот_ключ] = None
        # Возвращаем в инвентарь
        if 'инвентарь_обвесов' not in p:
            p['инвентарь_обвесов'] = []
        p['инвентарь_обвесов'].append(старый)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{старый}** снят с {оруж['название'].title()} (слот {слот}).")


# ==========================================
# ВЫДАТЬ ОБВЕС
# ==========================================
@bot.tree.command(name="выдать_обвес", description="Выдать обвес в инвентарь игроку")
@app_commands.autocomplete(обвес=автодополнение_обвесов)
@app_commands.describe(игрок="Кому выдать", обвес="Название обвеса")
async def выдать_обвес(interaction: discord.Interaction, игрок: discord.Member, обвес: str):
    персонажи = load_characters()
    цель_id = str(игрок.id)
    if цель_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` У {игрок.mention} нет персонажа!", ephemeral=True)
        return
    обвесы = load_attachments()
    if обвес not in обвесы:
        доступные = ', '.join(обвесы.keys())
        await interaction.response.send_message(f"`[ERR]` Обвес не найден! Доступные: {доступные}", ephemeral=True)
        return
    p = персонажи[цель_id]
    if 'инвентарь_обвесов' not in p:
        p['инвентарь_обвесов'] = []
    if обвес in p['инвентарь_обвесов']:
        await interaction.response.send_message(f"`[ERR]` У {игрок.mention} уже есть **{обвес}** в инвентаре!", ephemeral=True)
        return
    p['инвентарь_обвесов'].append(обвес)
    save_characters(персонажи)
    данные = обвесы[обвес]
    await interaction.response.send_message(
        f"`[SYS]` {игрок.mention} получил **{обвес}** в инвентарь!\n"
        f"Эффект: {данные['эффект']} | Цена: {данные['цена']} эдди"
    )


# ==========================================
# ОУ
# ==========================================
@bot.tree.command(name="оу", description="Выдать Очки Улучшений")
@app_commands.describe(игрок="Кому выдать (если не указано — себе)", количество="Сколько О.У. выдать")
async def оу(interaction: discord.Interaction, количество: int, игрок: discord.Member = None):
    персонажи = load_characters()
    if игрок is None:
        цель = interaction.user
    else:
        цель = игрок
    автор_id = str(цель.id)
    if автор_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` У {цель.mention} нет персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    p['оу'] += количество
    save_characters(персонажи)
    await interaction.response.send_message(f"`[ОУ]` +{количество} О.У. для {цель.mention}. Всего: **{p['оу']}** О.У.")


# ==========================================
# ЭДДИ
# ==========================================
@bot.tree.command(name="эдди", description="Добавить или потратить евродоллары")
@app_commands.describe(сумма="Сумма (отрицательное число — трата)")
async def эдди(interaction: discord.Interaction, сумма: int):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` Создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    p['эдди'] += сумма
    save_characters(персонажи)
    if сумма >= 0:
        await interaction.response.send_message(f"`[€$]` +{сумма} эдди. Баланс: **{p['эдди']}** €$")
    else:
        await interaction.response.send_message(f"`[€$]` {сумма} эдди. Баланс: **{p['эдди']}** €$")


# ==========================================
# ЭКИПИРОВАТЬ ОРУЖИЕ
# ==========================================
@bot.tree.command(name="экипировать", description="Взять оружие в руки")
@app_commands.describe(оружие_номер="Номер оружия из /оружие список")
async def экипировать(interaction: discord.Interaction, оружие_номер: int):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` Сначала создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    оружие_список = p.get('оружие', [])

    if not оружие_список:
        await interaction.response.send_message("У тебя нет оружия!", ephemeral=True)
        return
    if оружие_номер < 1 or оружие_номер > len(оружие_список):
        await interaction.response.send_message(f"`[ERR]` Оружие №{оружие_номер} не найдено!", ephemeral=True)
        return

    оруж = оружие_список[оружие_номер - 1]
    p['экипированное_оружие'] = оружие_номер - 1
    save_characters(персонажи)

    ш = оруж['шаблон']
    обвесы = оруж.get('обвесы', {})
    с1 = обвесы.get('слот1', None)
    с2 = обвесы.get('слот2', None)
    обвесы_стр = f" [{с1 or '—'} | {с2 or '—'}]" if (с1 or с2) else ""

    await interaction.response.send_message(
        f"`[SYS]` {interaction.user.mention} взял в руки: **{оруж['название'].title()}**\n"
        f"Урон: {ш['урон']} | Навык: {ш['навык']}{обвесы_стр}"
    )

# ==========================================
# АТАКА
# ==========================================
@bot.tree.command(name="атака", description="Атаковать экипированным оружием")
@app_commands.describe(удача="Сколько удачи потратить", мод="Доп. модификатор (+/-)")
async def атака(interaction: discord.Interaction, удача: int = 0, мод: int = 0):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)
    if автор_id not in персонажи:
        await interaction.response.send_message(f"`[ERR]` Сначала создай персонажа!", ephemeral=True)
        return
    p = персонажи[автор_id]
    оружие_список = p.get('оружие', [])
    экип = p.get('экипированное_оружие', None)

    if экип is None or экип >= len(оружие_список):
        await interaction.response.send_message("`[ERR]` Сначала экипируй оружие! `/экипировать [номер]`", ephemeral=True)
        return

    оруж = оружие_список[экип]
    ш = оруж['шаблон']
    навык = ш['навык']
    урон_формула = ш['урон']

    # Бросок навыка
    статы = p['статы']
    стат_бонус = статы.get(SKILLS[навык]['стат'], 1)
    уровень_навыка = p.get('навыки', {}).get(навык, 0)

    # Удача
    бонус_удачи = 0
    if удача > 0:
        макс_удача = статы.get('удача', 1)
        текущая = p.get('удача_текущая', макс_удача)
        новая, восст = восстановить_удачу(p)
        текущая = новая
        if удача > текущая:
            await interaction.response.send_message(f"`[ERR]` Недостаточно удачи! Запас: **{текущая}** / {макс_удача}", ephemeral=True)
            return
        p['удача_текущая'] = текущая - удача
        p['удача_последняя_трата'] = datetime.datetime.now().isoformat()
        save_characters(персонажи)
        бонус_удачи = удача

    общий_бонус = стат_бонус + уровень_навыка + бонус_удачи + мод

    # Бросок атаки
    бросок_атаки = random.randint(1, 10)
    результат_атаки = бросок_атаки + общий_бонус

    # Крит для атаки
    взрыв = 0
    взрыв_текст = ""
    тип_взрыва = ""
    if бросок_атаки == 10:
        взрыв = random.randint(1, 10)
        результат_атаки += взрыв
        тип_взрыва = "🔥 КРИТИЧЕСКАЯ УДАЧА!"
        взрыв_текст = f"\n║ 💥 Взрывной бросок: +{взрыв}"
    elif бросок_атаки == 1:
        взрыв = random.randint(1, 10)
        результат_атаки -= взрыв
        тип_взрыва = "💀 КРИТИЧЕСКАЯ НЕУДАЧА!"
        взрыв_текст = f"\n║ 💥 Крит-провал: -{взрыв}"

    # Бросок урона
    части = урон_формула.split('d')
    кубы = int(части[0])
    грани = int(части[1])
    бросок_урона = sum(random.randint(1, грани) for _ in range(кубы))

    await interaction.response.send_message(
        f"`[ATK]` {interaction.user.mention} атакует: **{оруж['название'].title()}**\n"
        f"╔═══ АТАКА ═══╗\n"
        f"║ D10: **{бросок_атаки}**\n"
        f"║ Навык ({навык}): +{уровень_навыка}\n"
        f"║ {SHORT_STATS[SKILLS[навык]['стат']]}: +{стат_бонус}" +
        (f"\n║ Удача: +{бонус_удачи}" if бонус_удачи > 0 else "") +
        (f"\n║ Мод: {'+' if мод >= 0 else ''}{мод}" if мод != 0 else "") +
        f"{взрыв_текст}\n"
        f"║ Итого атака: **{результат_атаки}**\n"
        f"╠═══ УРОН ═══╣\n"
        f"║ {урон_формула}: **{бросок_урона}**\n"
        f"╚═══ {тип_взрыва} ═══╝"
    )

# ==========================================
# КУБИК
# ==========================================
@bot.tree.command(name="к", description="Бросить кубики")
@app_commands.describe(запрос="Формат: d20, 3d6, 2d6+3")
async def к(interaction: discord.Interaction, запрос: str = "d6"):
    запрос = запрос.lower().replace(' ', '')
    match = re.match(r'^(\d*)d(\d+)([+-]\d+)?$', запрос)
    if not match:
        await interaction.response.send_message("`[ERR]` Формат: `d20`, `3d6`, `2d6+3`", ephemeral=True)
        return
    количество = int(match.group(1)) if match.group(1) else 1
    грани = int(match.group(2))
    модификатор_стр = match.group(3) if match.group(3) else "+0"
    модификатор = int(модификатор_стр)
    if количество > 20 or грани > 1000:
        await interaction.response.send_message("`[ERR]` Слишком много!", ephemeral=True)
        return
    броски = [random.randint(1, грани) for _ in range(количество)]
    сумма = sum(броски) + модификатор
    if количество == 1 and модификатор == 0:
        await interaction.response.send_message(f"`[DICE]` {interaction.user.mention} ▶ D{грани}: **{броски[0]}**")
    else:
        формула = f"{количество}D{грани}"
        if модификатор > 0:
            формула += f"+{модификатор}"
        elif модификатор < 0:
            формула += str(модификатор)
        текст = f"`[DICE]` {interaction.user.mention} ▶ {формула}\n"
        if количество > 1:
            текст += f"Броски: {', '.join(map(str, броски))}\n"
        текст += f"Результат: **{сумма}**"
        await interaction.response.send_message(текст)


# ==========================================
# ВАЙП
# ==========================================
@bot.tree.command(name="вайп", description="Удалить ВСЕХ персонажей (только админ)")
async def вайп(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("`[ERR]` Только администратор может использовать эту команду!", ephemeral=True)
        return
    персонажи = load_characters()
    if not персонажи:
        await interaction.response.send_message("`[SYS]` База данных и так пуста.", ephemeral=True)
        return
    await interaction.response.send_message(
        f"`[WARN]` ⚠️ Удалили **{len(персонажи)}** персонажей.\n"
        f"`[SYS]` 💀 Чистый лист. Выживших нет."
    )
    save_characters({})


# ==========================================
# ЗАПУСК
# ==========================================
bot.run(TOKEN)