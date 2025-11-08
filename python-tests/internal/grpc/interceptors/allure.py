import logging

import allure
import grpc
from google.protobuf.json_format import MessageToJson


class AllureInterceptor(grpc.UnaryUnaryClientInterceptor):

    def intercept_unary_unary(self, continuation, client_call_details, request):
        method_name = client_call_details.method.split('/')[-1]

        try:
            if hasattr(request, 'DESCRIPTOR'):
                request_json = MessageToJson(request, preserving_proto_field_name=True)
                allure.attach(
                    request_json,
                    name=f"gRPC запрос: {method_name}",
                    attachment_type=allure.attachment_type.JSON
                )
            else:
                allure.attach(
                    str(request),
                    name=f"gRPC запрос: {method_name}",
                    attachment_type=allure.attachment_type.TEXT
                )
            logging.debug(f"gRPC запрос: {method_name}")
        except Exception as e:
            error_msg = f"Ошибка логирования запроса: {str(e)}"
            logging.error(error_msg)
            allure.attach(
                error_msg,
                name=f"Ошибка запроса: {method_name}",
                attachment_type=allure.attachment_type.TEXT
            )

        response_future = continuation(client_call_details, request)

        def log_response_callback(response_future):
            try:
                response = response_future.result()
                if hasattr(response, 'DESCRIPTOR'):
                    response_json = MessageToJson(response, preserving_proto_field_name=True)
                    allure.attach(
                        response_json,
                        name=f"gRPC ответ: {method_name}",
                        attachment_type=allure.attachment_type.JSON
                    )
                else:
                    allure.attach(
                        str(response),
                        name=f"gRPC ответ: {method_name}",
                        attachment_type=allure.attachment_type.TEXT
                    )
                logging.info(f"gRPC ответ получен: {method_name}")
            except Exception as e:
                error_msg = f"Ошибка: {str(e)}"
                logging.error(error_msg)
                allure.attach(
                    error_msg,
                    name=f"Ошибка ответа: {method_name}",
                    attachment_type=allure.attachment_type.TEXT
                )

        response_future.add_done_callback(lambda f: log_response_callback(f))

        return response_future
