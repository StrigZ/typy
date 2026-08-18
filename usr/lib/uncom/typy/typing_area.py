from constants import _
from gi.repository import GLib, Gtk


class TypingArea(Gtk.Overlay):
    def __init__(self, **kwargs):
        super().__init__(
            css_classes=["typing-field-container"], focusable=True, **kwargs
        )
        self._build_ui()

    def blur(self):
        self.remove_css_class("active")
        self.hint_label.set_visible(True)

    def unblur(self):
        self.add_css_class("active")
        self.hint_label.set_visible(False)

    def render(self, string_to_type: str, pointer: int, missed_indices: set[int]):
        parts = []
        for i, ch in enumerate(string_to_type):
            escaped = GLib.markup_escape_text(ch)

            if i < pointer:
                color = "#e53935" if i in missed_indices else "#4caf50"
                parts.append(f'<span foreground="{color}">{escaped}</span>')
            elif i == pointer:
                parts.append(
                    f'<span foreground="#888888" underline="single">{escaped}</span>'
                )
            else:
                parts.append(f'<span foreground="#888888">{escaped}</span>')

        self.string_to_type_label.set_markup("".join(parts))

    def _build_ui(self):
        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=24,
            css_classes=["typing-field"],
        )

        self.string_to_type_label = Gtk.Label(
            css_classes=["string-to-type"], wrap=True, justify=Gtk.Justification.CENTER
        )
        content.append(self.string_to_type_label)

        self.key_display_label = Gtk.Label(css_classes=["key-display"])
        content.append(self.key_display_label)

        self.set_child(content)

        self.hint_label = Gtk.Label(
            label=_("Click or press Enter to start typing"),
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            css_classes=["dim-label"],
        )
        self.add_overlay(self.hint_label)
