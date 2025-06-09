import re
import time
import requests
import instaloader
from telegram import Update, ChatAction, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from fake_useragent import UserAgent
import json
# --- Global Setup ---
L = instaloader.Instaloader()
TELEGRAM_BOT_TOKEN = "7697054311:AAFfRUW-ImoGGB1weCB_j_Je0C2k05ywzaw"
user_last_used = {}  # For cooldown tracking (user_id: timestamp)

# --- Command: /start ---
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

def start(update: Update, context: CallbackContext):
    user_first_name = update.effective_user.first_name or "there"

    welcome_text = (
        f"👋 <b>Hello, {user_first_name}!</b>\n\n"
        "Welcome to <b>InstaInfo Bot</b> — your assistant to fetch public Instagram profile info 📸\n\n"
        "🔎 <b>What you can do:</b>\n"
        "• Lookup public Instagram <b>username</b> or <b>user ID</b>\n"
        "• Check if an AOL username is available\n"
        "• Send Instagram password reset links\n\n"
        "⚙️ <b>Commands:</b>\n"
        "• <code>/start</code> — Show welcome message\n"
        "• <code>/help</code> — How to use the bot\n"
        "• <code>/info &lt;username&gt;</code> — Get Instagram info by username\n"
        "• <code>/reset &lt;username&gt;</code> — Send IG reset link\n"
        "• <code>/aol &lt;username&gt;</code> — Check AOL username availability\n\n"
        "══════════════════════════════\n"
        "💎 <b>Developer:</b> <a href=\"https://t.me/PrayagRajj\">ＰｒａｙａｇＲａｊｊ</a> 💎\n"
        "══════════════════════════════"
    )

    update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )
def help_command(update: Update, context: CallbackContext):
    help_text = (
        "📖 <b>Help & Usage Guide</b>\n\n"
        "🔍 <b>Main Commands:</b>\n"
        "• <code>/info &lt;username&gt;</code> → Get Instagram info by username\n"
        "• <code>/reset &lt;username&gt;</code> → Send password reset link to IG account\n"
        "• <code>/aol &lt;username&gt;</code> → Check if an AOL email (username@aol.com) is available\n\n"
        "📦 <b>Instagram Info Includes:</b>\n"
        "• Username & Full Name\n"
        "• Bio, Followers, Following\n"
        "• Private / Public status\n"
        "• Account creation date\n"
        "• Business / Personal status\n"
        "• Former usernames & country (if available)\n\n"
        "⏱ <b>Cooldown:</b> 25 seconds between lookups to avoid spam.\n\n"
        "Need help? Contact the dev:<a href=\"https://t.me/PrayagRajj\">ＰｒａｙａｇＲａｊｊ</a>"
    )
    update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
import csv
import requests
import time
import re
from datetime import datetime
from telegram import Update, ParseMode, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackContext

# === Configuration ===
CSV_URL = "https://raw.githubusercontent.com/MrHacker274/Vortex/main/Member.csv"
BOT_TOKEN = "7697054311:AAFfRUW-ImoGGB1weCB_j_Je0C2k05ywzaw"
ADMIN_CHAT_ID = 5851767478
user_last_used = {}

# ===== Helper: Format Time Left =====
def format_remaining_time(expiry_str, user=None):
    now = datetime.now()
    try:
        expiry = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return "⚠️ Invalid expiry format."

    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() if user else "Unknown"
    user_info = (
        f"🙍‍♂️ <b>Name:</b> {full_name}\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
        f"🔗 <b>Profile:</b> {user.mention_html()}" if user else ""
    )

    if expiry <= now:
        return (
            f"❌ <b>Subscription Expired</b>\n"
            f"⏰ <b>Expired On:</b> <code>{expiry_str}</code>\n\n{user_info}"
        )

    delta = expiry - now
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    time_parts = []
    if days: time_parts.append(f"{days}d")
    if hours: time_parts.append(f"{hours}h")
    if minutes: time_parts.append(f"{minutes}m")
    if seconds: time_parts.append(f"{seconds}s")

    return (
        f"✅ <b>Subscription Active</b>\n"
        f"⏳ <b>Time Left:</b> {', '.join(time_parts)}\n"
        f"📅 <b>Expires On:</b> <code>{expiry_str}</code>\n\n{user_info}"
    )

# ===== CSV Expiry Fetch =====
def get_expiry_from_csv(user_id):
    try:
        response = requests.get(CSV_URL, timeout=10)
        response.raise_for_status()
        reader = csv.DictReader(response.text.splitlines())

        for row in reader:
            if row.get("id") == str(user_id):
                return row.get("expiry")
    except:
        pass
    return None

# ===== Paid Membership Check =====
def is_user_paid(user_id: int) -> bool:
    try:
        response = requests.get(CSV_URL)
        response.raise_for_status()
        reader = csv.DictReader(response.text.splitlines())
        for row in reader:
            if row.get("id") == str(user_id):
                expiry_str = row.get("expiry", "")
                expiry = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
                return expiry > datetime.now()
    except:
        pass
    return False

# ===== Dummy Placeholder: Convert ID to Username =====
def get_username_from_user_id(user_id):
    # This requires an external API or database access in reality.
    # For now, return dummy data:
    return f"user{user_id}"

# ===== Dummy Placeholder: Fetch Instagram Info =====
def fetch_instagram_info(username):
    # Placeholder for actual IG scraping or API call.
    # Return sample HTML-formatted data:
    return (
        f"<b>👤 Username:</b> @{username}\n"
        f"<b>🧾 Bio:</b> Sample bio for {username}\n"
        f"<b>🔢 Followers:</b> 12.3K\n"
        f"<b>📷 Posts:</b> 215"
    )

# ===== Subscription Status Command =====
def subscription_command(update: Update, context: CallbackContext):
    user = update.effective_user
    expiry_str = get_expiry_from_csv(user.id)

    if not expiry_str:
        update.message.reply_text(
            f"🚫 <b>No subscription found</b> for <b>{user.full_name}</b> (ID: <code>{user.id}</code>).\n📞 Please contact support.",
            parse_mode=ParseMode.HTML
        )
        return

    status = format_remaining_time(expiry_str, user=user)
    update.message.reply_text(status, parse_mode=ParseMode.HTML)
