import storm
import random
import json
import uuid
from kafka import KafkaConsumer

class WordSpout(storm.Spout):
    def initialize(self, conf, context):
        self._conf = conf
        self._context = context

        self._index = 0
        self._tuples = dict()
        self._tuple_retry = 3
        self._topic = 'temptopic_words'

        self._consumer = KafkaConsumer(
            self._topic,
            bootstrap_servers=[
                '10.78.68.45:9092',
                '10.78.68.46:9092',
                '10.78.68.47:9092'
            ],
            consumer_timeout_ms=100,
            group_id="word_count_spout",
            # enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        storm.logInfo("Spout instance starting...")

    def ack(self, tup_id):
        storm.logInfo("tuple %s acked" % tup_id)
        self._tuples.pop(tup_id)

    def fail(self, tup_id):
        record = self._tuples.get(tup_id)
        if not record:
            storm.logInfo("invalid tuple id %s: " % tup_id)
            return
        storm.logInfo("fail record: %s" % record)

        if record["fail_count"] < self._tuple_retry:
            storm.emit(record["data"], id=tup_id)
            storm.logInfo("re-emiting: %s" % record["data"])
            record["fail_count"] += 1
        else:
            storm.logInfo("re-emiting failed 3 time: %s" % record["data"])
            self._tuples.pop(tup_id)

    def nextTuple(self):        
        self._index += 1
        for msg in self._consumer:
            words = msg.value["data"]
            for word in words:
                tuple_id = str(uuid.uuid4())
                record = {
                    "data": [word],
                    "fail_count": 0
                }
                self._tuples[tuple_id] = record

                storm.logInfo("index %d - emiting: %s" % (self._index, word))
                storm.emit([word], id=tuple_id)

# Start the spout when it's invoked
WordSpout().run()
