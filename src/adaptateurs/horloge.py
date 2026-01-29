import datetime as dt
from typing import Callable


class Horloge:
    _maintenant: Callable[[], dt.datetime] = dt.datetime.now

    @staticmethod
    def maintenant() -> dt.datetime:
        return Horloge._maintenant()

    @staticmethod
    def frise(instant: dt.datetime) -> None:
        Horloge._maintenant = lambda: instant

    @staticmethod
    def reinitialise() -> None:
        Horloge._maintenant = dt.datetime.now


class AdaptateurHorloge:
    @staticmethod
    def maintenant() -> dt.datetime:
        return Horloge.maintenant()
