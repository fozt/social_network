import json
import os
import random
import re
import string
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from subprocess import check_output

import requests
from bs4 import BeautifulSoup

from app.core.config import settings
from app.schemas.telegram import BotDownload, ChannelDownload, StickerDownload


def assure_folder_exists(folder, root):
    full_path = os.path.join(root, folder)
    if os.path.isdir(full_path):
        pass
    else:
        os.mkdir(full_path)
    return full_path


def random_filename(length, ext):
    return "".join(
        [random.choice(string.ascii_lowercase) for _ in range(length)]
    ) + ".{}".format(ext)


class StickerDownloader:
    def __init__(self, token, session=None, multithreading=4):
        self.THREADS = multithreading
        self.token = token
        self.cwd = assure_folder_exists("/tmp/downloads", root=os.getcwd())
        if session is None:
            self.session = requests.Session()
        else:
            self.session = session
        self.api = "https://api.telegram.org/bot{}/".format(self.token)
        verify = self._api_request("getMe", {})
        if verify["ok"]:
            pass
        else:
            print("Invalid token.")
            exit()

    def _api_request(self, fstring, params):
        try:
            param_string = "?" + urllib.parse.urlencode(params)
            res = self.session.get("{}{}{}".format(self.api, fstring, param_string))
            if res.status_code != 200:
                raise Exception
            res = json.loads(res.content.decode("utf-8"))
            if not res["ok"]:
                raise Exception(res["description"])
            return res

        except Exception as e:
            print('API method {} failed. Error: "{}"'.format(fstring, e))
            return None

    def get_file(self, file_id):
        info = self._api_request("getFile", {"file_id": file_id})
        f = dict(
            name=info["result"]["file_path"].split("/")[-1],
            link="https://api.telegram.org/file/bot{}/{}".format(
                self.token, info["result"]["file_path"]
            ),
        )

        return f

    def get_sticker_set(self, name) -> StickerDownload:
        """
        Get a list of File objects.
        :param name:
        :return:
        """
        params = {"name": name}
        res = self._api_request("getStickerSet", params)
        if res is None:
            raise ValueError("Invalid sticker name")
        stickers = res["result"]["stickers"]
        files = []

        with ThreadPoolExecutor(max_workers=self.THREADS) as executor:
            futures = [
                executor.submit(self.get_file, i["thumb"]["file_id"]) for i in stickers
            ]
            for i in as_completed(futures):
                files.append(i.result())
        # print({
        #     'name': res['result']['name'].lower(),
        #     'title': res['result']['title'],
        #     "files:": [file['link'] for file in files]})
        sticker_set = StickerDownload.parse_obj(
            {
                "name": res["result"]["name"].lower(),
                "title": res["result"]["title"],
                "files": [file["link"] for file in files],
            }
        )
        return sticker_set

    def download_file(self, name, link, path):
        file_path = os.path.join(path, name)
        with open(file_path, "wb") as f:
            res = self.session.get(link)
            f.write(res.content)

        return file_path

    def download_sticker_set(self, sticker_set):
        swd = assure_folder_exists(sticker_set["name"], root=self.cwd)
        download_path = assure_folder_exists("webp", root=swd)
        downloads = []

        print(
            'Starting download of "{}" into {}'.format(
                sticker_set["name"], download_path
            )
        )
        start = time.time()
        with ThreadPoolExecutor(max_workers=self.THREADS) as executor:
            futures = [
                executor.submit(self.download_file, f.name, f.link, download_path)
                for f in sticker_set["files"]
            ]
            for i in as_completed(futures):
                downloads.append(i.result())

        end = time.time()
        print(
            "Time taken to download {} stickers - {:.3f}s".format(
                len(downloads), end - start
            )
        )
        print()

        return downloads

    @staticmethod
    def convert_file(_input, _output):
        command = 'dwebp -quiet "{}" -o "{}"'.format(_input, _output)
        check_output(command, shell=True)
        return _output

    def convert_to_pngs(self, name):
        swd = assure_folder_exists(name, root=self.cwd)
        webp_folder = assure_folder_exists("webp", root=swd)
        png_folder = assure_folder_exists("png", root=swd)

        webp_files = [os.path.join(webp_folder, i) for i in os.listdir(webp_folder)]
        png_files = []

        print('Converting stickers to pngs "{}"..'.format(name))
        start = time.time()
        with ThreadPoolExecutor(max_workers=self.THREADS) as executor:
            futures = [
                executor.submit(
                    self.convert_file,
                    _input,
                    os.path.join(png_folder, random_filename(6, "png")),
                )
                for _input in webp_files
            ]
            for i in as_completed(futures):
                png_files.append(i.result())

        end = time.time()
        print(
            "Time taken to convert {} stickers - {:.3f}s".format(
                len(png_files), end - start
            )
        )
        print()


class TgDownloader(StickerDownloader):
    def __init__(self, token):
        super().__init__(token)
        self.tg_url = "https://t.me/{}"

    # def get_count_subscribers(self, name) -> int:
    #     params = {"chat_id": f"@{name}"}
    #     res = self._api_request("getChatMemberCount", params)
    #     return res["result"]

    # def get_channel_base_info(self, name) -> BaseDownloadContent:
    #     params = {"chat_id": f"@{name}"}
    #     try:
    #         data = self._api_request("getChat", params)["result"]
    #         res = {
    #             "description": data.get("description"),
    #             "title": data["title"]
    #         }
    #         if "photo" in data:
    #             res["imageUrl"] = self.get_file(data["photo"]["small_file_id"])["link"]
    #     except (ValueError, TypeError):
    #         raise ValueError("Invalid content url")
    #
    #     return BaseDownloadContent.parse_obj(res)

    def download_sticker_info(self, name) -> StickerDownload:
        obj = self.get_sticker_set(name)

        return obj

    @staticmethod
    def _get_count_subscribers(html):
        try:
            count_subscribers = int(
                re.sub(
                    r"\s",
                    "",
                    re.search(
                        r"[\d\s]+",
                        html.body.find("div", {"class": "tgme_page_extra"}).text,
                    ).group(),
                )
            )
        except Exception as exc:
            raise ValueError(str(exc))
        return count_subscribers

    def _get_html(self, name):
        return BeautifulSoup(requests.get(self.tg_url.format(name)).text, "lxml")

    @staticmethod
    def _get_base_info(html):
        res = {
            "description": html.head.find(property="og:description")["content"],
            "title": html.head.find(property="og:title")["content"],
            "imageUrl": html.head.find(property="og:image")["content"],
            "url": html.head.find("meta", {"name": "twitter:app:url:googleplay"})[
                "content"
            ],
        }

        return res

    def download_bot_info(self, name) -> BotDownload:
        html = self._get_html(name)
        obj = self._get_base_info(html)
        return BotDownload.parse_obj(obj)

    def download_channel_info(self, name) -> ChannelDownload:
        html = self._get_html(name)
        obj = self._get_base_info(html)
        count_subscribers = self._get_count_subscribers(html)
        return ChannelDownload(**obj, countSubscribers=count_subscribers)


tg_downloader = TgDownloader(token=settings.TG_TOKEN)
