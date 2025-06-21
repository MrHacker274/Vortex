import re
import time
import requests
import instaloader
from telegram import Update, ChatAction, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from fake_useragent import UserAgent
import json
from user_agent import generate_user_agent
import uuid
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
def get_username_from_user_id(user_id):
    return f"user{user_id}"
def fetch_instagram_info(username):
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
    'sessionid': '5545662104%3ATSmn4hQ082l5P1%3A2%3AAYcvDY8dpiH3Ow4J3iq1ZHtvUPqL762SncIGuyc3sEI',
    'rur': '"CCO\\0545545662104\\0541781602163:01fe745731b1cc96919b73db50e263c59cf94d463ae2203f9014b6f9321143572eae63b5"',
    'wd': '1160x865',
    }
    headers = {
        'accept': '*/*',
    'accept-language': 'en-US,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'origin': 'https://www.instagram.com',
    'priority': 'u=1, i',
    'referer': 'https://www.instagram.com/zuck/',
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
    'cookie': 'datr=GAgjaB5R_liEM-dpATRTgjMj; ig_did=114B8FDB-7673-4860-A1D8-E88C655B9DD8; dpr=0.8999999761581421; ig_nrcb=1; ps_l=1; ps_n=1; mid=aDaRiAALAAFk8TVh8AGAIMVtWO_F; csrftoken=Pf0Us3q173jfLfTXAurrhCD8uY5KpFlf; ds_user_id=5545662104; sessionid=5545662104%3ATSmn4hQ082l5P1%3A2%3AAYcvDY8dpiH3Ow4J3iq1ZHtvUPqL762SncIGuyc3sEI; rur="CCO\\0545545662104\\0541781602163:01fe745731b1cc96919b73db50e263c59cf94d463ae2203f9014b6f9321143572eae63b5"; wd=1160x865',
    }
    params = {
        'appid': 'com.bloks.www.ig.about_this_account',
    'type': 'app',
    '__bkv': 'b029e4bcdab3e79d470ee0a83b0cbf57b9473dab4bc96d64c3780b7980436e7a',
    }
    data = {
        '__d': 'www',
    '__user': '0',
    '__a': '1',
    '__req': '1q',
    '__hs': '20255.HYP:instagram_web_pkg.2.1...0',
    'dpr': '1',
    '__ccg': 'EXCELLENT',
    '__rev': '1023865060',
    '__s': 'b6yo3f:r9wap4:221x37',
    '__hsi': '7516404270949342347',
    '__dyn': '7xeUjG1mxu1syaxG4Vp41twWwIxu13wvoKewSAx-bwNw9G2Saxa0DU6u3y4o2Gw6QCwjE1EEc87m0yE462mcw5Mx62G5UswoEcE7O2l0Fwqo31w9O1TwQzXw8W58jwGzEaE2iwNwh8lwuEjUlwhEe88o5i7U1oEbUGdG1QwTU9UaQ0z8c86-3u2WE5B08-269wr86C1mgcEed6hEhK2OubK5V89FbxG1oxe6UaUaE2xyUC4o16UsxWaCwHCw',
    '__csr': 'jgmMkgN3BR4Pl5hZaZd4tPWb9OndOl8jW8aDmRGZVBz8NmjQWK8XHmurmAJeO5qnVnFdG_GcWiheGGZaF7GFrgOaipJDWJ6JyO5G8y9FAXjJ4DyJ2k4Gx7C8aGbyVaHlbpTXQhuJbiy4jiKmimlkV8zykcBBV-c-mLiWWVqBUW4UgGHzVoiAqGvwTx6eypp801jd40ix1O1N_z89ElxibJ0em7o4m1-Cl0g8f88k1Bzrbc1myFQaIEcE9E9e9y1cMjolDwARxe1cAoabK0GhpQ8EM8UB7PBx64oog945EkDDz6u4Ge6Eyq0je0NN0178swoU3MwVw2440c2wa64V61BwmmEiigJ4S19g3fyFAawOHx11jx26C1pwmjZ5g2XII-aGmEpwm833wBClw5ixepm1hg4i4A0-A5AUuxalw8y0c0wMBw2_o5e0aVm6pm1kwpe4orgN2U05q208egeU2ygtyo2DAVQ087zUXU420XVUixvF0be4U2Fw3gu0dEU1BRw7fw',
    '__hsdp': 'gcQ8Ix2iPnkLsj6Qx5VCIQeYQ82RbMcAqGPlR5NG22OO96pdkxogFEeuSCIpM8QcNYGmD2fcyGIGAjBwNgJ3CUy4E7qe8UmG9yWUcJ2k8ym5toKi365UvzEiyN8oG2yewwyp9UjGh2ki36UswjFUKh1nwNK8h8pbBKF6SV9999p9viy8pwCAxeq8ykEW2a698mHwDglwRiBXBVeyJ39f-yaquFKFE-uijlV98-FSaBVofoyu2K1ixqEco5S4UGqqEuwlEaQ4ooxOEGu1XgkzEpwxwDgJefx6487WbCyEO4F8kzpUtK0y8eolAG58oxi7K1axG27hCex26V6EtxB0wwAGi4odo98Ocwxzo4iufGEO5A2BG8xl3o-fwLglF3omhE88SqdyHBKiuhAWyUG4oTDgy',
    '__hblp': '4DwjU463_gpwMze0zpoC4qy8hxa0Hp8tAUCnzFUxd3oyEap98-i4EbWAK5opGbye8xaqu48aqyUTh8oLmKqiqm8yUCl1q9x2iexSexaEvyawGVrJeufKi11LzoK4VoRRKegOurDiK2GicyoO0PFQu9ghwmK2u2O15wDyEy2ebAxu58vwg8dE6q0IpEzw861BK4VU6qcgkwDzUeEyiubx62C2O1bKq2i58Su7rxC1KwVxmu2S58uwIwWx_ymqu4pEoqx-9xu8zA2rCwjE9EHCx-78c9VUScxi48rq-azUPwLxuu6kaGdx27k4otKez6FKVponzEhw',
    '__comet_req': '7',
    'fb_dtsg': 'NAfvFnFYAHQSihrJhw_S2MNwUXVSowdxA6nZw-lssMGXpOcEo2gQ9xw:17843671327157124:1748946019',
    'jazoest': '26504',
    'lsd': '0C20psnepYh5AOGu5f1QAb',
    '__spin_r': '1023865060',
    '__spin_b': 'trunk',
    '__spin_t': '1750049244',
    '__crn': 'comet.igweb.PolarisProfilePostsTabRoute',
    'params': f'{{"referer_type":"ProfileMore","target_user_id":{user_id} }}',
    }

    response = requests.post('https://www.instagram.com/async/wbloks/fetch/', params=params, cookies=cookies, headers=headers, data=data)
    matches = re.findall(r'"text":"(.*?)"', response.text)
    return matches[0] if matches else None    

import secrets
import user_agent
import requests
import random
import re
cokANDdata=requests.get('https://login.aol.com/account/create',headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0','accept-language': 'en-US,en;q=0.9',})
AS=cokANDdata.cookies.get_dict()['AS']
A1=cokANDdata.cookies.get_dict()['A1']
A3=cokANDdata.cookies.get_dict()['A3']
A1S=cokANDdata.cookies.get_dict()['A1S']
specData=cokANDdata.text.split('''name="attrSetIndex">
        <input type="hidden" value="''')[1].split(f'" name="specData">')[0]
specId=cokANDdata.text.split('''name="browser-fp-data" id="browser-fp-data" value="" />
        <input type="hidden" value="''')[1].split(f'" name="specId">')[0]
crumb=cokANDdata.text.split('''name="cacheStored">
        <input type="hidden" value="''')[1].split(f'" name="crumb">')[0]
sessionIndex=cokANDdata.text.split('''"acrumb">
        <input type="hidden" value="''')[1].split(f'" name="sessionIndex">')[0]
acrumb=cokANDdata.text.split('''name="crumb">
        <input type="hidden" value="''')[1].split(f'" name="acrumb">')[0]
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
    'gpp': 'DBAA',
        'gpp_sid': '-1',
        'A1':A1,
        'A3':A3,
        'A1S':A1S,
        '__gads': 'ID=c0M0fd00676f0ea1:T='+'4'+':RT='+'5'+':S=ALNI_MaEGaVTSG6nQFkSJ-RnxSZrF5q5XA',
        '__gpi': 'UID=00000cf0e8904e94:T='+'7'+':RT='+'6'+':S=ALNI_MYCzPrYn9967HtpDSITUe5Z4ZwGOQ',
        'cmp': 't='+'0'+'&j=0&u=1---',
        'AS': AS,
    }
    headers = {
    'authority': 'login.aol.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://login.aol.com',
        'referer': f'https://login.aol.com/account/create?specId={specId}&done=https%3A%2F%2Fwww.aol.com',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'x-requested-with': 'XMLHttpRequest',
    }
    params = {
        'validateField': 'userId',
    }
    data = f'browser-fp-data=%7B%22language%22%3A%22en-US%22%2C%22colorDepth%22%3A24%2C%22deviceMemory%22%3A8%2C%22pixelRatio%22%3A1%2C%22hardwareConcurrency%22%3A4%2C%22timezoneOffset%22%3A-60%2C%22timezone%22%3A%22Africa%2FCasablanca%22%2C%22sessionStorage%22%3A1%2C%22localStorage%22%3A1%2C%22indexedDb%22%3A1%2C%22cpuClass%22%3A%22unknown%22%2C%22platform%22%3A%22Win32%22%2C%22doNotTrack%22%3A%22unknown%22%2C%22plugins%22%3A%7B%22count%22%3A5%2C%22hash%22%3A%222c14024bf8584c3f7f63f24ea490e812%22%7D%2C%22canvas%22%3A%22canvas%20winding%3Ayes~canvas%22%2C%22webgl%22%3A1%2C%22webglVendorAndRenderer%22%3A%22Google%20Inc.%20(Intel)~ANGLE%20(Intel%2C%20Intel(R)%20HD%20Graphics%204000%20(0x00000166)%20Direct3D11%20vs_5_0%20ps_5_0%2C%20D3D11)%22%2C%22adBlock%22%3A0%2C%22hasLiedLanguages%22%3A0%2C%22hasLiedResolution%22%3A0%2C%22hasLiedOs%22%3A0%2C%22hasLiedBrowser%22%3A0%2C%22touchSupport%22%3A%7B%22points%22%3A0%2C%22event%22%3A0%2C%22start%22%3A0%7D%2C%22fonts%22%3A%7B%22count%22%3A33%2C%22hash%22%3A%22edeefd360161b4bf944ac045e41d0b21%22%7D%2C%22audio%22%3A%22124.04347527516074%22%2C%22resolution%22%3A%7B%22w%22%3A%221600%22%2C%22h%22%3A%22900%22%7D%2C%22availableResolution%22%3A%7B%22w%22%3A%22860%22%2C%22h%22%3A%221600%22%7D%2C%22ts%22%3A%7B%22serve%22%3A1704793094844%2C%22render%22%3A1704793096534%7D%7D&specId={specId}&cacheStored=&crumb={crumb}&acrumb={acrumb}&sessionIndex={sessionIndex}&done=https%3A%2F%2Fwww.aol.com&googleIdToken=&authCode=&attrSetIndex=0&specData={specData}&multiDomain=&tos0=oath_freereg%7Cus%7Cen-US&firstName=zuck&lastName=zuck&userid-domain=yahoo&userId={username}&password=&mm=&dd=&yyyy=&signup='


    response = requests.post(
        'https://login.aol.com/account/module/create',
        params=params,
        cookies=cookies,
        headers=headers,
        data=data
    )
    return check_availability_from_text(response.text)
