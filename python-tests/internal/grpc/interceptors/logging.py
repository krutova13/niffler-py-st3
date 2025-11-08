import logging

import grpc
from google.protobuf.json_format import MessageToJson


class LoggingInterceptor(grpc.UnaryUnaryClientInterceptor):

    def intercept_unary_unary(self, continuation, client_call_details, request):
        method_name = client_call_details.method.split('/')[-1]
        logging.info(f"\n[gRPC] Вызов метода: /guru.qa.grpc.niffler.NifflerCurrencyService/{method_name}")

        try:
            if hasattr(request, 'DESCRIPTOR'):
                request_json = MessageToJson(request, preserving_proto_field_name=True)
                logging.debug(f"[gRPC запрос] {method_name}: {request_json}")
            else:
                logging.debug(f"[gRPC запрос] {method_name}: {str(request)}")
        except Exception as e:
            logging.error(f"Ошибка логирования запроса: {e}")

        response_future = continuation(client_call_details, request)

        def log_response_callback(response_future):
            try:
                response = response_future.result()
                if hasattr(response, 'DESCRIPTOR'):
                    response_json = MessageToJson(response, preserving_proto_field_name=True)
                    logging.debug(f"[gRPC ответ] {method_name}: {response_json}")
                else:
                    logging.debug(f"[gRPC ответ] {method_name}: {str(response)}")
            except Exception as e:
                logging.error(f"Ошибка в ответе: {e}")

        response_future.add_done_callback(lambda f: log_response_callback(f))

        return response_future
