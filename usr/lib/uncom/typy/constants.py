import gettext
import os

from gi.repository import GLib

from utility import load_word_list

TEXT_DOMAIN = "typy"
gettext.bindtextdomain(TEXT_DOMAIN, "/usr/share/locale")
gettext.textdomain(TEXT_DOMAIN)
_ = gettext.gettext

APP_DIR = os.path.dirname(os.path.abspath(__file__))
STYLE_CSS = os.path.join(APP_DIR, "style.css")

USER_DATA_DIR = os.path.join(GLib.get_user_data_dir(), "typy")
APP_SETTINGS_FILE = os.path.join(USER_DATA_DIR, "user_settings.json")
DAILY_GOAL_FILE = os.path.join(USER_DATA_DIR, "daily_goal.json")

INSTALLED_WORDS_DIR = "/usr/share/uncom/typy/words"

if os.path.exists(os.path.join(INSTALLED_WORDS_DIR, "words_en.csv")):
    WORDS_DIR = INSTALLED_WORDS_DIR
else:
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, "..", "..", "..", ".."))
    WORDS_DIR = os.path.join(PROJECT_ROOT, "usr", "share", "uncom", "typy", "words")

WORD_LIST = load_word_list(os.path.join(WORDS_DIR, "words_en.csv"))

LEARNING_MIN_SAMPLES = 5
LEARNING_ORDER = "ETAOINSRHDLUCMFYWGPBVKXJQZ"
