from fpdf import FPDF
from pathlib import Path
from const.const import (
    mean_of_three_events,
)
from util.util import (
    translate_text,
    centiseconds_to_minutes_seconds,
)
import os
from PIL import Image

TEAM_MASTER_IMAGE = Image.open(os.path.join("const", "teamMaster.png"))


class ScoreCard(FPDF):
    PATH_FONTS = os.path.join(os.path.dirname(__file__), "fonts")
    FONTS = {
        "arial-unicode-ms": [
            "Arial-UnicodeMS",
            "",
            os.path.join("fonts", "arial-unicode-ms.ttf"),
        ],
    }

    COLUMN_WIDTHS = [10, 10, 65, 10, 10]
    FONT_SIZE_LARGE = 16
    FONT_SIZE_MEDIUM = 14
    FONT_SIZE_MSMALL = 10
    FONT_SIZE_SMALL = 8

    # POSITIONS = [(0, 0), (105, 0), (0, 140), (105, 140)]
    POSITIONS = [(0, 0), (111, 0), (0, 140), (111, 140)]

    def __init__(
        self,
        lang: str = "es",
        water_mark_path: str = None,
        cuttof: dict = None,
        tournament_name: str = "",
        add_wca_id: bool = False,
    ):
        """Initialize the PDF with the lang, watermark, cuttof and tournament name

        :param lang: The lang object with the language to use in the texts of the PDF
        :type lang: Lang
        :param water_mark_path: The path to the watermark image, defaults to None
        :type water_mark_path: str, optional
        :param cuttof: The cuttof for the one category of the tournament, defaults to None
        :type cuttof: str, optional
        :param tournament_name: The name of the tournament, defaults to None
        :type tournament_name: str, optional
        """
        super().__init__(format="letter")
        self.set_auto_page_break(auto=False, margin=0)
        self.lang = lang
        self.water_mark_path = water_mark_path
        self.cuttof = cuttof
        self.tournament_name = tournament_name
        self.add_wca_id = add_wca_id

        # Add fonts
        for v in self.FONTS.values():
            self.add_font(*v)

    def get_competitor_position(self, competitor_counter: int) -> tuple[int, int]:
        """Calculate the position (x, y) for a competitor card based on the competitor counter.

        :param competitor_counter: The current competitor counter.
        :type competitor_counter: int
        :return: The position (x, y) for the competitor card.
        :rtype: Tuple[int, int]
        """
        return self.POSITIONS[competitor_counter % 4]

    def add_competition_card(
        self,
        competitor_name: str,
        category: str,
        group_num: int,
        total_groups: int,
        competitor_counter: int,
        registrant_id: int = None,
        wca_id: str = None,
        with_cuttof: bool = True,
    ):
        """Add a competition card to the PDF.

        :param competitor_name: The name of the competitor.
        :type competitor_name: str
        :param category: The category of the competition.
        :type category: str
        :param group_num: The group number of the competition.
        :type group_num: int
        :param total_groups: The total number of groups of the competition.
        :type total_groups: int
        :param competitor_counter: The current competitor counter.
        :type competitor_counter: int
        :param wca_id: The WCA ID of the competitor, defaults to None
        :type wca_id: str, optional
        :param with_cuttof: If the cuttof should be added to the card, defaults to True
        :type with_cuttof: bool, optional
        """
        if competitor_counter % 4 == 0:
            self.add_page()
        x, y = self.get_competitor_position(competitor_counter)
        self._add_watermark(x, y)
        self._add_header(x, y)
        self._add_category_info(x, category)
        self._add_round_info(x, group_num, total_groups)
        self._add_competitor_info(
            x=x,
            competitor_name=competitor_name,
            registrant_id=registrant_id,
            wca_id=wca_id,
            with_wca_id=self.add_wca_id,
        )
        self._add_table(x, y, category, with_cuttof)

    def draw_centered_text(
        self,
        x: int,
        text: str = None,
        max_width: int = 210,
        border: bool = False,
        array_text: list = None,
    ):
        """Draw a centered text in the card, with the option to add a border

        :param x: The x position to start the text
        :type x: int
        :param text: The text to add to the card
        :type text: str
        :param max_width: The max width of the text, defaults to 210
        :type max_width: int, optional
        :param border: If the text should have a border, defaults to False
        :type border: bool, optional
        """

        if array_text:
            self.set_x(x)
            for text in array_text:
                text_width = self.get_string_width(text) + 2
                start_x = x + (text["max_width"] - text_width) / 2
                self.set_x(start_x)
                border = 1 if text["border"] else 0
                widht = text["max_width"] if text["border"] else text_width
                self.cell(widht, 10, text["text"], border, 1, "C")

        if max_width == 210:
            total_width = ((x + max_width) - x) / 2
            text_width = self.get_string_width(text) + 2
            start_x = x + (total_width - text_width) / 2
            self.set_x(start_x)
        else:
            self.set_x(x)
        border = 1 if border else 0
        widht = max_width if border else text_width
        self.cell(widht, 10, text, border, 1, "C")

    def _add_watermark(self, x: int, y: int):
        """Add the watermark to the card

        :param x: The x position to start the watermark
        :type x: int
        :param y: The y position to start the watermark
        :type y: int
        """
        if self.water_mark_path:
            watermark = Image.open(self.water_mark_path)

            # Pegar la marca de agua en la tarjeta
            self.image(watermark, x + 10, y + 50, 80)

        # Dejar marca de agua en la esqquina superior izquierda de la tarjeta
        self.image(TEAM_MASTER_IMAGE, x - 7, y - 7, 30)

    def _add_header(self, x: int, y: int):
        """Add the header to the card with the tournament name

        :param x: The x position to start the header
        :type x: int
        :param y: The y position to start the header
        :type y: int
        """
        self.set_xy(x, y)
        self.set_font("Times", "B", self.FONT_SIZE_LARGE)
        self.draw_centered_text(x=x, text=self.tournament_name)

    def _add_category_info(self, x: int, category: str):
        """Add the category info to the card with the category name

        :param x: The x position to start the category name
        :type x: int
        :param category: The category name to add to the card
        :type category: str
        """
        category_text = translate_text(category, self.lang)
        self.set_font("Courier", "I", self.FONT_SIZE_MEDIUM)
        self.draw_centered_text(x=x, text=category_text)

    def _add_round_info(self, x: int, group: int, total_groups: int):
        """Add the round info to the card with the round number and the group number

        :param x: The x position to start the round info
        :type x: int
        :param group: The group number
        :type group: int
        :param total_groups: The total number of groups
        :type total_groups: int
        """
        round_text = translate_text("round", self.lang)
        group_text = translate_text("group", self.lang)
        of_text = translate_text("of", self.lang)

        text_round = (
            f"{round_text} 1 | {group_text} {group} {of_text} {total_groups}"
            if total_groups
            else f"{round_text}"
        )
        self.set_font("Courier", "B", self.FONT_SIZE_SMALL)
        self.draw_centered_text(x=x, text=text_round)

    def _add_competitor_info(
        self,
        x: int,
        competitor_name: str,
        registrant_id: str = None,
        wca_id: str = "",
        with_wca_id: bool = False,
    ):
        """Add the competitor info to the card with the competitor name and wca_id

        :param x: The x position to start the competitor info
        :type x: int
        :param competitor_name: The name of the competitor
        :type competitor_name: str
        :param wca_id: The WCA ID of the competitor, defaults to ""
        :type wca_id: str, optional
        :param with_wca_id: If the wca_id should be added to the card, defaults to False
        :type with_wca_id: bool, optional
        """

        self.set_font("Arial-UnicodeMS", "", self.FONT_SIZE_SMALL)
        name_competidor_wca = f"| {registrant_id} |        {competitor_name}"

        if competitor_name == "":
            name_competidor_wca = f""

        if with_wca_id and wca_id:
            name_competidor_wca = f"{name_competidor_wca}        | {wca_id}"

        self.draw_centered_text(
            x=x, text=name_competidor_wca, max_width=105, border=True
        )

    def _add_table(self, x: int, y: int, category: str, with_cuttof: bool = True):
        """Add the table to the card with the results of the competitor

        :param x: The x position to start the table
        :type x: int
        :param y: The y position to start the table
        :type y: int
        """

        limit_and_cuttof = self.cuttof

        limit = None
        cuttof = ""

        for lc in limit_and_cuttof:
            if lc.get(category, None):
                limit = lc[category]["limit"]
                cuttof = lc[category]["cutoff"]

        if limit:
            limit = centiseconds_to_minutes_seconds(limit)

        if cuttof:
            cuttof = centiseconds_to_minutes_seconds(cuttof)

        column_titles = [
            "A",
            "S",
            translate_text("result", self.lang)
            + " DNF "
            + translate_text("if", self.lang)
            + " >= "
            + limit,
            "J",
            "C",
        ]  # Ajustamos los títulos
        self.set_font("Arial", "B", 10)
        self.set_x(x)
        for width, title in zip(self.COLUMN_WIDTHS, column_titles):
            self.cell(width, 10, title, 1, 0, "C")

        self.ln(10)

        # Rows of the table
        self.set_font("Arial", "", self.FONT_SIZE_MSMALL)

        scramble_num = 1

        # cuttof = next(
        #     (cuttof["cutoff"] for cuttof in self.cuttof if cuttof["id"] == category),
        #     None,
        # )

        # cuttof = limit_and_cuttof.get(category, None)

        # if cuttof:
        #     cuttof = cuttof.get("cutoff", None)

        continue_if_text = translate_text("continue_if", self.lang)
        rows = 3 if category in mean_of_three_events else 5

        for i in range(rows):
            self.set_x(x)
            if i == 2 and category != "333" and with_cuttof:
                self.cell(
                    sum(self.COLUMN_WIDTHS),
                    10,
                    "------------- {} < {} -------------".format(
                        continue_if_text, cuttof
                    ),
                    0,
                    1,
                    "C",
                )
            self.set_x(x)

            self.cell(self.COLUMN_WIDTHS[0], 10, str(scramble_num), 1, 0, "C")
            scramble_num += 1

            for width in self.COLUMN_WIDTHS[1:]:
                self.cell(width, 10, str(i) if width == 35 else "", 1, 0, "C")
            self.ln(10)

        # Extra Row
        self.set_x(x)
        self.cell(
            sum(self.COLUMN_WIDTHS), 10, "------------- Extra -------------", 0, 1, "C"
        )

        for i in range(2):
            self.set_x(x)
            self.cell(self.COLUMN_WIDTHS[0], 10, f"E{i+1}", 1, 0, "C")
            for width in self.COLUMN_WIDTHS[1:]:
                self.cell(width, 10, "", 1, 0, "C")
            self.ln(10)

        self.rect(x, y, sum(self.COLUMN_WIDTHS), self.get_y() - y)


