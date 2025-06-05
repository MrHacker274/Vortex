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
        "• Lookup public Instagram <b>username</b>\n"
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
    'GUCS': 'ATblFArI',
    'GUC': 'AQEBCAFoQrxoa0IdaQRU&s=AQAAAGsKHyP7&g=aEFsow',
    'A1': 'd=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA',
    'A3': 'd=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA',
    'A1S': 'd=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA',
    'AS': 'v=1&s=fXGl2fuE&d=A6842c084|F5fkZcH.2TqOx3FZQHYR78BUZeJI_FqoQp7D_hT_9FBgPAdv72mhDn0T4qAh.G4DiOz6G5x.Db7R0hozzE7lQGWzzi5POuVvkYuuwqa6f1P0kRPp88kHvNMSeblE4N.0YRiOEANnQIH6TzScZQGqqL41DdZeJMgoJM.XLva0gs0DjW9yqKOKMtbSMFdmhH8HiX586Hde2.Rk5OR94LNvPmZcy5RbeuRzIvEyKzXQLe4sPH_Z5aVgCj8h3qG92tYBCRegbcI8xkAXcLmuFw9zpzkxEBngvMSl.388Xp.qWqHACM_3Xzd1.vIbsvs9SAz1uz5hxvXsnPSrshvpoSVIFg1wOeet7xJk45LYG2EI1u1TpkJgU4roBauiBME9L5JA2gQHu6gDMRkcWITbJLuMFtcV9vXQUcfePDlQeozUJSpKbjvp3maPXee3VeE0inuo6UvWdMJD1SHmh_w1KRX49OLdgE.I9vy7o0Q9FssJP9Coc.mAxxM0zWWXOH3u33nc7cm5N4tS93dchJtxd5mRrmRVvPamhai1QjbXHIHnKI42ki2WMjspar_R7e_koNU_NSAkKIb71tiYEr3Pqzg2ApE1EXJx7NcAP59mMMkkYsPVwI40ru_Re20wjwEKcSCGqcoNF8YKlKKwktYeFPyEs9XvTuGL3LOOiwgh_6LPGPCgx3kUkQr0iVrjbJKsW7pUdUezqdVvSQwDL.SAEmhoOA1onF7YW32On77qHl217AE6v2lI9Sf8m_DtZVcEm4.JkA1LBe2iE3kw_wrL5VoyrpHhva4n34gK0m3wCiF8koDgLAT0CVZLShswI8VbLSS3XHshMv4PGXAqBIyzLgVGIG6t0vl58u6Q.6jWYcAt.F1phAdfWdG.TsNFAmXVfX4YLcwVmQH6J5bnyHeY6vqMRa0p1JzNNmffrYz_.VUSUCzLJVVGBPM6HbcoMAvIXiX2BvG6qZMMkw2DCqfgvMr_RB27K18yrhgaGbQ1E9yvB.FtyVGOsq69RXnpV3aPc6d4vOVFXgRa7E4VnzE9CISkAL4C3vtc1teLldUoQc7.wyAk3n5GnFrEZ.qF9_U2ZfR0emZfRjLHsKfc2lByA72Azv0CoMgKEpFymz3b6dizvW6K9btlmxyHNVzuuFg6Y2Lo7FU-~A|C6842c07c|SJ7TIm_.2Tqhng.10OsyiZ82s5rkti1.AMqV5zThahuYBFk2emEgNRbhTas.q5IVMDnia178XQfbSHcJsDt.gdNFCBwmiiaIWPZZJcfcXKwhl9YZh4GXBUlMxUskarmdJNtDSD7CIoArfcdMN_TH5FMWcZSIcgFdaWKP14JsrUvOQXJqbcfakE2E5vYZb352nOqqtVaI7gXUDzgPna2mMCUaNq6rJcp9U.fjZepxdgmRWrKfJCFZ3knYuvH5be5p4KTrFcLwdGLGlVdJOtQr_GzIB_2Q_D.Siu93AQ2sK_coAWT.LKyWy1Ltnsw6TlCUZ14mhesXdtWrj6boYnSjpkDyWcQLWAC1MAsQK3c1u59y8rs2.uJOLgRhyHmVdq5kAToUMbRLt.U_pESLeSFGZOnJF2GpNvBNuNlogwVtrZ9PlCfMm7aK0meltlWpQTzIqA02Q7SszfODyIjnDM9KaxQv6mZu8CUbgXLBh9WVFx8_oRsWa_HDgOc6p7VwmS2ZSHzaDUiqgZO_gNjTNcZ9k8SDYNpsSQKOGNVB5dsXjNvaDOSY1w4_9YebINiDuz54PXll1fLx8MDGB1CElvTtgSx2rXFEb0S4kYvOALaig_SZop9hiS.gfBzsJUyjXac1OwUdz_hcNAtqmVjlMfwn98oFwFm2Vkat9c_3rhFVjxUNhIgiX.AsfvaXKML3pnPKR0MpaUhNPiDn1mLYRFBvKmJCmiMzyzuXnmPklT8Br.L8WcZrF.nFbKoSkHhSgWqooxYU65PikKmQ4dDKnLheGo45MQoRvLnNT22.N4ADlSdnx6f7XAD6YcqlxVRq5gQwnR8JI50k_3jkyCrgJdXEZ6RlRoIAtQROIwTsvw1ciykcK59s8j.mdXIA3CNg0smt6cTeY1mTzEFyrKh0gM.quSQ9hFyZWIbhmNYhTVlX7Xxx5M2l9FYjCGO0nSoCEbqDmTqL.gOgtjIGurtPZxChE88UiY0teEu_g9XG5_Yf.iSicSFzzlsENM3OMEuGX4La35NJs9h.0U4G0JFBf2kix6mihI5gQxWpHbhyLqj5HOcckOMAlr2PaYesImRWlEDvV.njT6ovL0pHbUMd2xBHOdjsSF54RAiYafesCbHMClwhKCaAt8_CSB53_CacxePUxB8M~A',
    }  
    headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.8',
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
    'cookie': 'weathergeo=%2223.03%7C72.60%7CAhmedabad%7CGJ%7CIndia%7C0%7C29219630%22; GUCS=ATblFArI; GUC=AQEBCAFoQrxoa0IdaQRU&s=AQAAAGsKHyP7&g=aEFsow; A1=d=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA; A3=d=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA; A1S=d=AQABBJe4NmgCEBTQJcSiUU8hK1heOS9q1ZQFEgEBCAG8QmhraFkPyyMA_eMDAAcIl7g2aC9q1ZQ&S=AQAAAoiOJ3tjABbT2_6BqH26jZA; AS=v=1&s=fXGl2fuE&d=A6842c084|F5fkZcH.2TqOx3FZQHYR78BUZeJI_FqoQp7D_hT_9FBgPAdv72mhDn0T4qAh.G4DiOz6G5x.Db7R0hozzE7lQGWzzi5POuVvkYuuwqa6f1P0kRPp88kHvNMSeblE4N.0YRiOEANnQIH6TzScZQGqqL41DdZeJMgoJM.XLva0gs0DjW9yqKOKMtbSMFdmhH8HiX586Hde2.Rk5OR94LNvPmZcy5RbeuRzIvEyKzXQLe4sPH_Z5aVgCj8h3qG92tYBCRegbcI8xkAXcLmuFw9zpzkxEBngvMSl.388Xp.qWqHACM_3Xzd1.vIbsvs9SAz1uz5hxvXsnPSrshvpoSVIFg1wOeet7xJk45LYG2EI1u1TpkJgU4roBauiBME9L5JA2gQHu6gDMRkcWITbJLuMFtcV9vXQUcfePDlQeozUJSpKbjvp3maPXee3VeE0inuo6UvWdMJD1SHmh_w1KRX49OLdgE.I9vy7o0Q9FssJP9Coc.mAxxM0zWWXOH3u33nc7cm5N4tS93dchJtxd5mRrmRVvPamhai1QjbXHIHnKI42ki2WMjspar_R7e_koNU_NSAkKIb71tiYEr3Pqzg2ApE1EXJx7NcAP59mMMkkYsPVwI40ru_Re20wjwEKcSCGqcoNF8YKlKKwktYeFPyEs9XvTuGL3LOOiwgh_6LPGPCgx3kUkQr0iVrjbJKsW7pUdUezqdVvSQwDL.SAEmhoOA1onF7YW32On77qHl217AE6v2lI9Sf8m_DtZVcEm4.JkA1LBe2iE3kw_wrL5VoyrpHhva4n34gK0m3wCiF8koDgLAT0CVZLShswI8VbLSS3XHshMv4PGXAqBIyzLgVGIG6t0vl58u6Q.6jWYcAt.F1phAdfWdG.TsNFAmXVfX4YLcwVmQH6J5bnyHeY6vqMRa0p1JzNNmffrYz_.VUSUCzLJVVGBPM6HbcoMAvIXiX2BvG6qZMMkw2DCqfgvMr_RB27K18yrhgaGbQ1E9yvB.FtyVGOsq69RXnpV3aPc6d4vOVFXgRa7E4VnzE9CISkAL4C3vtc1teLldUoQc7.wyAk3n5GnFrEZ.qF9_U2ZfR0emZfRjLHsKfc2lByA72Azv0CoMgKEpFymz3b6dizvW6K9btlmxyHNVzuuFg6Y2Lo7FU-~A|C6842c07c|SJ7TIm_.2Tqhng.10OsyiZ82s5rkti1.AMqV5zThahuYBFk2emEgNRbhTas.q5IVMDnia178XQfbSHcJsDt.gdNFCBwmiiaIWPZZJcfcXKwhl9YZh4GXBUlMxUskarmdJNtDSD7CIoArfcdMN_TH5FMWcZSIcgFdaWKP14JsrUvOQXJqbcfakE2E5vYZb352nOqqtVaI7gXUDzgPna2mMCUaNq6rJcp9U.fjZepxdgmRWrKfJCFZ3knYuvH5be5p4KTrFcLwdGLGlVdJOtQr_GzIB_2Q_D.Siu93AQ2sK_coAWT.LKyWy1Ltnsw6TlCUZ14mhesXdtWrj6boYnSjpkDyWcQLWAC1MAsQK3c1u59y8rs2.uJOLgRhyHmVdq5kAToUMbRLt.U_pESLeSFGZOnJF2GpNvBNuNlogwVtrZ9PlCfMm7aK0meltlWpQTzIqA02Q7SszfODyIjnDM9KaxQv6mZu8CUbgXLBh9WVFx8_oRsWa_HDgOc6p7VwmS2ZSHzaDUiqgZO_gNjTNcZ9k8SDYNpsSQKOGNVB5dsXjNvaDOSY1w4_9YebINiDuz54PXll1fLx8MDGB1CElvTtgSx2rXFEb0S4kYvOALaig_SZop9hiS.gfBzsJUyjXac1OwUdz_hcNAtqmVjlMfwn98oFwFm2Vkat9c_3rhFVjxUNhIgiX.AsfvaXKML3pnPKR0MpaUhNPiDn1mLYRFBvKmJCmiMzyzuXnmPklT8Br.L8WcZrF.nFbKoSkHhSgWqooxYU65PikKmQ4dDKnLheGo45MQoRvLnNT22.N4ADlSdnx6f7XAD6YcqlxVRq5gQwnR8JI50k_3jkyCrgJdXEZ6RlRoIAtQROIwTsvw1ciykcK59s8j.mdXIA3CNg0smt6cTeY1mTzEFyrKh0gM.quSQ9hFyZWIbhmNYhTVlX7Xxx5M2l9FYjCGO0nSoCEbqDmTqL.gOgtjIGurtPZxChE88UiY0teEu_g9XG5_Yf.iSicSFzzlsENM3OMEuGX4La35NJs9h.0U4G0JFBf2kix6mihI5gQxWpHbhyLqj5HOcckOMAlr2PaYesImRWlEDvV.njT6ovL0pHbUMd2xBHOdjsSF54RAiYafesCbHMClwhKCaAt8_CSB53_CacxePUxB8M~A',
    }
    params = {
        'validateField': 'userId',
    }
    data = F'browser-fp-data=%7B%22language%22%3A%22en-US%22%2C%22colorDepth%22%3A24%2C%22deviceMemory%22%3A4%2C%22pixelRatio%22%3A1%2C%22hardwareConcurrency%22%3A3%2C%22timezoneOffset%22%3A-330%2C%22timezone%22%3A%22Asia%2FCalcutta%22%2C%22sessionStorage%22%3A1%2C%22localStorage%22%3A1%2C%22indexedDb%22%3A1%2C%22cpuClass%22%3A%22unknown%22%2C%22platform%22%3A%22Win32%22%2C%22doNotTrack%22%3A%22unknown%22%2C%22plugins%22%3A%7B%22count%22%3A4%2C%22hash%22%3A%227ccc5fd5ea228d6b49c9fa7879809a37%22%7D%2C%22canvas%22%3A%22canvas%20winding%3Ayes~canvas%22%2C%22webgl%22%3A1%2C%22webglVendorAndRenderer%22%3A%22Google%20Inc.%20(Intel)~ANGLE%20(Intel%2C%20Intel(R)%20HD%20Graphics%20Direct3D9Ex%20vs_3_0%20ps_3_0%2C%20igdumd64.dll)%22%2C%22adBlock%22%3A0%2C%22hasLiedLanguages%22%3A0%2C%22hasLiedResolution%22%3A0%2C%22hasLiedOs%22%3A0%2C%22hasLiedBrowser%22%3A0%2C%22touchSupport%22%3A%7B%22points%22%3A0%2C%22event%22%3A0%2C%22start%22%3A0%7D%2C%22fonts%22%3A%7B%22count%22%3A29%2C%22hash%22%3A%2290ead5fa1a480b09b5b0239bd273a529%22%7D%2C%22audio%22%3A%22122.82769647920213%22%2C%22resolution%22%3A%7B%22w%22%3A%221680%22%2C%22h%22%3A%221050%22%7D%2C%22availableResolution%22%3A%7B%22w%22%3A%221050%22%2C%22h%22%3A%221680%22%7D%2C%22ts%22%3A%7B%22serve%22%3A1749118716684%2C%22render%22%3A1749118719276%7D%7D&specId=yidregsimplified&context=REGISTRATION&cacheStored=&crumb=v%2FnkkKGtxP3126Cthy3k3A&acrumb=fXGl2fuE&sessionIndex=Qw--&done=https%3A%2F%2Fapi.login.aol.com%2Foauth2%2Fauthorize%3Fclient_id%3Ddj0yJmk9ZXRrOURhMkt6bkl5JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWQ2%26intl%3Dus%26nonce%3DWSbk8RiHKdR86BSpvlDJfvkkiG7yZfSz%26redirect_uri%3Dhttps%253A%252F%252Foidc.www.aol.com%252Fcallback%26response_type%3Dcode%26scope%3Dmail-r%2Bopenid%2Bguce-w%2Bopenid2%2Bsdps-r%26src%3Dfp-us%26state%3DeyJhbGciOiJSUzI1NiIsImtpZCI6IjZmZjk0Y2RhZDExZTdjM2FjMDhkYzllYzNjNDQ4NDRiODdlMzY0ZjcifQ.eyJyZWRpcmVjdFVyaSI6Imh0dHBzOi8vd3d3LmFvbC5jb20vIn0.hlDqNBD0JrMZmY2k9lEi6-BfRidXnogtJt8aI-q2FdbvKg9c9EhckG0QVK5frTlhV8HY7Mato7D3ek-Nt078Z_i9Ug0gn53H3vkBoYG-J-SMqJt5MzG34rxdOa92nZlQ7nKaNrAI7K9s72YQchPBn433vFbOGBCkU_ZC_4NXa9E&googleIdToken=&authCode=&attrSetIndex=0&specData=&deviceCapability=%7B%22pa%22%3A%7B%22status%22%3Afalse%7D%2C%22isWebAuthnSupported%22%3Atrue%7D&tos0=oath_freereg%7Cus%7Cen-US&multiDomain=&asId=752a5565-478d-4203-afbf-957a3c32c115&fingerprintCaptured=&firstName=zuck&lastName=zuck&userid-domain=yahoo&userId={username}&password=&mm=&dd=&yyyy=&signup='
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

