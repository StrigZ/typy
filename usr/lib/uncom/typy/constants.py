import gettext
import os

from gi.repository import GLib

# (this is a global path, will not work during local testing)
TEXT_DOMAIN = "typy"
gettext.bindtextdomain(TEXT_DOMAIN, "/usr/share/locale")
gettext.textdomain(TEXT_DOMAIN)
_ = gettext.gettext

APP_DIR = os.path.dirname(os.path.abspath(__file__))
STYLE_CSS = os.path.join(APP_DIR, "style.css")
STATS_FILE = os.path.join(GLib.get_user_data_dir(), "typy", "stats.json")

COMMON_WORDS = ["the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog"]
