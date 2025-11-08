import json

import allure
import pytest
from faker import Faker

from clients.auth_client import AuthClient
from clients.kafka_client import KafkaClient
from databases.userdata_db import UserdataDB
from models.user import UserName, User
from utils.allure_helpers import Epic, Feature, Story
from utils.waiters import wait_until_timeout


@allure.epic(Epic.kafka)
@allure.feature(Feature.kafka_messaging)
@pytest.mark.kafka
class TestAuthRegistrationKafkaTest:
    @allure.title("Сообщение с пользователем публикуется в Kafka после успешной регистрации")
    @allure.story(Story.produced_messaging)
    @allure.tag("kafka", "messaging")
    def test_message_should_be_produced_to_kafka_after_successful_registration(
            self,
            auth_client: AuthClient,
            kafka: KafkaClient,
            userdata_db: UserdataDB
    ):
        username = Faker().user_name()
        password = Faker().password(special_chars=False)

        topic_partitions = kafka.subscribe_listen_new_offsets('users')

        result = auth_client.register(username, password)
        assert result.status_code == 201

        event = kafka.log_msg_and_json(topic_partitions)

        with allure.step('Проверка наличия сообщения из Kafka'):
            assert event != '' and event != b'', "Сообщение из Kafka пустое"

        with allure.step("Проверка содержимого сообщения"):
            data = json.loads(event.decode('utf8'))
            UserName.model_validate(data)

            assert 'username' in data, "Поле 'username' отсутствует в сообщении"

            user_from_db = wait_until_timeout(userdata_db.get_userdata_by_username)(username)
            assert user_from_db is not None, f"Пользователь {username} не найден в БД"

    @allure.title("После отправки в Kafka сообщения с пользователем в БД создается запись")
    @allure.story(Story.registration_messages)
    @allure.tag("kafka", "messaging")
    def test_user_registration_message_should_be_consumed_by_kafka(
            self,
            auth_client: AuthClient,
            kafka: KafkaClient,
            userdata_db: UserdataDB
    ):
        username = Faker().user_name()

        kafka.produce_message('users', {'username': username})

        user_from_db = wait_until_timeout(userdata_db.get_userdata_by_username)(username)

        with allure.step("Проверка создания пользователя в БД"):
            assert user_from_db.username == username
        with allure.step("Проверка установки дефолтной валюты"):
            assert user_from_db.currency == 'RUB'

    @allure.title("После отправки в Kafka n сообщений в БД создается n записей")
    @allure.story(Story.registration_messages)
    @allure.tag("kafka", "messaging")
    @pytest.mark.parametrize('user_count', [10])
    def test_multiple_registration_messages_should_be_consumed_by_kafka(
            self,
            user_count: int,
            auth_client: AuthClient,
            kafka: KafkaClient,
            userdata_db: UserdataDB
    ):
        all_users_db: list[User] = []
        added_username: list[str] = []
        for _ in range(user_count):
            username = Faker().user_name()
            added_username.append(username)
            kafka.produce_message('users', {'username': username})
            user_from_db = wait_until_timeout(userdata_db.get_userdata_by_username)(username)
            all_users_db.append(user_from_db)

        with allure.step("Проверка количества записей в БД"):
            assert len(all_users_db) == user_count

        with allure.step("Проверка соответствия usernames"):
            assert [user.username for user in all_users_db] == added_username

    @allure.title("После отправки дублирующего сообщения в БД не создается повторная запись")
    @allure.story(Story.registration_messages)
    @allure.tag("kafka", "messaging")
    def test_send_to_kafka_duplicate_user_registration_message(
            self,
            auth_client: AuthClient,
            kafka: KafkaClient,
            userdata_db: UserdataDB
    ):
        username = Faker().user_name()
        kafka.produce_message('users', {'username': username})
        wait_until_timeout(userdata_db.get_userdata_by_username)(username)

        kafka.produce_message('users', {'username': username})
        user_from_db = userdata_db.get_all_records_by_username(username)

        with allure.step("Проверка отсутствия дубликата в БД"):
            assert len(user_from_db) == 1
            assert user_from_db[0].username == username

    @allure.title("Сообщения обрабатываются в порядке их отправки")
    @allure.story(Story.produced_messaging)
    @allure.tag("kafka", "messaging")
    def test_messages_processed_in_order(
            self,
            kafka: KafkaClient,
            userdata_db: UserdataDB
    ):
        usernames = [Faker().user_name() for _ in range(5)]

        with allure.step("Отправка сообщений в Kafka по порядку"):
            for username in usernames:
                kafka.produce_message('users', {'username': username})

        with allure.step("Проверка, что все пользователи созданы в БД"):
            users_in_db = []
            for username in usernames:
                user = wait_until_timeout(userdata_db.get_userdata_by_username)(username)
                users_in_db.append(user)

            assert len(users_in_db) == len(usernames)
            for i, user in enumerate(users_in_db):
                assert user.username == usernames[i], f"Expected {usernames[i]}, got {user.username}"

    @allure.title("Сообщения с различными валютами корректно обрабатываются")
    @allure.story(Story.produced_messaging)
    @allure.tag("kafka", "messaging")
    @pytest.mark.parametrize('currency', ['RUB', 'USD', 'EUR'])
    def test_message_with_different_currencies(
            self,
            currency: str,
            kafka: KafkaClient,
            userdata_db: UserdataDB
    ):
        username = Faker().user_name()

        with allure.step(f"Отправка сообщения с валютой {currency}"):
            kafka.produce_message('users', {'username': username})

        with allure.step("Проверка создания пользователя с дефолтной валютой"):
            user_from_db = wait_until_timeout(userdata_db.get_userdata_by_username)(username)

            assert user_from_db is not None, f"User {username} not found in database"
            assert user_from_db.username == username
            assert user_from_db.currency == 'RUB'
