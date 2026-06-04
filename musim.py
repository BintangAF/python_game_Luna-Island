
from dataclasses import dataclass
from datetime import date
import calendar
import random

MONTH_NAMES = [
    'januari', 'februari', 'maret', 'april', 'mei', 'juni',
    'juli', 'agustus', 'september', 'oktober', 'november', 'desember'
]


@dataclass
class MonthSeasonState:
    month_index: int
    day: int
    year: int
    base_season: str
    visual_season: str
    is_rainy_day: bool


class MonthSeasonManager:
    """Mengatur bulan, tanggal, musim dasar, dan hujan harian."""

    def __init__(self):
        today = date.today()
        self.year = today.year
        self.month_index = today.month - 1
        self.day = today.day
        self._manual_offset = 0
        self._rng_seed = today.year * 10000 + today.month * 100 + today.day
        self.is_rainy_day = False
        self.roll_daily_weather()

    @property
    def month_number(self):
        return self.month_index + 1

    @property
    def month_name(self):
        return MONTH_NAMES[self.month_index]

    @property
    def date_text(self):
        return f'{self.day:02d}/{self.month_number:02d}/{self.year:04d}'

    @property
    def base_season(self):
        """Musim berdasarkan bulan.

        Desember sampai Februari memakai tema salju.
        September sampai November memakai tema gugur.
        Bulan lain memakai tema normal.
        """
        if self.month_number in (12, 1, 2):
            return 'snow'
        if self.month_number in (9, 10, 11):
            return 'autumn'
        return 'normal'

    @property
    def visual_season(self):
        """Mode visual yang dipakai level.

        Hujan mengubah cuaca secara random per hari.
        Saat tidak hujan, level memakai musim dasar sesuai bulan.
        """
        if self.is_rainy_day:
            return 'rain'
        return self.base_season

    def days_in_month(self):
        return calendar.monthrange(self.year, self.month_number)[1]

    def _clamp_day(self):
        self.day = max(1, min(int(self.day), self.days_in_month()))

    def advance_month(self):
        """Memajukan bulan saat tombol L ditekan."""
        if self.month_index == 11:
            self.month_index = 0
            self.year += 1
        else:
            self.month_index += 1
        self._manual_offset += 1
        self._clamp_day()
        self.roll_daily_weather()
        return self.state()

    def advance_day(self):
        """Memajukan tanggal saat hari game berganti."""
        self.day += 1
        if self.day > self.days_in_month():
            self.day = 1
            if self.month_index == 11:
                self.month_index = 0
                self.year += 1
            else:
                self.month_index += 1
        self.roll_daily_weather()
        return self.state()

    def roll_daily_weather(self):
        """Mengacak hujan untuk hari berjalan."""
        rainy_months = {1, 2, 3, 4, 10, 11, 12}
        chance = 0.42 if self.month_number in rainy_months else 0.18
        seed = (
            self._rng_seed
            + self.year * 17
            + self.month_index * 97
            + self.day * 131
            + self._manual_offset * 503
        )
        rng = random.Random(seed)
        self.is_rainy_day = rng.random() < chance
        return self.is_rainy_day

    def state(self):
        return MonthSeasonState(
            month_index=self.month_index,
            day=self.day,
            year=self.year,
            base_season=self.base_season,
            visual_season=self.visual_season,
            is_rainy_day=self.is_rainy_day,
        )
