from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

from fuzzywuzzy import process

from hordeqt.classes.Job import Job
from hordeqt.classes.Style import Style

if TYPE_CHECKING:
    from hordeqt.app import HordeQt


class StyleLibrary:
    styles: Dict[str, Style] = {}

    def __init__(self, styles: List[Style], parent: HordeQt):
        self.add_styles(styles)
        self.parent = parent

    def add_styles(self, styles: List[Style]):
        for s in styles:
            self.add_style(s)

    def add_style(self, s: Style):
        self.styles[s.name] = s

    def update_style(self, s: Style):
        self.styles[s.name] = s

    def apply_style_to_job_data(self, style_name: str, job: Job):
        style = self.get_style(style_name)
        if style is None:
            avail_styles = self.get_available_style_names()
            value = process.extractOne(style_name, avail_styles)
            correction = ""
            if value is not None and value[1] >= 50:
                correction = f' Did you mean "{value[0]}"? '
            self.parent.show_warn_toast(
                f'Couldn\'t find style "{style_name}".', correction
            )
            return job

    def get_available_styles(self):
        return [v for v in self.styles.values()]

    def get_available_style_names(self):
        return [k for k in self.styles.keys()]

    def get_style(self, style_name: str):
        return self.styles.get(style_name)

    def get_user_styles(self):
        return [v for v in self.styles.values() if not v.is_built_in]

    def delete_style(self, style: str | Style) -> bool:
        if isinstance(style, str):
            if self.styles.get(style) is None:
                return False
            self.styles.pop(style)
            return True
        elif isinstance(style, Style):
            return self.delete_style(style.name)
        return False
