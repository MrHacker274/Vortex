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

from telegram import Update, ChatAction, ParseMode, Message
from telegram.ext import CallbackContext
import time
import re
import requests

OWNER_ID = 5851767478
user_last_used = {}

def handle_info_command(update: Update, context: CallbackContext):
    message_text = update.message.text or ""
    command = message_text.lower().split()[0]

    if command not in ["/info", "/infonum"]:
        return

    user = update.effective_user
    user_id = user.id
    now = time.time()

    if user_id in user_last_used and now - user_last_used[user_id] < 25:
        wait_time = int(25 - (now - user_last_used[user_id]))
        update.message.reply_text(f"⏳ Please wait {wait_time}s before making another request.")
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
    loading_message: Message = update.message.reply_text("🔍 Processing your request...", parse_mode=ParseMode.HTML)
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
                loading_message.edit_text("❌ Could not find username for that user ID.", parse_mode=ParseMode.HTML)
                return
        else:
            if not re.match(r"^[a-zA-Z0-9._]{1,30}$", input_value):
                loading_message.edit_text("❌ Invalid username format.", parse_mode=ParseMode.HTML)
                return
            username = input_value

        loading_message.edit_text(f"🔍 Fetching info for Instagram user: <code>@{username}</code>", parse_mode=ParseMode.HTML)
        time.sleep(1.5)

        info = fetch_instagram_info(username)

        loading_message.edit_text(info, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

        telegram_username = user.username
        full_name = user.full_name
        requester_text = (
            f'<a href="https://t.me/{telegram_username}">@{telegram_username}</a>'
            if telegram_username else f'{full_name} (ID: <code>{user.id}</code>)'
        )

        context.bot.send_message(
            chat_id=OWNER_ID,
            text=(
                f"📩 <b>Request by:</b> {requester_text}\n"
                f"🔍 <b>Searched IG:</b> <code>{username}</code>\n\n"
                f"{info}"
            ),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

    except Exception as e:
        loading_message.edit_text(f"❌ Error occurred:\n<code>{str(e)}</code>", parse_mode=ParseMode.HTML)


# -------- Helper: Convert user ID to username -------- #
def get_username_from_user_id(user_id: str) -> str:
    # This must match your working Instagram request logic
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
    'sessionid': '5545662104%3ATSmn4hQ082l5P1%3A2%3AAYdHSaNBx20fZ845bJCugBgkJUma3TckTlONXimRcw',
    'wd': '1160x865',
    'rur': '"CCO\\0545545662104\\0541780650755:01fe20666d0d31af9d4735d51a08c1b53e680e93a8784173b044eaa054e0b6cb73376cdb"',
    }
    headers = {
        'accept': '*/*',
    'accept-language': 'en-US,en;q=0.8',
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'origin': 'https://www.instagram.com',
    'priority': 'u=1, i',
    'referer': 'https://www.instagram.com/nishval.x_17/',
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
    }
    params = {
        'appid': 'com.bloks.www.ig.about_this_account',
    'type': 'app',
    '__bkv': 'f4e32caf235c4c3198ceb3d7599c397741599ea3447ec2f785d4575aeb99766b',
    }
    data = {
        '__d': 'www','__user': '0','__a': '1','__req': '31','__hs': '20244.HYP:instagram_web_pkg.2.1...0','dpr': '1','__ccg': 'EXCELLENT','__rev': '1023521818','__s': 'jq5p2x:eibgln:k18zzf','__hsi': '7512390373916991035','__dyn': '7xeUjG1mxu1syaxG4Vp41twWwIxu13wvoKewSAx-bwNw9G2Saxa0DU6u3y4o0B-q1ew6ywMwto2awgo9oO0n24oaEnxO1ywOwv89k2C1Fwc60AEC0H8-U2exi4UaEW2G0AEco4i5o7G4-5o4q3y261kx-0ma2-azqwt8d-2u2J08O321LwTwKG1pg2fwxyo6O1FwlA3a3zhA6bwQyXxui2qiUqwm8jxK2K2G0EoK9x60hK78uyFE',
    '__csr': 'ghg8s8T6gJfdlNI_6RN74FiOn8IoHqd4ridq9fjBBkKteUJ2czZ4l9ykmh9piamJq_L8GsTH8ycF2AZi4mjWvDHVaiXQ-i8GZqGblbHUJ6iUPDbdySlblCBhQVRUGky8CdG9AyprGiFpWRTCl4Gjgz_ULKh24imXGZopVu-jDzUjCDhFbKuy5hV9_-9wHGq58kUoAGEGjKi5VF8x6xuvw05eww81cD-q0KUy1qO1Ki3mbg4igAWx51ip28bo9ogg8945A3yu1wwTpU-gAw4a5U-3K4EyuQvwOIuaKA4Wx50YEUK7FQ2y48o65gGhyUyF6fxlzoiwoA2yca0j63a8z40EbwfO0bzyA0jS0cgyki5VBwfq0AFE89no9mt0WU-FhoqgK1ig5q1bwEQjecg0wm15zYE2MDyaCwRo1e9VQaGi1wg0IO10wsE0Hu0vx04zxe17wTgC4Uzx2lojg0qYzE04g2cBRFk0Torwoo9o1zo2nUoLwuU3yAuA0JEiw0zPm0WVobU',
    '__hsdp': 'geXX59OOiRf5Enq4qhdpgKqQbQyugahJgdzY8nsZ9gIVl2p8Ex0z7590W8Q8suSSGbIKhb6CPcxoxBadCCD24b14wcW8iQy4gwUG216x1Clwj9UeU4i1WyE1hEarw6QU0wS0mi0S83rBw5swCwQwqodE4C0ja0im0he4oao',
    '__hblp': '1a18g4212Upz4bwGyE25Bx28yEKE-12wqQ4okV98N3oCFVVRBDx2umaz89-chrxS-aExbkKUF3rzoFeeCC-i5K6qoFDHGUym5SmFqixSejKaDUDS9m-2em22luQV8y9yfF2okz5yEbEN1N289Hye4rykq3uEW6EO0wU2_wywyUFa7U-0x9E43xy2icwPw821hwn888bQegOi7U8o8o2CzUdo8pEC1lz8-mVFUK7jVEoUboy5pQmmq26U4acxqayF8Jd2Upy8lwPx-3qbwyzEJ122ufwPwMwBx6bzUbUkDzUc8dEqzE6q2CcwioN2UigGU8Uy4K4Uhxq4k225orzZQ4CUjwyxl0ABxC',
    '__comet_req': '7',
    'fb_dtsg': 'NAfu0VZ-V7EA9l7Ji_RteyFgJUUrqZ-zaFOV1HB4AY-dORWJxtLnBIw:17843671327157124:1748946019',
    'jazoest': '26123',
    'lsd': '4n00rbnIGJIiuc4l8kqL2b',
    '__spin_r': '1023521818',
    '__spin_b': 'trunk','__spin_t': '1749114686','__crn': 'comet.igweb.PolarisProfilePostsTabRoute',
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
    'AS': 'v=1&s=CXNFiCaf&d=A68441ce7|X4q.L_3.2ToHPB9jJv25S3fvsjKtaa6YB.V9e0nUyGpvJEp411b5LAh39lECeKbrK2U32o9DNEVo0dVR3LPsOrbfP8cj9g0faGnid_U2RvyN7guUG03ejPHpgZJsh.BJ_gNGiIwTiYt1ql3NLZyx38HvauyL8gKl91EBBu8ZNVfmaO5bZDKV_rzsmqzaJVBZZnagC2O.guU8kXfrk8X7X0OW1xfXwocM9JdDuZiwStBAomwB7Gf95E2LphxqmFQ7VoJPDJiJwuJ9Ih5kEuCT3mEuKYrMRn6ZRkebvahmSSxj6625apWFJ20gN_9ovKrItR24WvOOHjCdp8obcrGsgM9kPyP1CPzJsRtNsXZ8Csx64klj6P1Rtc.KbpsB5Uhx6jhJFPbOgEUt.2wnOoj8J_d2TkZiM5GjXqrmUrVzeCyQR0FEKWi9uYpC3ArBuW54ncA6KBXmd__svc1bnMH7avBu1GE4Gu4Db2xWZlSGeJqiRb52kTUryGaN.DB8ANHGdmjCquXZusJ9ERlVLVpNupdYxtP6iM4ea3Zn70thXORYTCQIdl9x9hBbXTTVl_98ipylBIxa7UoIyR1ZIXZESXyrO7K6M7YAmYtRENPP.mQeiJLpFDDhANQ83RSWI0RXn5Fu.INFTEThA.Z3Jl8r2DzODb.bsTaCm47E2gtMHqap6prgiL23MHKJSmk1WhfMHp0BnWf_aIxAtZfwchCfGZ_pnMU7T6SOHM.G6aGjd2G9k_cd.onAoyy1HhnyLA9r9oXHYLhwR50Dwp.ZY3nkweEnbY5H.Tb29z958jvMCGS367NndKULJDnqWz5MxnRUqo7e_oj5SZsZWIfjqHzUvO5GiU9nsUc_lGb7sS7XnF2EWMK3QZva81Zl0CY1pW16qXBpKZd4Y0pDq14dZde4b.xyWqrnGV3e.d467RtfWrK4t6B_Ocm9mMAapK5dwwz8bxLvieVdarYIJmGrO6BWu54BooWD9Q.8BZ8QcdRqJk0BJ8TMZ0F6T_0xSzh073_kq2qbbZ1Dfpk59.8JpV3ViFdAdMNyDgH6Y8BFXDc12L2hbhWANrzkIYb9G_aXx8K14LDkx0L3lONeyn9Hd39eQVc7SdG4vIxbXWbQ5xu2xh5boF.jFNY1vCx29w5VC_vDHZd.~A|B68442021|AVlOk_L.2TqOmDMvLI3qgvOncwH3GmqQh2WQ4ddctGJQZWWbQpQB91rC0GIQz47BeR7UBSfIIVGFLD2okyv.z7u5i6aqtedC4ovxN82KC5U3m1AYOoascqrh1CNyHtt8lcFywUHAv2t4FMABfTmZMKbtOV1eXBgWG5E_PUrZIXJxwI5IfcYWewV98WUyPAar9SwiuQXEGJLNX1qYcnwyS3BRuI7EhUqNRF2VOJt.jgIfI0Y_tQLBY5_wV5RX5sDUQkMeGFH4dndUqmQOAzajijmDWMoSXHoKzfNU_SMvFaA6qjR4_ZKKW_6dl4z4VBwc85VU9inCqQBBSBwkbn3sNwzhh1tgnqPobJ0rovm.kiZ6PicthfXU1BIfpCx_AkSmzc6ugWnUhPBEgXx.IiSFz1lNBcAjn3fmb7wgaufSWez5oUDuXK330CuTUd87wCKZar5MmVMzdHwkAiAZ1Fm86kH0mVZuVmNVA0zMOrN.FxbzL1sIBkFqyNmMQ9XHymWqaoj9epMGjZLAsGTrvs1eICMwHayjfygDTvtmv9QxB3XsoU6RxTLdEZ3mw8IgWQMmzYnSYZliVYYVQ6e41bwqhDrecXiGAzCVXiaJ52k1Fk.0XdcvkhNcwbAxt1ZoKVK76lBdym4cT9LOLlJkrQNzzpAXSUpQsgLpMbN1FxYxoXwFoRbb1_.gFQBDQCcdQPJSywd.yA7oTMFZB4h8b4Ts5tI92mtlrS9jGiKZ8_CY3ECWglJQYqhVoV_FFLDKxySio9dkBX53gm56a66fdC5pGeak4vzXAYuMEsykdTsK9uY6fefwMNeYwfyJHhci7JiGJz.Y2UW7UK0OAQbblxYtztlM3UOyJjMFk1C6Qqq9jynix3aR4CiVfNeyr8YQldpjLzwcmJ08CCicwrsBh3aPqoErSZPlSVVwtVX4zVJvfKxZd4R57P85oeGhKgrugERYHjsuojVKcd3dSeGEvVvlXB4UZdSgGBtvQLt5kHZatrmtRSCENqMiUanew5N1II3qhOzOAPw89uK0t9Bsh7aU91jm.F6zNR.HjQCOg6aD27kQnSvGRPJxPaNz_jX7X1f7ZXGVrMqn0Jxc28Y9P5LxpiR15McNQ0lAngoT3xIK.bdTHm3Tl7DmbL.nck2nNimYnI76KQ--~A',
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
    # 'cookie': 'weathergeo=%2223.03%7C72.60%7CAhmedabad%7CGJ%7CIndia%7C0%7C29219630%22; GUC=AQEBCAFoQrxoa0IdaQRU&s=AQAAAGsKHyP7&g=aEFsow; A1=d=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA; A3=d=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA; A1S=d=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA; AS=v=1&s=CXNFiCaf&d=A68441ce7|X4q.L_3.2ToHPB9jJv25S3fvsjKtaa6YB.V9e0nUyGpvJEp411b5LAh39lECeKbrK2U32o9DNEVo0dVR3LPsOrbfP8cj9g0faGnid_U2RvyN7guUG03ejPHpgZJsh.BJ_gNGiIwTiYt1ql3NLZyx38HvauyL8gKl91EBBu8ZNVfmaO5bZDKV_rzsmqzaJVBZZnagC2O.guU8kXfrk8X7X0OW1xfXwocM9JdDuZiwStBAomwB7Gf95E2LphxqmFQ7VoJPDJiJwuJ9Ih5kEuCT3mEuKYrMRn6ZRkebvahmSSxj6625apWFJ20gN_9ovKrItR24WvOOHjCdp8obcrGsgM9kPyP1CPzJsRtNsXZ8Csx64klj6P1Rtc.KbpsB5Uhx6jhJFPbOgEUt.2wnOoj8J_d2TkZiM5GjXqrmUrVzeCyQR0FEKWi9uYpC3ArBuW54ncA6KBXmd__svc1bnMH7avBu1GE4Gu4Db2xWZlSGeJqiRb52kTUryGaN.DB8ANHGdmjCquXZusJ9ERlVLVpNupdYxtP6iM4ea3Zn70thXORYTCQIdl9x9hBbXTTVl_98ipylBIxa7UoIyR1ZIXZESXyrO7K6M7YAmYtRENPP.mQeiJLpFDDhANQ83RSWI0RXn5Fu.INFTEThA.Z3Jl8r2DzODb.bsTaCm47E2gtMHqap6prgiL23MHKJSmk1WhfMHp0BnWf_aIxAtZfwchCfGZ_pnMU7T6SOHM.G6aGjd2G9k_cd.onAoyy1HhnyLA9r9oXHYLhwR50Dwp.ZY3nkweEnbY5H.Tb29z958jvMCGS367NndKULJDnqWz5MxnRUqo7e_oj5SZsZWIfjqHzUvO5GiU9nsUc_lGb7sS7XnF2EWMK3QZva81Zl0CY1pW16qXBpKZd4Y0pDq14dZde4b.xyWqrnGV3e.d467RtfWrK4t6B_Ocm9mMAapK5dwwz8bxLvieVdarYIJmGrO6BWu54BooWD9Q.8BZ8QcdRqJk0BJ8TMZ0F6T_0xSzh073_kq2qbbZ1Dfpk59.8JpV3ViFdAdMNyDgH6Y8BFXDc12L2hbhWANrzkIYb9G_aXx8K14LDkx0L3lONeyn9Hd39eQVc7SdG4vIxbXWbQ5xu2xh5boF.jFNY1vCx29w5VC_vDHZd.~A|B68442021|AVlOk_L.2TqOmDMvLI3qgvOncwH3GmqQh2WQ4ddctGJQZWWbQpQB91rC0GIQz47BeR7UBSfIIVGFLD2okyv.z7u5i6aqtedC4ovxN82KC5U3m1AYOoascqrh1CNyHtt8lcFywUHAv2t4FMABfTmZMKbtOV1eXBgWG5E_PUrZIXJxwI5IfcYWewV98WUyPAar9SwiuQXEGJLNX1qYcnwyS3BRuI7EhUqNRF2VOJt.jgIfI0Y_tQLBY5_wV5RX5sDUQkMeGFH4dndUqmQOAzajijmDWMoSXHoKzfNU_SMvFaA6qjR4_ZKKW_6dl4z4VBwc85VU9inCqQBBSBwkbn3sNwzhh1tgnqPobJ0rovm.kiZ6PicthfXU1BIfpCx_AkSmzc6ugWnUhPBEgXx.IiSFz1lNBcAjn3fmb7wgaufSWez5oUDuXK330CuTUd87wCKZar5MmVMzdHwkAiAZ1Fm86kH0mVZuVmNVA0zMOrN.FxbzL1sIBkFqyNmMQ9XHymWqaoj9epMGjZLAsGTrvs1eICMwHayjfygDTvtmv9QxB3XsoU6RxTLdEZ3mw8IgWQMmzYnSYZliVYYVQ6e41bwqhDrecXiGAzCVXiaJ52k1Fk.0XdcvkhNcwbAxt1ZoKVK76lBdym4cT9LOLlJkrQNzzpAXSUpQsgLpMbN1FxYxoXwFoRbb1_.gFQBDQCcdQPJSywd.yA7oTMFZB4h8b4Ts5tI92mtlrS9jGiKZ8_CY3ECWglJQYqhVoV_FFLDKxySio9dkBX53gm56a66fdC5pGeak4vzXAYuMEsykdTsK9uY6fefwMNeYwfyJHhci7JiGJz.Y2UW7UK0OAQbblxYtztlM3UOyJjMFk1C6Qqq9jynix3aR4CiVfNeyr8YQldpjLzwcmJ08CCicwrsBh3aPqoErSZPlSVVwtVX4zVJvfKxZd4R57P85oeGhKgrugERYHjsuojVKcd3dSeGEvVvlXB4UZdSgGBtvQLt5kHZatrmtRSCENqMiUanew5N1II3qhOzOAPw89uK0t9Bsh7aU91jm.F6zNR.HjQCOg6aD27kQnSvGRPJxPaNz_jX7X1f7ZXGVrMqn0Jxc28Y9P5LxpiR15McNQ0lAngoT3xIK.bdTHm3Tl7DmbL.nck2nNimYnI76KQ--~A',
    }
    params = {
        'validateField': 'userId',
    }
    data = F'browser-fp-data=%7B%22language%22%3A%22en-US%22%2C%22colorDepth%22%3A24%2C%22deviceMemory%22%3A8%2C%22pixelRatio%22%3A1%2C%22hardwareConcurrency%22%3A4%2C%22timezoneOffset%22%3A-330%2C%22timezone%22%3A%22Asia%2FCalcutta%22%2C%22sessionStorage%22%3A1%2C%22localStorage%22%3A1%2C%22indexedDb%22%3A1%2C%22cpuClass%22%3A%22unknown%22%2C%22platform%22%3A%22Win32%22%2C%22doNotTrack%22%3A%22unknown%22%2C%22plugins%22%3A%7B%22count%22%3A4%2C%22hash%22%3A%22879774623977b14ab013aceca855878d%22%7D%2C%22canvas%22%3A%22canvas%20winding%3Ayes~canvas%22%2C%22webgl%22%3A1%2C%22webglVendorAndRenderer%22%3A%22Google%20Inc.%20(Intel)~ANGLE%20(Intel%2C%20Intel(R)%20HD%20Graphics%20Direct3D9Ex%20vs_3_0%20ps_3_0%2C%20igdumd64.dll)%22%2C%22adBlock%22%3A0%2C%22hasLiedLanguages%22%3A0%2C%22hasLiedResolution%22%3A0%2C%22hasLiedOs%22%3A0%2C%22hasLiedBrowser%22%3A0%2C%22touchSupport%22%3A%7B%22points%22%3A0%2C%22event%22%3A0%2C%22start%22%3A0%7D%2C%22fonts%22%3A%7B%22count%22%3A29%2C%22hash%22%3A%2290ead5fa1a480b09b5b0239bd273a529%22%7D%2C%22audio%22%3A%22123.79177350061218%22%2C%22resolution%22%3A%7B%22w%22%3A%221680%22%2C%22h%22%3A%221050%22%7D%2C%22availableResolution%22%3A%7B%22w%22%3A%221050%22%2C%22h%22%3A%221680%22%7D%2C%22ts%22%3A%7B%22serve%22%3A1749207911538%2C%22render%22%3A1749207913247%7D%7D&specId=yidregsimplified&context=REGISTRATION&cacheStored=&crumb=v%2FnkkKGtxP3126Cthy3k3A&acrumb=CXNFiCaf&sessionIndex=QQ--&done=https%3A%2F%2Fapi.login.aol.com%2Foauth2%2Fauthorize%3Fclient_id%3Ddj0yJmk9ZXRrOURhMkt6bkl5JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWQ2%26intl%3Dus%26nonce%3DWSbk8RiHKdR86BSpvlDJfvkkiG7yZfSz%26redirect_uri%3Dhttps%253A%252F%252Foidc.www.aol.com%252Fcallback%26response_type%3Dcode%26scope%3Dmail-r%2Bopenid%2Bguce-w%2Bopenid2%2Bsdps-r%26src%3Dfp-us%26state%3DeyJhbGciOiJSUzI1NiIsImtpZCI6IjZmZjk0Y2RhZDExZTdjM2FjMDhkYzllYzNjNDQ4NDRiODdlMzY0ZjcifQ.eyJyZWRpcmVjdFVyaSI6Imh0dHBzOi8vd3d3LmFvbC5jb20vIn0.hlDqNBD0JrMZmY2k9lEi6-BfRidXnogtJt8aI-q2FdbvKg9c9EhckG0QVK5frTlhV8HY7Mato7D3ek-Nt078Z_i9Ug0gn53H3vkBoYG-J-SMqJt5MzG34rxdOa92nZlQ7nKaNrAI7K9s72YQchPBn433vFbOGBCkU_ZC_4NXa9E&googleIdToken=&authCode=&attrSetIndex=0&specData=&deviceCapability=%7B%22pa%22%3A%7B%22status%22%3Afalse%7D%2C%22isWebAuthnSupported%22%3Atrue%7D&tos0=oath_freereg%7Cus%7Cen-US&multiDomain=&asId=97162952-9bce-4222-9b60-0eea2cf76bb6&fingerprintCaptured=&firstName=zuck&lastName=zuck&userid-domain=yahoo&userId={username}&password=&mm=&dd=&yyyy=&signup='
    response = requests.post(
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
    results = []
    for method in [method_1, method_2, method_3, method_4, method_5, method_6, method_7]:
        try:
            result = method(email_or_username)
            if result not in ["No Reset", "Failed", "Error"]:
                results.append(result)
                break
        except Exception as e:
            continue
    return results if results else ["No Reset"]

def method_1(email_or_username):
    try:
        headers = {
            'authority': 'www.instagram.com',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.instagram.com',
            'referer': 'https://www.instagram.com/accounts/password/reset/?hl=ar',
            'user-agent': 'Mozilla/5.0',
            'x-csrftoken': 'gpexs0wL6nxpdY955MzDDX',
            'x-ig-app-id': '936619743392459',
            'x-requested-with': 'XMLHttpRequest',
        }
        data = {'email_or_username': email_or_username, 'jazoest': '21965'}
        res = requests.post('https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/', headers=headers, data=data)
        if res.status_code == 200:
            contact = res.json().get("contact_point")
            if contact:
                if "@" in contact:
                    return f"Email: {contact}"
                return f"Phone: {contact}"
        return "No Reset"
    except:
        return "No Reset"

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
            return f"Contact: {match.group(1)}" if match else 'Unknown'
        return 'Failed'
    except:
        return 'Error'

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
        result = res.json()
        message = result.get('message', '')
        if result.get("status") == "ok":
            # Extract just the number using regex
            match = re.search(r'(\+\d[\d\s\-\*]+)', message)
            return match.group(1).strip() if match else message
        return "Failed"
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
        return f"Email: {contact}" if contact else 'No Reset'
    except:
        return 'Failed'

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
        return f"Email: {contact}" if contact else "No Reset"
    except:
        return 'Error'

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
        return f"Email: {contact}" if contact else "No Reset"
    except:
        return "Error"

def method_7(email_or_username):
    try:
        for num in range(1, 4):
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
            if '"status":"ok"' in res:
                if 'contact_point' in res:
                    contact = res.split('"contact_point":"')[1].split('"')[0]
                    if "@" in contact:
                        return f"Email: {contact}"
                    return f"Phone: {contact}"
                return "Not visible"
        return "Failed"
    except:
        return "Error"
# Cooldown tracker
user_last_used = {}
COMMAND_COOLDOWN = 25

def escape_markdown(text):
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!\\])', r'\\\1', text)

