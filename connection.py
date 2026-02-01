import sqlite3
from datetime import datetime, timedelta
from random import shuffle
from parse import Person

PATH = ""

con = sqlite3.connect(PATH)
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS history_search ("
            "request TEXT,"
            "date TEXT)")
con.commit()

cur.execute("CREATE TABLE IF NOT EXISTS Persons ("
            "name TEXT,"
            "href TEXT)")
con.commit()


def add_request_to_history_search(request):
    date = str(datetime.utcnow())

    if request in get_history_search():
        return


    cur.execute("INSERT INTO history_search (request, date) VALUES(?, ?)", (request, date[:date.rfind(".")]))
    con.commit()


def get_history_search():
    return [i[0] for i in cur.execute("SELECT request FROM history_search").fetchall()]


def person_exists(name):
    return cur.execute("SELECT name FROM Persons WHERE name == ?", (name,)).fetchone()


def request_exists(request):
    return cur.execute("SELECT request FROM history_search WHERE request = ?", (request,)).fetchone()


def update_tables():
    table_names = ["history_search", "Persons"]
    for name in table_names:
        for date in [i[0] for i in cur.execute(f"SELECT date FROM {name}").fetchall()]:
            date_of_searching = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    
            if datetime.utcnow() - timedelta(days=7) > date_of_searching:
                cur.execute(f"DELETE FROM {name} WHERE date == ?", (date, ))
                con.commit()


def add_persons(person1, person2):
    date = str(datetime.utcnow())

    for person in (person1, person2):
        name, href = person.name, person.href

        if not person_exists(name):
            cur.execute("INSERT INTO Persons (name, href, date) VALUES (?, ?, ?)", (name, href, date[:date.rfind(".")]))
            con.commit()

    request = f"{person1.name} x {person2.name}"

    add_request_to_history_search(request)


def get_persons(name1, name2):
    name, href = cur.execute("SELECT name, href FROM Persons WHERE name == ?", (name1, )).fetchone()
    person1 = Person(name, href)

    name, href = cur.execute("SELECT name, href FROM Persons WHERE name == ?", (name2, )).fetchone()
    person2 = Person(name, href)


    return person1, person2


def delete_request(request):
    cur.execute("DELETE FROM history_search WHERE request == ?", (request, ))
    con.commit()


def get_person_href_if_saved(name):
    href = cur.execute("SELECT href FROM Persons WHERE name == ?", (name, )).fetchone()

    if href:
        return Person(name, href[0])


def get_all_person_names():
    return [i[0] for i in cur.execute("SELECT name FROM Persons").fetchall()]


def get_continuation(text):
    if not text:
        return ""

    lst = get_all_person_names()
    shuffle(lst)

    for name in lst:
        if name.lower().startswith(text.lower()):
            return name

    return ""

