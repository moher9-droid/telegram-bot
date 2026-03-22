import os
import asyncio
import logging
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# =========================
# Config
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = 169522781

FILE_PATH = "equipment.xlsx"
USERS_FILE = "users.txt"
BOT_VERSION = "2.3"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# =========================
# User Storage
# =========================
def load_users():
    users = set()
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.isdigit():
                    users.add(int(line))
    return users


def save_user(user_id: int):
    users = load_users()
    if user_id not in users:
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_id}\n")


# =========================
# Language Texts
# =========================
TEXTS = {
    "en": {
        "welcome": (
            "🚛 Project Equipment Management System\n"
            f"Version {BOT_VERSION}\n\n"
            "Welcome.\n\n"
            "You can:\n"
            "🔍 Search by plate number\n"
            "📋 View projects\n"
            "📦 View project equipment\n"
            "🚛 View regional tankers\n"
            "📊 Check total equipment count\n"
            "📁 Download Excel file\n"
            "🌐 Change language\n"
        ),
        "help": (
            "ℹ️ Help\n\n"
            "How to use the bot:\n\n"
            "1️⃣ Search Plate\n"
            "Send a plate number directly\n"
            "Example: 2573\n\n"
            "2️⃣ View Projects\n"
            "Press '📋 View Projects'\n"
            "Then choose a project\n\n"
            "3️⃣ Regional Tankers\n"
            "Press '🚛 Regional Tankers'\n"
            "Then choose a region\n\n"
            "4️⃣ Change Language\n"
            "Press '🌐 Language'\n\n"
            "Technical Support:\n"
            "mustafa.abualrahi@yc.com.sa"
        ),
        "no_projects": "⚠️ No projects found.",
        "choose_project": "📋 Choose a project:",
        "project_not_found": "❌ Project not found.",
        "equipment_in_project": "📦 Equipment in project: {project_name}\n\n",
        "choose_tanker_region": "🚛 Choose tanker region:",
        "no_tankers_region": "⚠️ No tankers found for {region_name}.",
        "tankers_title": "🚛 {region_name} Tankers\n\n",
        "system_stats": (
            "📊 System Statistics\n\n"
            "Projects Count: {projects_count}\n"
            "Equipment Count: {equipment_count}\n"
            "Regional Tankers Count: {tankers_count}"
        ),
        "search_plate_prompt": "🔍 Send the plate number now.\nExample: 2573",
        "result_found": "✅ Result Found\n\n",
        "source_equipment": "📂 Source: Equipment Master",
        "source_tankers": "📂 Source: Regional Tankers",
        "no_result": "❌ No result found.",
        "returned_main": "Returned to main menu.",
        "file_not_found": "❌ Excel file not found. Please check the file path.",
        "excel_error": "❌ Excel format error:\n{error}",
        "unexpected_error": "❌ Unexpected error:\n{error}",
        "language_menu": "🌐 Choose language / اختر اللغة",
        "language_set_en": "Language set to English.",
        "language_set_ar": "تم تغيير اللغة إلى العربية.",
        "plate": "🚛 Plate",
        "equipment_type": "🔧 Equipment Type",
        "project": "📍 Project",
        "tanker_name": "📛 Tanker Name",
        "region": "📍 Region",
        "status": "📊 Status",
        "back": "🔙 Back",
        "search_plate": "🔍 Search Plate",
        "view_projects": "📋 View Projects",
        "regional_tankers": "🚛 Regional Tankers",
        "equipment_count": "📊 Equipment Count",
        "send_excel": "📁 Send Excel File",
        "help_btn": "ℹ️ Help",
        "language_btn": "🌐 Language",
        "eastern": "📍 Eastern",
        "central": "📍 Central",
        "western": "📍 Western",
        "broadcast_btn": "📢 Broadcast",
        "cancel_broadcast": "❌ Cancel Broadcast",
        "broadcast_prompt": "✉️ Send the message now. It will be sent to all saved users.",
        "broadcast_cancelled": "✅ Broadcast cancelled.",
        "broadcast_started": "⏳ Broadcast started...",
        "broadcast_done": "✅ Broadcast completed.\nSuccess: {success}\nFailed: {failed}",
        "broadcast_not_allowed": "❌ You do not have permission.",
    },
    "ar": {
        "welcome": (
            "🚛 نظام إدارة معدات المشاريع\n"
            f"الإصدار {BOT_VERSION}\n\n"
            "مرحباً بك.\n\n"
            "يمكنك:\n"
            "🔍 البحث برقم اللوحة\n"
            "📋 عرض المشاريع\n"
            "📦 عرض معدات المشروع\n"
            "🚛 عرض تناكر المناطق\n"
            "📊 معرفة عدد المعدات\n"
            "📁 تحميل ملف الإكسل\n"
            "🌐 تغيير اللغة\n"
        ),
        "help": (
            "ℹ️ المساعدة\n\n"
            "طريقة استخدام البوت:\n\n"
            "1️⃣ البحث عن لوحة\n"
            "أرسل رقم اللوحة مباشرة\n"
            "مثال: 2573\n\n"
            "2️⃣ عرض المشاريع\n"
            "اضغط '📋 عرض المشاريع'\n"
            "ثم اختر المشروع\n\n"
            "3️⃣ تناكر المناطق\n"
            "اضغط '🚛 تناكر المناطق'\n"
            "ثم اختر المنطقة\n\n"
            "4️⃣ تغيير اللغة\n"
            "اضغط '🌐 Language'\n\n"
            "الدعم الفني:\n"
            "mustafa.abualrahi@yc.com.sa"
        ),
        "no_projects": "⚠️ لا توجد مشاريع.",
        "choose_project": "📋 اختر المشروع:",
        "project_not_found": "❌ لم يتم العثور على المشروع.",
        "equipment_in_project": "📦 معدات المشروع: {project_name}\n\n",
        "choose_tanker_region": "🚛 اختر منطقة التناكر:",
        "no_tankers_region": "⚠️ لا توجد تناكر لمنطقة {region_name}.",
        "tankers_title": "🚛 تناكر {region_name}\n\n",
        "system_stats": (
            "📊 إحصائيات النظام\n\n"
            "عدد المشاريع: {projects_count}\n"
            "عدد المعدات: {equipment_count}\n"
            "عدد تناكر المناطق: {tankers_count}"
        ),
        "search_plate_prompt": "🔍 أرسل رقم اللوحة الآن.\nمثال: 2573",
        "result_found": "✅ تم العثور على النتيجة\n\n",
        "source_equipment": "📂 المصدر: سجل المعدات",
        "source_tankers": "📂 المصدر: تناكر المناطق",
        "no_result": "❌ لم يتم العثور على نتيجة.",
        "returned_main": "تم الرجوع للقائمة الرئيسية.",
        "file_not_found": "❌ لم يتم العثور على ملف الإكسل. تأكد من المسار.",
        "excel_error": "❌ خطأ في تنسيق الإكسل:\n{error}",
        "unexpected_error": "❌ خطأ غير متوقع:\n{error}",
        "language_menu": "🌐 Choose language / اختر اللغة",
        "language_set_en": "Language set to English.",
        "language_set_ar": "تم تغيير اللغة إلى العربية.",
        "plate": "🚛 رقم اللوحة",
        "equipment_type": "🔧 نوع المعدة",
        "project": "📍 المشروع",
        "tanker_name": "📛 اسم التنكر",
        "region": "📍 المنطقة",
        "status": "📊 الحالة",
        "back": "🔙 رجوع",
        "search_plate": "🔍 البحث عن لوحة",
        "view_projects": "📋 عرض المشاريع",
        "regional_tankers": "🚛 تناكر المناطق",
        "equipment_count": "📊 عدد المعدات",
        "send_excel": "📁 إرسال ملف الإكسل",
        "help_btn": "ℹ️ المساعدة",
        "language_btn": "🌐 Language",
        "eastern": "📍 الشرقية",
        "central": "📍 الوسطى",
        "western": "📍 الغربية",
        "broadcast_btn": "📢 إرسال جماعي",
        "cancel_broadcast": "❌ إلغاء الإرسال الجماعي",
        "broadcast_prompt": "✉️ أرسل الرسالة الآن وسيتم إرسالها إلى جميع المستخدمين المحفوظين.",
        "broadcast_cancelled": "✅ تم إلغاء الإرسال الجماعي.",
        "broadcast_started": "⏳ بدأ الإرسال الجماعي...",
        "broadcast_done": "✅ اكتمل الإرسال الجماعي.\nنجح: {success}\nفشل: {failed}",
        "broadcast_not_allowed": "❌ لا تملك صلاحية.",
    }
}


