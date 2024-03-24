import json, os


def centiseconds_to_minutes_seconds(centiseconds):
    if centiseconds is None:
        return None
    seconds = centiseconds / 100

    minutes = int(seconds // 60)
    seconds %= 60

    time_string = "{:02}:{:02}".format(minutes, int(seconds))

    return time_string


def get_events(wcif):
    return [event for event in wcif["events"]]


def get_limit_and_cuttoff(
    wcif,
):
    return [
        {
            event["id"]: {
                "limit": (
                    event["rounds"][0]["timeLimit"]["centiseconds"]
                    if event["rounds"][0]["timeLimit"]
                    else None
                ),
                "cutoff": (
                    event["rounds"][0]["cutoff"].get("attemptResult", None)
                    if event["rounds"][0]["cutoff"]
                    else None
                ),
            }
        }
        for event in get_events(wcif)
    ]


def get_competitors(wcif):
    return [
        person
        for person in wcif["persons"]
        if person.get("registration")
        and person["registration"].get("status") == "accepted"
    ]


def load_translation(lang: str):

    path_file = os.path.join(os.path.dirname(__file__), f"../locales/{lang}.json")

    with open(path_file, "r", encoding="utf-8") as file:
        translations = json.load(file)

    return translations


def tranlate_text(message_key: str, lang: str):
    translations = load_translation(lang)
    return translations.get(message_key, "No translation found for this key")
