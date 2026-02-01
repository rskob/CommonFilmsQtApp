from functools import partial

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QFont, QMouseEvent, QPainter, QFontMetrics
from PyQt5.QtWidgets import QLabel, QDialog, QPlainTextEdit, QPushButton, QWidget, QGridLayout, QVBoxLayout, \
    QListWidget, QListWidgetItem

from connection import add_persons
from parse import Person, Film



class Paginator:
    def __init__(self, obj: list or tuple, num: int, parent):
        self.parent = parent

        self.obj = obj
        self.num = num
        self.pagination_dict = {}

        page_num = 1
        temp = []
        for i in obj:
            if len(temp) == num:
                self.pagination_dict[page_num] = temp
                temp = []
                page_num += 1
            else:
                temp.append(i)

        if len(temp) != 0:
            self.pagination_dict[page_num] = temp


    def get_films_list(self, num):
        return self.pagination_dict.get(num)



class CommonFilmsWidget(QWidget):
    def __init__(self, person_1, person_2, parent):
        self.parent_window = parent
        super().__init__()
        try:
            self.initUI(person_1, person_2)
        except Exception as e:
            print(e)

    def initUI(self, person_1, person_2):
        if person_1 == person_2:
            self.parent_window.show()
            self.parent_window.error_bar.setText("Одна и та же личность")
            self.parent_window.widget = None
            return


        self.person_1 = person_1
        self.person_2 = person_2

        add_persons(person_1, person_2)


        self.setGeometry(600, 600, 600, 600)
        self.setFixedSize(600, 600)
        self.setWindowTitle("Общие фильмы")

        self.back_button = QPushButton(self)
        self.back_button.setText("Назад")
        self.back_button.move(250, 550)
        self.back_button.clicked.connect(self.back)

        films_list = person_1.get_common_films(person_2)

        self.title = QLabel(self)
        self.title.setText(f"{person_1.name} и {person_2.name} - Совместные фильмы")
        self.title.setFont(QFont("Times", 10))
        self.title.move(100, 20)

        self.first_person_name = ClickablePersonLabel(self)
        self.first_person_name.setText(person_1.name)
        self.first_person_name.setStyleSheet("QLabel { color: blue; text-decoration: underline; size: 12}")
        self.first_person_name.connect(partial(self.person_info, person_1))

        qp = QPixmap()
        qp.loadFromData(person_1.get_image())
        self.first_person_image = ClickablePersonLabel(self)
        self.first_person_image.setPixmap(qp)
        self.first_person_image.setScaledContents(True)
        self.first_person_image.resize(125, 165)
        self.first_person_image.connect(partial(self.person_info, person_1))

        self.second_person_name = ClickablePersonLabel(self)
        self.second_person_name.setText(person_2.name)
        self.second_person_name.setStyleSheet("QLabel { color: blue; text-decoration: underline; size: 12}")
        self.second_person_name.connect(partial(self.person_info, person_2))

        qp = QPixmap()
        qp.loadFromData(person_2.get_image())
        self.second_person_image = ClickablePersonLabel(self)
        self.second_person_image.setPixmap(qp)
        self.second_person_image.setScaledContents(True)
        self.second_person_image.resize(125, 165)
        self.second_person_image.connect(partial(self.person_info, person_2))

        if len(films_list) == 0:
            self.title.setText("Нет совместных фильмов")
            self.title.move(80, 20)

            self.first_person_name.move(30, 65)
            self.first_person_image.move(20, 85)
            self.second_person_name.move(230, 65)
            self.second_person_image.move(220, 85)

            self.setFixedSize(365, 290)
            self.back_button.move(135, 255)

        else:
            self.first_person_name.move(400, 100)
            self.first_person_image.move(400, 120)
            self.second_person_name.move(400, 335)
            self.second_person_image.move(400, 355)


            self.film_holder = QListWidget(self)
            self.film_holder.move(20, 100)


            for k, film in enumerate(films_list):
                try:
                    list_widget = QListWidgetItem(film.title)
                    list_widget.href = film.href
                    self.film_holder.addItem(list_widget)
                except Exception as e:
                    print(e)

            self.film_holder.itemClicked.connect(self.film_info)

        self.show()


    def film_info(self, list_widget):
        try:
            film = Film(list_widget.text(), list_widget.href)
            self.film = FilmWidget(film)
            self.film.setWindowModality(QtCore.Qt.ApplicationModal)
            self.film.show()
        except:
            pass


    def person_info(self, person):
        try:
            self.person = PersonWidget(person)
            self.person.setWindowModality(QtCore.Qt.ApplicationModal)
            self.person.show()
        except:
            pass


    def closeEvent(self, a) -> None:
        self.close()
        self.parent_window.show()


    def back(self):
        self.parent_window.first_person.setText("")
        self.parent_window.second_person.setText("")
        self.destroy()
        self.parent_window.widget = None
        self.parent_window.show()