# =========================
# Language Helpers
# =========================
def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "en")


def t(context: ContextTypes.DEFAULT_TYPE, key: str, **kwargs) -> str:
    lang = get_lang(context)
    text = TEXTS[lang][key]
    return text.format(**kwargs) if kwargs else text


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def get_main_keyboard(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    lang = get_lang(context)

    rows = [
        [TEXTS[lang]["search_plate"], TEXTS[lang]["view_projects"]],
        [TEXTS[lang]["regional_tankers"], TEXTS[lang]["equipment_count"]],
        [TEXTS[lang]["send_excel"], TEXTS[lang]["help_btn"]],
        [TEXTS[lang]["language_btn"]],
    ]

    if is_admin(user_id):
        rows.append([TEXTS[lang]["broadcast_btn"]])

    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def get_tankers_keyboard(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    lang = get_lang(context)
    return ReplyKeyboardMarkup(
        [
            [TEXTS[lang]["eastern"], TEXTS[lang]["central"]],
            [TEXTS[lang]["western"]],
            [TEXTS[lang]["back"]],
        ],
        resize_keyboard=True
    )


def get_language_keyboard():
    return ReplyKeyboardMarkup(
        [["🇬🇧 English", "🇸🇦 العربية"]],
        resize_keyboard=True
    )


def get_broadcast_keyboard(context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    return ReplyKeyboardMarkup(
        [[TEXTS[lang]["cancel_broadcast"]]],
        resize_keyboard=True
    )


# =========================
# Load Data
# =========================
def ensure_excel_exists():
    if not os.path.exists(FILE_PATH):
        raise FileNotFoundError(f"{FILE_PATH} not found")


def load_projects_data():
    ensure_excel_exists()
    df = pd.read_excel(FILE_PATH, sheet_name="Equipment_Master", dtype=str)
    df.columns = df.columns.str.strip()

    required_columns = ["Plate_No", "Equipment_Type", "Project_Name"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column in Equipment_Master: {col}")
        df[col] = df[col].fillna("").astype(str).str.strip()

    df = df[(df["Plate_No"] != "") | (df["Project_Name"] != "")]
    return df


def load_tankers_data():
    ensure_excel_exists()
    df = pd.read_excel(FILE_PATH, sheet_name="Regional_Tankers", dtype=str)
    df.columns = df.columns.str.strip()

    required_columns = ["Region", "Plate_No", "Tanker_Name", "Status", "Project_Name"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column in Regional_Tankers: {col}")
        df[col] = df[col].fillna("").astype(str).str.strip()

    df = df[(df["Plate_No"] != "") | (df["Tanker_Name"] != "") | (df["Project_Name"] != "")]
    return df


# =========================
# Dynamic Project Keyboard
# =========================
def get_projects():
    df = load_projects_data()
    projects = sorted(df["Project_Name"].dropna().astype(str).str.strip().unique())
    return [p for p in projects if p]


def build_projects_keyboard(context: ContextTypes.DEFAULT_TYPE):
    projects = get_projects()
    rows = []

    for i in range(0, len(projects), 2):
        rows.append(projects[i:i + 2])

    rows.append([TEXTS[get_lang(context)]["back"]])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


# =========================
# Helpers
# =========================
def search_plate_in_projects(text: str):
    df = load_projects_data()
    clean_text = text.replace(" ", "").lower()

    return df[
        df["Plate_No"]
        .str.replace(" ", "", regex=False)
        .str.lower()
        .str.contains(clean_text, na=False)
    ]


def search_plate_in_tankers(text: str):
    df = load_tankers_data()
    clean_text = text.replace(" ", "").lower()

    return df[
        df["Plate_No"]
        .str.replace(" ", "", regex=False)
        .str.lower()
        .str.contains(clean_text, na=False)
    ]


def get_tankers_by_region(region_name: str):
    df = load_tankers_data()
    return df[df["Region"].str.strip().str.lower() == region_name.lower()]


# =========================
# Commands
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)

    context.user_data["mode"] = "main"
    context.user_data["broadcast_mode"] = False

    if "lang" not in context.user_data:
        context.user_data["lang"] = "en"

    await update.message.reply_text(
        t(context, "welcome"),
        reply_markup=get_main_keyboard(context, user_id)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)

    await update.message.reply_text(
        t(context, "help"),
        reply_markup=get_main_keyboard(context, user_id)
    )


# =========================
# Projects
# =========================
async def show_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    projects = get_projects()

    if not projects:
        await update.message.reply_text(
            t(context, "no_projects"),
            reply_markup=get_main_keyboard(context, update.effective_user.id)
        )
        return

    context.user_data["mode"] = "projects"
    await update.message.reply_text(
        t(context, "choose_project"),
        reply_markup=build_projects_keyboard(context)
    )


async def show_project_equipment(update: Update, context: ContextTypes.DEFAULT_TYPE, project_name: str):
    df = load_projects_data()
    project_result = df[df["Project_Name"].str.strip().str.lower() == project_name.lower()]

    if project_result.empty:
        await update.message.reply_text(
            t(context, "project_not_found"),
            reply_markup=get_main_keyboard(context, update.effective_user.id)
        )
        return

    reply = t(context, "equipment_in_project", project_name=project_name)

    for _, row in project_result.iterrows():
        plate = row["Plate_No"] if row["Plate_No"] else "-"
        equipment = row["Equipment_Type"] if row["Equipment_Type"] else "-"
        reply += f"🚛 {plate} - {equipment}\n"

    await update.message.reply_text(reply, reply_markup=build_projects_keyboard(context))


# =========================
# Tankers
# =========================
async def show_tankers_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "tankers"
    await update.message.reply_text(
        t(context, "choose_tanker_region"),
        reply_markup=get_tankers_keyboard(context, update.effective_user.id)
    )


async def show_region_tankers(update: Update, context: ContextTypes.DEFAULT_TYPE, region_name: str):
    result = get_tankers_by_region(region_name)

    if result.empty:
        await update.message.reply_text(
            t(context, "no_tankers_region", region_name=region_name),
            reply_markup=get_tankers_keyboard(context, update.effective_user.id)
        )
        return

    reply = t(context, "tankers_title", region_name=region_name)

    for _, row in result.iterrows():
        plate = row["Plate_No"] if row["Plate_No"] else "-"
        tanker_name = row["Tanker_Name"] if row["Tanker_Name"] else "-"
        status = row["Status"] if row["Status"] else "-"
        project_name = row["Project_Name"] if row["Project_Name"] else "-"

        reply += (
            f"{t(context, 'plate')}: {plate}\n"
            f"{t(context, 'tanker_name')}: {tanker_name}\n"
            f"{t(context, 'project')}: {project_name}\n"
            f"{t(context, 'status')}: {status}\n"
            "━━━━━━━━━━━━━━━\n"
        )

    await update.message.reply_text(
        reply,
        reply_markup=get_tankers_keyboard(context, update.effective_user.id)
    )


# =========================
# Stats / File
# =========================
async def count_equipment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    projects_df = load_projects_data()
    tankers_df = load_tankers_data()

    total_equipment = len(projects_df)
    total_projects = len(get_projects())
    total_tankers = len(tankers_df)

    reply = t(
        context,
        "system_stats",
        projects_count=total_projects,
        equipment_count=total_equipment,
        tankers_count=total_tankers
    )

    await update.message.reply_text(
        reply,
        reply_markup=get_main_keyboard(context, update.effective_user.id)
    )


async def send_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_excel_exists()
    with open(FILE_PATH, "rb") as f:
        await update.message.reply_document(f, filename="equipment.xlsx")


# =========================
# Broadcast
# =========================
async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text(t(context, "broadcast_not_allowed"))
        return

    context.user_data["broadcast_mode"] = True
    await update.message.reply_text(
        t(context, "broadcast_prompt"),
        reply_markup=get_broadcast_keyboard(context)
    )


async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["broadcast_mode"] = False
    await update.message.reply_text(
        t(context, "broadcast_cancelled"),
        reply_markup=get_main_keyboard(context, update.effective_user.id)
    )


async def run_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text(t(context, "broadcast_not_allowed"))
        return

    await update.message.reply_text(t(context, "broadcast_started"))

    users = load_users()
    success = 0
    failed = 0

    for target_user_id in users:
        try:
            await context.bot.send_message(chat_id=target_user_id, text=message_text)
            success += 1
        except Exception as e:
            logger.warning("Broadcast failed to %s: %s", target_user_id, e)
            failed += 1

        await asyncio.sleep(0.2)

    context.user_data["broadcast_mode"] = False

    await update.message.reply_text(
        t(context, "broadcast_done", success=success, failed=failed),
        reply_markup=get_main_keyboard(context, user_id)
    )


# =========================
# Search
# =========================
async def search_plate(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    project_result = search_plate_in_projects(text)

    if not project_result.empty:
        row = project_result.iloc[0]
        reply = (
            t(context, "result_found")
            + f"{t(context, 'plate')}: {row['Plate_No']}\n"
            + f"{t(context, 'equipment_type')}: {row['Equipment_Type']}\n"
            + f"{t(context, 'project')}: {row['Project_Name']}\n"
            + t(context, "source_equipment")
        )

        await update.message.reply_text(
            reply,
            reply_markup=get_main_keyboard(context, update.effective_user.id)
        )
        return

    tanker_result = search_plate_in_tankers(text)

    if not tanker_result.empty:
        row = tanker_result.iloc[0]
        reply = (
            t(context, "result_found")
            + f"{t(context, 'plate')}: {row['Plate_No']}\n"
            + f"{t(context, 'tanker_name')}: {row['Tanker_Name']}\n"
            + f"{t(context, 'region')}: {row['Region']}\n"
            + f"{t(context, 'project')}: {row['Project_Name']}\n"
            + f"{t(context, 'status')}: {row['Status']}\n"
            + t(context, "source_tankers")
        )

        await update.message.reply_text(
            reply,
            reply_markup=get_main_keyboard(context, update.effective_user.id)
        )
        return

    await update.message.reply_text(
        t(context, "no_result"),
        reply_markup=get_main_keyboard(context, update.effective_user.id)
    )


# =========================
# Message Handler
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    save_user(user_id)

    try:
        if context.user_data.get("broadcast_mode", False):
            if text == TEXTS[get_lang(context)]["cancel_broadcast"]:
                await cancel_broadcast(update, context)
                return

            await run_broadcast(update, context, text)
            return

        if text == "🌐 Language":
            await update.message.reply_text(
                t(context, "language_menu"),
                reply_markup=get_language_keyboard()
            )
            return

        if text == "🇬🇧 English":
            context.user_data["lang"] = "en"
            await update.message.reply_text(
                t(context, "language_set_en"),
                reply_markup=get_main_keyboard(context, user_id)
            )
            return

        if text == "🇸🇦 العربية":
            context.user_data["lang"] = "ar"
            await update.message.reply_text(
                t(context, "language_set_ar"),
                reply_markup=get_main_keyboard(context, user_id)
            )
            return

        if text in [TEXTS["en"]["broadcast_btn"], TEXTS["ar"]["broadcast_btn"]]:
            await start_broadcast(update, context)
            return

        if text in ["🔍 Search Plate", "🔍 البحث عن لوحة"]:
            context.user_data["mode"] = "search"
            await update.message.reply_text(
                t(context, "search_plate_prompt"),
                reply_markup=get_main_keyboard(context, user_id)
            )
            return

        if text in ["📋 View Projects", "📋 عرض المشاريع"]:
            await show_projects(update, context)
            return

        if text in ["🚛 Regional Tankers", "🚛 تناكر المناطق"]:
            await show_tankers_menu(update, context)
            return

        if text in ["📊 Equipment Count", "📊 عدد المعدات"]:
            await count_equipment(update, context)
            return

        if text in ["📁 Send Excel File", "📁 إرسال ملف الإكسل"]:
            await send_excel(update, context)
            return

        if text in ["ℹ️ Help", "ℹ️ المساعدة"]:
            await help_command(update, context)
            return

        if text in ["🔙 Back", "🔙 رجوع"]:
            context.user_data["mode"] = "main"
            await update.message.reply_text(
                t(context, "returned_main"),
                reply_markup=get_main_keyboard(context, user_id)
            )
            return

        if text in get_projects():
            await show_project_equipment(update, context, text)
            return

        if text in ["📍 Eastern", "📍 الشرقية"]:
            await show_region_tankers(update, context, "Eastern")
            return

        if text in ["📍 Central", "📍 الوسطى"]:
            await show_region_tankers(update, context, "Central")
            return

        if text in ["📍 Western", "📍 الغربية"]:
            await show_region_tankers(update, context, "Western")
            return

        await search_plate(update, context, text)

    except FileNotFoundError:
        await update.message.reply_text(
            t(context, "file_not_found"),
            reply_markup=get_main_keyboard(context, user_id)
        )

    except ValueError as e:
        await update.message.reply_text(
            t(context, "excel_error", error=str(e)),
            reply_markup=get_main_keyboard(context, user_id)
        )

    except Exception as e:
        logger.exception("Unexpected error in handle_message")
        await update.message.reply_text(
            t(context, "unexpected_error", error=str(e)),
            reply_markup=get_main_keyboard(context, user_id)
        )


# =========================
# Main
# =========================
def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing. Add it in Railway Variables.")

    if ":" not in BOT_TOKEN:
        raise ValueError("BOT_TOKEN format looks invalid. Check the token from BotFather.")

    logger.info("Starting bot version %s", BOT_VERSION)
    logger.info("Excel file exists: %s", os.path.exists(FILE_PATH))

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"Bot running... Version {BOT_VERSION}")
    app.run_polling()


if __name__ == "__main__":
    main()
