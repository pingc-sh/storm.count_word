import storm
from collections import Counter

class CountBolt(storm.BasicBolt):
    def initialize(self, conf, context):
        self._conf = conf
        self._context = context
        self._counter = Counter()
        storm.logInfo("Counter bolt instance starting...")

    def process(self, tup):
        word = tup.values[0]
        self._counter[word] +=1
        count = self._counter[word]
        storm.logInfo("word_count %s:%s" % (word, count))
        # raise Exception("CountBolt: fake error")

# Start the bolt when it's invoked
CountBolt().run()