def reset_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    now = time.time()

    # Cooldown check
    if user_id in user_last_used and now - user_last_used[user_id] < COMMAND_COOLDOWN:
        wait_time = int(COMMAND_COOLDOWN - (now - user_last_used[user_id]))
        update.message.reply_text(f"⏳ Please wait {wait_time}s before using /reset again.")
        return
    user_last_used[user_id] = now

    if not context.args:
        update.message.reply_text("⚠️ Please provide a username.\nUsage: /reset <instagram_username>")
        return

    email_or_username = context.args[0].strip().lstrip("@")
    if not re.match(r'^[a-zA-Z0-9._]{1,30}$', email_or_username):
        update.message.reply_text("❌ Invalid username format. Only letters, numbers, dots, and underscores allowed.")
        return

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    time.sleep(10)  # Optional delay

    contact_points = send_recovery_request(email_or_username)
    contact_raw = contact_points[0] if contact_points else "No Reset"

    username_md = escape_markdown(email_or_username)

    if "@" in contact_raw:
        contact_point = contact_raw.replace("Email: ", "").strip()
        recovery_method = "Email"
        status = "✅ Success"
    elif re.search(r'\d', contact_raw):
        contact_point = contact_raw.replace("Phone: ", "").strip()
        recovery_method = "Phone"
        status = "✅ Success"
    elif contact_raw == "No Reset":
        contact_point = "Not Found"
        recovery_method = "Unavailable"
        status = "❌ Failed"
    else:
        contact_point = contact_raw
        recovery_method = "Unknown"
        status = "⚠️ Unknown"

    message = (
        f"🔄 *Instagram Reset Info*\n"
        f"👤 *Username:* `{username_md}`\n"
        f"📌 *Status:* `{status}`\n"
        f"📬 *Contact Point:* `{escape_markdown(contact_point)}`\n"
        f"🛠️ *Recovery Method:* `{recovery_method}`"
    )

    update.message.reply_text(message, parse_mode="MarkdownV2")

