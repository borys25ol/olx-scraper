import re


def clean_text(s):
    cleaned = s.strip()
    cleaned = re.sub(r"(?is)<(style).*?>.*?(</\1>)", u"", cleaned)
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", u"", cleaned)
    cleaned = re.sub(r"(?s)<.*?>", u" ", cleaned)
    cleaned = re.sub(r"&nbsp;", u" ", cleaned)
    cleaned = re.sub(r"\xa0", u" ", cleaned)
    cleaned = re.sub(r"\u2009", u" ", cleaned)
    cleaned = re.sub(r"  ", u" ", cleaned)
    cleaned = re.sub(r"  ", u" ", cleaned)
    return cleaned.strip()


def clean_spaces(s):
    cleaned = re.sub(r"[\r\n\t]+", u" ", s)
    cleaned = re.sub(r"  ", u" ", cleaned)
    cleaned = re.sub(r"  ", u" ", cleaned)
    return cleaned.strip()
