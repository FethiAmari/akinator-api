import cloudscraper
from bs4 import BeautifulSoup



class AkinatorError(Exception):
    pass


class Akinator():
    def __init__(self, theme: str = "characters", lang: str = "ar", child_mode: bool = False) -> None:
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome',
                     'platform': 'windows', 'desktop': True}
        )
        self.scraper.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        })
        self.ENDPOINT = f"https://{lang}.akinator.com/"
        self.name = None
        self.description = None
        self.photo = None
        self.answer_id = None
        self.akitude = None

        if theme == "characters":
            sid = 1
        elif theme == "objects":
            sid = 2
        elif theme == "animals":
            sid = 14
        else:
            raise AkinatorError(
                "Theme must be 'characters', 'objects', or 'animals'.")

        self.json = {
            "step": 0,
            "progression": 0.0,
            "sid": sid,
            "cm": child_mode,
            "answer": 0,
        }

    def start_game(self):
        self.name = None
        self.description = None
        self.photo = None
        self.answer_id = None
        self.akitude = "https://en.akinator.com/assets/img/akitudes_670x1096/defi.png"

        game = self.scraper.post(f"{self.ENDPOINT}game", json={
            "sid": self.json["sid"],
            "cm": self.json["cm"]

        }).text

        soup = BeautifulSoup(game, "html.parser")
        askSoundlike = soup.find(id="askSoundlike")
        question_label = soup.find(id="question-label").get_text()
        session_id = askSoundlike.find(id="session").get("value")
        signature_id = askSoundlike.find(id="signature").get("value")

        self.json["session"] = session_id
        self.json["signature"] = signature_id
        self.step = 0
        self.progression = 0.0
        self.question = question_label
        return question_label

    def post_answer(self, answer: str):
        answers_map = {"y": 0, "n": 1, "idk": 2, "p": 3, "pn": 4}
        if answer not in answers_map:
            raise AkinatorError(
                "Answer must be 'y', 'n', 'idk', 'p', or 'pn'.")

        self.json["answer"] = answers_map[answer]

        try:
            progression = self.scraper.post(
                f"{self.ENDPOINT}answer", json=self.json).json()

            if progression["completion"] == "KO":
                raise AkinatorError("completion: KO")
            elif progression["completion"] == "SOUNDLIKE":
                raise AkinatorError("completion: SOUNDLIKE")

            try:
                self.json["step"] = int(progression["step"])
                self.json["progression"] = float(progression["progression"])
                self.step = int(progression["step"])
                self.progression = float(progression["progression"])
                self.question = progression["question"]
                self.question_id = progression["question_id"]
                self.akitude = f"https://en.akinator.com/assets/img/akitudes_670x1096/{progression['akitude']}"
            except:
                self.name = progression["name_proposition"]
                self.description = progression["description_proposition"]
                self.photo = progression["img_character"]
                self.answer_id = progression["id_proposition"]
                self.json["step_last_proposition"] = int(self.json["step"])

            return progression
        except Exception as e:
            raise AkinatorError(f"Akinator request failed: {e}")

    def go_back(self):
        self.name = None
        self.description = None
        self.photo = None
        self.answer_id = None

        if self.json["step"] == 0:
            raise AkinatorError("It's the first question, can't go back.")

        self.json.pop("answer", None)

        try:
            goback = self.scraper.post(
                f"{self.ENDPOINT}cancel_answer", json=self.json).json()
            self.json["step"] = int(goback["step"])
            self.json["progression"] = float(goback["progression"])
            self.step = int(goback["step"])
            self.progression = float(goback["progression"])
            self.question = goback["question"]
            self.question_id = goback["question_id"]
            self.akitude = f"https://en.akinator.com/assets/img/akitudes_670x1096/{goback['akitude']}"
            return goback
        except Exception as e:
            raise AkinatorError(f"Go back failed: {e}")

    def exclude(self):
        self.name = None
        self.description = None
        self.photo = None
        self.answer_id = None
        self.json.pop("answer", None)

        try:
            exclude = self.scraper.post(
                f"{self.ENDPOINT}exclude", json=self.json).json()
            self.json["step"] = int(exclude["step"])
            self.json["progression"] = float(exclude["progression"])
            self.step = int(exclude["step"])
            self.progression = float(exclude["progression"])
            self.question = exclude["question"]
            self.question_id = exclude["question_id"]
            self.akitude = f"https://en.akinator.com/assets/img/akitudes_670x1096/{exclude['akitude']}"
            return exclude
        except Exception as e:
            raise AkinatorError(f"Exclude failed: {e}")