ua = UserAgent()
def send_recovery_request(email_or_username):
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
        'x-csrftoken': 'gpexs0wL6nxpdY955MzDDX',
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
            return response_json.get("contact_point", "No Reset")
        else:
            return "No Reset"

    except json.JSONDecodeError:
        return "No Reset"
    except requests.RequestException:
        return "No Reset"

def fetch_instagram_info(username):
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        user_id = profile.userid

        # --- Cookies ---
        cookies = {
            'datr': 'GAgjaB5R_liEM-dpATRTgjMj',
    'ig_did': '114B8FDB-7673-4860-A1D8-E88C655B9DD8',
    'dpr': '0.8999999761581421',
    'ig_nrcb': '1',
    'ps_l': '1',
    'ps_n': '1',
    'mid': 'aDaRiAALAAFk8TVh8AGAIMVtWO_F',
    'csrftoken': 'Pf0Us3q173jfLfTXAurrhCD8uY5KpFlf',
    'sessionid': '5545662104%3ATSmn4hQ082l5P1%3A2%3AAYdgDg9lyWSjzgnPCVk1bq0ogWmJjNH02sYain8odg',
    'ds_user_id': '5545662104',
    'rur': '"CCO\\0545545662104\\0541780482031:01fe59951bea304f73b32ce132b23d925ca281eeb01ddba97d4b7472f2a926a47fb2c657"',
    'wd': '1160x865',
        }

        # --- Headers ---
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
    'cookie': 'datr=GAgjaB5R_liEM-dpATRTgjMj; ig_did=114B8FDB-7673-4860-A1D8-E88C655B9DD8; dpr=0.8999999761581421; ig_nrcb=1; ps_l=1; ps_n=1; mid=aDaRiAALAAFk8TVh8AGAIMVtWO_F; csrftoken=Pf0Us3q173jfLfTXAurrhCD8uY5KpFlf; sessionid=5545662104%3ATSmn4hQ082l5P1%3A2%3AAYdgDg9lyWSjzgnPCVk1bq0ogWmJjNH02sYain8odg; ds_user_id=5545662104; rur="CCO\\0545545662104\\0541780482031:01fe59951bea304f73b32ce132b23d925ca281eeb01ddba97d4b7472f2a926a47fb2c657"; wd=1160x865',
        }
        params = {
            'appid': 'com.bloks.www.ig.about_this_account',
    'type': 'app',
    '__bkv': 'f4e32caf235c4c3198ceb3d7599c397741599ea3447ec2f785d4575aeb99766b',
        }

        # --- Data ---
        data = {
            '__d': 'www',
    '__user': '0',
    '__a': '1',
    '__req': '1d',
    '__hs': '20242.HYP:instagram_web_pkg.2.1...0',
    'dpr': '1',
    '__ccg': 'EXCELLENT',
    '__rev': '1023420941',
    '__s': 'mkhoq1:r5bbtn:4f72rn',
    '__hsi': '7511665972145784373',
    '__dyn': '7xeUjG1mxu1syaxG4Vp41twWwIxu13wvoKewSAwHwNw9G2Saxa0DU6u3y4o0B-q1ew6ywMwto2awgo9oO0n24oaEnxO1ywOwv89k2C1Fwc60D82IzXw8W58jwGzEaE2iwNwh8lwuEjUlwhEe88o5i7U1oEbUGdG1QwTU9UaQ0z8c86-3u2WE5B08-269wr86C1mgcEed6goK3ibK5V89FbxG1oxe6UaU3cyUC4o16UsxWaCw',
    '__csr': 'giMriN4bMpRNdgBsAj4lEZPpdORQOhrlbq8-jiXkKVSiilzakJ1a8ye-HyOlGXjFlQFfSQmyeAKCuHAKjAG-_hkCXx3XF5O9bRpbGF4AAKqT-maCx2VpDGXBCWyZBUGu4XQUGi49mECvFJ2kV-8zQ5qGAJaEWUybgSdDhUH8UD-FqKidixKUOibwyU-UK4EBoGV9ah801iHGppQPsU3-O0l-Pu1pwTx60-qwyx74Qu2p38nK4bDRwiE8Q0Y4489A2eieoCfhSi6poqxwjoty8y9y8Gq1WgcUCgAUW15xaE8kdzEao4Ou8yF202uE25w9y0eug12E0wi12x62p06PBgdEuhGAh4je3sEdQ2oMaUf8hxqu0HE35w4Oxi2p0EzQ1sQ0HQaxh1i7E6-gCq6E8U9E9EaA0aVwbu2S0n60qFF0zg38wUyrDx60QU4W1PxB3awGm5Gw1G_w0gyU2dQhm58qwfS3m1yw5-wba-rDweR0EBBm0UEG02duqu0VK2W',
    '__hsdp': 'geKohbbdET48hr6N5eSb2UgBYBJPI8h6waQqy_lEbmxsy2KBc4p5MXha14wbQgQhzSRaabDVOzoaojzk1Bh20XwwrK74fwto0AOext0dWi09Iw3Q82Awd60GU2Rw9a0TF80Ki0oK2u2S3y',
    '__hblp': '0mUO14AwAwywzgaU5C2ecxieyaG5o4q1RghVby8hyECiiUOi2eazFp8aEOqUO69ul1O2J4KqUqK9WGquujyohXJ1eV8DAgaoK7Erx2cxGmcwMAp4bxF7DCBVVUOU22Ax2dBAAypWxaWQFWxm0A9E4Gi48-bwZG0DSbw4LyUkxu1jxGewh9Q6UC584m3W0mW3q2i1xwqUpxW2K7omzU8A7FF8hw9SdwWwWwVBwKwwwgE4ai3q5Uy3Wi1JwGwhocobOx62i3Ci5ojg8ElwyAwGyEiK4o-2m8y8iwlVEnU-49oy2a5E-2y7olgqK2iEixG26lGmh4gjUaUny8',
    '__comet_req': '7',
    'fb_dtsg': 'NAfsDP_3Ms4Sn_-GxQcIT0KzN63VlOA65NrxQPba87bSn5FMjWsKzVg:17843671327157124:1748946019',
    'jazoest': '26126',
    'lsd': 'AW4NVFnjwlH5ihnj2Xh_E3',
    '__spin_r': '1023420941',
    '__spin_b': 'trunk',
    '__spin_t': '1748946023',
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

        # Extract details
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

        # Extract country
        country = re.search(r'"initial"\s*:\s*"([^"]+)"', response.text)
        country = country.group(1) if country else "N/A"
        reset_email = send_recovery_request(username)
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
                    if gmail_result is None:
                        reset_check = "❌ Unable to check Gmail"
                    elif gmail_result.get("available"):
                        reset_check = "Gmail is ✅ Available"
                    else:
                        reset_check = "Gmail is ❌ Taken"
                elif "a**" in domain:
                    reset_check = f"AOL is {(result)}"
                else:
                    reset_check = "Unknown domain"
            else:
                reset_check = "🔐 Reset is different"

        result_msg = f"""
══════════════════════════════        
🌟 𝗜ɢ 𝗙ᴇᴛᴄʜᴇʀ 𝗙ʀᴏᴍ <b>ᎮᗯᑎᗩGƐ | Ѵᴏʀᴛᴇx •</b> 🌟
══════════════════════════════
✨ <b>{'Username'.ljust(23)}</b> ➟ <code>{profile.username}</code>
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
        return f"USERNAME NOT FOUND OR API ERROR PLEASE CONTACT THE OWNER FOR FURTHER INFORMATION"
import time
import re
from telegram import Update, ChatAction
from telegram.ext import CallbackContext

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

    username = context.args[0].strip().lstrip("@")
    if not re.match(r'^[a-zA-Z0-9._]{1,30}$', username):
        update.message.reply_text("❌ Invalid username format. Only letters, numbers, dots, and underscores allowed.")
        return

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    time.sleep(10)  # 10-second delay

    contact_point = send_recovery_request(username)

    username_md = escape_markdown(username)
    if contact_point and contact_point != "No Reset":
        recovery_method = "Email" if "@" in contact_point else "Phone"
        status = "✅ Success"
    else:
        contact_point = "Not Found"
        recovery_method = "Unavailable"
        status = "❌ Failed"

    message = (
        f"🔄 *Instagram Reset Info*\n"
        f"👤 *Username:* `{username_md}`\n"
        f"📌 *Status:* `{status}`\n"
        f"📬 *Contact Point:* `{contact_point}`\n"
        f"🛠️ *Recovery Method:* `{recovery_method}`"
    )

    update.message.reply_text(message, parse_mode="MarkdownV2")


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

    print("🤖 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
