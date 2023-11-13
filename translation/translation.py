import gettext
import logging
from typing import Callable


logger = logging.getLogger("report_generator")


def install_translation(english: bool) -> Callable[[str], str]:
    if english:
        en = gettext.translation("report_generator", localedir="locales", languages=["en"])
        en.install()
        _ = en.gettext
        logger.info("English translation installed")
    else:

        def return_string(string: str) -> str:
            return string

        _ = return_string
    return _