def fetch_instagram_info(username):
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        user_id = profile.userid    
        cookies = {
            'sessionid': '5545662104%3ATSmn4hQ082l5P1%3A2%3AAYdHSaNBx20fZ845bJCugBgkJUma3TckTlONXimRcw','ds_user_id': '5545662104',
        }
        headers = {
           'accept': '*/*',
    'accept-language': 'en-US,en;q=0.8',
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
    'cookie': 'datr=GAgjaB5R_liEM-dpATRTgjMj; ig_did=114B8FDB-7673-4860-A1D8-E88C655B9DD8; dpr=0.8999999761581421; ig_nrcb=1; ps_l=1; ps_n=1; mid=aDaRiAALAAFk8TVh8AGAIMVtWO_F; csrftoken=Pf0Us3q173jfLfTXAurrhCD8uY5KpFlf; ds_user_id=5545662104; sessionid=5545662104%3ATSmn4hQ082l5P1%3A2%3AAYdHSaNBx20fZ845bJCugBgkJUma3TckTlONXimRcw; rur="CCO\\0545545662104\\0541780721438:01fec0abacd78f29d5feb9da71aa1e6f6b6222122e6686c4e1957ceb3f35e2e1705ce8fd"; wd=1160x865',
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
    '__req': '15',
    '__hs': '20245.HYP:instagram_web_pkg.2.1...0',
    'dpr': '1',
    '__ccg': 'EXCELLENT',
    '__rev': '1023555608',
    '__s': 'lctubq:aedh80:9l3naw',
    '__hsi': '7512694227045913317',
    '__dyn': '7xeUjG1mxu1syUbFp41twWwIxu13wvoKewSAwHwNw9G2S7o2vwa24o0B-q1ew6ywaq0yE462mcw5Mx62G5UswoEcE7O2l0Fwqo31w9O1TwQzXwae4UaEW2G0AEco5G1Wxfxm16wUwtE1wEbUGdG1QwTU9UaQ0Lo6-3u2WE5B08-269wr86C1mgcEed6goK2O4Xxui2K7E5y4UrwHwcObyohw4rxO2Cq',
    '__csr': 'jgan91x5T2Bp0yzhcZsBjn_qahnki89kyH8BREDhrGUOGtSbBAgCQ4p4Z6WF2fRDAHQiGBWleKBnAAF4hrzHnKGCWVSmkwXVFohBWKbiLG8-9BGGDoCcKBxO9zqiyFy7mEhAgKpyrGiQegiyU9rjAWQiUKdwJUKnKp4gW-3yt3EyEaoC48y2C6801kTQ1jy8Gl0cW4OwSzo4W3Gt0DVYU6y38WFo2VDyJ1ObK1FDQ1HyFA0UQ0fbw3_E0Fbo6Z2k7o1f83OCwFwskqt2F20aB4eEKl36npE0HEM94muawgm0jh6DgG0dZw085m08kw5Nw0LGw',
    '__hsdp': 'geXp1lWkIJhYpvN54Gj3wSzhEwShp0ekB8ci9NcP4QAOO0zC7ykimkq1CkgqbzF8vwm6vwrEa4owy9CxudoV5xOhe48gG4E4N10g2G2O7UG2yawhu1vAyFUcuUbE563l1d3FU16o4m2V3U16U-0bowbi1og4S1HwcK4E4S1mwu82Axq0Ky0Exx0uo5-0x85W3i484Z0i8y0x8c84Q-4oy3i',
    '__hblp': '4zE4y3O1fgC9wiU7efxGiaKFUkwko7CFE8UyqeCAHwEDxm3WEnUiwNxal0VKUih94Ugx2KbAwjVVpUK7EG26u5oOES5aCK5UCm7vwQwEzVV8vAUK2W1hwRgjgWu1Uwa2226ozwIQfxa0grzU6K1XxC7U1rU4q0J85x0RyoS13xi9Gm0yo464E4S17zE885u0F8mwbExo8Eog7Cu2-dxemU7ibwywXDwIx2q27xy8F0g88E5G9zoc89EsyjUWEyewBw',
    '__comet_req': '7',
    'fb_dtsg': 'NAftakOGNZTeuXFvCvlMnE009R_FA_exIa-FIt17Q7yMlYlt8t8FYZA:17843671327157124:1748946019',
    'jazoest': '26196',
    'lsd': 'nBC_SbrTDEE-0Osm5JQYsd',
    '__spin_r': '1023555608',
    '__spin_b': 'trunk',
    '__spin_t': '1749185431',
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
                elif domain.startswith("+") or any(c.isdigit() for c in domain):
                    reset_check = "📱 Reset is Phone Number"
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
 
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("reset", reset_command))
    dp.add_handler(CommandHandler(["info", "infonum"], handle_info_command))
    dp.add_handler(CommandHandler("aol", aol))
    dp.add_handler(CommandHandler("gmail", gmail))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_info_command))
    print("🤖 Bot is running...ENJOY")
    updater.start_polling()
    updater.idle()
if __name__ == "__main__":
    main()
