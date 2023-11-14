import gettext
import logging
import os
from typing import Callable


logger = logging.getLogger("report_generator")


def install_translation(english: bool) -> Callable[[str], str]:
    dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales")
    if english:
        en = gettext.translation("translation", localedir=dir_path, languages=["en"])
        en.install()
        _ = en.gettext
        logger.info("English translation installed")
    else:

        def return_string(string: str) -> str:
            return string

        _ = return_string
    return _
