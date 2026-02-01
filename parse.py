from time import sleep
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import urllib.request


class PersonException(BaseException):
    pass


class Person:
    fields = ["дата рождения", "место рождения", "рост"]

    def __init__(self, name, href):
        self.name = name
        self.href = href

    def get_films(self) -> list:
        src = requests.get(self.href).text
        soup = BeautifulSoup(src, "lxml")

        films = soup.find_all(class_="redesign_movies_block")

        films_list = []
        for film_block in films:
            title = film_block.find(class_="redesign_movies_block_main_title").text
            href = "https://www.film.ru/" + film_block.find(class_="redesign_movies_block_main_title").get("href")

            films_list.append(Film(title, href))

        return films_list

    def get_common_films(self, other) -> list:
        self_films = self.get_films()
        other_films = other.get_films()

        return sorted(list(set([i for i in other_films if i in self_films])),
                      key=lambda film: film.get_mean_rating(), reverse=True)

    def get_image(self) -> bytes or None:
        src = requests.get(self.href).text
        soup = BeautifulSoup(src, "lxml")

        image_block = soup.find("img", {"class": "", "alt": self.name})


        if not image_block:
            return

        photo_in_bytes = urllib.request.urlopen("https://www.film.ru" + image_block.get("src")).read()


        return photo_in_bytes


    def parse(self) -> None:
        self.data = {}
        src = requests.get(self.href).text
        soup = BeautifulSoup(src, "lxml")

        self.occupation = ", ".join([i.text for i in soup.find("div", class_="redesign_person_head_center")
                                    .find("h3").find_all("a")])

        self.best_films = [Film(film.text, "https://www.film.ru" + film.get("href"))
                           for film in soup.find("div", class_="redesign_person_head_right").find_all("a")]

        for block in soup.find_all(class_="redesign_person_head_center_info"):
            section, text = block.find_all("div")
            section, text = section.text, text.text.replace("\n", ", ").strip(", ")

            if section not in self.fields:
                continue

            self.data[section] = text

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other):
        return self.href == other.href


class Film:
    fields = ["длительность", "время", "режиссеры", "бюджет"]

    def __init__(self, title, href):
        self.rating = None
        self.title = title
        self.href = href

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return f"'{self.title}'"

    def __eq__(self, other) -> bool:
        return self.title == other.title and self.href == other.href

    def __hash__(self) -> int:
        return hash(self.title)

    def get_image(self) -> bytes or None:
        src = requests.get(self.href).text
        soup = BeautifulSoup(src, "lxml")

        image_block = soup.find("a", class_="wrapper_block_stack wrapper_movies_poster").find("img")

        if not image_block:
            return

        photo_in_bytes = urllib.request.urlopen("https://www.film.ru" + image_block.get("src")).read()

        return photo_in_bytes

    def get_rating(self) -> dict:
        self.rating = {}

        if not self.rating:
            src = requests.get(self.href).text
            soup = BeautifulSoup(src, "lxml")

            for rating in soup.find_all("div", class_="wrapper_movies_scores_score")[:-2]:
                service_rating = rating.text.split()

                if len(service_rating) < 2:
                    continue

                rating, service_name = service_rating

                self.rating[service_name] = rating

        return self.rating

    def get_mean_rating(self) -> int:
        rating = self.get_rating()

        return sum([float(i) for i in rating.values()])

    def parse(self) -> None:
        self.data = {}

        src = requests.get(self.href).text
        soup = BeautifulSoup(src, "lxml")

        for block in soup.find_all("div", class_="block_table"):
            section, text = block.find_all("div")
            section, text = section.text, text.text.replace("\n", ", ").strip(", ")

            if section not in self.fields:
                continue

            self.data[section] = text

        try:
            description = ""
            for i in soup.find("div", class_="wrapper_movies_text").find_all("p"):
                is_strong = i.find("strong")
                if is_strong:
                    text = "\n\n" + i.text + "\n\n"
                else:
                    text = i.text

                description += text

            self.description = description.strip("\n")
        except AttributeError:
            self.description = None


def get_person(driver, name) -> Person:
    search_bar = driver.find_element(By.NAME, "quick_search").find_element(By.TAG_NAME, "input")

    search_bar.click()
    sleep(0.5)

    search_bar.send_keys(name)
    sleep(2)

    soup = BeautifulSoup(driver.page_source, "lxml")

    options = soup.find("div", class_="autocomplete-box fast_search")

    if not options:
        options = soup.find("form", {"name": "quick_search"}).find_all("div")
    else:
        options = options.find_all("div")

    for option in options:
        if "Люди" in option.text and option.find("a").get("href").startswith("/person/"):
            first_and_actually_last_option = option
            break
    else:
        first_and_actually_last_option = None

    if not first_and_actually_last_option:
        raise PersonException(f"'{name}' - Не найдено")

    partial_href = first_and_actually_last_option.find("a").get("href")

    if not partial_href.startswith("/person"):
        raise PersonException(f"'{name}' - Не найдено")

    person_href = "https://www.film.ru" + partial_href
    name = first_and_actually_last_option.find("a").find("strong").text

    src = requests.get(person_href).text
    soup = BeautifulSoup(src, "lxml")

    films = soup.find_all(class_="redesign_movies_block")

    films_list = []
    for film_block in films:
        title = film_block.find(class_="redesign_movies_block_main_title").text
        href = "https://www.film.ru/" + film_block.find(class_="redesign_movies_block_main_title").get("href")

        films_list.append(Film(title, href))

    person = Person(name, person_href)

    print(person, person.href)

    return person
