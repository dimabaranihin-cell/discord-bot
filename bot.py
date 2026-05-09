import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import re
import json
import os
import yt_dlp
import datetime
import os

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
# АВТОДОПОЛНЕНИЕ НАВЫКОВ
# ==========================================
async def автодополнение_навыков(interaction: discord.Interaction, current: str):
    """Фильтрует навыки по введённому тексту"""
    все = list(SKILLS.keys())
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
        # Игрок смотрит свой лист или Анкетолог смотрит чужой
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
            
            # Для удачи показываем текущий запас
            if full_name == "удача":
                текущая = p.get('удача_текущая', значение)
                # Проверяем восстановление
                восстановить_удачу(p)
                текущая = p.get('удача_текущая', значение)
                стат_строки.append(f"{emoji} {short_name}: **{текущая}** / {значение}")
            # Для эмпатии показываем текущее / базовое
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

        # Здоровье = 5 * floor((тело + воля) / 2)
        здоровье = 5 * ((тело + воля) // 2)

        # Человечность — отдельное значение
        человечность = p.get('человечность', статы.get('эмпатия', 1) * 10)

        # Эмпатия = число десятков человечности
        эмпатия = человечность // 10
        статы['эмпатия'] = эмпатия  # Автообновление эмпатии

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

        # Статус киберпсихоза
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
        # Только Анкетолог
        if "Анкетолог" not in [роль.name for роль in interaction.user.roles]:
            await interaction.response.send_message("`[ERR]` Только Анкетолог может создавать персонажей!", ephemeral=True)
            return

        if имя_персонажа is None:
            await interaction.response.send_message("`[SYS]` Укажи имя персонажа!", ephemeral=True)
            return

        if len(имя_персонажа) > 30:
            await interaction.response.send_message("`[ERR]` Имя персонажа не может быть длиннее 30 символов!", ephemeral=True)
            return

        # Определяем цель
        if игрок is None:
            await interaction.response.send_message("`[SYS]` Укажи игрока через @упоминание!", ephemeral=True)
            return

        цель_id_str = str(игрок.id)

        if цель_id_str in персонажи:
            await interaction.response.send_message(f"`[WARN]` У {игрок.mention} уже есть персонаж! Используй `/персонаж удалить` чтобы сбросить.", ephemeral=True)
            return

        персонажи[цель_id_str] = {
            "имя": имя_персонажа,
            "оу": 0,
            "эдди": 1000,
            "статы": {
                "интеллект": 1,
                "сила воли": 1,
                "харизма": 1,
                "эмпатия": 1,
                "техника": 1,
                "реакция": 1,
                "удача": 1,
                "телосложение": 1,
                "ловкость": 1,
                "скорость": 1
            },
            "навыки": {},
            "удача_текущая": 1,
            "удача_последняя_трата": None,
            "человечность": 10,
            "базовая_эмпатия": 1,
            "импланты": [],
            "снаряжение": []
        }
        save_characters(персонажи)

        await interaction.response.send_message(
            f"`[SYS]` ✅ Персонаж **{имя_персонажа}** создан для {игрок.mention}!\n"
            f"`[INFO]` Стартовые очки характеристик: **35**\n"
            f"`[INFO]` Характеристики начинаются с 1 (макс. 8)\n"
            f"`[INFO]` Навыки начинаются с 0 (макс. 8, на старте макс. 4)\n"
            f"`[CMD]` `/стат повысить` — повысить характеристику\n"
            f"`[CMD]` `/навык повысить` — прокачать навык (1 уровень = 1 О.У.)"
        )

    elif действие == "удалить":
        # Только Анкетолог
        if "Анкетолог" not in [роль.name for роль in interaction.user.roles]:
            await interaction.response.send_message("`[ERR]` Только Анкетолог может удалять персонажей!", ephemeral=True)
            return

        # Определяем цель
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
    интеллект: int = 1,
    сила_воли: int = 1,
    харизма: int = 1,
    эмпатия: int = 1,
    техника: int = 1,
    реакция: int = 1,
    удача: int = 1,
    телосложение: int = 1,
    ловкость: int = 1,
    скорость: int = 1,
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
        "интеллект": интеллект,
        "сила воли": сила_воли,
        "харизма": харизма,
        "эмпатия": эмпатия,
        "техника": техника,
        "реакция": реакция,
        "удача": удача,
        "телосложение": телосложение,
        "ловкость": ловкость,
        "скорость": скорость,
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


async def автодополнение_навыков_анкетолог(interaction: discord.Interaction, current: str):
    все = ["не указано"] + list(SKILLS.keys())
    if not current:
        return [app_commands.Choice(name=n, value=n) for n in все[:25]]
    подходящие = [n for n in все if current.lower() in n.lower()]
    return [app_commands.Choice(name=n, value=n) for n in подходящие[:25]]


@bot.tree.command(name="установить_навыки", description="[Анкетолог] Установить навыки игроку")
@app_commands.autocomplete(навык1=автодополнение_навыков_анкетолог, навык2=автодополнение_навыков_анкетолог, навык3=автодополнение_навыков_анкетолог, навык4=автодополнение_навыков_анкетолог, навык5=автодополнение_навыков_анкетолог)
@app_commands.describe(
    игрок="Игрок",
    навык1="Первый навык", уровень1="Уровень (0-4 на старте, 0-8 после О.У.)",
    навык2="Второй навык", уровень2="Уровень (0-4 на старте, 0-8 после О.У.)",
    навык3="Третий навык", уровень3="Уровень (0-4 на старте, 0-8 после О.У.)",
    навык4="Четвёртый навык", уровень4="Уровень (0-4 на старте, 0-8 после О.У.)",
    навык5="Пятый навык", уровень5="Уровень (0-4 на старте, 0-8 после О.У.)",
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

    # Определяем лимит
    потрачено = sum(p.get('навыки', {}).values())
    if потрачено == 0 and p['оу'] == 0:
        лимит = 4
    else:
        лимит = 8

    установлено = []
    пары = [(навык1, уровень1), (навык2, уровень2), (навык3, уровень3), (навык4, уровень4), (навык5, уровень5)]

    for назв, ур in пары:
        if назв is None or назв.strip() == "" or назв == "не указано":
            continue
        if назв not in SKILLS:
            await interaction.response.send_message(f"`[ERR]` Навык «{назв}» не найден!", ephemeral=True)
            return
        if ур < 0 or ур > лимит:
            await interaction.response.send_message(f"`[ERR]` Уровень навыка должен быть 0-{лимит} на текущем этапе!", ephemeral=True)
            return
        if ур == 0:
            if назв in p['навыки']:
                del p['навыки'][назв]
        else:
            p['навыки'][назв] = ур
        установлено.append(f"**{назв.title()}**: ур.{ур}")

    save_characters(персонажи)

    if установлено:
        await interaction.response.send_message(
            f"`[SYS]` Навыки {игрок.mention} установлены!\n" + '\n'.join(установлено)
        )
    else:
        await interaction.response.send_message(f"`[SYS]` Навыки {игрок.mention} не изменены (не указаны).")


# ==========================================
# УДАЧА
# ==========================================
@bot.tree.command(name="удача", description="Показать или потратить удачу")
@app_commands.describe(тратить="Сколько единиц удачи потратить (1-текущий запас)")
async def удача(interaction: discord.Interaction, тратить: int = None):
    персонажи = load_characters()
    автор_id = str(interaction.user.id)

    if автор_id not in персонажи:
        await interaction.response.send_message("`[ERR]` Сначала создай персонажа!", ephemeral=True)
        return

    p = персонажи[автор_id]
    статы = p['статы']
    макс_удача = статы.get('удача', 1)

    if 'удача_текущая' not in p:
        p['удача_текущая'] = макс_удача
    if 'удача_последняя_трата' not in p:
        p['удача_последняя_трата'] = None

    текущая = p['удача_текущая']

    # Проверяем восстановление удачи
    новая_текущая, восстановлено = восстановить_удачу(p)
    if восстановлено > 0:
        текущая = новая_текущая
        save_characters(персонажи)

    if тратить is None:
        embed = discord.Embed(
            title=f"🍀 Удача — {p['имя']}",
            description=f"Текущий запас: **{текущая}** / {макс_удача}",
            color=0x00ff00
        )
        embed.add_field(name="Как работает", value=(
            "• Потрать удачу через `/удача [число]`\n"
            "• Каждая потраченная единица даёт **+1 к броску**\n"
            "• Восстановление: **1 единица раз в 48 часов**\n"
            "• Нельзя опуститься ниже 0"
        ))
        embed.set_footer(text="Удача любит смелых!")
        await interaction.response.send_message(embed=embed)
        return

    if тратить <= 0:
        await interaction.response.send_message("`[ERR]` Укажи положительное число!", ephemeral=True)
        return

    if тратить > текущая:
        await interaction.response.send_message(
            f"`[ERR]` У тебя только **{текущая}** единиц удачи!\nДождись восстановления (1 ед. / 48 часов).",
            ephemeral=True
        )
        return

    p['удача_текущая'] = текущая - тратить
    p['удача_последняя_трата'] = datetime.datetime.now().isoformat()
    save_characters(персонажи)

    await interaction.response.send_message(
        f"🍀 **{p['имя']}** тратит **{тратить}** ед. удачи!\n"
        f"Бонус к следующему броску: **+{тратить}**\n"
        f"Осталось удачи: **{p['удача_текущая']}** / {макс_удача}\n"
        f"`[INFO]` Восстановление: +1 ед. через 48 часов."
    )


def восстановить_удачу(p):
    """Восстанавливает удачу персонажа. Возвращает (новая_текущая, сколько_восстановлено)"""
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
@app_commands.describe(
    игрок="Игрок",
    изменение="На сколько изменить человечность (отрицательное — потеря)"
)
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

    # Нельзя превысить базовый максимум
    базовая = p.get('базовая_эмпатия', p['статы'].get('эмпатия', 1))
    максимум = базовая * 10
    if новая > максимум:
        новая = максимум

    p['человечность'] = новая
    # Эмпатия = число десятков человечности
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
            все_строки.append("")  # пустая строка-разделитель

    if все_строки:
        embed.add_field(
            name="\u200b",
            value='\n'.join(все_строки),
            inline=False
        )

    embed.set_footer(text=f"Цена: 1-2 О.У. | /бросок [навык] — проверка")
    await interaction.response.send_message(embed=embed)


# ==========================================
# НАВЫК АП (ПОВЫШЕНИЕ)
# ==========================================
@bot.tree.command(name="навык_ап", description="Повысить навык (1 О.У. = 1 уровень)")
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

    # Трата удачи
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

    # Штраф за киберпсихоз
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
# СНАРЯЖЕНИЕ
# ==========================================
@bot.tree.command(name="снаряжение", description="Управление снаряжением")
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
            список = '\n'.join([f"▸ {item}" for item in p['снаряжение']])
            await interaction.response.send_message(f"`[GEAR]` Снаряжение **{p['имя']}**:\n{список}")
        else:
            await interaction.response.send_message(f"`[INFO]` Инвентарь пуст.")

    elif действие == "добавить":
        if предмет is None:
            await interaction.response.send_message("`[ERR]` Укажи название предмета!", ephemeral=True)
            return
        p['снаряжение'].append(предмет)
        save_characters(персонажи)
        await interaction.response.send_message(f"`[SYS]` **{предмет}** добавлен в инвентарь!")

    elif действие == "удалить":
        if предмет is None:
            await interaction.response.send_message("`[ERR]` Укажи название предмета!", ephemeral=True)
            return
        if предмет in p['снаряжение']:
            p['снаряжение'].remove(предмет)
            save_characters(персонажи)
            await interaction.response.send_message(f"`[SYS]` **{предмет}** убран.")
        else:
            await interaction.response.send_message(f"`[ERR]` Предмет не найден.", ephemeral=True)


# ==========================================
# ОУ
# ==========================================
@bot.tree.command(name="оу", description="Выдать Очки Улучшений")
@app_commands.describe(игрок="Кому выдать (если не указано — себе)", количество="Сколько О.У. выдать")
async def оу(interaction: discord.Interaction, количество: int, игрок: discord.Member = None):
    персонажи = load_characters()

    # Определяем цель
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
# МУЗЫКА (ЛЕГАЛЬНЫЙ ПЛЕЕР С ОЧЕРЕДЬЮ)
# ==========================================

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# Очередь треков для каждого сервера
музыкальная_очередь = {}

def получить_очередь(guild_id):
    if guild_id not in музыкальная_очередь:
        музыкальная_очередь[guild_id] = []
    return музыкальная_очередь[guild_id]

async def проиграть_следующий(guild, voice_client):
    """Проигрывает следующий трек из очереди"""
    очередь = получить_очередь(guild.id)
    
    if очередь:
        следующий = очередь.pop(0)
        audio_source = discord.FFmpegPCMAudio(следующий, **FFMPEG_OPTIONS)
        
        def после_трека(error):
            if error:
                print(f"Ошибка: {error}")
            # После окончания трека — следующий
            import asyncio
            asyncio.run_coroutine_threadsafe(проиграть_следующий(guild, voice_client), guild.voice_client.loop)
        
        voice_client.play(audio_source, after=после_трека)
        return следующий
    return None


@bot.tree.command(name="play", description="Добавить трек в очередь и начать играть")
@app_commands.describe(ссылка="Прямая ссылка на аудиофайл")
async def play(interaction: discord.Interaction, ссылка: str):
    if not interaction.user.voice:
        await interaction.response.send_message("Сначала зайди в голосовой канал!", ephemeral=True)
        return

    разрешённые = ['.mp3', '.ogg', '.wav', '.flac', '.webm', '.m4a', '.aac']
    if not any(ссылка.lower().endswith(ext) for ext in разрешённые):
        await interaction.response.send_message(
            f"⚠️ Нужна прямая ссылка на аудиофайл!\n"
            f"Разрешённые форматы: {', '.join(разрешённые)}",
            ephemeral=True
        )
        return

    await interaction.response.defer()

    try:
        voice_client = interaction.guild.voice_client
        channel = interaction.user.voice.channel

        # Подключаемся если не подключены
        if voice_client:
            await voice_client.move_to(channel)
        else:
            await channel.connect()
            voice_client = interaction.guild.voice_client

        # Добавляем в очередь
        очередь = получить_очередь(interaction.guild_id)
        очередь.append(ссылка)

        # Если ничего не играет — запускаем сразу
        if not voice_client.is_playing():
            текущий = await проиграть_следующий(interaction.guild, voice_client)
            await interaction.followup.send(f"🎵 Играет: **{текущий}**")
        else:
            позиция = len(очередь)
            await interaction.followup.send(f"📋 Добавлен в очередь (позиция {позиция}): **{ссылка}**")

    except Exception as e:
        await interaction.followup.send(f"Ошибка: {e}")


@bot.tree.command(name="skip", description="Пропустить текущий трек")
async def skip(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if not voice_client or not voice_client.is_playing():
        await interaction.response.send_message("Ничего не играет!", ephemeral=True)
        return

    voice_client.stop()
    # Следующий трек запустится автоматически через after
    await interaction.response.send_message("⏭️ Пропущено! Запускаю следующий трек...")


@bot.tree.command(name="queue", description="Показать очередь треков")
async def queue(interaction: discord.Interaction):
    очередь = получить_очередь(interaction.guild_id)
    
    if not очередь:
        await interaction.response.send_message("📋 Очередь пуста. Добавь трек через `/play`!")
        return

    список = '\n'.join([f"{i+1}. {url}" for i, url in enumerate(очередь)])
    await interaction.response.send_message(f"📋 **Очередь треков:**\n{список}")


@bot.tree.command(name="clear", description="Очистить очередь треков")
async def clear(interaction: discord.Interaction):
    очередь = получить_очередь(interaction.guild_id)
    voice_client = interaction.guild.voice_client
    
    очищено = len(очередь)
    очередь.clear()
    
    if voice_client and voice_client.is_playing():
        voice_client.stop()
    
    await interaction.response.send_message(f"🗑️ Очищено {очищено} треков из очереди.")


@bot.tree.command(name="leave", description="Отключить бота от голосового канала")
async def leave(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        # Очищаем очередь при выходе
        получить_очередь(interaction.guild_id).clear()
        await voice_client.disconnect()
        await interaction.response.send_message("👋 Вышел из канала. Очередь очищена.")
    else:
        await interaction.response.send_message("Я не в голосовом канале!", ephemeral=True)


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