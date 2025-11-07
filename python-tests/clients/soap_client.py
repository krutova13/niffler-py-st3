import logging
from xml.etree import ElementTree as ET

import allure
import requests
from allure_commons.types import AttachmentType

from models.soap import PageInfo, SoapUser


class SoapClient:
    def __init__(self, base_url: str = "http://localhost:8089/ws"):
        self.base_url = base_url
        self.wsdl_url = f"{base_url}/userdata.wsdl"
        self.headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': ''
        }

    def _create_soap_envelope(self, body_content: str) -> str:
        return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="niffler-userdata">
    <soap:Body>
        {body_content}
    </soap:Body>
</soap:Envelope>"""

    @allure.step("[SOAP] Выполнить запрос: {operation}")
    def _make_soap_call(self, operation: str, xml_body: str) -> tuple[any, int]:
        envelope = self._create_soap_envelope(xml_body)

        allure.attach(
            envelope,
            name=f"SOAP запрос: {operation}",
            attachment_type=AttachmentType.XML
        )
        logging.debug(f"SOAP запрос: {operation}")

        try:
            response = requests.post(
                self.base_url,
                data=envelope,
                headers=self.headers,
                timeout=30
            )

            allure.attach(
                response.text,
                name=f"SOAP ответ: {operation} (статус {response.status_code})",
                attachment_type=AttachmentType.XML
            )

            logging.info(f"SOAP {operation}: статус {response.status_code}")

            return self._parse_soap_response(response.text), response.status_code

        except requests.exceptions.RequestException as e:
            error_msg = f"SOAP запрос не выполнен: {str(e)}"
            logging.error(error_msg)
            allure.attach(
                error_msg,
                name=f"Ошибка SOAP запроса: {operation}",
                attachment_type=AttachmentType.TEXT
            )
            return f"Запрос не выполнен: {str(e)}", 500

    def _parse_soap_response(self, xml_response: str) -> dict[str, any]:
        try:
            namespaces = {
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'ns2': 'niffler-userdata',
                'tns': 'niffler-userdata'
            }

            root = ET.fromstring(xml_response)

            body = root.find('.//soap:Body', namespaces)
            if body is None:
                body = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body')

            if body is not None and len(body) > 0:
                response_element = body[0]
                return self._parse_element_with_namespace(response_element)

            error_msg = "Тело ответа не найдено"
            logging.error(error_msg)
            return {"error": error_msg}

        except ET.ParseError as e:
            error_msg = f"Ошибка парсинга XML: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg}

    def _parse_element_with_namespace(self, element: ET.Element) -> dict[str, any]:
        result = {}

        for child in element:
            tag = self._remove_namespace(child.tag)

            if len(child) == 0:
                result[tag] = child.text
            else:
                child_data = self._parse_element_with_namespace(child)

                if tag in result:
                    if isinstance(result[tag], list):
                        result[tag].append(child_data)
                    else:
                        result[tag] = [result[tag], child_data]
                else:
                    result[tag] = child_data

        return result

    def _remove_namespace(self, tag: str) -> str:
        if '}' in tag:
            return tag.split('}', 1)[1]
        return tag

    def _extract_user_from_response(self, response_data: dict[str, any]) -> dict[str, any]:
        """Извлечь данные пользователя из ответа."""
        logging.debug(f"Извлечение пользователя из: {response_data}")

        user_keys = ['id', 'username', 'currency', 'friendshipStatus']
        if any(key in response_data for key in user_keys):
            return response_data

        if 'user' in response_data:
            user_data = response_data['user']
            if isinstance(user_data, dict):
                return user_data
            elif isinstance(user_data, list) and user_data:
                return user_data[0]

        for key, value in response_data.items():
            if isinstance(value, dict) and any(k in value for k in user_keys):
                return value

        return response_data


    @allure.step("[SOAP] Получить текущего пользователя: {username}")
    def get_current_user(self, username: str) -> tuple[dict[str, any], int]:
        xml_body = f"""
        <tns:currentUserRequest>
            <tns:username>{username}</tns:username>
        </tns:currentUserRequest>"""

        response, status_code = self._make_soap_call("currentUser", xml_body)
        user_data = self._extract_user_from_response(response)

        import json
        allure.attach(
            json.dumps(user_data, indent=2, ensure_ascii=False),
            name=f"Данные пользователя: {username}",
            attachment_type=AttachmentType.JSON
        )
        logging.info(f"Получены данные пользователя: {username}")

        return user_data, status_code

    @allure.step("[SOAP] Обновить пользователя")
    def update_user(self, user: SoapUser) -> tuple[dict[str, any], int]:
        user_xml_parts = [
            f"<tns:id>{user.id}</tns:id>" if user.id else "<tns:id></tns:id>",
            f"<tns:username>{user.username}</tns:username>",
            f"<tns:currency>{user.currency.value}</tns:currency>"
        ]

        if user.firstname:
            user_xml_parts.append(f"<tns:firstname>{user.firstname}</tns:firstname>")
        if user.surname:
            user_xml_parts.append(f"<tns:surname>{user.surname}</tns:surname>")
        if user.fullname:
            user_xml_parts.append(f"<tns:fullname>{user.fullname}</tns:fullname>")

        user_xml = "\n".join(user_xml_parts)

        xml_body = f"""
        <tns:updateUserRequest>
            <tns:user>
                {user_xml}
            </tns:user>
        </tns:updateUserRequest>"""

        response, status_code = self._make_soap_call("updateUser", xml_body)
        updated_user = self._extract_user_from_response(response)

        import json
        allure.attach(
            json.dumps(updated_user, indent=2, ensure_ascii=False),
            name=f"Обновленный пользователь: {user.username}",
            attachment_type=AttachmentType.JSON
        )
        logging.info(f"Пользователь обновлен: {user.username}")

        return updated_user, status_code

    @allure.step("[SOAP] Получить всех пользователей для: {username}")
    def get_all_users(self, username: str, search_query: str = None) -> tuple[list[dict[str, any]], int]:
        search_xml = f"<tns:searchQuery>{search_query}</tns:searchQuery>" if search_query else ""
        xml_body = f"""
        <tns:allUsersRequest>
            <tns:username>{username}</tns:username>
            {search_xml}
        </tns:allUsersRequest>"""

        response, status_code = self._make_soap_call("allUsers", xml_body)

        users = []
        if 'user' in response:
            user_data = response['user']
            if isinstance(user_data, list):
                users = user_data
            elif isinstance(user_data, dict):
                users = [user_data]

        import json
        allure.attach(
            json.dumps(users, indent=2, ensure_ascii=False),
            name=f"Все пользователи (всего: {len(users)})",
            attachment_type=AttachmentType.JSON
        )
        logging.info(f"Получено пользователей: {len(users)}")

        return users, status_code

    @allure.step("[SOAP] Получить страницу пользователей")
    def get_all_users_page(self, username: str, page_info: PageInfo, search_query: str = None) -> \
            tuple[dict[str, any], int]:
        search_xml = f"<tns:searchQuery>{search_query}</tns:searchQuery>" if search_query else ""

        sort_xml = ""
        for sort_item in page_info.sort:
            sort_xml += f"""
            <tns:sort>
                <tns:property>{sort_item.property}</tns:property>
                <tns:direction>{sort_item.direction.value}</tns:direction>
            </tns:sort>"""

        page_info_xml = f"""
        <tns:pageInfo>
            <tns:page>{page_info.page}</tns:page>
            <tns:size>{page_info.size}</tns:size>
            {sort_xml}
        </tns:pageInfo>"""

        xml_body = f"""
        <tns:allUsersPageRequest>
            <tns:username>{username}</tns:username>
            {page_info_xml}
            {search_xml}
        </tns:allUsersPageRequest>"""

        response, status_code = self._make_soap_call("allUsersPage", xml_body)

        import json
        allure.attach(
            json.dumps(response, indent=2, ensure_ascii=False),
            name="Страница пользователей",
            attachment_type=AttachmentType.JSON
        )

        return response, status_code

    @allure.step("[SOAP] Получить друзей: {username}")
    def get_friends(self, username: str, search_query: str = None) -> tuple[list[dict[str, any]], int]:
        search_xml = f"<tns:searchQuery>{search_query}</tns:searchQuery>" if search_query else ""
        xml_body = f"""
        <tns:friendsRequest>
            <tns:username>{username}</tns:username>
            {search_xml}
        </tns:friendsRequest>"""

        response, status_code = self._make_soap_call("friends", xml_body)

        users = []
        if 'user' in response:
            user_data = response['user']
            if isinstance(user_data, list):
                users = user_data
            elif isinstance(user_data, dict):
                users = [user_data]

        import json
        allure.attach(
            json.dumps(users, indent=2, ensure_ascii=False),
            name=f"Друзья пользователя {username} (всего: {len(users)})",
            attachment_type=AttachmentType.JSON
        )
        logging.info(f"Получено друзей для {username}: {len(users)}")

        return users, status_code

    @allure.step("[SOAP] Получить страницу друзей")
    def get_friends_page(self, username: str, page_info: PageInfo, search_query: str = None) -> \
            tuple[dict[str, any], int]:
        search_xml = f"<tns:searchQuery>{search_query}</tns:searchQuery>" if search_query else ""

        sort_xml = ""
        for sort_item in page_info.sort:
            sort_xml += f"""
            <tns:sort>
                <tns:property>{sort_item.property}</tns:property>
                <tns:direction>{sort_item.direction.value}</tns:direction>
            </tns:sort>"""

        page_info_xml = f"""
        <tns:pageInfo>
            <tns:page>{page_info.page}</tns:page>
            <tns:size>{page_info.size}</tns:size>
            {sort_xml}
        </tns:pageInfo>"""

        xml_body = f"""
        <tns:friendsPageRequest>
            <tns:username>{username}</tns:username>
            {page_info_xml}
            {search_xml}
        </tns:friendsPageRequest>"""

        response, status_code = self._make_soap_call("friendsPage", xml_body)

        import json
        allure.attach(
            json.dumps(response, indent=2, ensure_ascii=False),
            name="Страница друзей",
            attachment_type=AttachmentType.JSON
        )

        return response, status_code
