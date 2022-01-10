from datetime import datetime
import hashlib
import warnings

from dateparser import parse

warnings.filterwarnings("ignore")


def parse_date(date_str):
    return parse(date_str, settings={'RETURN_AS_TIMEZONE_AWARE': True,
                                     'RELATIVE_BASE': datetime.now()})


def get_id(link_str):
    _id = hashlib.md5(link_str.encode()).hexdigest()
    return _id
