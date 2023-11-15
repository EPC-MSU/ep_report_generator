import builtins
import gettext
import logging
import os


logger = logging.getLogger("report_generator")


def install_translation(english: bool) -> None:
    """
    :param english: if True, then the English translation is set.
    """

    dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales")
    if english:
        en = gettext.translation("translation", localedir=dir_path, languages=["en"])
        en.install()
        logger.info("English translation installed")
    else:
        builtins._ = lambda string: string
        logger.info("Russian translation installed")
