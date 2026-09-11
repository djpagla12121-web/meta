from __future__ import annotations

import asyncio
import json
import logging
import random
import re
import string
import time
import uuid
from typing import Optional, Tuple

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = "8602647816:AAFXDQHWxcTtK39kJ6yuk4QkoZhmj1LsVWc"

# ================= URL & API ENDPOINTS =================
TARGET_CREATE_URL = "https://auth.meta.com/login/device-based/register-save-credentials/"
TARGET_CONFIRM_URL = "https://auth.meta.com/api/graphql/"
TEMPMAIL_CREATE_URL = "https://instanttempemail.com/api/create"
TEMPMAIL_INBOX_URL = "https://instanttempemail.com/api/inbox/"

HEADERS_CREATE = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 12; itel S665L Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/x-www-form-urlencoded",
    "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Android WebView";v="152"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "x-asbd-id": "359341",
    "x-fb-lsd": "AdRLdRXnKs4_RAGnmEr-k2XaQu0",
    "origin": "https://auth.meta.com",
    "x-requested-with": "mark.via.gp",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://auth.meta.com/",
    "accept-language": "en-US,en;q=0.9",
    "priority": "u=1, i",
}

HEADERS_CONFIRM = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 12; itel S665L Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/x-www-form-urlencoded",
    "sec-ch-ua-full-version-list": "",
    "sec-ch-ua-platform": '"Android"',
    "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Android WebView";v="152"',
    "x-fb-friendly-name": "FRLConfirmEmailMutation",
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-model": '""',
    "x-asbd-id": "359341",
    "sec-ch-prefers-color-scheme": "light",
    "sec-ch-ua-platform-version": '""',
    "origin": "https://auth.meta.com",
    "x-requested-with": "mark.via.gp",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9,my-MM;q=0.8,my;q=0.7,fr-FR;q=0.6,fr;q=0.5",
    "priority": "u=1, i",
}

HEADERS_TEMPMAIL = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 12; itel S665L Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
    "sec-ch-ua-platform": '"Android"',
    "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Android WebView";v="152"',
    "sec-ch-ua-mobile": "?1",
    "x-requested-with": "mark.via.gp",
    "origin": "https://instanttempemail.com",
    "referer": "https://instanttempemail.com/",
}

BASE_FORM_CREATE = {
    "consent_version": "",
    "contact_point_type": "EMAIL_ADDRESS",
    "csi": "Scd0BS3l-yOix38o6lNKa_kT",
    "date_of_birth": "1993-09-11",
    "device_id": "",
    "fb_encrypted_access_token": "",
    "fb_oidc_access_token": "",
    "first_name": "Ajs",
    "google_id_token": "",
    "has_youth_consent": "false",
    "ig_encrypted_access_token": "",
    "ig_encrypted_auth_header": "",
    "ig_oidc_access_token": "",
    "last_name": "Sjs",
    "opt_into_marketing": "true",
    "password": "#PWD_BROWSER:5:1789066665:AcZQADoMrutQCauVmt6U7oTsG79gSy0TKLevqNqGn6zbyOggVegr2pN886zRpoaPQqwdc+KiHnYeD6XbrYwM2HEU04SfXU8gNNrmKXVZ50rsGbdozTDXzT2YkY1EJoBnG833WcAXL3t80TttfQk=",
    "reg_integrity": "Q8W2BTuKa24cQO_B6qvNeGtvmIjuAiCCCvXaCbgkwfWbqt-rPjXJArjnIu5K2myj2GHMJPPSr6BbjXBUFU17JuiZ3IvWTGB_fpfbXwr1sq6qX5lwBCHho2TWDE4ACpgpKGop91SIXofE0KTu2MBkdW1Ss0D6TG7isv6lz2N1CLlYDcRuoiMmSnzt_3_tNldGlheeYm1KVKQyQckdk6G2PoiceW2vxKWbivZ6HJPdq-QsNs4JB7yqEnYY2B3u6mfepC066IZYhv9ZgWpXIuYUsgim6pBbL6NyF84-UsOy8kYIOZlCHc_2PFK4SRPhdx0RMJipGYiIeb5y-Nwj_VHS1Tc2es-jc6aZ7hlBsBokGAeo-cnYEERpIKXz_OnmFTc48WHp2nMcJxww|kregenc",
    "should_save_credentials": "true",
    "waterfall_id": "701777af-c668-4a8d-976a-0c0f619d807a",
    "caa_event_flow": "ntf",
    "entry_point": "login_home",
    "event_client_time": "1789066665.654",
    "is_kadabra_zero": "false",
    "regulation_jurisdiction": '["BD"]',
    "qpl_join_id": "ff52ee3c05b3ec955",
    "__user": "0",
    "__a": "1",
    "__req": "1q",
    "__rev": "1047214234",
    "lsd": "AdRLdRXnKs4_RAGnmEr-k2XaQu0",
    "jazoest": "22293",
    "__spin_r": "1047214234",
    "__spin_b": "trunk",
    "__spin_t": "1789066629",
    "__jssesw": "1",
}

