from fastapi import APIRouter, UploadFile, File, Form
from datetime import datetime
from util.util import get_competitors, get_events, get_limit_and_cuttoff, upload_to_s3
from util.pdf import ScoreCard, Groups, NamesAndIds
import os
import json
import random

router = APIRouter()

BASE = "https://avatars-images.s3.amazonaws.com"


def worldRankingOfPersonInEvent(person, eventId):
    personalBests = person.get("personalBests", [])
    if personalBests is None or not any(
        pb.get("eventId") == eventId for pb in personalBests
    ):
        return 10**9
    return min(
        pb.get("worldRanking", 10**9)
        for pb in personalBests
        if pb.get("eventId") == eventId
    )


def calculateAge(birthdate: str) -> int:
    birthdate = datetime.strptime(birthdate, "%Y-%m-%d")
    fecha_actual = datetime.now()
    edad = (
        fecha_actual.year
        - birthdate.year
        - ((fecha_actual.month, fecha_actual.day) < (birthdate.month, birthdate.day))
    )
    return edad


def sortCompetitorsBySpeedInEvent(
    competitors: list,
    category: str,
    reverse: bool = False,
):
    return sorted(
        competitors,
        key=lambda x: worldRankingOfPersonInEvent(x, category),
        reverse=reverse,
    )


def generateBalancedGroup(
    competitors: list,
    eventID: str,
    num_groups: int = 2,
) -> list:

    competitors = [
        person
        for person in competitors
        if eventID in person.get("registration", {}).get("eventIds", [])
    ]

    # Inicializa una lista de listas para almacenar los grupos

    # Ordena los competidores por velocidad en el evento
    competitors = sortCompetitorsBySpeedInEvent(competitors, eventID, reverse=False)

    # Distribuye equitativamente los competidores basados en su ranking mundial
    for index, person in enumerate(competitors):
        age = calculateAge(person["birthdate"])
        person["age"] = age
        group_number = min(index % num_groups, num_groups - 1)
        if eventID not in person:
            person[eventID] = group_number + 1

    return competitors


def generateRandomGroup(
    wcif: list,
    eventID: str,
    num_groups: int = 2,
) -> list:

    # Filtrar los competidores registrados en el evento
    competitors = [
        person
        for person in wcif
        if eventID in person.get("registration", {}).get("eventIds", [])
        if person.get("registration", {}).get("status") == "accepted"
    ]

    # Inicializa una lista de listas para almacenar los grupos
    # groups = [[] for _ in range(num_groups)]

    # Ordena los competidores aleatoriamente
    random.shuffle(competitors)

    # Asigna cada competidor a un grupo
    for index, person in enumerate(competitors):
        age = calculateAge(person["birthdate"])
        person["age"] = age
        group_number = min(index % num_groups, num_groups - 1)
        if eventID not in person:
            person[eventID] = group_number + 1

    return competitors