def check_yahoo(username):
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

    cookies = {
    'GUCS': 'AWknsyh0',
    'GUC': 'AQEBCAFoSRdoeEIdQwQy&s=AQAAACCB4HIN&g=aEfHog',
    'A1': 'd=AQABBMaWOWgCEL-FOLxgsvlB2W8Ovy55PwIFEgEBCAEXSWh4aFkPyyMA_eMDAAcIxpY5aC55PwI&S=AQAAApTnrAS4ma9896ODHJgQIvo',
    'A3': 'd=AQABBMaWOWgCEL-FOLxgsvlB2W8Ovy55PwIFEgEBCAEXSWh4aFkPyyMA_eMDAAcIxpY5aC55PwI&S=AQAAApTnrAS4ma9896ODHJgQIvo',
    'A1S': 'd=AQABBMaWOWgCEL-FOLxgsvlB2W8Ovy55PwIFEgEBCAEXSWh4aFkPyyMA_eMDAAcIxpY5aC55PwI&S=AQAAApTnrAS4ma9896ODHJgQIvo',
    'AS': 'v=1&s=v5eswj9P&d=A6849191e|RM7R_af.2SqITqVCWEUuU2OsTZQGlvHZQO6ReSHM6JxxzqRwNttPVc.qMBCyzQ3vsi0PkXjsBchfbFvvr2ZGF.abxTZb41oLXF6_U9X0zcu5QL_UMnDMvKtPbWPTD5lPOcvDyLrehwVQl7zx4KXpXGtwRJwNiWTOXvV2CqsEkFMflcIy5ZpAtfGa5t2nplYgrhQOzMJZPofVqhnmQdXjqD4GquENpNV6OVv4f25gSjTvVICOowxkop1SIRsLehEBM0xlsvLYgKVUVV4Ed4FvjnEIWj_9aHOZGj35gv3RgH3UeqiIBAByvO_IAo_60otUrVcuIUZg4g02EASRKbj6o7YV5wtbvAmOAp1zUavHk6ZXgNXCUgRH0t1rbHLxHSEnR27lm5c8JAdaLuGG9eGY1_BpMJbSAoB.orhoZc4qFVuHM_hbWGckZpRTyv5w584MgE8eDZgqz2rkv5xWlhlTJwqJx58bD6Y6CXR9OcQXFYrJXPl1NxQVr1xaYCadabUzV3ZoQj0LZlffSEmUVmtLVm.hh72vU5Sl2Wg6GaDpp_wcJ6RCs.iTQLuXNjjBI5ZTo5BRmavQuuF275j1wAUQpDrqxUQlPlpI_fI7qK9.iKjSdfY9BifanZ5Q6VjH1oAfi8iCPz7ZcNBPYGDxRqJHIm61KQlQo5ts3NWN3nj1.EUdjhLcUqt_m9.rRtfZJP8OueRX.5RMOf8gSpc1mAv0jaJlmiMZTmUpQiZs_9iTHbL8ooDREiJK5hn6NGEH2WLQjo.LfyOJBirPfTnkkU079HG6i5z2qR7eNvLepT6srOLFxOaSf.QJdtOmNpL30IHaUbijM3KkfFa5NtcG40VqzVKAyHQ9I7101S9SBo2q26RK_rJCWzRIneEpaI06VEXSNKn91it9vPHUNs_dDsiLQDuo.TLzsuyI72nW6u6dbh2Yb23tQFwCPg2r1t1qsPRAnM3ujJvyyMYNFxin~A|B68491921|7u_g5jH.2Tpg6gyXmbiOAf2UdsjI6NGgF.mLeybcIo.sr_YTQTKBtmNNLvaPHoCCJQ5xND2zIqkCFQLeaJObaXGPc6P9MhODLWbMQRvZF.5.4.Q86Z62gWrRVeMMhxDF5ON4FlI_mmEVfpVndgMXK8iYeX0l1ssgrIKbqV7m9dLUGILMw0.hPvcC30QYUDxQbe4T2bkBmPqEIc36ECNu.6NfTzu_LltP5b_Z1JCkkKXNanL2k_Clx29IMR64W0c6O41Ewg.G5X.Q6nub_yqYM9.NI13JR5yii3Jw5iiaK3cL6MB5R0Xl6HRNZcdcExosg2hBV1kx_P4yzRA1DRd1fw_FgVRJVCBL0IwuMHq3mUO4T_Z4A6qT6tadtrTa8L9B2qZKgHATFbOsjpocUAeNdRDDU9pMtSlTq8L.emZbgSMbAp1V_5ETYuiQ2uYAKnthpCaNRd4EdePLOfB1c.8iKZitUOHa.uHcotm7112pDfRgr6Nbl05q6nUxoQBgKynyd0X20aXT2GF.oEp6jC2QaFBcZSNeYRZCtOM2VmJLAWfvxrf0s2xZagMhbLjSFwoCOooVIygqgQySZ0x_7t52jgJCW0kn_UY4XqUgkZ3z9epzU0ec81FMWw6RE98CcSd6lQKEdo4ofgVsdnyCN7ZFQOd66nus2Dp9_fJFzupfT8Ia4iaN60WMeqi8gy8rweKt72XqiML4_6m51vcnXJmAiRygy0qL_TnwoPJmc1E4r0lt.YPTmO_eVwQbgHSHTQuYrnj5eLAvguT_I_.Hb0S0IEQa88sNEerHf6eMv3GAPLYo5ADIQi_e1o9HraTdRZ4qwKZ4vW_LQ.ByA80bh2sYRR20ZWlXNg0dvyxb5privgDxkpMkhGUnoVjZdhqqA6uibukRgb14Dn71K.V5CSXDF1ilV6RgGWqzfo3yfgNB6WbL62zEOkiljCbAiPT0zfo8t_avjpxgpg1lM3Ifmgcmvhwgs.Knoac3iRB91QVRPh88taF3PN.hNVy0KV0eMossggxABIRqjh.EYIYicP0d5qEN4276B4liEPZQDl1lT2i.0ZFeURAX4DfKWUWs5tgvfL5kwI_cajbqu_f9tG9huP9SpMGDDWvLAOcAxHzIjsJ0gBWtvh.AyEnXHfA.K7NjQiNyt9k-~A',
    }
    headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://login.yahoo.com',
    'priority': 'u=1, i',
    'referer': 'https://login.yahoo.com/account/create?.lang=en-US&src=homepage&activity=ybar-signin&pspid=2023538075&.done=https%3A%2F%2Fwww.yahoo.com%2F%3Fguccounter%3D1&specId=yidregsimplified&done=https%3A%2F%2Fwww.yahoo.com%2F%3Fguccounter%3D1',
    'sec-ch-ua': '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    'cookie': 'GUCS=AWknsyh0; GUC=AQEBCAFoSRdoeEIdQwQy&s=AQAAACCB4HIN&g=aEfHog; A1=d=AQABBMaWOWgCEL-FOLxgsvlB2W8Ovy55PwIFEgEBCAEXSWh4aFkPyyMA_eMDAAcIxpY5aC55PwI&S=AQAAApTnrAS4ma9896ODHJgQIvo; A3=d=AQABBMaWOWgCEL-FOLxgsvlB2W8Ovy55PwIFEgEBCAEXSWh4aFkPyyMA_eMDAAcIxpY5aC55PwI&S=AQAAApTnrAS4ma9896ODHJgQIvo; A1S=d=AQABBMaWOWgCEL-FOLxgsvlB2W8Ovy55PwIFEgEBCAEXSWh4aFkPyyMA_eMDAAcIxpY5aC55PwI&S=AQAAApTnrAS4ma9896ODHJgQIvo; AS=v=1&s=v5eswj9P&d=A6849191e|RM7R_af.2SqITqVCWEUuU2OsTZQGlvHZQO6ReSHM6JxxzqRwNttPVc.qMBCyzQ3vsi0PkXjsBchfbFvvr2ZGF.abxTZb41oLXF6_U9X0zcu5QL_UMnDMvKtPbWPTD5lPOcvDyLrehwVQl7zx4KXpXGtwRJwNiWTOXvV2CqsEkFMflcIy5ZpAtfGa5t2nplYgrhQOzMJZPofVqhnmQdXjqD4GquENpNV6OVv4f25gSjTvVICOowxkop1SIRsLehEBM0xlsvLYgKVUVV4Ed4FvjnEIWj_9aHOZGj35gv3RgH3UeqiIBAByvO_IAo_60otUrVcuIUZg4g02EASRKbj6o7YV5wtbvAmOAp1zUavHk6ZXgNXCUgRH0t1rbHLxHSEnR27lm5c8JAdaLuGG9eGY1_BpMJbSAoB.orhoZc4qFVuHM_hbWGckZpRTyv5w584MgE8eDZgqz2rkv5xWlhlTJwqJx58bD6Y6CXR9OcQXFYrJXPl1NxQVr1xaYCadabUzV3ZoQj0LZlffSEmUVmtLVm.hh72vU5Sl2Wg6GaDpp_wcJ6RCs.iTQLuXNjjBI5ZTo5BRmavQuuF275j1wAUQpDrqxUQlPlpI_fI7qK9.iKjSdfY9BifanZ5Q6VjH1oAfi8iCPz7ZcNBPYGDxRqJHIm61KQlQo5ts3NWN3nj1.EUdjhLcUqt_m9.rRtfZJP8OueRX.5RMOf8gSpc1mAv0jaJlmiMZTmUpQiZs_9iTHbL8ooDREiJK5hn6NGEH2WLQjo.LfyOJBirPfTnkkU079HG6i5z2qR7eNvLepT6srOLFxOaSf.QJdtOmNpL30IHaUbijM3KkfFa5NtcG40VqzVKAyHQ9I7101S9SBo2q26RK_rJCWzRIneEpaI06VEXSNKn91it9vPHUNs_dDsiLQDuo.TLzsuyI72nW6u6dbh2Yb23tQFwCPg2r1t1qsPRAnM3ujJvyyMYNFxin~A|B68491921|7u_g5jH.2Tpg6gyXmbiOAf2UdsjI6NGgF.mLeybcIo.sr_YTQTKBtmNNLvaPHoCCJQ5xND2zIqkCFQLeaJObaXGPc6P9MhODLWbMQRvZF.5.4.Q86Z62gWrRVeMMhxDF5ON4FlI_mmEVfpVndgMXK8iYeX0l1ssgrIKbqV7m9dLUGILMw0.hPvcC30QYUDxQbe4T2bkBmPqEIc36ECNu.6NfTzu_LltP5b_Z1JCkkKXNanL2k_Clx29IMR64W0c6O41Ewg.G5X.Q6nub_yqYM9.NI13JR5yii3Jw5iiaK3cL6MB5R0Xl6HRNZcdcExosg2hBV1kx_P4yzRA1DRd1fw_FgVRJVCBL0IwuMHq3mUO4T_Z4A6qT6tadtrTa8L9B2qZKgHATFbOsjpocUAeNdRDDU9pMtSlTq8L.emZbgSMbAp1V_5ETYuiQ2uYAKnthpCaNRd4EdePLOfB1c.8iKZitUOHa.uHcotm7112pDfRgr6Nbl05q6nUxoQBgKynyd0X20aXT2GF.oEp6jC2QaFBcZSNeYRZCtOM2VmJLAWfvxrf0s2xZagMhbLjSFwoCOooVIygqgQySZ0x_7t52jgJCW0kn_UY4XqUgkZ3z9epzU0ec81FMWw6RE98CcSd6lQKEdo4ofgVsdnyCN7ZFQOd66nus2Dp9_fJFzupfT8Ia4iaN60WMeqi8gy8rweKt72XqiML4_6m51vcnXJmAiRygy0qL_TnwoPJmc1E4r0lt.YPTmO_eVwQbgHSHTQuYrnj5eLAvguT_I_.Hb0S0IEQa88sNEerHf6eMv3GAPLYo5ADIQi_e1o9HraTdRZ4qwKZ4vW_LQ.ByA80bh2sYRR20ZWlXNg0dvyxb5privgDxkpMkhGUnoVjZdhqqA6uibukRgb14Dn71K.V5CSXDF1ilV6RgGWqzfo3yfgNB6WbL62zEOkiljCbAiPT0zfo8t_avjpxgpg1lM3Ifmgcmvhwgs.Knoac3iRB91QVRPh88taF3PN.hNVy0KV0eMossggxABIRqjh.EYIYicP0d5qEN4276B4liEPZQDl1lT2i.0ZFeURAX4DfKWUWs5tgvfL5kwI_cajbqu_f9tG9huP9SpMGDDWvLAOcAxHzIjsJ0gBWtvh.AyEnXHfA.K7NjQiNyt9k-~A',
    }

    params = {
        'validateField': 'userId',
    }
    data = f'browser-fp-data=%7B%22language%22%3A%22en-US%22%2C%22colorDepth%22%3A24%2C%22deviceMemory%22%3A8%2C%22pixelRatio%22%3A1%2C%22hardwareConcurrency%22%3A3%2C%22timezoneOffset%22%3A-330%2C%22timezone%22%3A%22Asia%2FCalcutta%22%2C%22sessionStorage%22%3A1%2C%22localStorage%22%3A1%2C%22indexedDb%22%3A1%2C%22cpuClass%22%3A%22unknown%22%2C%22platform%22%3A%22Win32%22%2C%22doNotTrack%22%3A%22unknown%22%2C%22plugins%22%3A%7B%22count%22%3A4%2C%22hash%22%3A%229fd2e0f6cbbc12cbd2055f1976c5cbad%22%7D%2C%22canvas%22%3A%22canvas%20winding%3Ayes~canvas%22%2C%22webgl%22%3A1%2C%22webglVendorAndRenderer%22%3A%22Google%20Inc.%20(Intel)~ANGLE%20(Intel%2C%20Intel(R)%20HD%20Graphics%20Direct3D9Ex%20vs_3_0%20ps_3_0%2C%20igdumd64.dll)%22%2C%22adBlock%22%3A0%2C%22hasLiedLanguages%22%3A0%2C%22hasLiedResolution%22%3A0%2C%22hasLiedOs%22%3A0%2C%22hasLiedBrowser%22%3A0%2C%22touchSupport%22%3A%7B%22points%22%3A0%2C%22event%22%3A0%2C%22start%22%3A0%7D%2C%22fonts%22%3A%7B%22count%22%3A29%2C%22hash%22%3A%2290ead5fa1a480b09b5b0239bd273a529%22%7D%2C%22audio%22%3A%22123.991361015047%22%2C%22resolution%22%3A%7B%22w%22%3A%221680%22%2C%22h%22%3A%221050%22%7D%2C%22availableResolution%22%3A%7B%22w%22%3A%221050%22%2C%22h%22%3A%221680%22%7D%2C%22ts%22%3A%7B%22serve%22%3A1749534625138%2C%22render%22%3A1749534626560%7D%7D&specId=yidregsimplified&context=REGISTRATION&cacheStored=&crumb=Xit65ahjkHJ6bNHYETSZQ&acrumb=v5eswj9P&sessionIndex=Qg--&done=https%3A%2F%2Fwww.yahoo.com%2F%3Fguccounter%3D1&googleIdToken=&authCode=&attrSetIndex=0&specData=&deviceCapability=%7B%22pa%22%3A%7B%22status%22%3Afalse%7D%2C%22isWebAuthnSupported%22%3Atrue%7D&tos0=oath_freereg%7Cin%7Cen-IN&multiDomain=&asId=5957bdaa-ef9e-4f01-910c-fbfa76dd6aa1&fingerprintCaptured=&firstName=zuck&lastName=zuck&userid-domain=yahoo&userId={username}&yidDomainDefault=yahoo.com&yidDomain=yahoo.com&password=&mm=&dd=&yyyy=&signup='
    response = requests.post('https://login.yahoo.com/account/module/create', params=params, cookies=cookies, headers=headers, data=data)
    return check_availability_from_text(response.text)
