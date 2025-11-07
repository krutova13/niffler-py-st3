import grpc
import pytest

from internal.grpc.interceptors.allure import AllureInterceptor
from internal.grpc.interceptors.logging import LoggingInterceptor
from internal.pb.niffler_currency_pb2_pbreflect import NifflerCurrencyServiceClient

INTERCEPTORS = [
    LoggingInterceptor(),
    AllureInterceptor(),
]


class TestNifflerCurrencyServiceBase:

    @pytest.fixture
    def grpc_channel(self, settings):
        with grpc.insecure_channel(settings.GRPC_URL) as channel:
            intercepted_channel = grpc.intercept_channel(channel, *INTERCEPTORS)

            yield intercepted_channel

    @pytest.fixture
    def client(self, grpc_channel):
        return NifflerCurrencyServiceClient(grpc_channel)
