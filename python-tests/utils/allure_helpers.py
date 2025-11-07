import json
import logging
from json import JSONDecodeError

import allure
import curlify
from allure_commons.types import AttachmentType
from requests import Response


def allure_attach_request(function):
    def wrapper(*args, **kwargs):
        method, url = args[1], args[2]
        with allure.step(f"{method} {url}"):

            response: Response = function(*args, **kwargs)

            curl = curlify.to_curl(response.request)
            logging.debug(curl)
            logging.debug(response.text)

            allure.attach(
                body=curl.encode("utf8"),
                name=f"Request {response.status_code}",
                attachment_type=AttachmentType.TEXT,
                extension=".txt"
            )
            try:
                allure.attach(
                    body=json.dumps(response.json(), indent=4).encode("utf8"),
                    name=f"Response json {response.status_code}",
                    attachment_type=AttachmentType.JSON,
                    extension=".json"
                )
            except JSONDecodeError:
                allure.attach(
                    body=response.text.encode("utf8"),
                    name=f"Response text {response.status_code}",
                    attachment_type=AttachmentType.TEXT,
                    extension=".txt")
            allure.attach(
                body=json.dumps(dict(response.headers), indent=4).encode("utf8"),
                name=f"Response headers {response.status_code}",
                attachment_type=AttachmentType.JSON,
                extension=".json"
            )
        return response

    return wrapper


def allure_logger(config):
    listener = config.pluginmanager.get_plugin("allure_listener")
    return listener.allure_logger


def attach_sql(conn, cursor, statement, parameters, context, executemany):
    try:
        if parameters:
            statement_with_params = statement % parameters
        else:
            statement_with_params = statement
        name = statement.split(" ")[0] + " " + context.engine.url.database
        allure.attach(statement_with_params, name=name, attachment_type=AttachmentType.TEXT)
    except Exception:
        name = statement.split(" ")[0] if statement else "SQL"
        allure.attach(statement, name=name, attachment_type=AttachmentType.TEXT)


class Epic:
    app_name = "Приложение Niffler"
    api = "REST API"
    soap = "SOAP API"
    grpc = "gRPC сервисы"
    kafka = "Интеграция с Kafka"
    ui = "UI тесты"
    database = "Операции с БД"


class Feature:
    userdata = "Управление данными пользователей"
    auth = "Аутентификация"
    spending = "Управление тратами"
    category = "Управление категориями"
    currency = "Операции с валютами"
    kafka_messaging = "Обмен сообщениями Kafka"


class Story:
    user_management = "Управление пользователями"
    friends_management = "Управление друзьями"
    api_crud = "CRUD операции"
    boundary_tests = "Граничные тесты"
    produced_messaging = "Обработка сообщений в Kafka"
    registration_messages = "Создание записей в БД"
    search_filter = "Поиск и фильтрация"
