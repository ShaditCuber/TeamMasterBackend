from fpdf import FPDF


class GROUPS(FPDF):

    def __init__(self, tournament_name):
        super().__init__()
        self.tournament_name = tournament_name

    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, self.tournament_name, 0, 1, "C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")

    def agregar_tabla(self, eventos):

        for evento, grupos in eventos.items():
            if self.get_y() >= 210:
                self.add_page()
            self.set_font("Arial", "B", 16)
            self.cell(0, 10, f"Evento: {evento}", 0, 1, "C")
            self.ln(5)

            for grupo, participantes in grupos.items():
                if self.get_y() >= 210:
                    self.add_page()
                self.set_font("Arial", "B", 12)
                self.cell(0, 10, f"Grupo {grupo}:", 0, 1, "C")
                self.ln(5)

                self.crear_tabla(participantes)
                self.ln(5)

            self.ln(10)

    def crear_tabla(self, participantes):
        if self.get_y() >= 210:
            self.add_page()
        self.set_font("Arial", "", 9)
        self.set_fill_color(200, 220, 255)
        self.set_draw_color(0, 0, 0)
        col_width = self.w / 2.5
        row_height = self.font_size
        for row in participantes:
            self.set_x(65)
            self.cell(
                col_width,
                row_height * 2,
                row,
                border=1,
                ln=True,
                align="C",
            )
            



