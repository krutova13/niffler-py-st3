import allure
import pytest

from clients.soap_client import SoapClient
from marks import TestData
from models.enums import Currency, FriendshipStatus
from models.soap import PageInfo, SoapUser
from utils.allure_helpers import Feature, Epic, Story


@allure.epic(Epic.app_name)
@pytest.mark.usefixtures(
    "soap_client",
    "mock_users",
    "mock_friends",
    "soap_user",
    "cleanup"
)
@pytest.mark.soap
@pytest.mark.user_management
@allure.feature(Feature.userdata)
class TestSoapUsers:
    @staticmethod
    def map_pagination_error(page_info: PageInfo) -> str | None:
        if page_info.page < 0:
            return "Page index must not be less than zero"
        if page_info.size < 1:
            return "Page size must not be less than one"
        return None

    @allure.story(Story.user_management)
    def test_get_user_info_with_existing_username(self, soap_client: SoapClient, soap_user: str):
        user_data, status_code = soap_client.get_current_user(username=soap_user)

        with allure.step('Проверка корректности ответа'):
            assert status_code == 200, f"Expected 200, got {status_code}. Response: {user_data}"
            assert 'username' in user_data, f"Username not found in response: {user_data}"
            assert user_data['username'] == soap_user

            if user_data.get('id'):
                assert isinstance(user_data['id'], str), f"ID should be string, got {type(user_data['id'])}"
            assert user_data.get('currency'), f"У пользователя {soap_user} нет currency"
            assert user_data.get('friendshipStatus'), f"У пользователя {soap_user} нет friendshipStatus"

    @allure.story(Story.user_management)
    def test_get_user_that_doesnt_exist(self, soap_client: SoapClient):
        username = "a_user_that_has_never_existed_12345"
        user_data, status_code = soap_client.get_current_user(username=username)

        with allure.step('Проверка корректности ответа'):
            if status_code == 200:
                assert user_data is not None
                assert user_data.get('username') == username
                assert 'currency' in user_data
                assert 'friendshipStatus' in user_data
            else:
                assert status_code in [400, 404, 500]

    @allure.story(Story.user_management)
    def test_get_all_users(self, soap_client: SoapClient, soap_user: str):
        users, status_code = soap_client.get_all_users(username=soap_user)

        with allure.step('Проверка корректности ответа'):
            assert status_code == 200
            assert isinstance(users, list)
            # Может быть пустым списком или содержать пользователей
            for user in users:
                assert 'username' in user
                assert 'currency' in user

    @TestData.page_info([
        PageInfo(page=0, size=3),
        PageInfo(page=1, size=4),
        PageInfo(page=0, size=6),
        PageInfo(page=3, size=2)
    ])
    @allure.story(Story.user_management)
    def test_get_all_users_pagination(self, soap_client: SoapClient, soap_user: str, page_info: PageInfo):
        page_result, status_code = soap_client.get_all_users_page(
            username=soap_user,
            page_info=page_info
        )

        with allure.step('Проверка структуры ответа с пагинацией'):
            assert status_code == 200, f"Expected 200, got {status_code}. Response: {page_result}"
            assert isinstance(page_result, dict)

            # Проверяем наличие полей пагинации
            if 'size' in page_result:
                size_value = page_result['size']
                if isinstance(size_value, str) and size_value.isdigit():
                    assert int(size_value) == page_info.size
                else:
                    assert size_value == page_info.size

            if 'number' in page_result:
                number_value = page_result['number']
                if isinstance(number_value, str) and number_value.isdigit():
                    assert int(number_value) == page_info.page
                else:
                    assert number_value == page_info.page

    @TestData.page_info([
        PageInfo(page=100, size=10),
        PageInfo(page=999, size=5),
    ])
    @allure.story(Story.user_management)
    def test_get_all_users_page_out_of_range(self, soap_client: SoapClient, soap_user: str, page_info: PageInfo):
        page_result, status_code = soap_client.get_all_users_page(
            username=soap_user,
            page_info=page_info
        )

        with allure.step('Проверка структуры ответа с пагинацией'):
            if status_code == 200:
                assert isinstance(page_result, dict)
                users = page_result.get('user', [])
                if isinstance(users, dict):
                    users = [users]
                assert len(users) == 0
            else:
                assert status_code in [400, 500]

    @TestData.page_info([
        PageInfo(page=-1, size=1),
        PageInfo(page=0, size=0),
        PageInfo(page=1, size=-1),
    ])
    @allure.story(Story.user_management)
    def test_get_all_users_page_invalid_parameters(self, soap_client: SoapClient, soap_user: str, page_info: PageInfo):
        page_result, status_code = soap_client.get_all_users_page(
            username=soap_user,
            page_info=page_info
        )

        with allure.step('Проверка корректности ответа'):
            assert status_code in [200, 400, 500]

    @allure.story(Story.user_management)
    def test_cannot_update_user_without_id(
            self,
            user_without_id: str,
            soap_client: SoapClient
    ):
        current_user, status_code = soap_client.get_current_user(username=user_without_id)
        assert status_code == 200
        assert not current_user.get('id'), f"User {user_without_id} should not have ID"

        update_data = SoapUser(
            id="",
            username=user_without_id,
            currency=Currency.USD
        )

        response, status_code = soap_client.update_user(update_data)

        with allure.step('Проверка что обновление невозможно без ID'):
            assert status_code in [400, 500], f"Expected error for user without ID, got {status_code}"

    @pytest.mark.friends_management
    @allure.story(Story.friends_management)
    def test_get_friends(self, soap_client: SoapClient, soap_friends_user: str):
        friends, status_code = soap_client.get_friends(username=soap_friends_user)

        with allure.step('Проверка корректности ответа'):
            assert isinstance(friends, list)
            for friend in friends:
                assert 'username' in friend
                assert 'friendshipStatus' in friend
                if friends:
                    assert friend['friendshipStatus'] == FriendshipStatus.FRIEND.value

    @TestData.page_info([
        PageInfo(page=1, size=5),
        PageInfo(page=2, size=3),
        PageInfo(page=4, size=2)
    ])
    @pytest.mark.friends_management
    @allure.story(Story.friends_management)
    def test_get_friends_page(
            self,
            soap_client: SoapClient,
            soap_friends_user: str,
            page_info: PageInfo,
    ):
        page_result, status_code = soap_client.get_friends_page(
            username=soap_friends_user,
            page_info=page_info
        )

        with allure.step('Проверка структуры ответа с пагинацией'):
            if status_code == 200:
                assert isinstance(page_result, dict)
                if 'size' in page_result:
                    assert int(page_result.get('size')) == page_info.size
                if 'number' in page_result:
                    assert int(page_result.get('number')) == page_info.page

    @TestData.page_info([
        PageInfo(page=4, size=100),
        PageInfo(page=100, size=100),
        PageInfo(page=1000, size=1)
    ])
    @pytest.mark.friends_management
    @allure.story(Story.friends_management)
    def test_get_friends_page_out_of_range(
            self,
            soap_client: SoapClient,
            soap_friends_user: str,
            page_info: PageInfo
    ):
        page_result, status_code = soap_client.get_friends_page(
            username=soap_friends_user,
            page_info=page_info
        )

        with allure.step('Проверка структуры ответа с пагинацией'):
            if status_code == 200:
                assert isinstance(page_result, dict)
                users = page_result.get('user', [])
                if isinstance(users, dict):
                    users = [users]
                assert len(users) == 0

                if 'size' in page_result:
                    assert int(page_result.get('size')) == page_info.size
                if 'number' in page_result:
                    assert int(page_result.get('number')) == page_info.page

    @TestData.page_info([
        PageInfo(page=-1, size=1),
        PageInfo(page=1, size=-1),
        PageInfo(page=1, size=0),
        PageInfo(page=-1, size=-1)
    ])
    @pytest.mark.friends_management
    @allure.story(Story.friends_management)
    def test_get_friends_page_invalid_parameters(
            self,
            soap_client: SoapClient,
            soap_friends_user: str,
            page_info: PageInfo
    ):
        page_result, status_code = soap_client.get_friends_page(
            username=soap_friends_user,
            page_info=page_info
        )
        error_text = self.map_pagination_error(page_info)

        with allure.step('Проверка корректности ответа'):
            if status_code == 500:
                assert error_text in str(page_result)
