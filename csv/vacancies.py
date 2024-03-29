import psycopg2
import requests


# Класс получения вакансий по заранее подготовленным работодателям у которых есть открытые вакансии и их больше 5
class Vacancies:
    @classmethod
    def get_id_emloyers(cls, cur):

        cur.execute("""
        select employer_id from employers
        """)
        temp = [el[0] for el in cur]

        return temp

    @classmethod
    def get_vacancies(cls, employer_id, page=0):
        """
        Получение одной страницы работодателей
        """
        params = {
            'employer_id': employer_id,  # id работодателя
            'area': 2,  # Поиск в зоне
            'page': page,  # Номер страницы
            'per_page': 100  # Кол-во вакансий на 1 странице
        }
        req = requests.get('https://api.hh.ru/vacancies', params=params)

        return req.json()['items'] if "items" in req.json().keys() else []

    @classmethod
    def page_to_list(cls, cur):
        """
        Цикл из доступных id работодателей на HH
        """
        employers_id = Vacancies.get_id_emloyers(cur)
        temp = []
        for employer_id in employers_id:
            list_page = Vacancies.get_vacancies(employer_id)
            temp.append(list_page)

        return temp

    @classmethod
    def make_table(cls, cur, conn):
        vacancies = sum([value for value in Vacancies.page_to_list(cur) if value], [])

        cur.execute("""
                create table vacancies
                (
                vacancie_id int primary key,
                name varchar(200),
                url varchar(200),
                employer_id int,
                salary int,
                foreign key (employer_id) references employers (employer_id)                
                )

            """)

        for vacancie in vacancies:
            cur.execute(
                f"insert into vacancies values(%s, %s, %s, %s, %s)", [
                    vacancie["id"],
                    vacancie["name"],
                    vacancie["alternate_url"],
                    vacancie["employer"]["id"],
                    vacancie["salary"]["from"] if isinstance(vacancie["salary"], dict) else None
                ]
            )

        # запись в бд
        conn.commit()