class TruncateWordsLabel(QLabel):
    def paintEvent(self, event):
        painter = QPainter(self)

        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.ElideRight, self.width())

        painter.drawText(self.rect(), self.alignment(), elided)


class WidgetMixinException(Exception):
    pass


class WidgetMixin(QDialog):
    def __init__(self, obj):
        super().__init__()
        self.initUI(obj)

    def initUI(self, obj):
        obj.parse()

        if isinstance(obj, Person):
            obj_name = obj.name
            self.occupation = TruncateWordsLabel(self)

        elif isinstance(obj, Film):
            obj_name = obj.title
        else:
            raise WidgetMixinException(f"Неверный тип объекта: {type(obj)}")


        self.setWindowTitle(obj_name)

        qp = QPixmap()
        img_in_bytes = obj.get_image()
        if not img_in_bytes:
            self.image_label = None
        else:
            qp.loadFromData(img_in_bytes)
            self.pixmap = qp

            self.image_label = QLabel(self)
            self.image_label.setScaledContents(True)
            self.image_label.setPixmap(self.pixmap)
            self.image_label.setFixedSize(150, 200)

        self.title = QLabel(self)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setText(f"<a href={obj.href}>{obj_name}</a>")
        self.title.setOpenExternalLinks(True)
        self.title.setFont(QFont("Times", 10))

        self.data = QVBoxLayout()
        for data in obj.data.items():
            section, text = data
            text = f"<b>{section.title()}:</b> {text}<br/>"

            label = QLabel(self)
            label.setText(text)
            self.data.addWidget(label)




class FilmWidget(WidgetMixin):
    def get_coordinates(self):
        coordinates = [(1, 0, 1, 3),  # title
                       (2, 0),  # image_label
                       (2, 1),  # description
                       (3, 0, 1, 3),  # data
                       ]

        if not self.description:
            coordinates[2] = None

        return coordinates

    def __init__(self, film):
        super().__init__(film)

        layout = QGridLayout()

        if film.description:
            self.description = QPlainTextEdit(self)
            self.description.insertPlainText(film.description)
            self.description.setReadOnly(True)
        else:
            self.description = None

        coordinates = self.get_coordinates()
        attrs = (self.title, self.image_label, self.description, self.data)

        for i, j in enumerate(attrs):
            if coordinates[i]:
                if not isinstance(j, QVBoxLayout):
                    layout.addWidget(j, *coordinates[i])
                else:
                    layout.addLayout(j, *coordinates[i])


        self.setLayout(layout)
        self.setFixedSize(layout.sizeHint())


class ClickableFilmLabel(QLabel):
    clicked = pyqtSignal()

    def connect(self, function):
        self.func = function

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if ev.button() == Qt.LeftButton:
            self.func()
        else:
            self.clicked.emit()


class ClickablePersonLabel(QLabel):
    clicked = pyqtSignal()

    def connect(self, function):
        self.func = function

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if ev.button() == Qt.LeftButton:
            self.func()
        else:
            self.clicked.emit()


class PersonWidget(WidgetMixin):
    def get_coordinates(self):
        coordinates = [(1, 0, 1, 3),  # title
                       (2, 0, 1, 3),  # occupation
                       (3, 0),  # image_label
                       (3, 1, 1, 2),  # best_films_and_series
                       (4, 0, 1, 3),  # data
                       ]

        if not self.best_films_and_series:
            coordinates[3] = None


        return coordinates


    def __init__(self, person):
        super().__init__(person)

        layout = QGridLayout()

        self.occupation.setText(person.occupation)
        self.occupation.setAlignment(QtCore.Qt.AlignCenter)
        self.occupation.setStyleSheet("QLabel {size: 7}")


        if person.best_films:
            text = "<b>Лучшие фильмы и сериалы</b><br/>"
            for film in person.best_films:
                text += f"<a href={film.href}>{film.title}</a><br/>"

            self.best_films_and_series = QLabel(self)
            self.best_films_and_series.setOpenExternalLinks(True)
            self.best_films_and_series.setText(text)
        else:
            self.best_films_and_series = None

        coordinates = self.get_coordinates()
        attrs = (self.title, self.occupation, self.image_label, self.best_films_and_series, self.data)


        for i, j in enumerate(attrs):
            if coordinates[i]:
                if not isinstance(j, QVBoxLayout):
                    layout.addWidget(j, *coordinates[i])
                else:
                    layout.addLayout(j, *coordinates[i])

        self.setLayout(layout)
        self.setFixedSize(layout.sizeHint())