def handle_info_command(update: Update, context: CallbackContext):
    message_text = update.message.text or ""
    command = message_text.lower().split()[0]
    if command not in ["/info", "/infonum"]:
        return

    user = update.effective_user
    user_id = user.id
    now = time.time()
    if command == "/infonum" and not is_user_paid(user_id):
        update.message.reply_text("⛔ This command is for paid members only.\nPlease contact admin to subscribe.")
        return
    if user_id in user_last_used and now - user_last_used[user_id] < 25:
        wait_time = int(25 - (now - user_last_used[user_id]))
        update.message.reply_text(f"⏳ Please wait {wait_time}s before trying again.")
        return
    user_last_used[user_id] = now
    parts = message_text.split(maxsplit=1)
    if len(parts) < 2:
        usage = "Example: <code>/info instagram</code>\nOr: <code>/infonum 1234567890</code>"
        update.message.reply_text(f"❌ Please provide a username or user ID.\n{usage}", parse_mode=ParseMode.HTML)
        return

    input_value = parts[1].strip().lstrip("@")
    is_userid = command == "/infonum"

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    loading_message = update.message.reply_text("🔍 Processing your request...", parse_mode=ParseMode.HTML)
    time.sleep(1.5)

    try:
        if is_userid:
            if not input_value.isdigit():
                loading_message.edit_text("❌ Invalid user ID format. Only digits allowed.", parse_mode=ParseMode.HTML)
                return
            loading_message.edit_text(f"🔄 Resolving username for user ID <code>{input_value}</code> ...", parse_mode=ParseMode.HTML)
            time.sleep(1.5)
            username = get_username_from_user_id(input_value)
            if not username:
                loading_message.edit_text("❌ Could not resolve username for this ID.", parse_mode=ParseMode.HTML)
                return
        else:
            if not re.match(r"^[a-zA-Z0-9._]{1,30}$", input_value):
                loading_message.edit_text("❌ Invalid username format.", parse_mode=ParseMode.HTML)
                return
            username = input_value

        loading_message.edit_text(f"🔍 Fetching info for <code>@{username}</code>", parse_mode=ParseMode.HTML)
        time.sleep(1.5)

        info = fetch_instagram_info(username)
        loading_message.edit_text(info, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

        requester = f'<a href="https://t.me/{user.username}">@{user.username}</a>' if user.username else f"{user.full_name} (ID: <code>{user.id}</code>)"
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(f"📩 <b>Request by:</b> {requester}\n"
                  f"🔎 <b>Searched IG:</b> <code>{username}</code>\n\n{info}"),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

    except Exception as e:
        loading_message.edit_text(f"❌ Error:\n<code>{str(e)}</code>", parse_mode=ParseMode.HTML)
def get_username_from_user_id(user_id: str) -> str:
    cookies = {
        'datr': 'GAgjaB5R_liEM-dpATRTgjMj',
    'ig_did': '114B8FDB-7673-4860-A1D8-E88C655B9DD8',
    'dpr': '0.8999999761581421',
    'ig_nrcb': '1',
    'ps_l': '1',
    'ps_n': '1',
    'mid': 'aDaRiAALAAFk8TVh8AGAIMVtWO_F',
    'csrftoken': 'Pf0Us3q173jfLfTXAurrhCD8uY5KpFlf',
    'ds_user_id': '5545662104',
    'sessionid': '5545662104%3ATSmn4hQ082l5P1%3A2%3AAYfGQJkf9uoykg9E_EqpP4vuo--TjaReYFdz8ClhDCE',
    'rur': '"CCO\\0545545662104\\0541780979422:01fe117434d511dfb250ee87303ff8299cf0902d289cc28615e1b2dfef597cb2f073fd8d"',
    'wd': '1160x865',
    }
    headers = {
        'accept': '*/*',
    'accept-language': 'en-US,en;q=0.6',
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'origin': 'https://www.instagram.com',
    'priority': 'u=1, i',
    'referer': 'https://www.instagram.com/cristiano/',
    'sec-ch-ua': '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-full-version-list': '"Brave";v="137.0.0.0", "Chromium";v="137.0.0.0", "Not/A)Brand";v="24.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'cookie': 'datr=GAgjaB5R_liEM-dpATRTgjMj; ig_did=114B8FDB-7673-4860-A1D8-E88C655B9DD8; dpr=0.8999999761581421; ig_nrcb=1; ps_l=1; ps_n=1; mid=aDaRiAALAAFk8TVh8AGAIMVtWO_F; csrftoken=Pf0Us3q173jfLfTXAurrhCD8uY5KpFlf; ds_user_id=5545662104; sessionid=5545662104%3ATSmn4hQ082l5P1%3A2%3AAYfGQJkf9uoykg9E_EqpP4vuo--TjaReYFdz8ClhDCE; rur="CCO\\0545545662104\\0541780979422:01fe117434d511dfb250ee87303ff8299cf0902d289cc28615e1b2dfef597cb2f073fd8d"; wd=1160x865',
    }
    params = {
        'appid': 'com.bloks.www.ig.about_this_account',
    'type': 'app',
    '__bkv': 'f4e32caf235c4c3198ceb3d7599c397741599ea3447ec2f785d4575aeb99766b',
    }
    data = {
        '__d': 'www',
    '__user': '0',
    '__a': '1',
    '__req': '1f',
    '__hs': '20248.HYP:instagram_web_pkg.2.1...0',
    'dpr': '1',
    '__ccg': 'EXCELLENT',
    '__rev': '1023623731',
    '__s': '499qrl:ctig8q:csc88m',
    '__hsi': '7513802066483034222',
    '__dyn': '7xeUjG1mxu1syUbFp41twWwIxu13wvoKewSAwHwNw9G2S7o2vwa24o0B-q1ew6ywaq0yE462mcw5Mx62G5UswoEcE7O2l0Fwqo31w9O0H8-U2zxe2GewGw9a361qwuEjUlwhEe87q0oa2-azqwt8d-2u2J0bS1LwTwKG1pg2fwxyo6O1FwlA3a3zhA6bwgbxui2K7E5y4UrwHwcObyohw4rxO2C',
    '__csr': 'iMigtEp3QrOgxOAl4dldbHf-JQWaWWty8CKnUgCYzBzaWjKrGmVGQhAK_BrJi4RgzCADiiDD9GHuulykiQ9iWAh5ZafgGuaHBgvUKJ38yu4Fb8VRjCF6CyoyUOuFCcy8-4ogigLzkiRx28zrABmE-aUO7F4iEC48tx2UoKt2Erw05kng4iut2E3VwHg5q3Gcg9-ve1EwEA9eW80NSt1GWyE565k0wA0L80V22K6U0i3w2fVZ0oK4FF84V7Pwh40Sp62C0x9U9k1PDDgHe0GkkOy8x36no13ouEE4a0jqlQ0BFkdgBk0KFF8qwCg0V-00wI80PO030i',
    '__hsdp': 'gcI9cx2-xsQhONZEIKFbb34-d4hQtp0d5FHsdEmOoBPt8g2fC7yrG1T73onxGdxcOG3C0y44O0XwMpKh1i0XU1Ko1dEaE2Nw4_w3CE7m4U21wdq0BU2bwbi3m0bmwcWE7a5o2dxq',
    '__hblp': '4g5m13wgk8wIxuqE2eyEkGayqxK0J8iCxq4pEWcBqwNUK1bzt5xm2eh6wiELG4mcAGh2EyazFEgyErG224EjxaU9ppoZa8wwRwEzEc99oapUS5omwFwEwOw8u1hxm15wGDyoK1bCwg81b8iy84i1RhEnw-zE1A84C0zo8Ud9Ukxe14wyxlaUlwn85ebw9uEdU520J8do2KAt6xq2dwiUtwgEO4GwwwTBgcUuwjFU88yq6o9kEy3S7E5GeDzo5eeggB4krCzUW2u',
    '__comet_req': '7',
    'fb_dtsg': 'NAft8PCC95bUa6gG43Ooiu-xcZobNgkxRKPE6gn2LAtOuc1Qc3jPlnQ:17843671327157124:1748946019',
    'jazoest': '26205',
    'lsd': 'vg_3IThEEP07uATl42SAxX',
    '__spin_r': '1023623731',
    '__spin_b': 'trunk',
    '__spin_t': '1749443371',
    '__crn': 'comet.igweb.PolarisProfilePostsTabRoute',
        'params': f'{{"referer_type":"ProfileUsername","target_user_id":"{user_id}"}}'
    }

    response = requests.post('https://www.instagram.com/async/wbloks/fetch/', params=params, cookies=cookies, headers=headers, data=data)
    matches = re.findall(r'"text":"(.*?)"', response.text)
    return matches[0] if matches else None    

import secrets
import user_agent
import requests
import random
import re
def check_aol_username(username):
    def check_availability_from_text(response_text):
        response_text = response_text.strip()
        taken_errors = [
            '{"errors":[{"name":"userId","error":"IDENTIFIER_NOT_AVAILABLE"},{"name":"birthDate","error":"INVALID_BIRTHDATE"},{"name":"password","error":"FIELD_EMPTY"}]}',
            '{"errors":[{"name":"userId","error":"IDENTIFIER_EXISTS"},{"name":"birthDate","error":"INVALID_BIRTHDATE"},{"name":"password","error":"FIELD_EMPTY"}]}',
            '{"errors":[{"name":"userId","error":"RESERVED_WORD_PRESENT"},{"name":"birthDate","error":"INVALID_BIRTHDATE"},{"name":"password","error":"FIELD_EMPTY"}]}',
        ]
        if response_text in taken_errors:
            return "❌ Taken"
        
        pattern = (
            r'^\{"errors":\['
            r'\{"name":"userId","error":"ERROR_\d{3}"\},'
            r'\{"name":"birthDate","error":"INVALID_BIRTHDATE"\},'
            r'\{"name":"password","error":"FIELD_EMPTY"\}'
            r'\]\}$'
        )
        if re.match(pattern, response_text):
            return "❌ Taken"
        
        return "✅ Available"

    # [YOUR COOKIES AND HEADERS HERE - ALREADY OK IN YOUR SCRIPT]
    cookies = {
    'weathergeo': '%2223.03%7C72.60%7CAhmedabad%7CGJ%7CIndia%7C0%7C29219630%22',
    'GUC': 'AQEBCAFoQrxoa0IdaQRU&s=AQAAAGsKHyP7&g=aEFsow',
    'A1': 'd=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA',
    'A3': 'd=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA',
    'A1S': 'd=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA',
    'AS': 'v=1&s=oUo1Wjzb&d=A6847b4b9|DjrgY.3.2TobLMu03xmPd_T_ShkQdtLFPwdx1fh74Arr6sIypTXiSQPrYoXKb8ktFdhp10oVYU1J5AOk_mE_YwYEY5rBEA0XcRwQDWF_M6U7prTDqBqLiqHuQGL4eTUeegfipWdx4jlaSLUIhi7fGXGMR_y9ZJC.KBaurz6V9EP3TZTzuV_jKgIUG8F5v6383cD_JTrNwGV5XprRoMfiKLdxi8V5mUZ90NiH1HO4UqGqY_TXR0d2x8aYqZdGvE1fHFHDVn1uKSjAZBVTpX61H6zyhxvzm6kqAA76b_G_FLu1R3rhvU.Y.YNi6ofrrY.Lnt9ZaImnkyeR.n3MALifDIJSUAoLDg3bcjnQ3UUS05J_ldhgClc6HiAczm15tj8FD7gW_p7hqmFh7h3CGBlbDb5.3JwFSLsr.O9BQ3tcicaVzU9X3uq8G1epTokS2bjuutN7lkvGq8hMe_QDzO21Xt9j8FQ8CgLCi0tS9TwBTmH7EyObzkGkmq0zsPRGlr38IoIU3D8KZo8pYCBSkMODcsdCw2NL5YA2Xar9MUX_4tCPNrFZqk58mBfunLKjg6ow2JRQ6vgUWPn4JD6v51My3ivl1sDdzma0R6u.rowqObErXiF1x6mvpenFXpdnzLNqjbrsvIkgmbLKDNuD4Aqk3TyQzw07TlBw1wj0zDKM0UwaJ3ssCx8DHwCIgkuVQl7pFoNZBR3illcu4nbZqagU1vLZVyA4GZxRpwvXWC9l7bSeFublHTcUyeDgeDjO2V020EGducMK_1gukSRQQayxuJZpOoznG5BF8y9_rqxa6Cqe9oGjp9Y..GTHHVG4bymsMVG4Vvy19GyqBoULeIIsryMWca9yqEgfGvPuyXIFtpZFM9e6lGX5L7uxycU_6pktQ_9CFOtAUAwZArjV_i6ic2C.0AVEN4vzA0B_vw9dfihipE6mi.ljCTjyILED5M_oUTpAgQhVBBYpk1_wP2uHyQwsutXlVOACa1ouysS9svo64X3fwb3epJCjOj9CzQdcoav8GWlOBrlmMUn9jslURqfubJIOePR3uJXcHsEZA.tqDOPV8wlXN56MrYEANRJt7EDkW4r6Dp07xK8NwYSuGqL5DCHqE_zX0T49PJohWHYiD0knd7QEiIzXdP7B46R.FUM-~A|B6847fc5d|IKpUeE3.2Tqo.hb5N09df8PUsLXvg8Id_04RuJ68sNMG9Aq3pB6LLgkDQ9h.xmFC0En_JnlRYuX5OTqrBdSaqe263qgsmTW0TFqEfIRMYStj6OHmeyMZbDm.xIenEmcg2e_jpR9caapIHRmuZe.DJM1HQA3Xua0sEXEWSYBSW8vdiG.qhHmYym0uEf4QWxZEdVoK4tj5u5Pd8_prqsmLLvXEjWQFRoIdxlfYqh6ktRkthQyKAJzPT3cFwvMLdfFk7hOSLzQY3wp8hLoGtmH4VmSCrG02uhWIhQzq33mFKfkQsRNAAAK4LeHEbGEsBDbbf5j8OB._VYuagzcSty9shGYwcSA9f.NuBQL2FGJMKWkDimrS53ZnGBJJU5.M7MEEbY9YxxzgRQaD_L_FLnPaGsnGUBuhnptv3asqxszytpvs1N7y0yMb7vUU1GqN.h7N7.R9z2AujfTKd2pcc7B4F78xxohquKOPWHsZ.jWcitibwkbt5om3S5JaUZ5u5GYhytoiNB282lpbsFJM15z6mTpkM7F3.SG9byeM06Ee0ImiYINhVQaPTdD9d3HNePqGnsduHedu23mJCyrVVlj7KuhXi81LNS_wMhoOoASkwLRpTunYRHcVyMTKJMmaj4sm2BOf6cSTjROy0VNvruZsOVpdQGRxtqzQ2hEif1d7Phol5nRZPygaCJNn1YmJZEpWjmJ75B7C9ubSBu85nb21qESLWX9qTaM2diuZLnOEKJlx2RQ87vWWMKissMfJBO84BiD.5qA_r1cwu71pJroE2hCWwu.2hKRvtOFTh7mF7SwzG6d_0VQ0EEdQc5.djgzWF33jq0o_6DpTP1lhr8cDOiCtil926w4SNs8n.3UU9Hwt766VlosP4APotI.ma.ah9xL3Tipu5VWzLRZ5PShm6ph0HmjZka7.PJzb9V.LbP8T0bM_SMvsQMAvDNte_PLzDQw7wdDmgMpLh2HODpW3heH4F5na0LdC6VDmHRuqGwfBkg3cc7wPmhm.xd0Fx_jgzXiEq_gFSZ0hUksJhV_.Fz.NS2mwTm5v0posaa5N_wOz1mLrR99nBCyDGlnQep_vney1JoIOY77TzyyuA.DScZKm0eDPEetZV4OGPjccWlxMilri1ypn4M69vsBw.TvHOg--~A',
    }  
    headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://login.aol.com',
    'priority': 'u=1, i',
    'referer': 'https://login.aol.com/account/create?intl=us&src=fp-us&activity=default&pspid=1197803361&done=https%3A%2F%2Fapi.login.aol.com%2Foauth2%2Fauthorize%3Fclient_id%3Ddj0yJmk9ZXRrOURhMkt6bkl5JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWQ2%26intl%3Dus%26nonce%3DWSbk8RiHKdR86BSpvlDJfvkkiG7yZfSz%26redirect_uri%3Dhttps%253A%252F%252Foidc.www.aol.com%252Fcallback%26response_type%3Dcode%26scope%3Dmail-r%2Bopenid%2Bguce-w%2Bopenid2%2Bsdps-r%26src%3Dfp-us%26state%3DeyJhbGciOiJSUzI1NiIsImtpZCI6IjZmZjk0Y2RhZDExZTdjM2FjMDhkYzllYzNjNDQ4NDRiODdlMzY0ZjcifQ.eyJyZWRpcmVjdFVyaSI6Imh0dHBzOi8vd3d3LmFvbC5jb20vIn0.hlDqNBD0JrMZmY2k9lEi6-BfRidXnogtJt8aI-q2FdbvKg9c9EhckG0QVK5frTlhV8HY7Mato7D3ek-Nt078Z_i9Ug0gn53H3vkBoYG-J-SMqJt5MzG34rxdOa92nZlQ7nKaNrAI7K9s72YQchPBn433vFbOGBCkU_ZC_4NXa9E&specId=yidregsimplified',
    'sec-ch-ua': '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    'cookie': 'weathergeo=%2223.03%7C72.60%7CAhmedabad%7CGJ%7CIndia%7C0%7C29219630%22; GUC=AQEBCAFoQrxoa0IdaQRU&s=AQAAAGsKHyP7&g=aEFsow; A1=d=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA; A3=d=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA; A1S=d=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA; AS=v=1&s=oUo1Wjzb&d=A6847b4b9|DjrgY.3.2TobLMu03xmPd_T_ShkQdtLFPwdx1fh74Arr6sIypTXiSQPrYoXKb8ktFdhp10oVYU1J5AOk_mE_YwYEY5rBEA0XcRwQDWF_M6U7prTDqBqLiqHuQGL4eTUeegfipWdx4jlaSLUIhi7fGXGMR_y9ZJC.KBaurz6V9EP3TZTzuV_jKgIUG8F5v6383cD_JTrNwGV5XprRoMfiKLdxi8V5mUZ90NiH1HO4UqGqY_TXR0d2x8aYqZdGvE1fHFHDVn1uKSjAZBVTpX61H6zyhxvzm6kqAA76b_G_FLu1R3rhvU.Y.YNi6ofrrY.Lnt9ZaImnkyeR.n3MALifDIJSUAoLDg3bcjnQ3UUS05J_ldhgClc6HiAczm15tj8FD7gW_p7hqmFh7h3CGBlbDb5.3JwFSLsr.O9BQ3tcicaVzU9X3uq8G1epTokS2bjuutN7lkvGq8hMe_QDzO21Xt9j8FQ8CgLCi0tS9TwBTmH7EyObzkGkmq0zsPRGlr38IoIU3D8KZo8pYCBSkMODcsdCw2NL5YA2Xar9MUX_4tCPNrFZqk58mBfunLKjg6ow2JRQ6vgUWPn4JD6v51My3ivl1sDdzma0R6u.rowqObErXiF1x6mvpenFXpdnzLNqjbrsvIkgmbLKDNuD4Aqk3TyQzw07TlBw1wj0zDKM0UwaJ3ssCx8DHwCIgkuVQl7pFoNZBR3illcu4nbZqagU1vLZVyA4GZxRpwvXWC9l7bSeFublHTcUyeDgeDjO2V020EGducMK_1gukSRQQayxuJZpOoznG5BF8y9_rqxa6Cqe9oGjp9Y..GTHHVG4bymsMVG4Vvy19GyqBoULeIIsryMWca9yqEgfGvPuyXIFtpZFM9e6lGX5L7uxycU_6pktQ_9CFOtAUAwZArjV_i6ic2C.0AVEN4vzA0B_vw9dfihipE6mi.ljCTjyILED5M_oUTpAgQhVBBYpk1_wP2uHyQwsutXlVOACa1ouysS9svo64X3fwb3epJCjOj9CzQdcoav8GWlOBrlmMUn9jslURqfubJIOePR3uJXcHsEZA.tqDOPV8wlXN56MrYEANRJt7EDkW4r6Dp07xK8NwYSuGqL5DCHqE_zX0T49PJohWHYiD0knd7QEiIzXdP7B46R.FUM-~A|B6847fc5d|IKpUeE3.2Tqo.hb5N09df8PUsLXvg8Id_04RuJ68sNMG9Aq3pB6LLgkDQ9h.xmFC0En_JnlRYuX5OTqrBdSaqe263qgsmTW0TFqEfIRMYStj6OHmeyMZbDm.xIenEmcg2e_jpR9caapIHRmuZe.DJM1HQA3Xua0sEXEWSYBSW8vdiG.qhHmYym0uEf4QWxZEdVoK4tj5u5Pd8_prqsmLLvXEjWQFRoIdxlfYqh6ktRkthQyKAJzPT3cFwvMLdfFk7hOSLzQY3wp8hLoGtmH4VmSCrG02uhWIhQzq33mFKfkQsRNAAAK4LeHEbGEsBDbbf5j8OB._VYuagzcSty9shGYwcSA9f.NuBQL2FGJMKWkDimrS53ZnGBJJU5.M7MEEbY9YxxzgRQaD_L_FLnPaGsnGUBuhnptv3asqxszytpvs1N7y0yMb7vUU1GqN.h7N7.R9z2AujfTKd2pcc7B4F78xxohquKOPWHsZ.jWcitibwkbt5om3S5JaUZ5u5GYhytoiNB282lpbsFJM15z6mTpkM7F3.SG9byeM06Ee0ImiYINhVQaPTdD9d3HNePqGnsduHedu23mJCyrVVlj7KuhXi81LNS_wMhoOoASkwLRpTunYRHcVyMTKJMmaj4sm2BOf6cSTjROy0VNvruZsOVpdQGRxtqzQ2hEif1d7Phol5nRZPygaCJNn1YmJZEpWjmJ75B7C9ubSBu85nb21qESLWX9qTaM2diuZLnOEKJlx2RQ87vWWMKissMfJBO84BiD.5qA_r1cwu71pJroE2hCWwu.2hKRvtOFTh7mF7SwzG6d_0VQ0EEdQc5.djgzWF33jq0o_6DpTP1lhr8cDOiCtil926w4SNs8n.3UU9Hwt766VlosP4APotI.ma.ah9xL3Tipu5VWzLRZ5PShm6ph0HmjZka7.PJzb9V.LbP8T0bM_SMvsQMAvDNte_PLzDQw7wdDmgMpLh2HODpW3heH4F5na0LdC6VDmHRuqGwfBkg3cc7wPmhm.xd0Fx_jgzXiEq_gFSZ0hUksJhV_.Fz.NS2mwTm5v0posaa5N_wOz1mLrR99nBCyDGlnQep_vney1JoIOY77TzyyuA.DScZKm0eDPEetZV4OGPjccWlxMilri1ypn4M69vsBw.TvHOg--~A',
    }
    params = {
        'validateField': 'userId',
    }
    data = f'browser-fp-data=%7B%22language%22%3A%22en-US%22%2C%22colorDepth%22%3A24%2C%22deviceMemory%22%3A8%2C%22pixelRatio%22%3A1%2C%22hardwareConcurrency%22%3A4%2C%22timezoneOffset%22%3A-330%2C%22timezone%22%3A%22Asia%2FCalcutta%22%2C%22sessionStorage%22%3A1%2C%22localStorage%22%3A1%2C%22indexedDb%22%3A1%2C%22cpuClass%22%3A%22unknown%22%2C%22platform%22%3A%22Win32%22%2C%22doNotTrack%22%3A%22unknown%22%2C%22plugins%22%3A%7B%22count%22%3A4%2C%22hash%22%3A%22879774623977b14ab013aceca855878d%22%7D%2C%22canvas%22%3A%22canvas%20winding%3Ayes~canvas%22%2C%22webgl%22%3A1%2C%22webglVendorAndRenderer%22%3A%22Google%20Inc.%20(Intel)~ANGLE%20(Intel%2C%20Intel(R)%20HD%20Graphics%20Direct3D9Ex%20vs_3_0%20ps_3_0%2C%20igdumd64.dll)%22%2C%22adBlock%22%3A0%2C%22hasLiedLanguages%22%3A0%2C%22hasLiedResolution%22%3A0%2C%22hasLiedOs%22%3A0%2C%22hasLiedBrowser%22%3A0%2C%22touchSupport%22%3A%7B%22points%22%3A0%2C%22event%22%3A0%2C%22start%22%3A0%7D%2C%22fonts%22%3A%7B%22count%22%3A29%2C%22hash%22%3A%2290ead5fa1a480b09b5b0239bd273a529%22%7D%2C%22audio%22%3A%22123.79177350061218%22%2C%22resolution%22%3A%7B%22w%22%3A%221680%22%2C%22h%22%3A%221050%22%7D%2C%22availableResolution%22%3A%7B%22w%22%3A%221050%22%2C%22h%22%3A%221680%22%7D%2C%22ts%22%3A%7B%22serve%22%3A1749443385307%2C%22render%22%3A1749443390533%7D%7D&specId=yidregsimplified&context=REGISTRATION&cacheStored=&crumb=v%2FnkkKGtxP3126Cthy3k3A&acrumb=oUo1Wjzb&sessionIndex=QQ--&done=https%3A%2F%2Fapi.login.aol.com%2Foauth2%2Fauthorize%3Fclient_id%3Ddj0yJmk9ZXRrOURhMkt6bkl5JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWQ2%26intl%3Dus%26nonce%3DWSbk8RiHKdR86BSpvlDJfvkkiG7yZfSz%26redirect_uri%3Dhttps%253A%252F%252Foidc.www.aol.com%252Fcallback%26response_type%3Dcode%26scope%3Dmail-r%2Bopenid%2Bguce-w%2Bopenid2%2Bsdps-r%26src%3Dfp-us%26state%3DeyJhbGciOiJSUzI1NiIsImtpZCI6IjZmZjk0Y2RhZDExZTdjM2FjMDhkYzllYzNjNDQ4NDRiODdlMzY0ZjcifQ.eyJyZWRpcmVjdFVyaSI6Imh0dHBzOi8vd3d3LmFvbC5jb20vIn0.hlDqNBD0JrMZmY2k9lEi6-BfRidXnogtJt8aI-q2FdbvKg9c9EhckG0QVK5frTlhV8HY7Mato7D3ek-Nt078Z_i9Ug0gn53H3vkBoYG-J-SMqJt5MzG34rxdOa92nZlQ7nKaNrAI7K9s72YQchPBn433vFbOGBCkU_ZC_4NXa9E&googleIdToken=&authCode=&attrSetIndex=0&specData=&deviceCapability=%7B%22pa%22%3A%7B%22status%22%3Afalse%7D%2C%22isWebAuthnSupported%22%3Atrue%7D&tos0=oath_freereg%7Cus%7Cen-US&multiDomain=&asId=57b2f097-550f-42eb-87ed-a942403cae9d&fingerprintCaptured=&firstName=zuck&lastName=zuck&userid-domain=yahoo&userId={username}&password=&mm=&dd=&yyyy=&signup='
        'https://login.aol.com/account/module/create',
        params=params,
        cookies=cookies,
        headers=headers,
        data=data
    )
    return check_availability_from_text(response.text)
