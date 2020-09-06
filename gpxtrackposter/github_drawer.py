# Copyright 2020 Florian Pigorsch & Contributors. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import calendar
import datetime
import locale

import svgwrite  # type: ignore

from gpxtrackposter import utils
from gpxtrackposter.exceptions import PosterError
from gpxtrackposter.poster import Poster
from gpxtrackposter.tracks_drawer import TracksDrawer
from gpxtrackposter.xy import XY


class GithubDrawer(TracksDrawer):
    """Draw a gtihub profile-like poster"""

    def __init__(self, the_poster: Poster):
        super().__init__(the_poster)

    def draw(self, dr: svgwrite.Drawing, size: XY, offset: XY) -> None:
        if self.poster.tracks is None:
            raise PosterError("No tracks to draw")
        year_size = 200 * 4.0 / 80.0
        year_style = f"font-size:{year_size}px; font-family:Arial;"
        year_length_style = f"font-size:{110 * 3.0 / 80.0}px; font-family:Arial;"
        month_names_style = "font-size:2.5px; font-family:Arial"
        total_length_year_dict = self.poster.total_length_year_dict
        for year in self.poster.years.iter():
            start_date_weekday, _ = calendar.monthrange(year, 1)
            github_rect_first_day = datetime.date(year, 1, 1)
            # Github profile the first day start from the last Monday of the last year or the first Monday of this year
            # It depands on if the first day of this year is Monday or not.
            github_rect_day = github_rect_first_day + datetime.timedelta(-start_date_weekday)
            year_length = total_length_year_dict.get(year, 0)
            year_length_str = utils.format_float(self.poster.m2u(year_length))
            month_names = [
                locale.nl_langinfo(day)[:3]  # Get only first three letters
                for day in [
                    locale.MON_1,
                    locale.MON_2,
                    locale.MON_3,
                    locale.MON_4,
                    locale.MON_5,
                    locale.MON_6,
                    locale.MON_7,
                    locale.MON_8,
                    locale.MON_9,
                    locale.MON_10,
                    locale.MON_11,
                    locale.MON_12,
                ]
            ]
            km_or_mi = "mi"
            if self.poster.units == "metric":
                km_or_mi = "km"
            dr.add(
                dr.text(
                    f"{year}",
                    insert=offset.tuple(),
                    fill=self.poster.colors["text"],
                    alignment_baseline="hanging",
                    style=year_style,
                )
            )

            dr.add(
                dr.text(
                    f"{year_length_str} {km_or_mi}",
                    insert=(offset.tuple()[0] + 165, offset.tuple()[1] + 2),
                    fill=self.poster.colors["text"],
                    alignment_baseline="hanging",
                    style=year_length_style,
                )
            )
            # add month name up to the poster one by one because of svg text auto trim the spaces.
            for num, name in enumerate(month_names):
                dr.add(
                    dr.text(
                        f"{name}",
                        insert=(offset.tuple()[0] + 15.5 * num, offset.tuple()[1] + 14),
                        fill=self.poster.colors["text"],
                        style=month_names_style,
                    )
                )

            rect_x = 10.0
            dom = (2.6, 2.6)
            # add every day of this year for 53 weeks and per week has 7 days
            for _i in range(54):
                rect_y = offset.y + year_size + 2
                for _j in range(7):
                    if int(github_rect_day.year) > year:
                        break
                    rect_y += 3.5
                    color = "#444444"
                    date_title = str(github_rect_day)
                    if date_title in self.poster.tracks_by_date:
                        tracks = self.poster.tracks_by_date[date_title]
                        length = sum([t.length for t in tracks])
                        distance1 = self.poster.special_distance["special_distance"]
                        distance2 = self.poster.special_distance["special_distance2"]
                        has_special = distance1 < length / 1000 < distance2
                        color = self.color(self.poster.length_range_by_date, length, has_special)
                        if length / 1000 >= distance2:
                            special_color = self.poster.colors.get("special2") or self.poster.colors.get("special")
                            if special_color is not None:
                                color = special_color
                        str_length = utils.format_float(self.poster.m2u(length))
                        date_title = f"{date_title} {str_length} {km_or_mi}"

                    rect = dr.rect((rect_x, rect_y), dom, fill=color)
                    rect.set_desc(title=date_title)
                    dr.add(rect)
                    github_rect_day += datetime.timedelta(1)
                rect_x += 3.5
            offset.y += 3.5 * 9 + year_size + 1.5