def generateGroupsBySpeed(
    competitors: list,
    eventID: str,
    reverse: bool = False,
    num_groups: int = 2,
) -> list:

    # Filtrar los competidores registrados en el evento
    competitors = [
        person
        for person in competitors
        if eventID in person.get("registration", {}).get("eventIds", [])
    ]

    # Calcula el tamaño de cada grupo
    size_of_group = len(competitors) // num_groups
    # Ordena los competidores por velocidad en el evento
    competitors = sortCompetitorsBySpeedInEvent(competitors, eventID, reverse=reverse)

    # Asigna cada competidor a un grupo
    for index, person in enumerate(competitors):
        age = calculateAge(person["birthdate"])
        person["age"] = age
        group_number = min(index // size_of_group, num_groups - 1)
        if eventID not in person:
            person[eventID] = group_number + 1

    return competitors


@router.post("/generateGroups")
def generate_groups(wcif: dict, data: dict):
    new_competitors = []
    criteria = data["criteria"]

    for event in get_events(wcif):
        eventID = event["id"]

        if criteria == "equilibrated":
            competitors = generateBalancedGroup(
                get_competitors(wcif), eventID, num_groups=data[eventID]
            )

        elif criteria == "random":
            competitors = generateRandomGroup(
                get_competitors(wcif), eventID, num_groups=data[eventID]
            )

        elif criteria == "speedFirst":
            competitors = generateGroupsBySpeed(
                get_competitors(wcif), eventID, reverse=False, num_groups=data[eventID]
            )

        elif criteria == "speedLast":
            competitors = generateGroupsBySpeed(
                get_competitors(wcif), eventID, reverse=True, num_groups=data[eventID]
            )

        new_competitors.extend(competitors)

    new_competitors = list({v["name"]: v for v in new_competitors}.values())

    new_competitors = sorted(new_competitors, key=lambda k: k["name"])

    wcif["persons"] = new_competitors

    return wcif


def generate_pdf_groups(wcif):
    tournament_name = wcif["name"]
    tournament_id = wcif["id"]
    lang = wcif["lang"]
    eventos = {}

    for participante in wcif["persons"]:
        for evento_id in participante["registration"]["eventIds"]:
            if evento_id not in eventos:
                eventos[evento_id] = {}

            grupo = participante[evento_id]
            if grupo not in eventos[evento_id]:
                eventos[evento_id][grupo] = []

            wca_id = participante.get("wcaId")
            if wca_id is None:
                wca_id = "-"
            eventos[evento_id][grupo].append(f"{participante['name']} | {wca_id}")

    for evento_id, grupos in eventos.items():
        eventos[evento_id] = dict(sorted(grupos.items(), key=lambda x: int(x[0])))

    groups = Groups(tournament_name=tournament_name, lang=lang)

    groups.add_page()
    groups.agregar_tabla(eventos)

    name_file = f"Groups-{tournament_id}.pdf"

    return upload_to_s3(name_file=name_file, constructor=groups)


def generate_name_and_id(wcif):
    name_and_ids = NamesAndIds(wcif=wcif)

    name_and_ids.generate()

    name_file = f"Names-{wcif['id']}.pdf"

    return upload_to_s3(name_file=name_file, constructor=name_and_ids)


def generate_csv(wcif):
    persons = wcif["persons"]
    colums = ["ID", "Name", "id_wca", "birthdate", "age"]
    events = [event["id"] for event in wcif["events"]]

    colums.extend(events)

    name_file = f"Groups-{wcif['id']}.csv"

    with open(f"/tmp/{name_file}", "w", encoding="utf-8") as file:
        file.write(";".join(colums) + "\n")

        for person in persons:
            wca_id = person.get("wcaId") if person.get("wcaId") != None else ""
            row = [
                person["registrantId"],
                person["name"],
                wca_id,
                person["birthdate"],
                person["age"],
            ]

            for event in events:
                row.append(person.get(event, ""))

            file.write(";".join(map(str, row)) + "\n")

    return upload_to_s3(name_file=name_file)


async def save_uploaded_file(upload_file: UploadFile) -> str:
    file_path = os.path.join("/tmp", upload_file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())
    return file_path


from PIL import Image


def convert_to_watermark(input_image_path, output_image_path):
    # devolver la imagen original con menos opacidad

    image = Image.open(input_image_path).convert("RGBA")

    # Convert
    r, g, b, a = image.split()

    a = a.point(lambda p: int(p * 0.1))

    # Recombinar los canales
    image = Image.merge("RGBA", (r, g, b, a))

    # Guardar la nueva imagen
    image.save(output_image_path)

    return output_image_path


# # si viene jpg or jpeg convertir a png
# if input_image_path.endswith(".jpg") or input_image_path.endswith(".jpeg"):
#     output_image_path = output_image_path.replace(".jpg", ".png")
#     output_image_path = output_image_path.replace(".jpeg", ".png")

# # Abrir la imagen original
# original = Image.open(input_image_path).convert("RGBA")

# # Convertir a blanco y negro
# grayscale = original.convert("L")

# # Crear una nueva imagen con canales RGBA (incluyendo alfa para la opacidad)
# result = Image.new("RGBA", original.size, (255, 255, 255, 0))

# # Combinar la imagen en escala de grises con la imagen de alfa (opacidad)
# for x in range(result.width):
#     for y in range(result.height):
#         gray = grayscale.getpixel((x, y))
#         result.putpixel(
#             (x, y), (gray, gray, gray, 40)
#         )  # 40 es el nivel de opacidad

# # Guardar la imagen resultante
# result.save(output_image_path)


# async def generate_all_files(wcif, image):
#     tasks = [
#         generate_scorecard(wcif, image),
#         generate_pdf_groups(wcif),
#         generate_name_and_id(wcif),
#         generate_csv(wcif),
#     ]

#     results = await asyncio.gather(*tasks)
#     return {
#         "scoreCard": results[0]["scoreCard"],
#         "emptyScoreCard": results[0]["emptyScoreCard"],
#         "groupsPDF": results[1],
#         "groupsCSV": results[2],
#         "namesPDF": results[3],
#     }


async def generate_scorecard(wcif, image):
    tournament_id = wcif["id"]
    tournament_name = wcif["name"]
    lang = wcif["lang"]
    groups = wcif["groups"]
    add_wca_id = wcif["addWcaId"]
    competitors = get_competitors(wcif)
    events = get_events(wcif)
    cuttof = get_limit_and_cuttoff(wcif)
    image_path = None
    if image:
        image_path = await save_uploaded_file(image)
        convert_to_watermark(image_path, image_path)

    ScoreCardConstructor = ScoreCard(
        lang=lang,
        tournament_name=tournament_name,
        cuttof=cuttof,
        add_wca_id=add_wca_id,
        water_mark_path=image_path,
    )

    competitor_counter = 0

    for event in events:
        event_id = event["id"]

        for person in competitors:
            person_group = person.get(event_id, 0)

            if person_group == 0:
                continue

            ScoreCardConstructor.add_competition_card(
                competitor_name=person["name"],
                category=event_id,
                group_num=person_group,
                total_groups=groups[event_id],
                competitor_counter=competitor_counter,
                registrant_id=person["registrantId"],
                wca_id=person["wcaId"],
            )

            competitor_counter += 1

    scoreCard = f"{tournament_id}.pdf"

    emptyScoreCardConstructor = ScoreCard(
        lang=lang,
        tournament_name=tournament_name,
        cuttof=cuttof,
        water_mark_path=image_path,
    )

    counter_empty = 0

    for event in events:
        for i in range(4):
            emptyScoreCardConstructor.add_competition_card(
                competitor_name="",
                category=event["id"],
                group_num=0,
                total_groups=None,
                competitor_counter=counter_empty,
                with_cuttof=False,
            )
            counter_empty += 1

    emptyScoreCard = f"Empty-ScoreCard-{tournament_id}.pdf"

    return {
        "scoreCard": upload_to_s3(scoreCard, ScoreCardConstructor),
        "emptyScoreCard": upload_to_s3(emptyScoreCard, emptyScoreCardConstructor),
    }


@router.post("/generateScoresheet")
async def generate_scoresheet(wcif: str = Form(...), image: UploadFile = File(None)):
    wcif = json.loads(wcif)

    scoreCards = await generate_scorecard(wcif, image)
    scoreCard = scoreCards["scoreCard"]
    emptyScoreCard = scoreCards["emptyScoreCard"]
    groups = generate_pdf_groups(wcif)
    names = generate_name_and_id(wcif)
    csv = generate_csv(wcif)

    return {
        "scoreCard": scoreCard,
        "emptyScoreCard": emptyScoreCard,
        "groupsPDF": groups,
        "groupsCSV": csv,
        "namesPDF": names,
    }