USER_SESSIONS = {}

def get_main_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton("Create")]], resize_keyboard=True)

def get_cancel_inline():
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")]])

def generate_random_token(length=24):
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))

def parse_meta_response(text: str):
    clean = text.strip()
    if clean.startswith("for (;;);"):
        clean = clean[len("for (;;);"):]
    try:
        return json.loads(clean)
    except Exception:
        return None

def calculate_jazoest(token: str) -> str:
    if not token:
        return "25584"
    return "2" + str(sum(ord(c) for c in str(token)))

def extract_tokens_and_uid(html: str):
    fb_dtsg = ""
    lsd = ""
    actor_id = ""

    dtsg_patterns = [
        r'\["DTSGInitialData",\[\],\{"token":"([^"]+)"\}',
        r'\["DTSGInitData",\[\],\{"token":"([^"]+)"\}',
        r'name="fb_dtsg"\s+value="([^"]+)"',
        r'"token":"(NAf[^"]+)"',
        r'DTSGInitialData.*?\{"token":"([^"]+)"\}',
    ]
    for p in dtsg_patterns:
        m = re.search(p, html)
        if m:
            fb_dtsg = m.group(1)
            break

    lsd_patterns = [
        r'\["LSD",\[\],\{"token":"([^"]+)"\}',
        r'name="lsd"\s+value="([^"]+)"',
        r'"LSD":\{"token":"([^"]+)"\}',
        r'"token":"([0-9a-zA-Z_\-]{20,})"',
    ]
    for p in lsd_patterns:
        m = re.search(p, html)
        if m:
            lsd = m.group(1)
            break

    uid_patterns = [
        r'"ACCOUNT_ID":"(\d+)"',
        r'"USER_ID":"(\d+)"',
        r'"actor_id":"(\d+)"',
        r'"account_id":"(\d+)"',
    ]
    for p in uid_patterns:
        m = re.search(p, html)
        if m and m.group(1) != "0":
            actor_id = m.group(1)
            break

    return fb_dtsg, lsd, actor_id

def classify_create_response(status_code: int, data: Optional[dict], raw_text: str):
    if data is None:
        if "uid" in raw_text:
            m = re.search(r'"uid":\s*"?(\d+)"?', raw_text)
            if m:
                return True, m.group(1)
            return True, "UID detected"
        return False, "Unable to parse response"

    payload = data.get("payload") or {}
    if isinstance(payload, dict) and payload.get("uid"):
        return True, f"{payload.get('uid')}"

    if "error" in data:
        desc = data.get("errorDescription") or data.get("errorSummary") or "Unknown error"
        return False, desc

    return False, "Unknown response"

# ================= TEMP MAIL FUNCTIONS =================
async def create_temp_mail() -> Optional[dict]:
    try:
        async with httpx.AsyncClient(http2=True, timeout=15.0) as client:
            resp = await client.post(TEMPMAIL_CREATE_URL, headers=HEADERS_TEMPMAIL)
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        logging.error(f"Temp mail error: {e}")
    return None