class Groups(FPDF):

    def __init__(self, tournament_name, lang="es"):
        super().__init__()
        self.tournament_name = tournament_name
        self.lang = lang
        self.first_page = True

    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, self.tournament_name, 0, 1, "C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(
            0, 10, f"{translate_text('page', self.lang)} {self.page_no()}", 0, 0, "C"
        )

    def agregar_tabla(self, eventos):

        for evento, grupos in eventos.items():

            for grupo, participantes in grupos.items():
                if self.first_page:
                    self.first_page = False
                else:
                    self.add_page()

                self.image(TEAM_MASTER_IMAGE, 3, 3, 30)
                self.set_font("Arial", "B", 16)
                self.cell(
                    0,
                    10,
                    f"{translate_text('event', self.lang)}: {translate_text(evento, self.lang)}",
                    0,
                    1,
                    "C",
                )
                self.ln(5)
                self.set_font("Arial", "B", 12)
                self.cell(
                    0, 10, f"{translate_text('group', self.lang)} {grupo}:", 0, 1, "C"
                )
                self.ln(5)
                self.crear_tabla(participantes)

    def crear_tabla(self, participantes):
        self.set_font("Arial", "", 9)
        self.set_fill_color(200, 220, 255)
        self.set_draw_color(0, 0, 0)
        col_width = self.w / 2.5
        row_height = self.font_size * 2
        for row in participantes:
            self.set_x(65)
            self.cell(col_width, row_height, row, border=1, ln=True, align="C")


class NamesAndIds(FPDF):

    def __init__(self, wcif, lang="es"):
        super().__init__()
        self.wcif = wcif
        self.lang = lang

    def generate(self):
        self.add_page()
        self.image(TEAM_MASTER_IMAGE, 3, 3, 30)
        self.set_font("Arial", "B", 16)
        self.cell(200, 10, f"{self.wcif['name']}", 0, 1, "C")
        self.ln(10)

        # Crear tabla para los participantes
        self.set_font("Arial", "", 10)
        col_widths = [30, 80, 50, 30]
        header = ["ID", "Nombre", "WCA ID", "Check"]
        data = [header]

        for person in self.wcif['persons']:
            wca_id = person.get("wcaId") if person.get("wcaId") != None else ""
            data.append([person["registrantId"], person["name"], wca_id, " "])

        data = sorted(data[1:], key=lambda x: x[0])

        # Agregar la tabla al PDF
        for row in data:
            for col, width in zip(row, col_widths):
                self.cell(width, 10, str(col), border=1, align="C")
            self.ln()