def check_Outlook(username):
    url = "https://signup.live.com/API/CheckAvailableSigninNames"
    cookies = {
    'mkt': 'en-US',
    'mkt1': 'en-US',
    'amsc': 'A9pd8YMIs1weZ0Isc+MXX1J4QBH7lXbIHKDtjZ07IkBEFVO6525LiDaDMYeXwikB0xBBf41JGryAG3CjcOZGmAqs573mJ5pHJKExreZ0Nt/ttxZoE+owVcg5Mgy3Hyjrqd+a9ntspRAVuxvSDY1nWWECJbpk9GaQ153OvzlKaypAOfUPL6J2Tf1xZH4/4wNLSjIEjYl+8UrHMThztrd1t4epzjCXXuLmbm/zDSWLRGLiHNHWK4jbIwUAsGVQB9ylLV7v7jvRL3ieOLu8HkYFDk6krIbfHRHYB+fbD8Qn0vbsfE+vttCCdqTkjfHg9W+qlTr+zuK+aoUw34MWfX1O23yJDsd9SOG7fGVeFOqom+M=:2:3c',
    'MicrosoftApplicationsTelemetryDeviceId': 'e208198f-a506-41d5-adca-1b39c973c995',
    '_pxvid': '10ef2c67-45b4-11f0-8116-221b4e2c3734',
    'MUID': 'c91d3e2e44be4d36b36ce7131a222599',
    'fptctx2': 'taBcrIH61PuCVH7eNCyH0OPzOrGnaCb%252f7mTjN%252fuIW2tjmqx5EG4h0qOw4khA6M8yPuVXaNwZq2GHZv2T2hgQ01ORymKMkiSpkcjGCmNn%252bfTweoXFyvDUFFkOigLUkd5UdLB7a%252b%252fgERqeRCh3dhH3bXid9%252fZTjDA1i0AReva8b%252fHyqrpjCiciBPDUVQo7FH%252fAShY140rMEIOwY4VjYSuy428TOd0dL6wbjgQKI0AlKtltJPTRGvZZyKPL71tcde09TqvDzusjMZJEepM0QCsU4pSsTZYrvMzcl7jPeE57rFcXT82kgvNQz5x8PtdFNdv3z5qHa4ObIUoEet3s7mybig%253d%253d',
    'MSFPC': 'GUID=9cd2a407f17942d5b7f44b221c0a9ce5&HASH=9cd2&LV=202506&V=4&LU=1749530016486',
    '_px3': 'c333167a8fe1f4cf66c47fd0a0f1905e4a9ad39ce9c1aae2f1f1c182a02f5b3b:WMQLENvGmL+hN17z/KiLy6y5XG8RMF1wSEyWuqBlj8X1GFDedkVnU7riZM/n9thwr4bxy+NcbArUzy6RuCgrQg==:1000:ZxFqjsSZ2o9qJkTROjgecATmlHXtBD5DwjZZeQk05Cj788Vt1OTIDUdj++dGwL5niI4xEIKvZcN0ZCgzVpoFtgYOWl4BfDbIgFDY2cp8hqVfcPewK2b9yQ5KzkGSZXuPakmUgr1TMZ1GBxwTtz51FacMZzAb/P9VvwzX0FEoWxQ+bC0p54VwRUDyyoUxmJEZ+T4CgFRors9wIOobpuuamDCSqLZymBUR3532sURq7zQ=',
    'ai_session': 'k/uwW/kRF+kg/QYRwmz+lm|1749533577717|1749534302731',
    }
    headers = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.5',
    'canary': 'JyJ3DOy6lEVg8s9cSkM95VNJvbm0QEZgNKWKgNOfY0tqFG/2/vHaDKjj4K3gZ8l4aJx3jbf2Hfe+5R6GibsVPy/hgJ/Vnx/8bwei4doIHiuBJFy/gQgD5tNGoHHum1NJJix4/nOCElN3rTVHVu21GlTJyQxj6pDOt/uUVjYI4G8vabOAMNKubrSOdPf87gRSXrtVz3PQwNezDep+rhyaPrAx5gq4jfGdVnZ2eQ1f2/E7ERAC8FTx1KjAnB6HyN5t:2:3c',
    'client-request-id': '5266376b2a3c214445564e543a0be83b',
    'content-type': 'application/json; charset=utf-8',
    'correlationid': '5266376b2a3c214445564e543a0be83b',
    'hpgact': '0',
    'hpgid': '200225',
    'origin': 'https://signup.live.com',
    'priority': 'u=1, i',
    'referer': 'https://signup.live.com/signup?sru=https%3a%2f%2flogin.live.com%2foauth20_authorize.srf%3flc%3d1033%26client_id%3d9199bf20-a13f-4107-85dc-02114787ef48%26cobrandid%3dab0455a0-8d03-46b9-b18b-df2f57b9e44c%26mkt%3dEN-US%26opid%3d41670EBB54EA78C0%26opidt%3d1749530008%26uaid%3d5266376b2a3c214445564e543a0be83b%26contextid%3d3F9EEF61C9DA5A78%26opignore%3d1&mkt=EN-US&uiflavor=web&fl=dob%2cflname%2cwld&cobrandid=ab0455a0-8d03-46b9-b18b-df2f57b9e44c&client_id=9199bf20-a13f-4107-85dc-02114787ef48&uaid=5266376b2a3c214445564e543a0be83b&suc=9199bf20-a13f-4107-85dc-02114787ef48&fluent=2&lic=1',
    'sec-ch-ua': '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'cookie': 'mkt=en-US; mkt1=en-US; amsc=A9pd8YMIs1weZ0Isc+MXX1J4QBH7lXbIHKDtjZ07IkBEFVO6525LiDaDMYeXwikB0xBBf41JGryAG3CjcOZGmAqs573mJ5pHJKExreZ0Nt/ttxZoE+owVcg5Mgy3Hyjrqd+a9ntspRAVuxvSDY1nWWECJbpk9GaQ153OvzlKaypAOfUPL6J2Tf1xZH4/4wNLSjIEjYl+8UrHMThztrd1t4epzjCXXuLmbm/zDSWLRGLiHNHWK4jbIwUAsGVQB9ylLV7v7jvRL3ieOLu8HkYFDk6krIbfHRHYB+fbD8Qn0vbsfE+vttCCdqTkjfHg9W+qlTr+zuK+aoUw34MWfX1O23yJDsd9SOG7fGVeFOqom+M=:2:3c; MicrosoftApplicationsTelemetryDeviceId=e208198f-a506-41d5-adca-1b39c973c995; _pxvid=10ef2c67-45b4-11f0-8116-221b4e2c3734; MUID=c91d3e2e44be4d36b36ce7131a222599; fptctx2=taBcrIH61PuCVH7eNCyH0OPzOrGnaCb%252f7mTjN%252fuIW2tjmqx5EG4h0qOw4khA6M8yPuVXaNwZq2GHZv2T2hgQ01ORymKMkiSpkcjGCmNn%252bfTweoXFyvDUFFkOigLUkd5UdLB7a%252b%252fgERqeRCh3dhH3bXid9%252fZTjDA1i0AReva8b%252fHyqrpjCiciBPDUVQo7FH%252fAShY140rMEIOwY4VjYSuy428TOd0dL6wbjgQKI0AlKtltJPTRGvZZyKPL71tcde09TqvDzusjMZJEepM0QCsU4pSsTZYrvMzcl7jPeE57rFcXT82kgvNQz5x8PtdFNdv3z5qHa4ObIUoEet3s7mybig%253d%253d; MSFPC=GUID=9cd2a407f17942d5b7f44b221c0a9ce5&HASH=9cd2&LV=202506&V=4&LU=1749530016486; _px3=c333167a8fe1f4cf66c47fd0a0f1905e4a9ad39ce9c1aae2f1f1c182a02f5b3b:WMQLENvGmL+hN17z/KiLy6y5XG8RMF1wSEyWuqBlj8X1GFDedkVnU7riZM/n9thwr4bxy+NcbArUzy6RuCgrQg==:1000:ZxFqjsSZ2o9qJkTROjgecATmlHXtBD5DwjZZeQk05Cj788Vt1OTIDUdj++dGwL5niI4xEIKvZcN0ZCgzVpoFtgYOWl4BfDbIgFDY2cp8hqVfcPewK2b9yQ5KzkGSZXuPakmUgr1TMZ1GBxwTtz51FacMZzAb/P9VvwzX0FEoWxQ+bC0p54VwRUDyyoUxmJEZ+T4CgFRors9wIOobpuuamDCSqLZymBUR3532sURq7zQ=; ai_session=k/uwW/kRF+kg/QYRwmz+lm|1749533577717|1749534302731',
    }
    json_data = {
    'includeSuggestions': True,
    'signInName': f'{username}@outlook.com',
    'uiflvr': 1001,
    'scid': 100118,
    'uaid': '5266376b2a3c214445564e543a0be83b',
    'hpgid': 200225,
    }
    try:
        response = requests.post(url, headers=headers, json=json_data,cookies=cookies, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("isAvailable") == True:
            return "✅ Available"
        else:
            return "❌ Taken"
    except:
        return "error"
def check_hotmail(username):
    url = "https://signup.live.com/API/CheckAvailableSigninNames"
    cookies = {
    'mkt': 'en-US',
    'mkt1': 'en-US',
    'amsc': 'A9pd8YMIs1weZ0Isc+MXX1J4QBH7lXbIHKDtjZ07IkBEFVO6525LiDaDMYeXwikB0xBBf41JGryAG3CjcOZGmAqs573mJ5pHJKExreZ0Nt/ttxZoE+owVcg5Mgy3Hyjrqd+a9ntspRAVuxvSDY1nWWECJbpk9GaQ153OvzlKaypAOfUPL6J2Tf1xZH4/4wNLSjIEjYl+8UrHMThztrd1t4epzjCXXuLmbm/zDSWLRGLiHNHWK4jbIwUAsGVQB9ylLV7v7jvRL3ieOLu8HkYFDk6krIbfHRHYB+fbD8Qn0vbsfE+vttCCdqTkjfHg9W+qlTr+zuK+aoUw34MWfX1O23yJDsd9SOG7fGVeFOqom+M=:2:3c',
    'MicrosoftApplicationsTelemetryDeviceId': 'e208198f-a506-41d5-adca-1b39c973c995',
    '_pxvid': '10ef2c67-45b4-11f0-8116-221b4e2c3734',
    'MUID': 'c91d3e2e44be4d36b36ce7131a222599',
    'fptctx2': 'taBcrIH61PuCVH7eNCyH0OPzOrGnaCb%252f7mTjN%252fuIW2tjmqx5EG4h0qOw4khA6M8yPuVXaNwZq2GHZv2T2hgQ01ORymKMkiSpkcjGCmNn%252bfTweoXFyvDUFFkOigLUkd5UdLB7a%252b%252fgERqeRCh3dhH3bXid9%252fZTjDA1i0AReva8b%252fHyqrpjCiciBPDUVQo7FH%252fAShY140rMEIOwY4VjYSuy428TOd0dL6wbjgQKI0AlKtltJPTRGvZZyKPL71tcde09TqvDzusjMZJEepM0QCsU4pSsTZYrvMzcl7jPeE57rFcXT82kgvNQz5x8PtdFNdv3z5qHa4ObIUoEet3s7mybig%253d%253d',
    '_px3': '07fc421b7033f52142f26a41c52c9204cb0a62d7d78ed2b23f78065dabb57fdb:PxG8MhhBx0wnyiskfgnxlgVyZpgfCFqlLJa1dBFTBDeWEns9GzSvMTkheUhl+UAq72zg3lyftXG+YZ0zhFyW4Q==:1000:7yRLpjzHAoyPssSSWqZvuveMo9wyhx0Htq4mATYQ9FttndS8YDCiR/Jv55fRzPmgFeCHszst69juWBRedJITWeLoqD8xgL7/Zwmu3m1nDDtrbGpeZ6/ZYkKgsoJAmSUA7O82jYEfQsfGyTV9BHDLkSAT7pX1/jZfdKskfbcLzLQQGsoOaVLrEvET7RrL/Ta0l0L1NPchzM1Xa8kPa0mihEnpH0hNWl74uCfWxQUNxRM=',
    '_pxde': '1835c47dc29d3b44f1c0e95317b68d68a38f32d9a1f0d07911261e9ed60729c0:eyJ0aW1lc3RhbXAiOjE3NDk1MzAwMTU4MzcsImZfa2IiOjB9',
    'MSFPC': 'GUID=9cd2a407f17942d5b7f44b221c0a9ce5&HASH=9cd2&LV=202506&V=4&LU=1749530016486',
    'ai_session': 'nQFlLO01vWFvOnUdj2oEzE|1749530012894|1749530169060',
    }
    headers = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.5',
    'canary': 'BUaG3MNOM4oYxVkFPtHJo5kh9k/e089tnIZv01H4MSwNxMj1Y75N/29Av4GNffog8iLjTMrfN3E0VZG+Ro1rcfe1SrIgfyR8KuLnjO5OQwHcZl48YutF6U8zlPgo7fg976esrT7MgxdQaTf+HizkKbWsbVPIllPFuBv9YCBEQ1zlZprMGLwsG7jzys2GAf6gCrd+Z8dGvWUMBiibk9qmozapCzztdyZGHHs2FVhSpP6DAfjfie1LvRqit7YTy990:2:3c',
    'client-request-id': '5266376b2a3c214445564e543a0be83b',
    'content-type': 'application/json; charset=utf-8',
    'correlationid': '5266376b2a3c214445564e543a0be83b',
    'hpgact': '0',
    'hpgid': '200225',
    'origin': 'https://signup.live.com',
    'priority': 'u=1, i',
    'referer': 'https://signup.live.com/signup?sru=https%3a%2f%2flogin.live.com%2foauth20_authorize.srf%3flc%3d1033%26client_id%3d9199bf20-a13f-4107-85dc-02114787ef48%26cobrandid%3dab0455a0-8d03-46b9-b18b-df2f57b9e44c%26mkt%3dEN-US%26opid%3d41670EBB54EA78C0%26opidt%3d1749530008%26uaid%3d5266376b2a3c214445564e543a0be83b%26contextid%3d3F9EEF61C9DA5A78%26opignore%3d1&mkt=EN-US&uiflavor=web&fl=dob%2cflname%2cwld&cobrandid=ab0455a0-8d03-46b9-b18b-df2f57b9e44c&client_id=9199bf20-a13f-4107-85dc-02114787ef48&uaid=5266376b2a3c214445564e543a0be83b&suc=9199bf20-a13f-4107-85dc-02114787ef48&fluent=2&lic=1',
    'sec-ch-ua': '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'cookie': 'mkt=en-US; mkt1=en-US; amsc=A9pd8YMIs1weZ0Isc+MXX1J4QBH7lXbIHKDtjZ07IkBEFVO6525LiDaDMYeXwikB0xBBf41JGryAG3CjcOZGmAqs573mJ5pHJKExreZ0Nt/ttxZoE+owVcg5Mgy3Hyjrqd+a9ntspRAVuxvSDY1nWWECJbpk9GaQ153OvzlKaypAOfUPL6J2Tf1xZH4/4wNLSjIEjYl+8UrHMThztrd1t4epzjCXXuLmbm/zDSWLRGLiHNHWK4jbIwUAsGVQB9ylLV7v7jvRL3ieOLu8HkYFDk6krIbfHRHYB+fbD8Qn0vbsfE+vttCCdqTkjfHg9W+qlTr+zuK+aoUw34MWfX1O23yJDsd9SOG7fGVeFOqom+M=:2:3c; MicrosoftApplicationsTelemetryDeviceId=e208198f-a506-41d5-adca-1b39c973c995; _pxvid=10ef2c67-45b4-11f0-8116-221b4e2c3734; MUID=c91d3e2e44be4d36b36ce7131a222599; fptctx2=taBcrIH61PuCVH7eNCyH0OPzOrGnaCb%252f7mTjN%252fuIW2tjmqx5EG4h0qOw4khA6M8yPuVXaNwZq2GHZv2T2hgQ01ORymKMkiSpkcjGCmNn%252bfTweoXFyvDUFFkOigLUkd5UdLB7a%252b%252fgERqeRCh3dhH3bXid9%252fZTjDA1i0AReva8b%252fHyqrpjCiciBPDUVQo7FH%252fAShY140rMEIOwY4VjYSuy428TOd0dL6wbjgQKI0AlKtltJPTRGvZZyKPL71tcde09TqvDzusjMZJEepM0QCsU4pSsTZYrvMzcl7jPeE57rFcXT82kgvNQz5x8PtdFNdv3z5qHa4ObIUoEet3s7mybig%253d%253d; _px3=07fc421b7033f52142f26a41c52c9204cb0a62d7d78ed2b23f78065dabb57fdb:PxG8MhhBx0wnyiskfgnxlgVyZpgfCFqlLJa1dBFTBDeWEns9GzSvMTkheUhl+UAq72zg3lyftXG+YZ0zhFyW4Q==:1000:7yRLpjzHAoyPssSSWqZvuveMo9wyhx0Htq4mATYQ9FttndS8YDCiR/Jv55fRzPmgFeCHszst69juWBRedJITWeLoqD8xgL7/Zwmu3m1nDDtrbGpeZ6/ZYkKgsoJAmSUA7O82jYEfQsfGyTV9BHDLkSAT7pX1/jZfdKskfbcLzLQQGsoOaVLrEvET7RrL/Ta0l0L1NPchzM1Xa8kPa0mihEnpH0hNWl74uCfWxQUNxRM=; _pxde=1835c47dc29d3b44f1c0e95317b68d68a38f32d9a1f0d07911261e9ed60729c0:eyJ0aW1lc3RhbXAiOjE3NDk1MzAwMTU4MzcsImZfa2IiOjB9; MSFPC=GUID=9cd2a407f17942d5b7f44b221c0a9ce5&HASH=9cd2&LV=202506&V=4&LU=1749530016486; ai_session=nQFlLO01vWFvOnUdj2oEzE|1749530012894|1749530169060',
    }
    json_data = {
    'includeSuggestions': True,
    'signInName': f'{username}@hotmail.com',
    'uiflvr': 1001,
    'scid': 100118,
    'uaid': '5266376b2a3c214445564e543a0be83b',
    'hpgid': 200225,
    }
    try:
        response = requests.post(url, headers=headers, json=json_data,cookies=cookies, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("isAvailable") == True:
            return "✅ Available"
        else:
            return "❌ Taken"
    except:
        return "error"

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
def check_gmail(username):
    try:
        gmail_checker = Gm(username)
        result = gmail_checker.check()

        if result is None:
            return "Error"
        if result["available"] == True:
            return "✅ Available"
        else:
            return "❌ Taken"
    except:
        return "Error"
        
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
        ("Method 7", method_7),
        ("Method 8", method_8)
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
    try:
        url = "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/"
        headers = {
            "accept": "*/*",
            "accept-language": "tr-TR,tr;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "cookie": "csrftoken=BbJnjd.Jnw20VyXU0qSsHLV; mid=ZpZMygABAAH0176Z6fWvYiNly3y2; ig_did=BBBA0292-07BC-49C8-ACF4-AE242AE19E97; datr=ykyWZhA9CacxerPITDOHV5AE; ig_nrcb=1; dpr=2.75; wd=393x466",
            "origin": "https://www.instagram.com",
            "referer": "https://www.instagram.com/accounts/password/reset/?source=fxcal",
            "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; M2101K786) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "x-asbd-id": "129477",
            "x-csrftoken": "BbJnjd.Jnw20VyXU0qSsHLV",
            "x-ig-app-id": "1217981644879628",
            "x-ig-www-claim": "0",
            "x-instagram-ajax": "1015181662",
            "x-requested-with": "XMLHttpRequest"
        }

        data = {
            "email_or_username": email_or_username,
            "flow": "fxcal"
        }

        res = requests.post(url, headers=headers, data=data).text
        match = re.search(r'lütfen (.*?) adresine', res)
        if match:
            contact = match.group(1)
            return f"Email: {contact}" if "@" in contact else f"Phone: {contact}"
        return "No Reset"
    except:
        return "Error"

def method_2(email_or_username):
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

def method_3(email_or_username):
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
def method_4(email_or_username):
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
def method_5(email_or_username):
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
def method_6(email_or_username):
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
def method_7(email_or_username):
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
def method_8(email_or_username):
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
def lookup_instagram(username):
    uid_val = str(uuid.uuid4())
    token = uuid.uuid4().hex * 2
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "i.instagram.com",
        "Connection": "Keep-Alive",
        "User-Agent": generate_user_agent(),
        "Cookie": f"mid={uuid.uuid4()}; csrftoken={token}",
        "Accept-Language": "en-US",
        "X-IG-Capabilities": "AQ==",
    }
    data = {
        "q": username,
        "device_id": f"android-{uid_val}",
        "guid": uid_val,
        "_csrftoken": token
    }
    try:
        response = requests.post("https://i.instagram.com/api/v1/users/lookup/", headers=headers, data=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
import re
import pycountry

def name_to_flag(country_name):
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            for c in pycountry.countries:
                if country_name.lower() in c.name.lower():
                    country = c
                    break
        if not country:
            return "🏳️"  # Unknown flag

        code = country.alpha_2.upper()
        flag = ''.join(chr(127397 + ord(c)) for c in code)
        return flag
    except:
        return "🏳️"
    
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
    'sessionid': '5545662104%3ATSmn4hQ082l5P1%3A2%3AAYdHDzA1tyszVuFGKVB1B10CO6N-12_HYlOGD5v5Yd0',
    'wd': '1160x865',
    'rur': '"CLN\\0545545662104\\0541781843768:01fe6f6cebaf9f776a2c7d8112ce2e69cbdd41045ef1aae9fa26461f7ffda69250116b44"',
        }
        headers = {
           'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
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
    'cookie': 'datr=GAgjaB5R_liEM-dpATRTgjMj; ig_did=114B8FDB-7673-4860-A1D8-E88C655B9DD8; dpr=0.8999999761581421; ig_nrcb=1; ps_l=1; ps_n=1; mid=aDaRiAALAAFk8TVh8AGAIMVtWO_F; csrftoken=Pf0Us3q173jfLfTXAurrhCD8uY5KpFlf; ds_user_id=5545662104; sessionid=5545662104%3ATSmn4hQ082l5P1%3A2%3AAYdHDzA1tyszVuFGKVB1B10CO6N-12_HYlOGD5v5Yd0; wd=1160x865; rur="CLN\\0545545662104\\0541781843768:01fe6f6cebaf9f776a2c7d8112ce2e69cbdd41045ef1aae9fa26461f7ffda69250116b44"',
    }
        params = {
            'appid': 'com.bloks.www.ig.about_this_account',
    'type': 'app',
    '__bkv': 'b029e4bcdab3e79d470ee0a83b0cbf57b9473dab4bc96d64c3780b7980436e7a',
        }
        data = {
            '__d': 'www',
    '__user': '0',
    '__a': '1',
    '__req': '2p',
    '__hs': '20258.HYP:instagram_web_pkg.2.1...0',
    'dpr': '1',
    '__ccg': 'EXCELLENT',
    '__rev': '1023998261',
    '__s': 'gcaoy7:wa5j8m:1tv631',
    '__hsi': '7517513604345486152',
    '__dyn': '7xeUjG1mxu1syUbFp41twWwIxu13wvoKewSAwHwNw9G2S7o2vwpUe8hw2nVE4W0qa0FE2awgo9oO0n24oaEnxO1ywOwv89k2C1Fwc60D87u3ifK0EUjwGzEaE2iwNwmE7G4-5o4q3y1Sw62wLyESE7i3vwDwHg2cwMwrUdUbGwmk0zU8oC1Iwqo5p0OwUQp1yUb8jK5V8aUuwm8jxK2K2G0EoK9x60hK78apEaU',
    '__csr': 'giEl1p3cl3I9P-RR9cPFsR8AJb8Bqh5OR8KSyyF5DKSm-ABx5dARigOuF9ntaBizdqZoijWHHBVp6cQmFtKQA9AJm88iGyUGmaUCEjUgCUkBz9rypoKqFDzayVrxjAiUx95AolCKXCUC8BHiytbByO7BCAAxOiWCxTAyqAxaqbyEKh1uHUKUigmwBAw056EDw3ipZw4txe0Zo44ES2p0ExO2W2O2B8QXAWxkw3-wPyo2jgkgkzHy40dHwto0oewa5xi0Z8kCw5bwJCkUcA0CqgW0Qm1Kyqybh1g0Cgx9Ub8xk2Kpw4-ppQ0fow0vzo0l-w0E2w',
    '__hsdp': 'ge48bftl92kx3MFdFAgyAwJoJkkkD7Ob0LVxF4BieMB4iPhy866u4gzAEno62NojzU-axqE413Cq3G2Z2u9Ayy0Ux67mu8cEZei9wXJ540i898uzE4qfUqwIDwgo2mz89awXxW0Vo98lwaq3a0iW4o0M60z8vxm586u1Bg9U2Dwho2iw860SV82ZP1m2Lo5C0SUe85G3C6UnDyqa1mG1_wDwnEqwj8O',
    '__hblp': '4zU4W3a1Cx_CG2i1vwAxucG8AWxa16w8qm5ogKfyp9Q2Om8zE4au8Az94ayaAUC6U4SaBBAgKA-EC7EsyEa89EkBwEzK3e9CGuLxB3UsDwgo7-eG4p8vCKq4U9FECufU2YzE998gwNwt8cE19AWByU4u0x986i0oe16waO5oWm7U4uu1tgtyoK1zwKy84m1bwCx-221wwdKi0LsMlwHS3q2a19wg851122q223C4U8-EoxuuqGabwtEd88u2m1uxdAwNz8Scw',
    '__comet_req': '7',
    'fb_dtsg': 'NAfuyDM2oRqyvjWSgcz2RQObmALutJ7sblUy-srQoA9Y0zlZZc6KFig:17843671327157124:1748946019',
    'jazoest': '26523',
    'lsd': 'Mm1Nq-s3RdmTyzYOnmqVQ5',
    '__spin_r': '1023998261',
    '__spin_b': 'trunk',
    '__spin_t': '1750307531',
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
        flag = name_to_flag(country)
        result = send_recovery_request(username)
        reset_email = result[0].replace("Email: ", "").replace("Phone: ", "").strip() if result and result[0] not in ["No Reset", "Failed", "Error"] else "Not Found"
        result = check_aol_username(username)
        Yahoo = check_yahoo(username)
        hotmail = check_hotmail(username)
        Outlook = check_Outlook(username)
        gmail_checker = Gm(username)
        gmail_result = gmail_checker.check()
        reset_check = "🔐 Reset not available"
        lookup_result = lookup_instagram(profile.username)
        email = lookup_result.get("obfuscated_email")
        phone = lookup_result.get("obfuscated_phone")
        if email and phone:
            linked_info = "Email and Phone"
        elif email:
            linked_info = "Email"
        elif phone:
            linked_info = "Phone"
        else:
            linked_info = "Not Linked"
        if reset_email and username:
            if reset_email.startswith("+"):
                reset_check = "📱 Phone Number Reset"
            elif "@" in reset_email:
                visible = reset_email.split("@")[0]
                domain = reset_email.split("@")[1].lower()
                first_visible = visible[0]
                last_visible = visible[-1]
                
                if username[0].lower() == first_visible.lower() and username[-1].lower() == last_visible.lower():
                    if "gmail" in domain:
                        if gmail_result is None:
                            reset_check = "❌ Unable to check Gmail"
                        elif gmail_result.get("available"):
                            reset_check = "Gmail is ✅ Available"
                        else:
                            reset_check = "Gmail is ❌ Taken"
                    elif "a**" in domain or "aol" in domain.lower():
                        reset_check = f"AOL is {result}"
                    elif "hotmail" in domain:
                        reset_check = f"Hotmail is {hotmail}"
                    elif "outlook" in domain:
                        reset_check = f"Outlook is {Outlook}"
                    elif "yahoo" in domain:
                        reset_check = f"Yahoo is {Yahoo}"
                    else:
                        reset_check = "Unknown domain"
                else:
                    reset_check = "🔐 Reset is different"
        result_msg = f"""
══════════════════════════════        
🌟 𝗜ɢ 𝗙ᴇᴛᴄʜᴇʀ 𝗙ʀᴏᴍ <b>ᎮᗯᑎᗩGƐ | Ѵᴏʀᴛᴇx •</b> 🌟       
══════════════════════════════
✨ <b>{'Username'.ljust(23)}</b> ➟ <code>{profile.username}</code>
📡  <b>{'Name'.ljust(23)}</b> ➟ <code>{profile.full_name or 'N/A'}</code>
🆔 <b>{'User ID'.ljust(23)}</b> ➟ <code>{profile.userid}</code>
🔗 <b>{'Profile Link'.ljust(23)}</b> ➟ <a href="https://www.instagram.com/{profile.username}">Click Here</a>
👤 <b>{'Profile Picture'.ljust(23)}</b> ➟ {"<a href='" + profile.profile_pic_url + "'>📷 View</a>" if profile.profile_pic_url else 'Not Available'}
📊 <b>{'Followers'.ljust(23)}</b> ➟ <b>{profile.followers}</b>
🔄 <b>{'Following'.ljust(23)}</b> ➟ <b>{profile.followees}</b>
📸 <b>{'Total Posts'.ljust(23)}</b> ➟ <b>{profile.mediacount}</b>
📽️ <b>{'Reels'.ljust(23)}</b> ➟ <b>{profile.igtvcount if hasattr(profile, 'igtvcount') else 0}</b>
📖 <b>{'Stories (Highlights)'.ljust(23)}</b> ➟ <b>{profile.highlight_reels if hasattr(profile, 'highlight_reels') else 0}</b>
📝 <b>{'Bio'.ljust(23)}</b> ➟ <code>{(profile.biography[:90] + '...') if profile.biography and len(profile.biography) > 90 else (profile.biography or 'No Bio')}</code>
🌏 <b>{'Country'.ljust(23)}</b> ➟ <b>{flag}{country or 'N/A'}</b>
📅 <b>{'Date Joined'.ljust(23)}</b> ➟ <b>{results.get("Date joined", "N/A")}</b>
🔐 <b>{'Account Privacy'.ljust(23)}</b> ➟ <b>{'Private' if profile.is_private else 'Public'}</b>
💌 <b>{'Already Verified'.ljust(23)}</b> ➟ <b>{'Yes' if profile.is_verified else 'No'}</b>
⚕️ <b>{'Business Account'.ljust(23)}</b> ➟ <b>{'Yes' if profile.is_business_account else 'No'}</b>
🔒 <b>{'Verified On'.ljust(23)}</b> ➟ <b>{results.get("Verified On", "N/A")}</b>
🕵️ <b>{'Former Usernames'.ljust(23)}</b> ➟ <b>{results.get("Former usernames", "N/A")}</b>
🛡️ <b>{'Linked With'.ljust(23)}</b> ➟ <b>{linked_info}</b>
🔐 <b>{'Reset Email'.ljust(23)}</b> ➟ <code>{reset_email or 'Not Available'}</code>
📧 <b>{'Email Availability'.ljust(23)}</b> ➟ <code>{reset_check}</code>
══════════════════════════════
💎 ✦ <b>Developer</b> ➟ <a href="https://t.me/PrayagRajj">ＰｒａｙａｇＲａｊｊ</a> ✦ 💎
══════════════════════════════
        """.strip() 

        return result_msg

    except Exception as e:
        return f"ERROR Failed to fetch info for {username}. Reason: {str(e)}"

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
        reset_contact = raw.strip()
        status = "✅ Success"

        # Smart domain-based recovery method detection
        if "Email:" in raw:
            email = raw.replace("Email:", "").strip().lower()
            reset_contact = email
            if "@gmail" in email:
                recovery_type = "📧 Gmail"
            elif "@a**" in email:
                recovery_type = "📧 AOL"
            elif "@hotmail" in email:
                recovery_type = "📧 Hotmail"
            elif "@yahoo" in email:
                recovery_type = "📧 Yahoo"
            elif "@outlook" in email:
                recovery_type = "📧 Outlook"
            else:
                recovery_type = "📧 Email"
        elif "Phone:" in raw:
            reset_contact = raw.replace("Phone:", "").strip()
            recovery_type = "📱 Phone"
        else:
            recovery_type = "ℹ️ Unknown"

    message = (
        f"🔁 *Instagram Reset Info*\n"
        f"👤 *Username:* `{username}`\n"
        f"📌 *Status:* `{status}`\n"
        f"📬 *Contact Point:* `{reset_contact}`\n"
        f"🛠️ *Recovery Method:* `{recovery_type}`"
    )

    update.message.reply_text(message, parse_mode="Markdown")

def is_valid_username(username):
    return re.fullmatch(r'^[a-zA-Z0-9_.]+$', username) is not None

# === AOL ===
def aol(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /aol <username>")
        return

    username = context.args[0]
    if not is_valid_username(username):
        update.message.reply_text("Username can only contain letters, numbers, underscores (_) and dots (.)")
        return

    update.message.chat.send_action(ChatAction.TYPING)
    result = check_aol_username(username)

    if result is None:
        update.message.reply_text("❌ Couldn't check the username right now. Try again later.")
    else:
        update.message.reply_text(
            f"🔎 Username *{username}@aol.com* is {result}",
            parse_mode='Markdown'
        )

def yahoo(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /yahoo <username>")
        return

    username = context.args[0]
    if not is_valid_username(username):
        update.message.reply_text("Username can only contain letters, numbers, underscores (_) and dots (.)")
        return

    update.message.chat.send_action(ChatAction.TYPING)
    result = check_yahoo(username)

    if result is None:
        update.message.reply_text("❌ Couldn't check the username right now. Try again later.")
    else:
        update.message.reply_text(
            f"🔎 Username *{username}@YAHOO.com* is {result}",
            parse_mode='Markdown'
        )

# === Gmail ===
def gmail(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /gmail <username>")
        return

    username = context.args[0]
    if not is_valid_username(username):
        update.message.reply_text("Username can only contain letters, numbers, underscores (_) and dots (.)")
        return

    update.message.chat.send_action(ChatAction.TYPING)
    checker = Gm(username)
    result = checker.check()

    if result is None:
        update.message.reply_text("❌ Couldn't check the username right now. Try again later.")
    else:
        availability = "✅ Available" if result.get("available") else "❌ Taken"
        update.message.reply_text(
            f"🔎 Username *{username}@gmail.com* is {availability}",
            parse_mode='Markdown'
        )

# === Hotmail ===
def hotmail(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /hotmail <username>")
        return

    username = context.args[0]
    if not is_valid_username(username):
        update.message.reply_text("Username can only contain letters, numbers, underscores (_) and dots (.)")
        return

    update.message.chat.send_action(ChatAction.TYPING)
    result = check_hotmail(username)

    if result == "error":
        update.message.reply_text("❌ Something went wrong. Try again.")
    else:
        update.message.reply_text(
            f"🔎 Username *{username}@hotmail.com* is {result}",
            parse_mode='Markdown'
        )

# === Outlook ===
def outlook(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /outlook <username>")
        return

    username = context.args[0]
    if not is_valid_username(username):
        update.message.reply_text("Username can only contain letters, numbers, underscores (_) and dots (.)")
        return

    update.message.chat.send_action(ChatAction.TYPING)
    result = check_Outlook(username)

    if result == "error":
        update.message.reply_text("❌ Something went wrong. Try again.")
    else:
        update.message.reply_text(
            f"🔎 Username *{username}@outlook.com* is {result}",
            parse_mode='Markdown'
        )
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
import time
OWNER_ID = 5851767478  # 🔁 Replace with your actual Telegram ID

def status_command(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("⛔ You are not authorized to use this command.")
        return

    overall_start = time.time()
    username = "ansh"
    results = []

    # --- /info check ---
    try:
        start = time.time()
        info = fetch_instagram_info(username)  # HTML string
        duration = round(time.time() - start, 2)

        if "United States" in info:
            results.append(f"✅ /info is working ({duration} sec)")
        else:
            results.append(f"❌ /info failed — Country is not United States ({duration} sec)")
    except Exception as e:
        results.append(f"❌ /info error — {str(e)}")

    # --- Email domain services ---
    services = {
        "gmail": check_gmail,
        "aol": check_aol_username,
        "yahoo": check_yahoo,
        "hotmail": check_hotmail,
        "outlook": check_Outlook
    }

    for name, func in services.items():
        try:
            start = time.time()
            result = func(username).strip()
            duration = round(time.time() - start, 2)

            if result == "❌ Taken":
                results.append(f"✅ /{name} is working ({duration} sec)")
            else:
                results.append(f"❌ /{name} failed — returned '{result}' ({duration} sec)")
        except Exception as e:
            results.append(f"❌ /{name} error — {str(e)}")

    total_time = round(time.time() - overall_start, 2)

    status_report = (
        f"<b>📊 Status Check for username: <code>{username}</code></b>\n\n"
        + "\n".join(results)
        + f"\n\n⏱ <b>Total Time Taken:</b> <code>{total_time} sec</code>"
    )

    update.message.reply_text(status_report, parse_mode=ParseMode.HTML)


# === VORTEX MARKET TELEGRAM BOT ===
# Description: Telegram bot to handle /sell command for Instagram accounts.
# Stores info in GitHub CSV files inside "Vortex" repo.
# Files: Item storage.csv (stock), Sellerinfo.csv (sellers)

import requests
import base64
import random
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import secrets
import user_agent
import requests
import instaloader
from user_agent import generate_user_agent
import uuid
import random
import re

    
# === CONFIGURATION ===
GITHUB_TOKEN = "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"
GITHUB_OWNER = "MrHacker274"
REPO_NAME = "Vortex"
STOCK_CSV_PATH = "Item storage.csv"
SELLERS_CSV_PATH = "Sellerinfo.csv"


user_states = {}  # user_id -> step
# === /start COMMAND ===
def startsell(update: Update, context: CallbackContext):
    BOT_OWNER_USERNAME = "PrayagRajj"  # Replace with your Telegram username (no @)

    update.message.reply_text(
        f"👋 *Welcome to Vortex Market!*\n\n"
        f"📦 Buy and sell high-quality Instagram accounts with ease.\n\n"
        f"💼 *To Get Started:*\n"
        f"• Use /sell to list your IG account for sale.\n"
        f"• Use /buy to browse accounts or search by filters.\n"
        f"• Use /helpsell to view detailed instructions.\n\n"
        f"🔒 For support or issues, contact admin: [@{BOT_OWNER_USERNAME}](https://t.me/{BOT_OWNER_USERNAME})",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
def helpsell(update: Update, context: CallbackContext):
    BOT_OWNER_USERNAME = "PrayagRajj"  # Replace with your Telegram username (no @)

    help_text = (
        "📘 *Vortex Market Help Menu*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔹 */startsell* – Welcome message & intro\n"
        "🔹 */helpsell* – This help guide\n"
        "🔹 */sell* – List your Instagram account for sale\n"
        "🔹 */buy* – Browse or search accounts by ID/followers\n"
        "🔹 */stock* – View current IG stock available\n"
        "🛒 *How to Buy:*\n"
        "1️⃣ Use /buy\n"
        "2️⃣ Choose 'Search by ID' or 'Filter by Stats'\n"
        "3️⃣ Follow instructions to find a match\n\n"
        "💼 *How to Sell:*\n"
        "1️⃣ Use /sell\n"
        "2️⃣ Select item to sell (Instagram only for now)\n"
        "3️⃣ Enter the Instagram username\n"
        "4️⃣ Provide the selling price\n"
        "5️⃣ Done! The listing goes live instantly.\n\n"
        f"🛠 *Need Help?*\n"
        f"Contact the admin: [@{BOT_OWNER_USERNAME}](https://t.me/{BOT_OWNER_USERNAME})"
    )
    update.message.reply_text(help_text, parse_mode="Markdown", disable_web_page_preview=True)

# === GITHUB CSV FUNCTIONS ===
def get_file(path, default_header):
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{REPO_NAME}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        content = base64.b64decode(r.json()["content"]).decode()
        sha = r.json()["sha"]
        return content, sha

    upload_csv(path, default_header + "\n", f"Create {path} with headers")
    return default_header + "\n", None

def upload_csv(path, new_content, message, sha=None):
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{REPO_NAME}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {
        "message": message,
        "content": base64.b64encode(new_content.encode()).decode(),
        "branch": "main"
    }
    if sha:
        data["sha"] = sha
    r = requests.put(url, headers=headers, json=data)
    return r.status_code in [200, 201]

def get_existing_product_ids_and_usernames():
    content, _ = get_file(STOCK_CSV_PATH, "product_id,username,seller_id,seller_username,type,price,followers,following,posts,reels,stories,bio,country,date_joined,privacy,verified,business,verified_on,former_usernames,linked_with,reset_email,email_availability,date")
    lines = content.strip().split("\n")[1:] if content else []
    return [(line.split(",")[0], line.split(",")[1], line.split(",")[2]) for line in lines]

def generate_unique_id(existing_ids):
    while True:
        pid = f"IG{random.randint(100000, 999999)}"
        if pid not in existing_ids:
            return pid

def add_stock_row(product_id, username, seller_id, seller_username, price, info):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    row = f"{product_id},{username},{seller_id},{seller_username},instagram,{price},{info['followers']},{info['following']},{info['posts']},{info['date_joined']},{info['verified']},{info['business']},{now}"
    content, sha = get_file(STOCK_CSV_PATH, "product_id,username,seller_id,seller_username,type,price,followers,following,posts,date_joined,verified,business,date")
    updated_csv = content.strip() + "\n" + row
    return upload_csv(STOCK_CSV_PATH, updated_csv, f"Add {product_id}", sha)

def update_seller_csv(user_id, product_id):
    content, sha = get_file(SELLERS_CSV_PATH, "user_id,product_ids")
    lines = content.strip().split("\n") if content else []
    headers = lines[0] if lines else "user_id,product_ids"
    body = lines[1:] if len(lines) > 1 else []
    updated = False
    for i, line in enumerate(body):
        uid, pids = line.split(",", 1)
        if uid == str(user_id):
            pids += f"|{product_id}"
            body[i] = f"{uid},{pids}"
            updated = True
            break
    if not updated:
        body.append(f"{user_id},{product_id}")
    final_csv = headers + "\n" + "\n".join(body)
    return upload_csv(SELLERS_CSV_PATH, final_csv, f"Update seller {user_id}", sha)
#---------------------------------------------------------------------username fetecher-------------------------------------------------------------------
import logging
import requests
import json
import re
from uuid import uuid4
from secrets import token_hex
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
logging.basicConfig(level=logging.INFO)
L = instaloader.Instaloader()
def Fetch_iG_info(username):
    try:
        profile = instaloader.Profile.from_username(L.context, username)

        return {
            "followers": profile.followers,
            "following": profile.followees,
            "posts": profile.mediacount,
            "date_joined": profile.mediacount,
            "verified": "Yes" if profile.is_verified else "No",
            "business": "Yes" if profile.is_business_account else "No",
        }

    except Exception as e:
        return {"error": str(e)}    

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, CallbackContext,
                          MessageHandler, Filters, CallbackQueryHandler)
from datetime import datetime

# === GLOBAL STATE ===
user_states = {}

# === /SELL COMMAND FLOW ===
def sell(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_states[user_id] = {'flow': 'sell', 'step': 'choose_item'}
    keyboard = [[InlineKeyboardButton("Instagram Account", callback_data='sell_ig')]]
    update.message.reply_text("🏍 What do you want to sell?", reply_markup=InlineKeyboardMarkup(keyboard))

def sell_button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()

    if query.data == 'sell_ig':
        user_states[user_id] = {'flow': 'sell', 'step': 'ask_ig_username'}
        query.edit_message_text("📋 Enter the Instagram username you want to sell:")

def sell_message_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    seller_username = update.effective_user.username or "unknown"
    GITHUB_CSV_URL = "https://raw.githubusercontent.com/Mrhacker274/vortex/main/Item%20storage.csv"
    BOT_OWNER_USERNAME = "PrayagRajj"  # 👈 Replace with your bot owner Telegram username (without @)

    try:
        if user_id not in user_states:
            update.message.reply_text("ℹ️ Please start the selling process using /sell.")
            return

        step = user_states[user_id]['step']

        if step == 'ask_ig_username':
            username = text.lower()
            existing_stock = read_stock_csv_from_github(GITHUB_CSV_URL)

            # Check if this username already exists in stock
            for item in existing_stock:
                if item.get("username", "").lower() == username:
                    existing_seller_id = str(item.get("seller_id"))
                    existing_seller = item.get("seller_username", "unknown")
                    product_id = item.get("product_id", "N/A")

                    if existing_seller_id == str(user_id):
                        # Already listed by this user
                        update.message.reply_text(
                            f"⚠️ You have already listed *@{username}*.\n"
                            f"🆔 Product ID: `{product_id}`\n\n"
                            f"If you need to change something, please contact the bot owner: [PRAYAGRAJ](https://t.me/{BOT_OWNER_USERNAME})",
                            parse_mode="Markdown",
                            disable_web_page_preview=True
                            )
                        user_states.pop(user_id, None)
                        return
                    else:
                        # Listed by someone else — block and refer to bot owner
                        update.message.reply_text(
                            f"🚫 This account *@{username}* is already listed by another seller.\n"
                            f"🆔 Product ID: `{product_id}`\n\n"
                            f"If this is your account or you believe there's a mistake, please contact the bot admin: [PRAYAGRAJJ](https://t.me/{BOT_OWNER_USERNAME})",
                            parse_mode="Markdown",
                            disable_web_page_preview=True
                        )
                        user_states.pop(user_id, None)
                        return

            # Fetch IG info
            ig_info = Fetch_iG_info(username)
            if "error" in ig_info:
                update.message.reply_text(
                    f"❌ Could not fetch info for *{username}*. Reason: `{ig_info['error']}`",
                    parse_mode="Markdown"
                )
                user_states.pop(user_id, None)
                return

            # Save state and ask for price
            user_states[user_id].update({
                'step': 'ask_price',
                'username': username,
                'ig_info': ig_info
            })

            update.message.reply_text(
                f"📸 Instagram account *@{username}* found!\n\n"
                f"💰 Please enter the price in INR (₹):",
                parse_mode="Markdown"
            )

        elif step == 'ask_price':
            price = text
            state = user_states[user_id]
            username = state['username']
            ig_info = state['ig_info']
            existing_ids = [row["product_id"] for row in read_stock_csv_from_github(GITHUB_CSV_URL)]

            product_id = generate_unique_id(existing_ids)

            added = add_stock_row(product_id, username, user_id, seller_username, price, ig_info)
            linked = update_seller_csv(user_id, product_id)

            if added and linked:
                update.message.reply_text(
                    f"✅ Successfully listed *@{username}* for sale!\n"
                    f"🆔 Product ID: `{product_id}`\n"
                    f"💵 Price: ₹{price}\n"
                    f"📤 Uploaded to stock and linked to your profile.",
                    parse_mode="Markdown"
                )
            else:
                update.message.reply_text("❌ Failed to list your account. Please try again later.")

            user_states.pop(user_id, None)

    except Exception as e:
        update.message.reply_text(f"⚠️ Error: `{e}`", parse_mode="Markdown")
        print(f"[ERROR] sell_message_handler: {e}")

# === /BUY COMMAND FLOW ===
def buy(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_states[user_id] = {"flow": "buy", "step": "choose_buy_mode"}
    keyboard = [
        [InlineKeyboardButton("Search by Product ID", callback_data="buy_by_id")],
        [InlineKeyboardButton("Search by Specification", callback_data="buy_by_spec")]
    ]
    update.message.reply_text("🔍 Choose how you'd like to search:", reply_markup=InlineKeyboardMarkup(keyboard))

def buy_button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()

    if user_id not in user_states:
        query.edit_message_text("❌ Please use /buy to start.")
        return

    if query.data == "buy_by_id":
        user_states[user_id]["step"] = "ask_product_id"
        query.edit_message_text("📏 Enter the Product ID (e.g., IG123456):")

    elif query.data == "buy_by_spec":
        user_states[user_id]["step"] = "choose_spec"
        keyboard = [
            [InlineKeyboardButton("Followers", callback_data="spec_followers"),
             InlineKeyboardButton("Following", callback_data="spec_following")],
            [InlineKeyboardButton("Posts", callback_data="spec_posts"),
             InlineKeyboardButton("Price", callback_data="spec_price")],
            [InlineKeyboardButton("Verified", callback_data="spec_verified"),
             InlineKeyboardButton("Business", callback_data="spec_business")]
        ]
        query.edit_message_text("🔎 Select a filter:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("spec_"):
        spec = query.data.replace("spec_", "")
        user_states[user_id]["step"] = f"spec_value_{spec}"
        user_states[user_id]["spec_type"] = spec
        query.edit_message_text(f"Enter desired value for *{spec}*:", parse_mode="Markdown")
def get_product_info(product_id):
    content, _ = get_file(STOCK_CSV_PATH, "")
    if not content:
        return None

    lines = content.strip().split("\n")
    headers = lines[0].split(",") if lines else []
    for line in lines[1:]:
        fields = line.strip().split(",")
        if fields[0] == product_id:
            return dict(zip(headers, fields))
    return None


def buy_message_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in user_states:
        return

    state = user_states[user_id]

    if state["step"] == "choose_buy_mode":
        update.message.reply_text("🔘 Please tap a button to continue.")
        return

    if state["step"] == "ask_product_id":
        product_id = text.upper()
        info = get_product_info(product_id)
        if not info:
            update.message.reply_text("❌ No product found.")
            return

        seller_username = info.get("seller_username", "unknown")
        if seller_username != "unknown":
            contact = f"[@{seller_username}](https://t.me/{seller_username})"
        else:
            seller_id = info.get("seller_id", "")
            contact = f"[Click to chat](https://t.me/user?id={seller_id})"

        msg = (
            f"🆔 *Product ID*: `{info['product_id']}`\n"
            f"💰 *Price*: ₹{info['price']}\n"
            f"📅 *Listed*: {info['date']}\n"
            f"👥 *Followers*: {info['followers']}\n"
            f"🔁 *Following*: {info['following']}\n"
            f"🖼 *Posts*: {info['posts']}\n"
            f"✅ *Verified*: {info['verified']}\n"
            f"🏢 *Business*: {info['business']}\n"
            f"📞 *Seller Contact*: {contact}"
        )
        update.message.reply_text(msg, parse_mode="Markdown")
        user_states.pop(user_id)

    elif state["step"].startswith("spec_value_"):
        spec_type = state.get("spec_type")
        value = text.lower()

        index_map = {
            "followers": 6, "following": 7, "posts": 8,
            "price": 5, "verified": 10, "business": 11, "date": 12
        }
        col_index = index_map.get(spec_type)

        content, _ = get_file(STOCK_CSV_PATH, "")
        if not content:
            update.message.reply_text("⚠️ No data found.")
            return

        lines = content.strip().split("\n")[1:]
        matches = []

        for line in lines:
            parts = line.split(",")
            if len(parts) <= col_index:
                continue

            if spec_type in ["verified", "business"]:
                if value not in ["yes", "no"]:
                    update.message.reply_text("❗ Please type yes or no.")
                    return
                if parts[col_index].strip().lower() == value:
                    matches.append(parts)
            else:
                if not value.isdigit():
                    update.message.reply_text("❗ Enter a valid number.")
                    return
                num_value = int(value)
                lower, upper = (num_value // 50) * 50, (num_value // 50 + 1) * 50
                if parts[col_index].isdigit():
                    val = int(parts[col_index])
                    if lower <= val <= upper:
                        matches.append(parts)

        if matches:
            formatted = "\n\n".join([
                f"🆔 *Product ID*: `{f[0]}`\n💰 *Price*: ₹{f[5]}\n👥 *Followers*: {f[6]}\n🔁 *Following*: {f[7]}\n🖼 *Posts*: {f[8]}\n✅ *Verified*: {f[10]}\n🏢 *Business*: {f[11]}"
                for f in matches[:5]
            ])
            update.message.reply_text(f"Top matches:\n\n{formatted}", parse_mode="Markdown")
        else:
            update.message.reply_text("❌ No matching accounts found.")

        user_states.pop(user_id)


# === UNIFIED MESSAGE HANDLER ===
def unified_message_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    state = user_states.get(user_id, {})
    flow = state.get("flow")

    if flow == "sell":
        return sell_message_handler(update, context)
    elif flow == "buy":
        return buy_message_handler(update, context)
    else:
        update.message.reply_text("ℹ️ Please use /sell or /buy to begin.")
import csv
import requests
import csv
import io

def read_stock_csv_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status
        content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        return list(reader)
    except Exception as e:
        print(f"[ERROR] Failed to fetch GitHub CSV: {e}")
        return []
def stock(update: Update, context: CallbackContext):
    GITHUB_CSV_URL = "https://raw.githubusercontent.com/Mrhacker274/vortex/main/Item%20storage.csv"
    
    try:
        stock_data = read_stock_csv_from_github(GITHUB_CSV_URL)

        if not stock_data:
            update.message.reply_text("📦 No accounts found in stock.")
            return

        message = "🛒 *Premium Instagram Stock List*\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"

        for item in stock_data[:10]:  # Show up to 10 items
            username = item.get("username", "N/A")
            price = item.get("price", "N/A")
            product_id = item.get("product_id", "N/A")
            followers = item.get("followers", "N/A")
            following = item.get("following", "N/A")
            posts = item.get("posts", "N/A")
            date_joined = item.get("date_joined", "N/A")
            verified = "✅ Yes" if item.get("verified", "No") == "Yes" else "❌ No"
            business = "🏢 Yes" if item.get("business", "No") == "Yes" else "🙅‍♂️ No"

            message += (
                f"*🆔 ID:* `{product_id}`\n"
                f"*💰 Price:* ₹{price}\n"
                f"*👥 Followers:* {followers}  |  *🔁 Following:* {following}\n"
                f"*📸 Posts:* {posts}  | \n"
                f"*☑️ Verified:* {verified}  |  *🏬 Business:* {business}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
            )

        update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        update.message.reply_text(f"⚠️ Failed to load stock:\n`{e}`", parse_mode="Markdown")
        print(f"[ERROR] /stock: {e}")



# === REGISTER HANDLERS ===
def register_handlers(updater: Updater):
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("startsell", startsell))
    dp.add_handler(CommandHandler("helpsell", helpsell))
    dp.add_handler(CommandHandler("sell", sell))
    dp.add_handler(CommandHandler("buy", buy))
    dp.add_handler(CallbackQueryHandler(sell_button_handler, pattern='^sell_ig$'))
    dp.add_handler(CallbackQueryHandler(buy_button_handler, pattern='^(buy_by_id|buy_by_spec|spec_.*)$'))
    dp.add_handler(CommandHandler("stock", stock))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, unified_message_handler))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("reset", reset_command))
    dp.add_handler(CommandHandler(["info", "infonum"], handle_info_command))
    dp.add_handler(CommandHandler("aol", aol))
    dp.add_handler(CommandHandler("yahoo", yahoo))
    dp.add_handler(CommandHandler("gmail", gmail))
    dp.add_handler(CommandHandler("subscription", subscription_command))
    dp.add_handler(CommandHandler("hotmail", hotmail))
    dp.add_handler(CommandHandler("outlook", outlook))
    dp.add_handler(CommandHandler("status", status_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_info_command))
    print("🤖 Bot is running...ENJOY")

# === MAIN FUNCTION ===
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    register_handlers(updater)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
