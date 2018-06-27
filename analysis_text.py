import os
import concurrent.futures

from statistics import mean
from collections import defaultdict
from wit import Wit
from wit.wit import WitError
from settings import WIT_AI_ACCESS_TOKEN


class AnalysisText:
    __slots__ = ["client"]

    def __init__(self):
        self.client = Wit(WIT_AI_ACCESS_TOKEN)

    def _sentimental_results_generator(self, text):
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as executor:
            future_results = [executor.submit(self.get_sentiment_of_sentence, sentence) for sentence in text.split(".")]
            concurrent.futures.wait(future_results)
            for future in future_results:
                try:
                    yield future.result()[0]
                except:
                    yield []

    @staticmethod
    def _get_sentiment_with_max_confidence(text_sentiment_confidence):
        text_sentiment_confidence_means = {key: mean(val) for key, val in text_sentiment_confidence.items() if val}
        if text_sentiment_confidence_means:
            return max(text_sentiment_confidence, key=text_sentiment_confidence.get)
        else:
            raise ValueError("No sentiment context")

    def get_sentiment_of_sentence(self, sentence):
        try:
            resp = self.client.message(sentence)
        except WitError:
            return []
        else:
            return resp["entities"].get("sentiment", [])

    def get_sentiment_for_text(self, text):
        text_sentiment_confidence = defaultdict(list)
        for sentense_result in self._sentimental_results_generator(text):
            if sentense_result:
                text_sentiment_confidence[sentense_result["value"]].append(sentense_result["confidence"])

        return self._get_sentiment_with_max_confidence(text_sentiment_confidence)