class Gm:
    def __init__(self, email):
        self.email = email
        if "@" in self.email:
            self.email = self.email.split("@")[0]
        self.TL = None
        self.__Host_GAPS = None
        self.base_url = 'https://accounts.google.com/_/signup'
        self.headers = {
            'user-agent': user_agent.generate_user_agent(),
            'google-accounts-xsrf': '1',
        }

    def check(self):
        try:
            url = self.base_url + '/validatepersonaldetails'
            params = {'hl': "ar", '_reqid': "74404", 'rt': "j"}
            payload = {
                'f.req': "[\"AEThLlymT9V_0eW9Zw42mUXBqA3s9U9ljzwK7Jia8M4qy_5H3vwDL4GhSJXkUXTnPL_roS69KYSkaVJLdkmOC6bPDO0jy5qaBZR0nGnsWOb1bhxEY_YOrhedYnF3CldZzhireOeUd-vT8WbFd7SXxfhuWiGNtuPBrMKSLuMomStQkZieaIHlfdka8G45OmseoCfbsvWmoc7U\",\"L7N\",\"ToPython\",\"L7N\",\"ToPython\",0,0,null,null,null,0,null,1,[],1]",
                'deviceinfo': "[null,null,null,null,null,\"IQ\",null,null,null,\"GlifWebSignIn\",null,[],null,null,null,null,1,null,0,1,\"\",null,null,1,1,2]",
            }
            __Host_GAPS = ''.join(secrets.choice("qwertyuiopasdfghjklzxcvbnm") for _ in range(secrets.randbelow(16) + 15))
            cookies = {'__Host-GAPS': __Host_GAPS}
            response = requests.post(url, cookies=cookies, params=params, data=payload, headers=self.headers, timeout=10)

            if response.status_code != 200 or '",null,"' not in response.text:
                return None

            self.TL = str(response.text).split('",null,"')[1].split('"')[0]
            self.__Host_GAPS = response.cookies.get_dict().get('__Host-GAPS')

            url = self.base_url + '/usernameavailability'
            cookies = {'__Host-GAPS': self.__Host_GAPS}
            params = {'TL': self.TL}
            data = {
                'continue': 'https://mail.google.com/mail/u/0/',
                'ddm': '0',
                'flowEntry': 'SignUp',
                'service': 'mail',
                'theme': 'mn',
                'f.req': f'["TL:{self.TL}","{self.email}",0,0,1,null,0,5167]',
                'azt': 'AFoagUUtRlvV928oS9O7F6eeI4dCO2r1ig:1712322460888',
                'cookiesDisabled': 'false',
                'deviceinfo': '[null,null,null,null,null,"NL",null,null,null,"GlifWebSignIn",null,[],null,null,null,null,2,null,0,1,"",null,null,2,2]',
                'gmscoreversion': 'undefined',
                'flowName': 'GlifWebSignIn'
            }
            response = requests.post(url, params=params, cookies=cookies, headers=self.headers, data=data, timeout=10)
            if response.status_code == 200:
                return {"available": '"gf.uar",1' in response.text}
            else:
                return None
        except:
            return None
