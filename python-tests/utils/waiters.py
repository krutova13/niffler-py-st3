import datetime
import logging
import time

import allure


@allure.step("Ожидание результата с тайм-аутом")
def wait_until_timeout(function):
    def wrapper(*args, **kwargs):
        default_timeout = 12
        timeout = kwargs.pop("timeout", default_timeout)
        polling_interval = kwargs.pop("polling_interval", 0.1)
        err = kwargs.pop("err", None)
        start_time = datetime.datetime.now().timestamp()
        result = None
        logging.debug(f'{start_time} начало ожидания')

        with allure.step(f"Ожидание результата функции {function.__name__} (тайм-аут: {timeout}с)"):
            while datetime.datetime.now().timestamp() < start_time + timeout + 0.1:
                result = function(*args, **kwargs)
                if result is not None and result != [] and result != '':
                    logging.info(f"Результат получен за {datetime.datetime.now().timestamp() - start_time:.2f}с")
                    break
                time.sleep(polling_interval)

            if err and result is None:
                error_msg = (
                    f"{datetime.datetime.now().isoformat()} "
                    f"Результаты функции {function.__name__} не найдены за {timeout}с"
                )
                logging.error(error_msg)
                raise TimeoutError(error_msg)

            if result is None:
                logging.warning(f"{datetime.datetime.now().timestamp()} результат не получен (None)")

        return result

    return wrapper
