# from fpdf import FPDF
# from util.util import tranlate_text


# class GROUPS(FPDF):

#     def __init__(self, tournament_name, lang="es"):
#         super().__init__()
#         # self.set_auto_page_break(auto=True, margin=115)
#         self.tournament_name = tournament_name
#         self.lang = lang

#     def header(self):
#         self.set_font("Arial", "B", 12)
#         self.cell(0, 10, self.tournament_name, 0, 1, "C")
#         self.ln(10)

#     def footer(self):
#         self.set_y(-15)
#         self.set_font("Arial", "I", 8)
#         self.cell(
#             0, 10, f"{tranlate_text('page',self.lang)} {self.page_no()}", 0, 0, "C"
#         )

#     def agregar_tabla(self, eventos):

#         for evento, grupos in eventos.items():
#             # if self.get_y() >= 190:
#             #     self.add_page()
#             # self.set_font("Arial", "B", 16)
#             # print(self.get_y(),'Nombre del evento:',evento)
#             # self.cell(
#             #     0,
#             #     10,
#             #     f"{tranlate_text('event',self.lang)}: {tranlate_text(evento,self.lang)}",
#             #     0,
#             #     1,
#             #     "C",
#             # )
#             # self.ln(5)

#             for grupo, participantes in grupos.items():
#                 # if self.get_y() >= 190:
#                 #     self.add_page()
#                 self.set_font("Arial", "B", 16)
#                 print(self.get_y(),'Nombre del evento:',evento)
#                 self.cell(
#                     0,
#                     10,
#                     f"{tranlate_text('event',self.lang)}: {tranlate_text(evento,self.lang)}",
#                     0,
#                     1,
#                     "C",
#                 )
#                 self.ln(5)
#                 self.set_font("Arial", "B", 12)
#                 self.cell(
#                     0, 10, f"{tranlate_text('group',self.lang)} {grupo}:", 0, 1, "C"
#                 )
#                 self.ln(5)

#                 self.crear_tabla(participantes)
#                 self.ln(5)

#             self.add_page()

#     def crear_tabla(self, participantes):
#         # if self.get_y() >= 190:
#         #     self.add_page()
#         self.set_font("Arial", "", 9)
#         self.set_fill_color(200, 220, 255)
#         self.set_draw_color(0, 0, 0)
#         col_width = self.w / 2.5
#         row_height = self.font_size
#         for row in participantes:
#             self.set_x(65)
#             self.cell(
#                 col_width,
#                 row_height * 2,
#                 row,
#                 border=1,
#                 ln=True,
#                 align="C",
#             )
from fpdf import FPDF
from util.util import translate_text
import os
from PIL import Image


class GROUPS(FPDF):

    def __init__(self, tournament_name, lang="es"):
        super().__init__()
        self.tournament_name = tournament_name
        self.lang = lang

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
                team_master = Image.open(os.path.join("const", "teamMaster.png"))
                self.image(team_master, 3, 3, 30)
                self.set_font("Arial", "B", 16)
                print(self.get_y(), "Nombre del evento:", evento)
                # if self.get_y() >= 260:
                #     self.add_page()
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
                self.add_page()  # Agrega una nueva página para cada grupo

    def crear_tabla(self, participantes):
        self.set_font("Arial", "", 9)
        self.set_fill_color(200, 220, 255)
        self.set_draw_color(0, 0, 0)
        col_width = self.w / 2.5
        row_height = self.font_size
        for row in participantes:
            # if (
            #     self.get_y() > 190
            # ):  # Si la tabla llega al final de la página, añade un salto de página
            #     self.add_page()
            self.set_x(65)
            self.cell(col_width, row_height * 2, row, border=1, ln=True, align="C")
