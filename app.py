import re
import hashlib
import collections
import tornado.ioloop
import tornado.web

from tornado.httpclient import AsyncHTTPClient
from bs4 import BeautifulSoup
from analysis_text import AnalysisText
from db import objects, WordsModel, UrlsModel, PUBLIC_KEY, PRIVATE_KEY
from encryption_decryption import encrypt_message, decrypt_message
from settings import SALT


class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        self.render("templates/index.html")

    async def post(self):
        url = self.get_argument('url')
        http_client = AsyncHTTPClient()
        response = await http_client.fetch(url)
        text = await self.get_text_from_response(response.body)

        if text:
            sentiment_analysis = AnalysisText().get_sentiment_for_text(text)
            await self.get_or_update_urls_info(sentiment_analysis, url)
            await self.calculate_words_freq(text)

            return self.write("Words from this url was been added to db")
        else:
            return self.write("Can't find text in this url")

    @staticmethod
    async def get_text_from_response(answ):
        bs_body = BeautifulSoup(answ, "lxml")
        for script in bs_body(["script", "style"]):
            script.extract()
        text = bs_body.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = str('\n'.join(chunk for chunk in chunks if chunk))
        return text

    @staticmethod
    async def get_or_update_urls_info(sentiment_analysis, url):
        try:
            urls_obj = await objects.get(UrlsModel, url=url)
        except UrlsModel.DoesNotExist:
            await objects.create(UrlsModel, url_with_salt=hashlib.sha256(
                (url + SALT).encode('utf-8')).digest(), url=url, sentiment_analysis=sentiment_analysis)
        else:
            urls_obj.sentiment_analysis = sentiment_analysis
            await objects.update(urls_obj)

    @staticmethod
    async def calculate_words_freq(text):
        text = re.sub(r'[^\w\s]', '', text)
        words = collections.Counter(text.split()).most_common(100)
        for w, freq in words:
            w = w.strip()
            enc_word = encrypt_message(w, PUBLIC_KEY)
            try:
                words_obj = await objects.get(
                    WordsModel,
                    enc_text=enc_word
                )
            except WordsModel.DoesNotExist:
                await objects.create(
                    WordsModel,
                    text_with_salt=hashlib.sha256((w + SALT).encode('utf-8')).digest(),
                    enc_text=enc_word,
                    freq=freq
                )
            else:
                words_obj.freq = (freq + words_obj.freq) // 2
                await objects.update(words_obj)


class AdminHandler(tornado.web.RequestHandler):
    async def get(self):
        all_words = await objects.execute(WordsModel.select().order_by(WordsModel.freq.desc()))
        for word in all_words:
            word.enc_text = decrypt_message(word.enc_text, PRIVATE_KEY)
        all_urls = await objects.execute(UrlsModel.select())
        self.render("templates/lists.html", all_words=all_words, all_urls=all_urls)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/admin", AdminHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
