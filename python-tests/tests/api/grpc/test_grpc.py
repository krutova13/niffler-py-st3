import allure
import grpc
import pytest
from google.protobuf import empty_pb2

from fixtures.grpc_fixtures import TestNifflerCurrencyServiceBase
from internal.pb.niffler_currency_pb2 import CalculateRequest, CurrencyValues, CurrencyResponse


@allure.epic("gRPC сервисы")
@allure.feature("Сервис валют")
@allure.tag("grpc", "currency", "integration")
@pytest.mark.grpc
class TestNifflerCurrencyServiceIntegration(TestNifflerCurrencyServiceBase):

    @allure.title("Получение всех валют - успешное получение")
    @allure.story("Управление валютами")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("""
    Тест успешного получения всех доступных валют из gRPC сервиса.
    Проверяет что все ожидаемые валюты присутствуют с корректными курсами обмена.
    """)
    @pytest.mark.integration
    def test_get_all_currencies_success(self, client):
        with allure.step("Выполнить gRPC вызов GetAllCurrencies"):
            response = client.get_all_currencies(empty_pb2.Empty())

        with allure.step("Проверить структуру и содержимое ответа"):
            assert isinstance(response, CurrencyResponse), "Ответ должен быть типа CurrencyResponse"
            assert len(response.allCurrencies) == 4, f"Ожидается 4 валюты, получено {len(response.allCurrencies)}"

            currencies_dict = {
                currency.currency: currency.currencyRate
                for currency in response.allCurrencies
            }

            allure.attach(
                str(currencies_dict),
                name="Полученные валюты",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Проверить наличие всех ожидаемых валют"):
            expected_currencies = [
                CurrencyValues.RUB, CurrencyValues.USD,
                CurrencyValues.EUR, CurrencyValues.KZT
            ]

            for currency in expected_currencies:
                with allure.step(f"Проверка валюты {currency}"):
                    assert currency in currencies_dict, f"Валюта {currency} отсутствует"
                    assert currencies_dict[currency] > 0, f"Курс валюты {currency} должен быть положительным"
                    allure.attach(
                        f"Валюта: {currency}, Курс: {currencies_dict[currency]}",
                        name=f"Валюта_{currency}",
                        attachment_type=allure.attachment_type.TEXT
                    )

    @allure.title("Расчет курса - точные конвертации: {spend_currency} -> {desired_currency}")
    @allure.story("Конвертация валют")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
    Тест точных конвертаций валют на основе известных курсов обмена.
    Проверяет точность расчетов конвертации валют.
    """)
    @pytest.mark.integration
    @pytest.mark.parametrize(
        "spend_currency,desired_currency,amount,expected_amount",
        [
            (CurrencyValues.EUR, CurrencyValues.RUB, 100.0, 7200.0),
            (CurrencyValues.USD, CurrencyValues.EUR, 100.0, 92.592),
            (CurrencyValues.RUB, CurrencyValues.USD, 1000.0, 15.0),
            (CurrencyValues.KZT, CurrencyValues.EUR, 10000.0, 19.444),
        ],
        ids=lambda x: f"{x}" if not isinstance(x, float) else f"{x:.1f}"
    )
    def test_calculate_rate_exact_conversions(self, client, spend_currency,
                                              desired_currency, amount, expected_amount):
        with allure.step(f"Подготовить запрос конвертации: {amount} {spend_currency} -> {desired_currency}"):
            request = CalculateRequest(
                spendCurrency=spend_currency,
                desiredCurrency=desired_currency,
                amount=amount
            )

        with allure.step("Выполнить gRPC вызов CalculateRate"):
            response = client.calculate_rate(request)

        with allure.step("Проверить результат конвертации с допуском"):
            tolerance = 0.1
            actual_amount = response.calculatedAmount
            difference = abs(actual_amount - expected_amount)

            allure.attach(
                f"Ожидается: {expected_amount}\nПолучено: {actual_amount}\nРазница: {difference}\nДопуск: {tolerance}",
                name="Детали конвертации",
                attachment_type=allure.attachment_type.TEXT
            )

            assert difference <= tolerance, (
                f"Ожидалось {expected_amount}, получено {actual_amount}, разница {difference} > допуска {tolerance}"
            )


@allure.epic("gRPC сервисы")
@allure.feature("Сервис валют")
@allure.tag("grpc", "currency", "boundary")
@pytest.mark.grpc
class TestNifflerCurrencyServiceBoundaryValues(TestNifflerCurrencyServiceBase):

    @allure.title("Граничные значения сумм: {description}")
    @allure.story("Граничные значения")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Тест конвертации валют с различными граничными значениями сумм.")
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "amount,expected_result,description",
        [
            (0.000001, 0.0, "Микро сумма - сервер возвращает 0"),
            (0.001, 0.0, "Очень маленькая сумма - сервер возвращает 0"),
            (0.01, 0.00926, "Минимальная рабочая сумма USD->EUR"),
            (0.1, 0.0926, "Небольшая сумма USD->EUR"),
            (1.0, 0.926, "Единичная сумма USD->EUR"),
            (100.0, 92.59, "Нормальная сумма USD->EUR"),
            (1000.0, 925.93, "Большая сумма USD->EUR"),
            (100000.0, 92592.59, "Очень большая сумма USD->EUR"),
            (1000000.0, 925925.93, "Экстремальная сумма USD->EUR"),
        ]
    )
    def test_calculate_rate_amount_boundaries(self, client, amount, expected_result,
                                              description):
        with allure.step(f"Подготовить запрос с суммой: {amount}"):
            request = CalculateRequest(
                spendCurrency=CurrencyValues.USD,
                desiredCurrency=CurrencyValues.EUR,
                amount=amount
            )

        with allure.step("Выполнить конвертацию"):
            response = client.calculate_rate(request)

        with allure.step(f"Проверить результат для '{description}'"):
            actual_amount = response.calculatedAmount

            if expected_result == 0.0:
                assert actual_amount == 0.0, (
                    f"Ожидалось 0.0, получено {actual_amount}"
                )
                allure.attach(
                    f"Сумма: {amount}\nРезультат: {actual_amount}\nПоведение: Возвращает 0 для очень маленьких сумм",
                    name="Поведение при нулевом результате",
                    attachment_type=allure.attachment_type.TEXT
                )
            else:
                tolerance = 0.01 if amount <= 1.0 else amount * 0.01
                difference = abs(actual_amount - expected_result)

                allure.attach(
                    f"Сумма: {amount}\nОжидается: {expected_result}\nПолучено: {actual_amount}\nРазница: {difference}\nДопуск: {tolerance}",
                    name="Детали конвертации",
                    attachment_type=allure.attachment_type.TEXT
                )

                assert difference <= tolerance, (
                    f"Ожидалось ~{expected_result}, получено {actual_amount}, разница {difference} > допуска {tolerance}"
                )

    @allure.title("Валютные пары: {description}")
    @allure.story("Валютные пары")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "spend_currency,desired_currency,amount,description",
        [
            (CurrencyValues.RUB, CurrencyValues.USD, 1000.0, "RUB->USD обычная"),
            (CurrencyValues.USD, CurrencyValues.RUB, 100.0, "USD->RUB обычная"),
            (CurrencyValues.EUR, CurrencyValues.KZT, 50.0, "EUR->KZT обычная"),
            (CurrencyValues.KZT, CurrencyValues.EUR, 50000.0, "KZT->EUR обычная"),
            (CurrencyValues.USD, CurrencyValues.KZT, 10.0, "USD->KZT обычная"),
        ]
    )
    def test_calculate_rate_currency_pairs_positive(self, client, spend_currency,
                                                    desired_currency, amount, description):
        with allure.step(f"Тест валютной пары: {spend_currency} -> {desired_currency}"):
            request = CalculateRequest(
                spendCurrency=spend_currency,
                desiredCurrency=desired_currency,
                amount=amount
            )

            response = client.calculate_rate(request)

        with allure.step("Проверить положительный результат"):
            assert response.calculatedAmount >= 0, (
                f"Результат должен быть неотрицательным, получено {response.calculatedAmount}"
            )

        with allure.step(
                "Проверка обработки одинаковой валюты" if spend_currency == desired_currency else "Проверка результата конвертации"):
            if spend_currency == desired_currency:
                assert response.calculatedAmount == amount, (
                    "Одинаковая валюта должна вернуть исходную сумму"
                )
            else:
                allure.attach(
                    f"Из: {spend_currency}\nВ: {desired_currency}\nСумма: {amount}\nРезультат: {response.calculatedAmount}",
                    name="Результат конвертации",
                    attachment_type=allure.attachment_type.TEXT
                )

    @allure.title("Отрицательные суммы: {description}")
    @allure.story("Обработка ошибок")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "amount,description",
        [
            (-0.01, "Маленькая отрицательная сумма"),
            (-1.0, "Единичная отрицательная сумма"),
            (-100.0, "Средняя отрицательная сумма"),
            (-1000.0, "Большая отрицательная сумма"),
        ]
    )
    def test_calculate_rate_negative_amounts(self, client, amount, description):
        with allure.step(f"Тест с отрицательной суммой: {amount}"):
            request = CalculateRequest(
                spendCurrency=CurrencyValues.USD,
                desiredCurrency=CurrencyValues.EUR,
                amount=amount
            )

            response = client.calculate_rate(request)

        with allure.step("Проверить неположительный результат для отрицательного входа"):
            assert response.calculatedAmount <= 0, (
                f"Отрицательный вход должен давать неположительный результат, получено {response.calculatedAmount}"
            )

            allure.attach(
                f"Вход: {amount}\nВыход: {response.calculatedAmount}",
                name="Обработка отрицательной суммы",
                attachment_type=allure.attachment_type.TEXT
            )


@allure.epic("gRPC сервисы")
@allure.feature("Сервис валют")
@allure.tag("grpc", "currency", "error-handling")
@pytest.mark.grpc
class TestNifflerCurrencyServiceErrorScenarios(TestNifflerCurrencyServiceBase):
    @allure.title("Обработка неуказанной валюты")
    @allure.story("Сценарии ошибок")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Тест проверяет что UNSPECIFIED валюта возвращает корректную gRPC ошибку.")
    @pytest.mark.boundary
    def test_calculate_rate_unspecified_currency(self, client):
        with allure.step("Подготовить запрос с UNSPECIFIED валютой"):
            request = CalculateRequest(
                spendCurrency=CurrencyValues.UNSPECIFIED,
                desiredCurrency=CurrencyValues.USD,
                amount=100.0
            )

        with allure.step("Проверить что возникает gRPC ошибка"):
            with pytest.raises(grpc.RpcError) as exc_info:
                client.calculate_rate(request)

        with allure.step("Проверить код и детали ошибки"):
            assert exc_info.value.code() == grpc.StatusCode.UNKNOWN, "Ожидается код ошибки UNKNOWN"

            allure.attach(
                f"Код ошибки: {exc_info.value.code()}\nДетали: {exc_info.value.details()}",
                name="Детали gRPC ошибки",
                attachment_type=allure.attachment_type.TEXT
            )


@allure.epic("gRPC сервисы")
@allure.feature("Сервис валют")
@allure.tag("grpc", "currency", "equivalence")
@pytest.mark.grpc
class TestNifflerCurrencyServiceEquivalencePartitioning(TestNifflerCurrencyServiceBase):

    @allure.title("Эквивалентность сумм: {description}")
    @allure.story("Разбиение по эквивалентности")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "amount,expected_behavior,description",
        [
            (0.0, "valid", "Нулевая сумма"),
            (0.01, "valid", "Минимальная рабочая сумма"),
            (100.0, "valid", "Обычная сумма"),
            (1000000.0, "valid", "Большая сумма"),
            (0.001, "valid_returns_zero", "Очень маленькая сумма возвращает 0"),
            (0.0001, "valid_returns_zero", "Микро сумма возвращает 0"),
            (-0.01, "valid_negative", "Маленькая отрицательная сумма"),
            (-100.0, "valid_negative", "Средняя отрицательная сумма"),
        ]
    )
    def test_amount_equivalence_partitions(self, client, amount, expected_behavior,
                                           description):
        with allure.step(f"Тест суммы: {amount} ({description})"):
            request = CalculateRequest(
                spendCurrency=CurrencyValues.USD,
                desiredCurrency=CurrencyValues.EUR,
                amount=amount
            )

            response = client.calculate_rate(request)

        with allure.step(f"Проверить поведение '{expected_behavior}'"):
            actual_amount = response.calculatedAmount

            behavior_info = {
                "valid": "Положительный или нулевой результат",
                "valid_returns_zero": "Возвращает точно 0",
                "valid_negative": "Отрицательный или нулевой результат"
            }

            allure.attach(
                f"Сумма: {amount}\nОжидаемое поведение: {expected_behavior}\n"
                f"Фактический результат: {actual_amount}\nОписание: {behavior_info[expected_behavior]}",
                name="Результат разбиения по эквивалентности",
                attachment_type=allure.attachment_type.TEXT
            )

            if expected_behavior == "valid":
                assert actual_amount >= 0, f"Ожидается неотрицательный результат, получено {actual_amount}"
            elif expected_behavior == "valid_returns_zero":
                assert actual_amount == 0.0, f"Ожидается точно 0.0, получено {actual_amount}"
            elif expected_behavior == "valid_negative":
                assert actual_amount <= 0, f"Ожидается неположительный результат, получено {actual_amount}"
