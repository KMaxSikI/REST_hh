import requests
import json


def search_vacancies(city, job_title):
    base_url = 'https://api.hh.ru/vacancies'
    params = {
        'text': job_title,
        'area': city,
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        return []


def get_vacancy_requirements(vacancy_id):
    base_url = f'https://api.hh.ru/vacancies/{vacancy_id}'
    response = requests.get(base_url)
    if response.status_code == 200:
        return response.json().get('key_skills', [])
    else:
        return []


def analyze_vacancies(vacancies):
    num_vacancies = 0
    total_salary_rur = 0
    total_salary_usd = 0
    requirements = {}

    for vacancy in vacancies:
        salary = vacancy.get('salary')
        if isinstance(salary, dict):
            rur_from = salary.get('from', 0)
            rur_to = salary.get('to', 0)
            usd_from = salary.get('from', 0)
            usd_to = salary.get('to', 0)

            if salary.get('currency') == 'RUR':
                if rur_from is not None and rur_to is not None:
                    total_salary_rur += (rur_from + rur_to) / 2
                elif rur_from is not None:
                    total_salary_rur += rur_from
                elif rur_to is not None:
                    total_salary_rur += rur_to
            elif salary.get('currency') == 'USD':
                if usd_from is not None and usd_to is not None:
                    total_salary_usd += (usd_from + usd_to) / 2
                elif usd_from is not None:
                    total_salary_usd += usd_from
                elif usd_to is not None:
                    total_salary_usd += usd_to
                total_salary_usd *= 10

            num_vacancies += 1

        vacancy_requirements = get_vacancy_requirements(vacancy['id'])
        if vacancy_requirements:
            for skill in vacancy_requirements:
                skill_name = skill.get('name')
                if skill_name:
                    requirements[skill_name] = requirements.get(skill_name, 0) + 1

    average_salary_rur = total_salary_rur / num_vacancies if num_vacancies > 0 else 0
    average_salary_usd = total_salary_usd / num_vacancies if num_vacancies > 0 else 0

    total_requirements = sum(requirements.values())
    requirements_percentage = {requirement: (count / total_requirements) * 100 for requirement, count in
                               requirements.items()}

    return num_vacancies, average_salary_rur, average_salary_usd, requirements, requirements_percentage


city = '1'  # Москва
job_title = input('Введите наименование вакансии: ')

vacancies = search_vacancies(city, job_title)
num_vacancies, average_salary_rur, average_salary_usd, requirements, requirements_percentage = analyze_vacancies(
    vacancies)

result = [{
    'keywords': job_title,
    'count': num_vacancies,
    'average salary RUR': round(average_salary_rur, 2),
    'average salary USD': round(average_salary_usd, 2),
    'requirements': [{
        'name': requirement,
        'count': count,
        'persent': round(percentage, 1),

        } for requirement, count, percentage in
        sorted(zip(requirements.keys(), requirements.values(), requirements_percentage.values()), key=lambda x: x[1],
               reverse=True)
    ]}]


with open('result.json', 'w', encoding='utf-8') as json_file:
    json.dump(result, json_file, ensure_ascii=False, indent=4)

print("Результат записан в файл 'result.json'")
