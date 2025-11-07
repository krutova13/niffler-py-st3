import json
import logging

import allure
from allure_commons.types import AttachmentType
from confluent_kafka import Producer, Consumer, TopicPartition
from confluent_kafka.admin import AdminClient

from config import Settings
from utils.waiters import wait_until_timeout


class KafkaClient:

    def __init__(
            self,
            settings: Settings,
            client_id: str = 'tester',
            group_id: str = 'tester'
    ):
        self.server = settings.KAFKA_ADDRESS
        self.admin = AdminClient(
            {"bootstrap.servers": self.server}
        )
        self.producer = Producer(
            {"bootstrap.servers": self.server}
        )
        self.consumer = Consumer(
            {
                "bootstrap.servers": self.server,
                "group.id": group_id,
                "client.id": client_id,
                "auto.offset.reset": "latest",
                "enable.auto.commit": False,
                "enable.ssl.certificate.verification": False
            }
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.consumer.close()
        self.producer.flush()

    @allure.step("[Kafka] Получить список доступных топиков")
    def list_topics_name(self, attempts: int = 5):
        try:
            topics = self.admin.list_topics(timeout=attempts).topics
            topics_list = [topics.get(item).topic() for item in topics]
            allure.attach(
                json.dumps(topics_list, indent=2, ensure_ascii=False),
                name="Список топиков Kafka",
                attachment_type=AttachmentType.JSON
            )
            logging.info(f"Получено топиков: {len(topics_list)}")
            return topics_list
        except RuntimeError as err:
            logging.error(f'Топики в Kafka не найдены: {err}')
            allure.attach(
                str(err),
                name="Ошибка получения топиков",
                attachment_type=AttachmentType.TEXT
            )
            return []

    @allure.step("[Kafka] Отправить сообщение в топик '{topic}'")
    def produce_message(self, topic: str, value, key: str | None = None):
        if isinstance(value, dict):
            value_str = json.dumps(value, ensure_ascii=False)
            value = value_str.encode('utf-8')
        elif isinstance(value, str):
            value_str = value
            value = value.encode('utf-8')
        else:
            value_str = str(value)

        self.producer.produce(
            topic=topic,
            key=key.encode('utf-8') if key else None,
            value=value,
            headers=[('__TypeId__', b'guru.qa.niffler.model.UserJson')]
        )
        self.producer.flush()

        allure.attach(
            value_str,
            name=f"Сообщение отправлено в топик '{topic}'",
            attachment_type=AttachmentType.JSON if isinstance(value, dict) else AttachmentType.TEXT
        )
        logging.info(f"Сообщение отправлено в топик '{topic}': {value_str[:100]}")

    @wait_until_timeout
    def consume_message(self, partitions, **kwargs):
        self.consumer.assign(partitions)
        try:
            message = self.consumer.poll(1.0)
            msg_value = message.value()
            logging.debug(f'Получено сообщение: {msg_value}')
            return msg_value
        except AttributeError:
            pass

    @allure.step("[Kafka] Получить последний оффсет для топика '{topic}'")
    def get_last_offset(self, topic: str = '', partition_id=0):
        partition = TopicPartition(topic, partition_id)
        try:
            low, high = self.consumer.get_watermark_offsets(partition, timeout=10)
            allure.attach(
                f"Топик: {topic}\nПартиция: {partition_id}\nОффсет: {high}",
                name=f"Оффсет топика '{topic}'",
                attachment_type=AttachmentType.TEXT
            )
            logging.info(f"Последний оффсет для топика '{topic}' (партиция {partition_id}): {high}")
            return high
        except Exception as err:
            logging.error(f"Топик не найден: {topic}: {err}")
            allure.attach(
                f"Ошибка получения оффсета для топика '{topic}': {err}",
                name="Ошибка получения оффсета",
                attachment_type=AttachmentType.TEXT
            )
            return None

    @allure.step("[Kafka] Прочитать и залогировать сообщение")
    def log_msg_and_json(self, topic_partitions):
        msg = self.consume_message(topic_partitions, timeout=25)
        if msg:
            try:
                msg_json = json.loads(msg)
                allure.attach(
                    json.dumps(msg_json, indent=2, ensure_ascii=False),
                    name="Полученное сообщение",
                    attachment_type=AttachmentType.JSON
                )
            except (json.JSONDecodeError, TypeError):
                allure.attach(
                    str(msg),
                    name="Полученное сообщение (текст)",
                    attachment_type=AttachmentType.TEXT
                )
            logging.info(f"Получено сообщение: {msg}")
        return msg

    @allure.step("[Kafka] Подписаться на топик '{topic}' и получить оффсеты")
    def subscribe_listen_new_offsets(self, topic):
        self.consumer.subscribe([topic])

        p_ids = self.consumer.list_topics(topic).topics[topic].partitions.keys()
        partitions_offsets_event = {k: self.get_last_offset(topic, k) for k in p_ids}

        allure.attach(
            json.dumps(partitions_offsets_event, indent=2, ensure_ascii=False),
            name=f"Оффсеты топика '{topic}'",
            attachment_type=AttachmentType.JSON
        )
        logging.info(f"Оффсеты топика '{topic}': {partitions_offsets_event}")

        topic_partitions = [TopicPartition(topic, k, v) for k, v in partitions_offsets_event.items()]
        return topic_partitions
