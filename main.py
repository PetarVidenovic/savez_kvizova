from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty, ListProperty, NumericProperty
import random
import re
import itertools
# main.py (vrh fajla)
from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', '0')

import kivy
kivy.require('2.1.0')

class QuestionScreen(Screen):
    question_text = StringProperty("")
    options = ListProperty(["", "", "", ""])
    correct_index = NumericProperty(-1)
    score = NumericProperty(0)
    time_left = NumericProperty(10.00)
    current_question = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.questions = []
        self.sound = None

    def on_enter(self):
        # reset stanje pri svakom ulasku
        self.current_question = 0
        self.score = 0
        self.questions = []
        self.load_questions()
        self.next_question()

        # učitaj zvuk samo ako već nije učitan ili nije aktivan
        if not getattr(self, "sound", None):
            self.sound = SoundLoader.load("tech-quiz-news-loop-274362.mp3")
        if self.sound and getattr(self.sound, "state", None) != "play":
            self.sound.loop = True
            try:
                self.sound.play()
            except Exception:
                # ako reprodukcija zakaže, ignoriši grešku da aplikacija ne padne
                pass

        # ostavljamo logiku tajmera kakva je bila (korisnik je tražio da se ne menja)
        Clock.schedule_interval(self.update_timer, 0.01)


    def load_questions(self):
        try:
            with open("pitanja_2.txt", encoding="utf-8") as f1, open("odgovori_2.txt", encoding="utf-8") as f2:
                pitanja_raw = f1.read()
                odgovori_raw = f2.read()
        except FileNotFoundError:
            # ako fajlovi ne postoje, ostavi pitanja praznim
            self.questions = []
            return

        # podela na blokove (po numeraciji pitanja)
        pitanja_blocks = re.split(r"\n(?=\d+\.\s)", pitanja_raw.strip()) if pitanja_raw.strip() else []
        odgovori_blocks = re.split(r"\n(?=\d+\.\s)", odgovori_raw.strip()) if odgovori_raw.strip() else []

        combined = []
        for p_block, o_block in itertools.zip_longest(pitanja_blocks, odgovori_blocks, fillvalue=""):
            if not p_block or not p_block.strip():
                continue
            p_lines = [ln for ln in p_block.strip().split("\n") if ln.strip()]
            if len(p_lines) < 5:
                # preskoči nekompletna pitanja
                continue

            # izvuci tekst pitanja (bez broja)
            q_text = re.sub(r'^\d+\.\s*', '', p_lines[0]).strip()

            # izvuci do 4 opcije i ukloni prefikse kao "a)", "A.", "b-" itd.
            opts_lines = p_lines[1:5]
            opts = [re.sub(r'^[A-Da-d][\)\.\-]?\s*', '', line.strip()) for line in opts_lines]

            # parsiraj blok odgovora; pokušaj da uzmeš linije koje predstavljaju opcije
            o_lines = [ln for ln in o_block.strip().split("\n") if ln.strip()] if o_block and o_block.strip() else []
            if not o_lines:
                # nema odgovora za ovo pitanje, preskoči
                continue

            # ako prvi red odgovora počinje brojem, uzmi sledeća 4 reda; inače uzmi prve 4
            if re.match(r'^\d+\.', o_lines[0]):
                ans_opts = o_lines[1:5]
            else:
                ans_opts = o_lines[:4]

            if not ans_opts:
                continue

            # pronađi indeks tačnog odgovora (case-insensitive pretraga "tacno")
            correct = [i for i, line in enumerate(ans_opts) if "tacno" in line.lower()]
            if correct:
                combined.append((q_text, opts, correct[0]))
            else:
                # ako nema eksplicitnog "tacno", preskoči unos
                continue

        # ako nema dovoljno pitanja, uzmi koliko ima; izbegni grešku pri random.sample
        if not combined:
            self.questions = []
            return

        self.questions = random.sample(combined, k=min(10, len(combined)))


    def update_timer(self, dt):
        if self.time_left > 0:
            self.time_left -= dt
        else:
            self.handle_answer(-1)

    def next_question(self):
        if self.current_question >= len(self.questions):
            # kraj kviza
            self.manager.current = "result"
            self.manager.get_screen("result").score = self.score
            return

        q, opts, correct = self.questions[self.current_question]
        self.question_text = q
        self.options = opts
        self.correct_index = correct
        self.time_left = 10.00

        # resetuj boje dugmadi bez pretpostavke da svi id-jevi postoje
        for btn_id in ("btn_a", "btn_b", "btn_c", "btn_d"):
            if btn_id in self.ids:
                try:
                    self.ids[btn_id].background_color = [1, 1, 1, 1]
                except Exception:
                    pass

    def handle_answer(self, index):
        # zadržavamo postojeću logiku za tajmer (korisnik je tražio da se ne menja)
        Clock.unschedule(self.update_timer)

        if index == self.correct_index:
            self.score += 10
            btn_name = f"btn_{chr(97+index)}"
            if btn_name in self.ids:
                try:
                    self.ids[btn_name].background_color = [0, 1, 0, 1]
                except Exception:
                    pass
        elif index != -1:
            self.score -= 5
            selected = f"btn_{chr(97+index)}"
            correct_btn = f"btn_{chr(97+self.correct_index)}"
            if selected in self.ids:
                try:
                    self.ids[selected].background_color = [1, 0, 0, 1]
                except Exception:
                    pass
            if correct_btn in self.ids:
                try:
                    self.ids[correct_btn].background_color = [0, 1, 0, 1]
                except Exception:
                    pass
        else:
            correct_btn = f"btn_{chr(97+self.correct_index)}"
            if correct_btn in self.ids:
                try:
                    self.ids[correct_btn].background_color = [0, 1, 0, 1]
                except Exception:
                    pass

        Clock.schedule_once(lambda dt: self.advance(), 1)

    def advance(self):
        self.current_question += 1
        self.next_question()
        # ostavljamo zakazivanje tajmera kako je bilo u originalu
        Clock.schedule_interval(self.update_timer, 0.01)

class ResultScreen(Screen):
    score = NumericProperty(0)

class QuizApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(QuestionScreen(name="quiz"))
        sm.add_widget(ResultScreen(name="result"))
        return sm

if __name__ == "__main__":
    QuizApp().run()

