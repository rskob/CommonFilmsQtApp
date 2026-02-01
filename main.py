import io
import sys
import typing
from time import sleep
from PyQt5 import uic
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow
from selenium import webdriver
from fake_useragent import FakeUserAgent

from parse import get_person, PersonException
from template import template

from widgets import *
from history_search import SearchBar
from connection import get_person_href_if_saved, get_continuation, update_tables


class CommonFilms(QMainWindow):
    URL = "https://www.film.ru/"

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.widget = None

        f = io.StringIO(template)
        uic.loadUi(f, self)

        self.submit_button.clicked.connect(self.show_common_films)
        self.error_bar.setStyleSheet("QLabel { color: red}")


        self.search_bar_label = QLabel(self)
        self.search_bar_label.setText("История поиска")
        self.search_bar_label.resize(200, 23)
        self.search_bar_label.setAlignment(Qt.AlignCenter)
        self.search_bar_label.move(300, 100)

        self.search_bar = SearchBar(self)
        self.search_bar.move(300, 120)
        self.search_bar.resize(200, 23)
        self.search_bar.textChanged.connect(self.search_bar.themChanges)

        self.first_person.mousePressEvent = self.mousePressEvent
        self.second_person.mousePressEvent = self.mousePressEvent

        self.first_person.textChanged.connect(partial(self.get_continuation, self.first_person, 1))
        self.second_person.textChanged.connect(partial(self.get_continuation, self.second_person, 2))

        self.continuation_button_1 = QPushButton(self)
        self.continuation_button_1.resize(150, 20)
        self.continuation_button_1.clicked.connect(partial(self.set_continuation, 1))

        self.continuation_button_2 = QPushButton(self)
        self.continuation_button_2.resize(150, 20)
        self.continuation_button_2.clicked.connect(partial(self.set_continuation, 2))

        self.continuation_button_1.hide()
        self.continuation_button_2.hide()

        self.setFixedSize(550, 400)

    def get_persons(self, name_1, name_2):
        options = webdriver.ChromeOptions()
        user_agent = FakeUserAgent()

        options.add_argument(f'user-agent={user_agent.random}')
        options.add_argument("headless")

        self.driver = webdriver.Chrome(options=options)

        self.driver.maximize_window()
        self.driver.get(self.URL)
        sleep(0.5)

        try:
            person_1 = get_person_href_if_saved(name_1)
            if not person_1:
                person_1 = get_person(self.driver, name_1)

            print(name_1, person_1)

            #print(person_1.best_films)
            self.driver.get(self.URL)
            sleep(0.5)
            person_2 = get_person_href_if_saved(name_2)
            if not person_2:
                person_2 = get_person(self.driver, name_2)

            print(name_2, person_2)
            return person_1, person_2
        except PersonException as exception:
            self.error_bar.setText(exception.args[0])
            self.show()
        except:
            self.error_bar.setText("Что-то пошло не так")
            self.show()

    def show_common_films(self):
        if not self.first_person.text() or not self.second_person.text():
            self.error_bar.setText("Имя не может быть пустым")
            return

        if self.first_person.text() == self.second_person.text():
            self.error_bar.setText("Одна и та же личность")
            return

        self.hide()
        self.error_bar.setText("")
        result = self.get_persons(self.first_person.text(), self.second_person.text())
        self.driver.close()

        if result:
            person_1, person_2 = result
            self.widget = CommonFilmsWidget(person_1, person_2, self)



    def get_continuation(self, line_edit, key):
        coordinates_data = {1: (300, 23),
                            2: (300, 56)}

        button_data = {1: self.continuation_button_1,
                       2: self.continuation_button_2}

        text = line_edit.text()

        continuation_button = button_data[key]

        if not text:
            continuation_button.hide()
            return

        continuation = get_continuation(text)
        if not continuation:
            continuation_button.hide()
            return


        continuation_button.setText(continuation)
        continuation_button.move(*coordinates_data[key])
        continuation_button.show()


    def set_continuation(self, key):
        line_edit_data = {1: self.first_person,
                          2: self.second_person}

        button_data = {1: self.continuation_button_1,
                       2: self.continuation_button_2}

        line_edit = line_edit_data[key]
        button = button_data[key]

        line_edit.setText(button.text())
        button.hide()


    def mousePressEvent(self, event: typing.Optional[QMouseEvent]) -> None:
        try:
            self.search_bar.list_widget.close()
        except AttributeError:
            return

    def closeEvent(self, a0: QCloseEvent) -> None:
        exit()


if __name__ == '__main__':
    update_tables()
    app = QApplication(sys.argv)
    ex = CommonFilms()
    ex.show()
    sys.exit(app.exec())
