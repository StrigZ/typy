from gi.repository import Gtk
from learning_progress import LEARNING_ORDER
from app_settings import get_app_settings

app_settings = get_app_settings()


class LearningProgressUI(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(halign=Gtk.Align.CENTER, **kwargs)

        self._char_boxes: dict[str, Gtk.Box] = {}
        self._char_labels: dict[str, Gtk.Label] = {}
        self._providers: dict[str, Gtk.CssProvider] = {}
        self._build_ui()

        app_settings.connect("notify::string-language", self._on_language_change)

    def update(self, active_chars: list[str], proficiencies: dict[str, float]):
        active_set = set(active_chars)
        for char, box in self._char_boxes.items():
            if char not in active_set:
                css = ".learning-char { background-color: alpha(currentColor, 0.35); }"
            else:
                color = self._proficiency_color(proficiencies.get(char, 0.0))
                css = f".learning-char {{ background-color: {color}; }}"
            self._providers[char].load_from_data(css.encode())

    def _proficiency_color(self, proficiency: float) -> str:
        # proficiency: 0.0 (worst/red) to 1.0 (best/green)
        proficiency = max(0.0, min(1.0, proficiency))
        r = int(155 * (1 - proficiency))
        g = int(155 * proficiency)
        return f"rgb({r},{g},60)"

    def _build_ui(self):
        for char in LEARNING_ORDER[app_settings.string_language]:
            box = Gtk.Box(css_classes=["learning-char"])
            label = Gtk.Label(
                label=char, width_chars=2, css_classes=["learning-char-text"]
            )
            provider = Gtk.CssProvider()
            box.get_style_context().add_provider(
                provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            box.append(label)

            self._char_boxes[char] = box
            self._char_labels[char] = label
            self._providers[char] = provider
            self.append(box)

    def _on_language_change(self, obj, _pspec):
        child = self.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            self.remove(child)
            child = next_child

        self._char_boxes.clear()
        self._char_labels.clear()
        self._providers.clear()
        self._build_ui()
