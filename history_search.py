import typing
from fuzzywuzzy import fuzz
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QLineEdit
from connection import get_history_search, get_persons, delete_request
from widgets import CommonFilmsWidget


class SingletonQListWidget(QListWidget):
    counter = 0

    def __new__(cls, *args, **kwargs):
        cls.counter += 1
        if cls.counter > 1:
            raise TypeError("More than one QListWidget")

        return super().__new__(cls, *args, **kwargs)



class SearchBar(QLineEdit):
    clicked = pyqtSignal()

    def get_items(self):
        lst = get_history_search()
        lst_with_k = []

        text = self.text().lower()

        if text:
            for i in lst:
                first, second = i.split(" x ")
                k = fuzz.partial_ratio(text, first.lower()) + fuzz.partial_ratio(text, second.lower())
                lst_with_k.append((first, second, k))

            return [(i[0], i[1]) for i in [i for i in sorted(lst_with_k, key=lambda x: x[2], reverse=True)]
                    if i[2] >= 85]

        return [i.split(" x ") for i in lst]

    def mousePressEvent(self, event: typing.Optional[QMouseEvent]) -> None:
        if event.button() == Qt.LeftButton:
            history_search = self.get_items()

            if not self.text() and len(history_search) != 0:
                try:
                    self.list_widget = SingletonQListWidget(self.parent())
                except TypeError:
                    pass
                self.list_widget.clear()
                self.list_widget.itemClicked.connect(self.set_fields)
                self.list_widget.itemDoubleClicked.connect(self.delete_request)


                for pare in history_search:
                    item = QListWidgetItem(f"{pare[0]} x {pare[1]}")
                    self.list_widget.addItem(item)

                self.list_widget.move(300, 141)
                self.list_widget.resize(200, 200)
                self.list_widget.show()
            else:
                self.clicked.emit()

    def delete_request(self, request):
        try:
            delete_request(request.text())
            self.themChanges()
        except Exception as e:
            print(e)


    def themChanges(self):
        try:
            self.list_widget = SingletonQListWidget(self.parent())
        except TypeError:
            pass

        self.list_widget.clear()

        history_search = self.get_items()

        if len(history_search) == 0:
            self.list_widget.close()
            return

        for pare in history_search:
            item = QListWidgetItem(f"{pare[0]} x {pare[1]}")
            self.list_widget.addItem(item)

        self.list_widget.move(300, 141)
        self.list_widget.resize(200, 200)
        self.list_widget.show()



    def set_fields(self, item):
        try:
            parent = self.parent()
            print(item.text().split(" x "))
            text1, text2 = item.text().split(" x ")
            self.destroy()
            parent.hide()


            result = get_persons(text1, text2)

            if result:
                person_1, person_2 = result
                parent.widget = CommonFilmsWidget(person_1, person_2, parent)
        except Exception as e:
            print(e)