import logging
import requests
import json
import re
from uuid import uuid4
from secrets import token_hex
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
logging.basicConfig(level=logging.INFO)
def send_recovery_request(email_or_username):
    methods = [
        ("Method 1", method_1),
        ("Method 2", method_2),
        ("Method 3", method_3),
        ("Method 4", method_4),
        ("Method 5", method_5),
        ("Method 6", method_6),
        ("Method 7", method_7)
    ]

    for name, method in methods:
        try:
            result = method(email_or_username)
            if result not in ["No Reset", "Failed", "Error"]:
                print(f"[✅] {name} succeeded: {result}")
                return [f"{result}"]
            else:
                print(f"[❌] {name} returned: {result}")
        except Exception as e:
            print(f"[⚠️] {name} raised an exception: {e}")
            continue

    return ["No Reset"]

ua = UserAgent()

def method_1(email_or_username):
    cookies = {
        'csrftoken': 'gpexs0wL6nxpdY955MzDDX',
        'datr': '_s3HZ5T-vg2PnLjgub9fdKw4',
        'ig_did': '6D20CB61-D866-4513-8735-F6E4488FF4BB',
        'mid': 'Z8fOAAABAAHq9LOzjjUU7ImwpR_6',
        'ig_nrcb': '1',
        'dpr': '2.1988937854766846',
        'ps_l': '1',
        'ps_n': '1',
        'wd': '891x896',
    }

    headers = {
        'authority': 'www.instagram.com',
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.instagram.com',
        'referer': 'https://www.instagram.com/accounts/password/reset/?hl=ar',
        'user-agent': ua.random,
        'x-csrftoken': cookies['csrftoken'],
        'x-ig-app-id': '936619743392459',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'email_or_username': email_or_username,
        'jazoest': '21965',
    }

    try:
        response = requests.post(
            'https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/',
            cookies=cookies,
            headers=headers,
            data=data,
        )

        if response.status_code == 200:
            response_json = response.json()
            contact = response_json.get("contact_point")
            if contact:
                return f"Email: {contact}" if "@" in contact else f"Phone: {contact}"
            else:
                return "No Reset"
        else:
            return "No Reset"

    except (requests.RequestException, json.JSONDecodeError, Exception):
        return "Error"

