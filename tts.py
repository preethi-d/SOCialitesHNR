import logging
import os

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from gtts import gTTS

PORT = int(os.environ.get('PORT', 5000))

token = "1590146552:AAHiUBLHNSWzknPRk0rxDV7Fsl5sl4GQuyU"

raw_languages = """af: Afrikaans
ar: Arabic
bn: Bengali
bs: Bosnian
ca: Catalan
cs: Czech
cy: Welsh
da: Danish
de: German
el: Greek
en-au: English (Australia)
en-ca: English (Canada)
en-gb: English (UK)
en-gh: English (Ghana)
en-ie: English (Ireland)
en-in: English (India)
en-ng: English (Nigeria)
en-nz: English (New Zealand)
en-ph: English (Philippines)
en-tz: English (Tanzania)
en-uk: English (UK)
en-us: English (US)
en-za: English (South Africa)
en: English
eo: Esperanto
es-es: Spanish (Spain)
es-us: Spanish (United States)
es: Spanish
et: Estonian
fi: Finnish
fr-ca: French (Canada)
fr-fr: French (France)
fr: French
gu: Gujarati
hi: Hindi
hr: Croatian
hu: Hungarian
hy: Armenian
id: Indonesian
is: Icelandic
it: Italian
ja: Japanese
jw: Javanese
km: Khmer
kn: Kannada
ko: Korean
la: Latin
lv: Latvian
mk: Macedonian
ml: Malayalam
mr: Marathi
my: Myanmar (Burmese)
ne: Nepali
nl: Dutch
no: Norwegian
pl: Polish
pt-br: Portuguese (Brazil)
pt-pt: Portuguese (Portugal)
pt: Portuguese
ro: Romanian
ru: Russian
si: Sinhala
sk: Slovak
sq: Albanian
sr: Serbian
su: Sundanese
sv: Swedish
sw: Swahili
ta: Tamil
te: Telugu
th: Thai
tl: Filipino
tr: Turkish
uk: Ukrainian
ur: Urdu
vi: Vietnamese
zh-CN: Chinese
zh-cn: Chinese (Mandarin/China)
zh-tw: Chinese (Mandarin/Taiwan)"""

languages_names = []
languages = {}

for line in raw_languages.split("\n"):
    a, b = line.split(": ")
    languages[b] = a
    languages_names.append(b)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

language = 'en'
awaiting_choice = False


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def lang_command(update: Update, context: CallbackContext) -> int:
    """Send a message when the command /lang is issues."""
    reply_keyboard = [languages_names]
    update.message.reply_text('Choose the language',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    global awaiting_choice
    awaiting_choice = True


def set_language(update, new_lang):
    if new_lang not in languages:
        update.message.reply_text('Language {} not supported'.format(update.message.text),
                                  reply_markup=ReplyKeyboardRemove())
        return
    logger.info("Language chosen: %s", new_lang)
    update.message.reply_text('Language set to {}'.format(update.message.text),
                              reply_markup=ReplyKeyboardRemove())
    global language, awaiting_choice
    language = languages[new_lang]
    awaiting_choice = False


def text_to_speech(update: Update, context: CallbackContext) -> None:
    """Convert the user message to speech and send the audio message."""
    print(update.message.text)

    global awaiting_choice

    if awaiting_choice:
        return set_language(update, update.message.text)

    tts = gTTS(update.message.text, lang=language)
    tts.save("audio_message.ogg")
    update.message.reply_audio(open("audio_message.ogg", "rb"))


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(CommandHandler('lang', lang_command))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_to_speech))

    # Start the Bot
    updater.start_polling()
    #
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=int(PORT),
    #                       url_path=token)
    # updater.bot.setWebhook('https://fast-meadow-54421.herokuapp.com/' + token)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