async def poll_temp_mail_otp_realtime(token: str, status_msg, base_text: str, user_id: int, max_retries: int = 20, delay: float = 3.0) -> Tuple[Optional[str], str]:
    inbox_url = f"{TEMPMAIL_INBOX_URL}{token}"
    async with httpx.AsyncClient(http2=True, timeout=15.0) as client:
        for attempt in range(1, max_retries + 1):
            if USER_SESSIONS.get(user_id, {}).get("is_canceled"):
                return None, "CANCELED"

            try:
                await status_msg.edit_text(
                    f"{base_text}\n"
                    f"⏳ **Step 3/4:** Checking inbox for OTP... `(Attempt: {attempt}/{max_retries})`\n"
                    "━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown",
                    reply_markup=get_cancel_inline()
                )
            except BadRequest:
                pass
            except Exception:
                pass

            try:
                resp = await client.get(inbox_url, headers=HEADERS_TEMPMAIL)
                if resp.status_code == 200:
                    data = resp.json()
                    emails = data.get("emails", [])
                    for em in emails:
                        subject = em.get("subject", "")
                        body = (em.get("body_text") or "") + " " + (em.get("body_html") or "")

                        if "Confirm that you're human" in body or "Action needed" in subject:
                            return None, "CHECKPOINT_HUMAN"

                        otp_match = re.search(r'Confirmation code\s*[:\s]*(\d{6})', body, re.IGNORECASE) or re.search(r'\b(\d{6})\b', body)
                        if otp_match:
                            return otp_match.group(1), "SUCCESS"
            except Exception:
                pass
            await asyncio.sleep(delay)
    return None, "TIMEOUT"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_SESSIONS[user_id] = {"state": "NONE", "is_canceled": False}
    await update.message.reply_text(
        "👋 **Welcome!**\n\nClick the **'Create'** button below to create and confirm an account automatically:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "cancel_action":
        if user_id in USER_SESSIONS:
            USER_SESSIONS[user_id]["is_canceled"] = True
            USER_SESSIONS[user_id]["state"] = "NONE"
        try:
            await query.edit_message_text("❌ **Process has been cancelled.**", parse_mode="Markdown")
        except Exception:
            pass

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in USER_SESSIONS:
        USER_SESSIONS[user_id] = {"state": "NONE", "is_canceled": False}

    if text == "Create":
        USER_SESSIONS[user_id]["state"] = "PROCESSING"
        USER_SESSIONS[user_id]["is_canceled"] = False

        status_msg = await update.message.reply_text(
            "⚡ **REAL-TIME ACCOUNT CREATOR**\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "⏳ **Step 1/4:** Generating Temp Mail...\n"
            "━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=get_cancel_inline(),
            parse_mode="Markdown"
        )

        # 1. Create Temp Mail
        temp_data = await create_temp_mail()
        if not temp_data or "address" not in temp_data:
            USER_SESSIONS[user_id]["state"] = "NONE"
            try:
                await status_msg.edit_text("❌ Failed to generate Temp Mail! Please try again.")
            except Exception:
                pass
            return

        temp_email = temp_data["address"]
        temp_token = temp_data.get("token")

        if USER_SESSIONS[user_id].get("is_canceled"):
            return

        dashboard_step1 = (
            "⚡ **REAL-TIME ACCOUNT CREATOR**\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ **Step 1:** Temp Mail ready:\n"
            f"📧 **Email:** `{temp_email}`\n\n"
            f"⏳ **Step 2/4:** Creating Meta Account...\n"
            "━━━━━━━━━━━━━━━━━━━━━"
        )
        try:
            await status_msg.edit_text(dashboard_step1, parse_mode="Markdown", reply_markup=get_cancel_inline())
        except Exception:
            pass

        # 2. Meta Account Creation
        data = dict(BASE_FORM_CREATE)
        data["contact_point"] = temp_email
        data["redirect_uri"] = (
            "https://auth.meta.com/recover/success/?redirect_uri="
            "https%3A%2F%2Fauth.meta.com%2Foidc%3Fapp_id%3D1522763855472543"
        )

        try:
            async with httpx.AsyncClient(http2=True, timeout=30.0) as client:
                resp = await client.post(TARGET_CREATE_URL, headers=HEADERS_CREATE, data=data)

            raw_text = resp.text
            parsed = parse_meta_response(raw_text)
            success, reason = classify_create_response(resp.status_code, parsed, raw_text)

            response_cookies = dict(resp.cookies)

            full_cookie_dict = {
                "datr": generate_random_token(24),
                "ps_l": "1",
                "ps_n": "1",
                "locale": "en_GB"
            }
            for k, v in response_cookies.items():
                full_cookie_dict[k] = v

            cookie_str = "; ".join([f"{k}={v}" for k, v in full_cookie_dict.items()])

            extracted_uid = ""
            if parsed and isinstance(parsed.get("payload"), dict):
                extracted_uid = str(parsed["payload"].get("uid", ""))
            elif success and reason.isdigit():
                extracted_uid = reason

            if not success or not extracted_uid:
                USER_SESSIONS[user_id]["state"] = "NONE"
                fail_card = (
                    "❌ **ACCOUNT CREATION FAILED!**\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📧 **Email:** `{temp_email}`\n"
                    f"⚠️ **Reason:** {reason}\n"
                    "━━━━━━━━━━━━━━━━━━━━━"
                )
                try:
                    await status_msg.edit_text(fail_card, parse_mode="Markdown")
                except Exception:
                    pass
                return

            saved_csi = BASE_FORM_CREATE["csi"]
            saved_wf = BASE_FORM_CREATE["waterfall_id"]

            confirm_link = (
                "https://auth.meta.com/register/confirm/?redirect_uri=https%3A%2F%2Fauth.meta.com%2Foidc%2F%3Fapp_id%3D1522763855472543"
                f"&waterfall_id={saved_wf}&csi={saved_csi}&event_flow=login_manual"
            )
            check_headers = dict(HEADERS_CONFIRM)
            check_headers["Cookie"] = cookie_str
            check_headers["referer"] = confirm_link

            live_dtsg, live_lsd, page_uid = "", "", ""
            try:
                async with httpx.AsyncClient(http2=True, timeout=15.0, follow_redirects=True) as client:
                    conf_res = await client.get(confirm_link, headers=check_headers)
                    live_dtsg, live_lsd, page_uid = extract_tokens_and_uid(conf_res.text)
            except Exception:
                pass

            final_uid = extracted_uid or page_uid

            if USER_SESSIONS[user_id].get("is_canceled"):
                return

            # Live Update: Account Created, Polling OTP
            dashboard_step2 = (
                "⚡ **REAL-TIME ACCOUNT CREATOR**\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ **Step 1:** Email: `{temp_email}`\n"
                f"✅ **Step 2:** Account Created! `(UID: {final_uid})`\n"
            )

            otp_code, status_otp = await poll_temp_mail_otp_realtime(
                temp_token, status_msg, dashboard_step2, user_id, max_retries=20, delay=3.0
            )

            if USER_SESSIONS[user_id].get("is_canceled"):
                return

            if status_otp == "CHECKPOINT_HUMAN":
                USER_SESSIONS[user_id]["state"] = "NONE"
                checkpoint_msg = (
                    "⚠️ **HUMAN VERIFICATION CHECKPOINT!**\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📧 **Email:** `{temp_email}`\n"
                    f"🆔 **UID:** `{final_uid}`\n\n"
                    "Meta requested 'Confirm that you are human' for this address.\n"
                    "━━━━━━━━━━━━━━━━━━━━━"
                )
                try:
                    await status_msg.edit_text(checkpoint_msg, parse_mode="Markdown")
                except Exception:
                    pass
                return

            elif not otp_code:
                USER_SESSIONS[user_id]["state"] = "NONE"
                timeout_msg = (
                    "⚠️ **OTP TIMEOUT!**\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📧 **Email:** `{temp_email}`\n"
                    f"🆔 **UID:** `{final_uid}`\n"
                    "Meta did not deliver the code in time.\n"
                    "━━━━━━━━━━━━━━━━━━━━━"
                )
                try:
                    await status_msg.edit_text(timeout_msg, parse_mode="Markdown")
                except Exception:
                    pass
                return

            # Live Update: OTP Found, Confirming
            dashboard_step3 = (
                "⚡ **REAL-TIME ACCOUNT CREATOR**\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ **Step 1:** Email: `{temp_email}`\n"
                f"✅ **Step 2:** UID: `{final_uid}`\n"
                f"✅ **Step 3:** OTP Code received: `{otp_code}` 🔥\n\n"
                "⏳ **Step 4/4:** Confirming Meta Account...\n"
                "━━━━━━━━━━━━━━━━━━━━━"
            )
            try:
                await status_msg.edit_text(dashboard_step3, parse_mode="Markdown")
            except Exception:
                pass

            # 3. Confirm OTP
            fb_dtsg = live_dtsg or "NAfw3-iVgzAwb3wze6-QRU-d6X36d-knUVwny-8I9gCaoBHl9mph0_A:16:1789089771"
            lsd = live_lsd or "mVvZ2A2krrrCYh31NtUS0j"
            jazoest = calculate_jazoest(fb_dtsg)
            qpl_join_id = f"f{''.join(random.choices('0123456789abcdef', k=16))}"

            variables_payload = {
                "input": {
                    "confirmation_code": {"sensitive_string_value": str(otp_code)},
                    "confirmation_code_type": "OTP_CODE",
                    "event_flow": "login_manual",
                    "rl_client_session_id": saved_csi,
                    "waterfall_id": saved_wf,
                    "source_app_id": "1522763855472543",
                    "qpl_join_id": qpl_join_id,
                    "actor_id": str(final_uid),
                    "client_mutation_id": "1",
                }
            }

            form_data = {
                "av": str(final_uid),
                "__user": "0",
                "__a": "1",
                "__req": "g",
                "__hs": "20707.HYP:frl_comet_auth_pkg.2.1...0",
                "dpr": "2",
                "__ccg": "MODERATE",
                "__rev": "1047236770",
                "__s": "le1ban:0ytxdz:jokh1r",
                "__hsi": str(random.randint(7000000000000000000, 7999999999999999999)),
                "__dyn": "7xeUmwlEnwn8K2Wmh0no6u5U4e0yoW3q32360CEbo1nEhw2nVE4W099w8G1Dz81s8hwnU2lwv89k2C1Fwc60D82IzXwae4UaEW0Loco5G0zK1swa-0raazo7u0zE2ZwrU6C0hq1Iwqo5u1qwUw8S1Tw8q0JU0Vy3mew",
                "__csr": "g_8BH89a--KgUACXB99ilbbb428kDxeczoC6Vpu4HBQ2CbGaw1kq0ty0dDw0JQ7FAhp21CuexetoaE2KwiUd8mzX9Ax25E8U06sG00g9y013jwSDwcWkAw0k_wb20qisCEjw7N-0eBw27E3NwXz82BxK0gUw0Jl4wmQ3K69VU1yA9w2fO0fe06sEgyVU04Nx1mfo2cw2B10O2x0",
                "__hsdp": "gd5ZN4qQbQEjg0b_o1E806b4w0DG06HU",
                "__hblp": "09G6e0ti029C581uo09ZU04ny0l-06HU0wi2u17xyfwtU0pQw8W0fTw8e0bZw31o",
                "__sjsp": "gd5ZN4BOd2Za4Q",
                "__comet_req": "33",
                "fb_dtsg": fb_dtsg,
                "jazoest": jazoest,
                "lsd": lsd,
                "__spin_r": "1047236770",
                "__spin_b": "trunk",
                "__spin_t": str(int(time.time())),
                "__jssesw": "1",
                "fb_api_caller_class": "RelayModern",
                "fb_api_req_friendly_name": "FRLConfirmEmailMutation",
                "server_timestamps": "true",
                "variables": json.dumps(variables_payload, separators=(',', ':')),
                "doc_id": "9851798224911796",
            }

            headers_conf = dict(HEADERS_CONFIRM)
            headers_conf["Cookie"] = cookie_str
            headers_conf["x-fb-lsd"] = lsd
            headers_conf["referer"] = confirm_link

            async with httpx.AsyncClient(http2=True, timeout=30.0) as client:
                conf_response = await client.post(TARGET_CONFIRM_URL, headers=headers_conf, data=form_data)

            res_parsed = parse_meta_response(conf_response.text)
            confirm_info = (res_parsed.get("data") or {}).get("confirm_email") or {}

            USER_SESSIONS[user_id]["state"] = "NONE"

            # 4. Final Output Card
            if confirm_info.get("isConfirmed") is True:
                confirmed_acc_id = confirm_info.get("accountId", final_uid)
                final_dashboard = (
                    "🎉 **ACCOUNT CREATED & CONFIRMED!**\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ Step 1 (Email): `{temp_email}`\n"
                    f"✅ Step 2 (UID): `{confirmed_acc_id}`\n"
                    f"✅ Step 3 (OTP Code): `{otp_code}`\n"
                    "✅ Password arafat@@## 🟢\n"
                    "━━━━━━━━━━━━━━━━━━━━━"
                )
            else:
                final_dashboard = (
                    "⚠️ **ACCOUNT CREATED BUT OTP NOT CONFIRMED!**\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ Step 1 (Email): `{temp_email}`\n"
                    f"✅ Step 2 (UID): `{final_uid}`\n"
                    f"✅ Step 3 (OTP Code): `{otp_code}`\n"
                    "✅ Password arafat@@## 🟢\n"
                    "━━━━━━━━━━━━━━━━━━━━━"
                )

            try:
                await status_msg.edit_text(final_dashboard, parse_mode="Markdown")
            except Exception:
                pass

        except Exception as e:
            USER_SESSIONS[user_id]["state"] = "NONE"
            try:
                await status_msg.edit_text(f"❌ Error: {e}")
            except Exception:
                pass
        return

    await update.message.reply_text("Please click the **'Create'** button below to start.", reply_markup=get_main_keyboard())

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Exception while handling update:", exc_info=context.error)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    app.add_error_handler(error_handler)
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()