def method_2(email_or_username):
    try:
        headers = {
            'Referer': 'https://www.instagram.com/accounts/password/reset/',
            'X-CSRFToken': 'csrftoken',
            'User-Agent': 'Mozilla/5.0'
        }
        data = {'email_or_username': email_or_username, 'recaptcha_challenge_field': ''}
        res = requests.post('https://www.instagram.com/accounts/account_recovery_send_ajax/', headers=headers, data=data)
        if res.status_code == 200:
            match = re.search('<b>(.*?)</b>', res.text)
            contact = match.group(1) if match else None
            if contact:
                return f"Email: {contact}" if "@" in contact else f"Phone: {contact}"
        return "No Reset"
    except:
        return "Error"
def method_3(email_or_username):
    try:
        headers = {
            'accept': '*/*',
            'referer': 'https://www.instagram.com/accounts/password/reset/?source=fxcal&hl=en',
            'content-type': 'application/x-www-form-urlencoded',
            'x-csrftoken': 'umwHlWf6r3AGDowkZQb47m',
            'x-ig-app-id': '936619743392459'
        }
        data = {'email_or_username': email_or_username, 'flow': 'fxcal'}
        res = requests.post('https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/', headers=headers, data=data)
        if res.status_code == 200:
            result = res.json()
            message = result.get('message', '')
            match = re.search(r'(\+\d[\d\s\-\*]+|[\w\.\*]+@[\w\.\*]+)', message)
            if match:
                contact = match.group(1).strip()
                return f"Email: {contact}" if "@" in contact else f"Phone: {contact}"
        return "No Reset"
    except:
        return "Error"
