from datetime import datetime

from tornkts.utils import to_int


def now_ts():
    return to_int(datetime.now().timestamp() * 1000)