def method_4(email_or_username):
    try:
        headers = {
            'User-Agent': 'Instagram 6.12.1 Android',
            'Cookie': 'csrftoken=u6c8M4zaneeZBfR5scLVY43lYSIoUhxL'
        }
        res = requests.get(f"https://www.instagram.com/api/v1/users/web_profile_info/?username={email_or_username}", headers=headers)
        user_id = res.json()['data']['user']['id']
        payload = {'user_id': user_id, 'device_id': str(uuid4())}
        res2 = requests.post('https://i.instagram.com/api/v1/accounts/send_password_reset/', headers=headers, data=payload)
        contact = res2.json().get('obfuscated_email')
        if contact:
            return f"Email: {contact}" if "@" in contact else f"Phone: {contact}"
        return "No Reset"
    except:
        return "Error"
def method_5(email_or_username):
    try:
        headers = {
            'User-Agent': 'Instagram 100.0.0.17.129 Android',
            'X-Bloks-Version-Id': 'c80c5fb30dfae9e273e4009f03b18280bb343b0862d663f31a3c63f13a9f31c0',
            'X-IG-App-ID': '567067343352427',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        body = json.dumps({
            "_csrftoken": "9y3N5kLqzialQA7z96AMiyAKLMBWpqVj",
            "adid": str(uuid4()),
            "guid": str(uuid4()),
            "device_id": "android-b93ddb37e983481c",
            "query": email_or_username
        })
        data = {
            'signed_body': f'0d067c2f86cac2c17d655631c9cec2402012fb0a329bcafb3b1f4c0bb56b1f1f.{body}',
            'ig_sig_key_version': '4',
        }
        res = requests.post('https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/', headers=headers, data=data)
        contact = res.json().get("email")
        if contact:
            return f"Email: {contact}"
        return "No Reset"
    except:
        return "Error"
def method_6(email_or_username):
    try:
        headers = {
            'User-Agent': 'Instagram 100.0.0.17.129 Android',
            'X-Bloks-Version-Id': '009f03b18280bb343b0862d663f31ac80c5fb30dfae9e273e43c63f13a9f31c0',
            'X-IG-App-ID': '567067343352427',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        signed_data = json.dumps({
            "_csrftoken": token_hex(8) * 2,
            "adid": str(uuid4()),
            "guid": str(uuid4()),
            "device_id": f"android-{uuid4().hex[:16]}",
            "query": email_or_username
        })
        data = {
            "signed_body": f"sig.{signed_data}",
            "ig_sig_key_version": "4"
        }
        res = requests.post('https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/', headers=headers, data=data)
        contact = res.json().get("email")
        if contact:
            return f"Email: {contact}"
        return "No Reset"
    except:
        return "Error"
def method_7(email_or_username):
    try:
        for _ in range(3):
            headers = {
                'authority': 'www.instagram.com',
                'accept': '*/*',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/accounts/password/reset/',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10)',
                'x-asbd-id': '129477',
                'x-csrftoken': 'missing',
                'x-ig-app-id': '936619743392459',
                'x-requested-with': 'XMLHttpRequest',
            }
            data = {'email_or_username': email_or_username, 'jazoest': '22210'}
            res = requests.post("https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/", headers=headers, data=data).text
            if '"status":"ok"' in res and 'contact_point' in res:
                contact = res.split('"contact_point":"')[1].split('"')[0]
                return f"Email: {contact}" if "@" in contact else f"Phone: {contact}"
        return "No Reset"
    except:
        return "Error"
def fetch_instagram_info(username):
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        user_id = profile.userid    
        cookies = {
            'datr': 'GAgjaB5R_liEM-dpATRTgjMj',
    'ig_did': '114B8FDB-7673-4860-A1D8-E88C655B9DD8',
    'dpr': '0.8999999761581421',
    'ig_nrcb': '1',
    'ps_l': '1',
    'ps_n': '1',
    'mid': 'aDaRiAALAAFk8TVh8AGAIMVtWO_F',
    'csrftoken': 'Pf0Us3q173jfLfTXAurrhCD8uY5KpFlf',
    'ds_user_id': '5545662104',
    'sessionid': '5545662104%3ATSmn4hQ082l5P1%3A2%3AAYfGQJkf9uoykg9E_EqpP4vuo--TjaReYFdz8ClhDCE',
    'rur': '"CCO\\0545545662104\\0541780979422:01fe117434d511dfb250ee87303ff8299cf0902d289cc28615e1b2dfef597cb2f073fd8d"',
    'wd': '1160x865',
        }
        headers = {
           'accept': '*/*',
    'accept-language': 'en-US,en;q=0.6',
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'origin': 'https://www.instagram.com',
    'priority': 'u=1, i',
    'referer': f'https://www.instagram.com/{username}/',
    'sec-ch-ua': '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-full-version-list': '"Brave";v="137.0.0.0", "Chromium";v="137.0.0.0", "Not/A)Brand";v="24.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'cookie': 'datr=GAgjaB5R_liEM-dpATRTgjMj; ig_did=114B8FDB-7673-4860-A1D8-E88C655B9DD8; dpr=0.8999999761581421; ig_nrcb=1; ps_l=1; ps_n=1; mid=aDaRiAALAAFk8TVh8AGAIMVtWO_F; csrftoken=Pf0Us3q173jfLfTXAurrhCD8uY5KpFlf; ds_user_id=5545662104; sessionid=5545662104%3ATSmn4hQ082l5P1%3A2%3AAYfGQJkf9uoykg9E_EqpP4vuo--TjaReYFdz8ClhDCE; rur="CCO\\0545545662104\\0541780979422:01fe117434d511dfb250ee87303ff8299cf0902d289cc28615e1b2dfef597cb2f073fd8d"; wd=1160x865',
        }
        params = {
            'appid': 'com.bloks.www.ig.about_this_account',
    'type': 'app',
    '__bkv': 'f4e32caf235c4c3198ceb3d7599c397741599ea3447ec2f785d4575aeb99766b',
        }
        data = {
            '__d': 'www',
    '__user': '0',
    '__a': '1',
    '__req': '1f',
    '__hs': '20248.HYP:instagram_web_pkg.2.1...0',
    'dpr': '1',
    '__ccg': 'EXCELLENT',
    '__rev': '1023623731',
    '__s': '499qrl:ctig8q:csc88m',
    '__hsi': '7513802066483034222',
    '__dyn': '7xeUjG1mxu1syUbFp41twWwIxu13wvoKewSAwHwNw9G2S7o2vwa24o0B-q1ew6ywaq0yE462mcw5Mx62G5UswoEcE7O2l0Fwqo31w9O0H8-U2zxe2GewGw9a361qwuEjUlwhEe87q0oa2-azqwt8d-2u2J0bS1LwTwKG1pg2fwxyo6O1FwlA3a3zhA6bwgbxui2K7E5y4UrwHwcObyohw4rxO2C',
    '__csr': 'iMigtEp3QrOgxOAl4dldbHf-JQWaWWty8CKnUgCYzBzaWjKrGmVGQhAK_BrJi4RgzCADiiDD9GHuulykiQ9iWAh5ZafgGuaHBgvUKJ38yu4Fb8VRjCF6CyoyUOuFCcy8-4ogigLzkiRx28zrABmE-aUO7F4iEC48tx2UoKt2Erw05kng4iut2E3VwHg5q3Gcg9-ve1EwEA9eW80NSt1GWyE565k0wA0L80V22K6U0i3w2fVZ0oK4FF84V7Pwh40Sp62C0x9U9k1PDDgHe0GkkOy8x36no13ouEE4a0jqlQ0BFkdgBk0KFF8qwCg0V-00wI80PO030i',
    '__hsdp': 'gcI9cx2-xsQhONZEIKFbb34-d4hQtp0d5FHsdEmOoBPt8g2fC7yrG1T73onxGdxcOG3C0y44O0XwMpKh1i0XU1Ko1dEaE2Nw4_w3CE7m4U21wdq0BU2bwbi3m0bmwcWE7a5o2dxq',
    '__hblp': '4g5m13wgk8wIxuqE2eyEkGayqxK0J8iCxq4pEWcBqwNUK1bzt5xm2eh6wiELG4mcAGh2EyazFEgyErG224EjxaU9ppoZa8wwRwEzEc99oapUS5omwFwEwOw8u1hxm15wGDyoK1bCwg81b8iy84i1RhEnw-zE1A84C0zo8Ud9Ukxe14wyxlaUlwn85ebw9uEdU520J8do2KAt6xq2dwiUtwgEO4GwwwTBgcUuwjFU88yq6o9kEy3S7E5GeDzo5eeggB4krCzUW2u',
    '__comet_req': '7',
    'fb_dtsg': 'NAft8PCC95bUa6gG43Ooiu-xcZobNgkxRKPE6gn2LAtOuc1Qc3jPlnQ:17843671327157124:1748946019',
    'jazoest': '26205',
    'lsd': 'vg_3IThEEP07uATl42SAxX',
    '__spin_r': '1023623731',
    '__spin_b': 'trunk',
    '__spin_t': '1749443371',
    '__crn': 'comet.igweb.PolarisProfilePostsTabRoute',
    'params': f'{{"referer_type":"ProfileMore","target_user_id":{user_id} }}',
        }
        response = requests.post(
            'https://www.instagram.com/async/wbloks/fetch/',
            params=params,
            cookies=cookies,
            headers=headers,
            data=data
        )
        texts = re.findall(r'"text":"(.*?)"', response.text)
        results = {}
        for i in range(len(texts) - 1):
            if texts[i] == "Date joined":
                results["Date joined"] = texts[i + 1]
            elif texts[i] == "Verified":
                results["Verified"] = "Yes"
                results["Verified On"] = texts[i + 1]
            elif texts[i] == "Former usernames":
                results["Former usernames"] = texts[i + 1]
        country = re.search(r'"initial"\s*:\s*"([^"]+)"', response.text)
        country = country.group(1) if country else "N/A"
        result = send_recovery_request(username)
        reset_email = result[0].replace("Email: ", "").replace("Phone: ", "").strip() if result and result[0] not in ["No Reset", "Failed", "Error"] else "Not Found"
        result = check_aol_username(username)
        gmail_checker = Gm(username)
        gmail_result = gmail_checker.check()
        has_pic = "Yes" if profile.profile_pic_url else "No"
        pic_view = f'<a href="{profile.profile_pic_url}">📷 View</a>' if profile.profile_pic_url else ''
        reset_check = "🔐 Reset not available"  # default value
        if reset_email and "@" in reset_email and username:
            visible = reset_email.split("@")[0]
            domain = reset_email.split("@")[1].lower()
            first_visible = visible[0]
            last_visible = visible[-1]
            if username[0].lower() == first_visible.lower() and username[-1].lower() == last_visible.lower():
                if "gmail" in domain:
                    if gmail_result is None:reset_check = "❌ Unable to check Gmail"
                    elif gmail_result.get("available"):reset_check = "Gmail is ✅ Available"
                    else:reset_check = "Gmail is ❌ Taken"
                elif "a**" in domain or "aol" in domain.lower():
                    reset_check = f"AOL is {(result)}"
                else:reset_check = "Unknown domain"
            else:reset_check = "🔐 Reset is different"
        result_msg = f"""
══════════════════════════════        
🌟 𝗜ɢ 𝗙ᴇᴛᴄʜᴇʀ 𝗙ʀᴏᴍ <b>ᎮᗯᑎᗩGƐ | Ѵᴏʀᴛᴇx •</b> 🌟
══════════════════════════════
✨ <b>{'Username'.ljust(23)}</b> ➟ <code>{profile.username}</code>
📡  <b>{'Name'.ljust(23)}</b> ➟ <code>{profile.full_name or 'N/A'}</code>
🆔 <b>{'User ID'.ljust(23)}</b> ➟ <code>{profile.userid}</code>
🔗 <b>{'Profile Link'.ljust(23)}</b> ➟ <a href="https://www.instagram.com/{profile.username}">Click Here</a>
👤 <b>{'Profile Picture'.ljust(23)}</b> ➟ <b>{has_pic}</b> {pic_view}
📊 <b>{'Followers'.ljust(23)}</b> ➟ <b>{profile.followers}</b>
🔄 <b>{'Following'.ljust(23)}</b> ➟ <b>{profile.followees}</b>
📸 <b>{'Total Posts'.ljust(23)}</b> ➟ <b>{profile.mediacount}</b>
📽️ <b>{'Reels'.ljust(23)}</b> ➟ <b>{profile.igtvcount if hasattr(profile, 'igtvcount') else 0}</b>
📖 <b>{'Stories (Highlights)'.ljust(23)}</b> ➟ <b>{profile.highlight_reels if hasattr(profile, 'highlight_reels') else 0}</b>
📝 <b>{'Bio'.ljust(23)}</b> ➟ <code>{(profile.biography[:90] + '...') if profile.biography and len(profile.biography) > 90 else (profile.biography or 'No Bio')}</code>
🌏 <b>{'Country'.ljust(23)}</b> ➟ <b>{country or 'N/A'}</b>
📅 <b>{'Date Joined'.ljust(23)}</b> ➟ <b>{results.get("Date joined", "N/A")}</b>
🔐 <b>{'Account Privacy'.ljust(23)}</b> ➟ <b>{'Private' if profile.is_private else 'Public'}</b>
💌 <b>{'Already Verified'.ljust(23)}</b> ➟ <b>{'Yes' if profile.is_verified else 'No'}</b>
⚕️ <b>{'Business Account'.ljust(23)}</b> ➟ <b>{'Yes' if profile.is_business_account else 'No'}</b>
🔒 <b>{'Verified On'.ljust(23)}</b> ➟ <b>{results.get("Verified On", "N/A")}</b>
🕵️ <b>{'Former Usernames'.ljust(23)}</b> ➟ <b>{results.get("Former usernames", "N/A")}</b>
🔐 <b>{'Reset Email'.ljust(23)}</b> ➟ <code>{reset_email or 'Not Available'}</code>
📧 <b>{'Email Availability'.ljust(23)}</b> ➟ <code>{reset_check}</code>
══════════════════════════════
💎 ✦ <b>Developer</b> ➟ <a href="https://t.me/PrayagRajj">ＰｒａｙａｇＲａｊｊ</a> ✦ 💎
══════════════════════════════
        """.strip() 

        return result_msg

    except Exception as e:
        return f"ERROR Failed to fetch info for {username}. Reason: {str(e)}"
def aol(update, context):
    if not context.args:
        update.message.reply_text(
            "Please provide a username after the command.\nExample: /aol example123"
        )
        return

    username = context.args[0]
    if not username.isalnum():
        update.message.reply_text("Please provide a valid alphanumeric username.")
        return

    result = check_aol_username(username)
    if result is None:
        update.message.reply_text("Sorry, I couldn't check the username right now. Try again later.")
    else:
        # Send reply with Markdown formatting
        update.message.reply_text(
            f"Username *{username}* is {result}",
            parse_mode='Markdown'
        )
def gmail(update, context):
    if not context.args:
        update.message.reply_text(
            "Please provide a username after the command.\nExample: /gmail example123"
        )
        return

    username = context.args[0]
    if not username.isalnum():
        update.message.reply_text("Please provide a valid alphanumeric username.")
        return

    checker = Gm(username)
    result = checker.check()

    if result is None:
        update.message.reply_text("Sorry, I couldn't check the username right now. Try again later.")
    else:
        availability = "✅ Available" if result["available"] else "❌ Taken"
        update.message.reply_text(
            f"Username *{username}@gmail.com* is {availability}",
            parse_mode='Markdown'
        )
def reset_command(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("⚠️ Please provide a username.\nUsage: /reset <instagram_username>")
        return

    username = context.args[0].strip().lstrip("@")
    result = send_recovery_request(username)

    if not result or result[0] in ["No Reset", "Failed", "Error"]:
        reset_contact = "❌ Not Found"
        recovery_type = "Unavailable"
        status = "❌ Failed"
    else:
        raw = result[0]
        if "Email:" in raw:
            reset_contact = raw.replace("Email:", "").strip()
            recovery_type = "📧 Email"
        elif "Phone:" in raw:
            reset_contact = raw.replace("Phone:", "").strip()
            recovery_type = "📱 Phone"
        else:
            reset_contact = raw.strip()
            recovery_type = "ℹ️ Unknown"

        status = "✅ Success"

    message = (
        f"🔁 *Instagram Reset Info*\n"
        f"👤 *Username:* `{username}`\n"
        f"📌 *Status:* `{status}`\n"
        f"📬 *Contact Point:* `{reset_contact}`\n"
        f"🛠️ *Recovery Method:* `{recovery_type}`"
    )

    update.message.reply_text(message, parse_mode="Markdown")


def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("reset", reset_command))
    dp.add_handler(CommandHandler(["info", "infonum"], handle_info_command))
    dp.add_handler(CommandHandler("aol", aol))
    dp.add_handler(CommandHandler("gmail", gmail))
    dp.add_handler(CommandHandler("subscription", subscription_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_info_command))
    print("🤖 Bot is running...ENJOY")
    updater.start_polling()
    updater.idle()
if __name__ == "__main__":
    main()
