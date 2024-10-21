import certifi
import parse
import requests
import datetime
import json
import telegram
from bs4 import BeautifulSoup
from dateutil.parser import parse as date_parse
from telegram.helpers import escape_markdown
from azure_blob import AzureBlob


class KNUNoticeBot:
    ACADEMY = "academy"
    AI = "ai"
    COMPUTER = "computer"
    NOTICE = "notice"
    SEMINAR = "seminar"
    SWEDU = "swedu"

    verify = certifi.where()
    headers = {"User-Agent": "Mozilla/5.0"}

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

        self.bot = telegram.Bot(token=self.bot_token)

    def parse_table(self, url: str):
        request = requests.get(url, verify=self.verify, headers=self.headers)
        soup = BeautifulSoup(request.text, "html.parser")
        return soup.find("tbody")

    def fetch_notice_posts(self) -> list:
        table = self.parse_table(
            "https://www.knu.ac.kr/wbbs/wbbs/bbs/btin/list.action?bbs_cde=1&menu_idx=67"
        )
        posts = []
        rows = table.find_all("tr")
        if rows:
            for row in rows:
                if row.find("td", "num notice") is None:
                    link = parse.parse(
                        "doRead('{}', '000000', '1', 'row');return false;",
                        row.find("a")["onclick"],
                    )
                    number = int(row.find("td", "num").text.strip())
                    title = row.find("a").text.strip()
                    writer = row.find("td", "writer").text.strip()
                    date = date_parse(row.find("td", "date").text.strip())
                    url = f"https://www.knu.ac.kr/wbbs/wbbs/bbs/btin/viewBtin.action?btin.bbs_cde=1&btin.doc_no={link[0]}&btin.appl_no=000000&btin.page=1&btin.search_type=search_subject&btin.search_text=&popupDeco=&btin.note_div=row&menu_idx=67"

                    posts.append(
                        {
                            "number": number,
                            "title": title,
                            "writer": writer,
                            "date": date,
                            "url": url,
                        }
                    )
        posts.reverse()
        return posts

    def fetch_academy_posts(self) -> list:
        table = self.parse_table(
            "https://www.knu.ac.kr/wbbs/wbbs/bbs/btin/stdList.action?menu_idx=42"
        )
        posts = []
        rows = table.find_all("tr")
        if rows:
            for row in rows:
                if row.find("td", "num notice") is None:
                    link = parse.parse(
                        "javascript:doRead('stu_812', 'row', '{}');",
                        row.find("a")["href"],
                    )

                    number = int(row.find("td", "num").text.strip())
                    title = row.find("a").text.strip()
                    writer = row.find("td", "writer").text.strip()
                    date = date_parse(row.find("td", "date").text.strip())
                    url = f"https://www.knu.ac.kr/wbbs/wbbs/bbs/btin/stdViewBtin.action?search_type=&search_text=&popupDeco=&note_div=row&bltn_no={link[0]}&menu_idx=42&bbs_cde=stu_812"

                    posts.append(
                        {
                            "number": number,
                            "title": title,
                            "writer": writer,
                            "date": date,
                            "url": url,
                        }
                    )
        posts.reverse()
        return posts

    def fetch_computer_posts(self) -> list:
        table = self.parse_table(
            "https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1"
        )
        posts = []
        rows = table.find_all("tr")
        if rows:
            for row in rows:
                if row.find("strong", "notice_icon") is None:
                    number = int(row.find("td", "td_num2").text.strip())
                    title = row.find("div", "bo_tit").find("a").text.strip()
                    writer = row.find("span", "sv_member").text.strip()
                    date = date_parse(
                        row.find("td", "td_datetime hidden-xs").text.strip()
                    )
                    url = row.find("div", "bo_tit").find("a")["href"].strip()

                    posts.append(
                        {
                            "number": number,
                            "title": title,
                            "writer": writer,
                            "date": date,
                            "url": url,
                        }
                    )
        posts.reverse()
        return posts

    def fetch_swedu_posts(self) -> list:
        table = self.parse_table("https://swedu.knu.ac.kr/05_sub/01_sub.html")
        posts = []
        rows = table.find_all("tr")
        if rows:
            for row in rows:
                if row.find("span").text != "공지":
                    number = int(row.find("span").text.strip())
                    title = row.find("a").text.strip()
                    writer = row.find_all("td")[4].text.strip()
                    date = date_parse(row.find_all("td")[5].text.strip())
                    url = f'https://swedu.knu.ac.kr/05_sub/01_sub.html{row.find("a")["href"].strip()}'
                    posts.append(
                        {
                            "number": number,
                            "title": title,
                            "writer": writer,
                            "date": date,
                            "url": url,
                        }
                    )
        posts.reverse()
        return posts

    def fetch_ai_posts(self) -> list:
        table = self.parse_table(
            "https://home.knu.ac.kr/HOME/aic/sub.htm?nav_code=aic1635293208"
        )
        posts = []
        rows = table.find_all("tr")
        if rows:
            for row in rows:
                if row.find("td", "num"):
                    number = int(row.find("td", "num").text.strip())
                    title = row.find("td", "subject").text.strip()
                    writer = row.find("td", "writer").text.strip()
                    date = date_parse(row.find("td", "date").text.strip())
                    url = f'https://home.knu.ac.kr{row.find("a")["href"].strip()}'

                    posts.append(
                        {
                            "number": number,
                            "title": title,
                            "writer": writer,
                            "date": date,
                            "url": url,
                        }
                    )
        posts.reverse()
        return posts

    def fetch_seminar_posts(self) -> list:
        table = self.parse_table(
            "https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_4"
        )
        posts = []
        rows = table.find_all("tr")
        if rows:
            for row in rows:
                if row.find("td", "td_num2").text.strip().isdigit():
                    number = int(row.find("td", "td_num2").text.strip())
                    title = row.find("div", "bo_tit").find("a").text.strip()
                    writer = row.find("span", "sv_member").text.strip()
                    date = date_parse(
                        row.find("td", "td_datetime hidden-xs").text.strip()
                    )
                    url = row.find("div", "bo_tit").find("a")["href"].strip()

                    posts.append(
                        {
                            "number": number,
                            "title": title,
                            "writer": writer,
                            "date": date,
                            "url": url,
                        }
                    )
        posts.reverse()
        return posts

    def convert_posts_to_json(self, posts: list) -> str:
        def datetime_to_string(obj):
            if isinstance(obj, (datetime.time, datetime.datetime)):
                return obj.isoformat()

        return json.dumps(posts, default=datetime_to_string, indent=2)

    def date_to_string(self, date: datetime.datetime) -> str:
        date_format = "%Y년 %m월 %d일"
        return date.strftime(date_format)

    async def send_posts(
        self, notification_title: str, posts: list, latest_number: int
    ):
        for post in posts:
            if post["number"] <= latest_number:
                continue

            number = escape_markdown(str(post["number"]), 2)
            title = escape_markdown(post["title"], 2)
            writer = escape_markdown(post["writer"], 2)
            date = escape_markdown(self.date_to_string(post["date"]), 2)
            url = escape_markdown(post["url"], 2)

            text = f"*{notification_title}*\n\n번호: {number}\n제목: {title}\n작성자: {writer}\n등록일: {date}\n\n[바로가기]({url})\n"
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode="MarkdownV2",
                disable_web_page_preview=True,
            )

    async def send_error_message(self, notification_title: str, exception: Exception):
        text = f"*{notification_title}*\n\n공지사항을 가져오는 중 문제가 발생하였습니다\.{escape_markdown(str(exception), 2)}"
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode="MarkdownV2",
            disable_web_page_preview=True,
        )

    async def send_and_save_posts(
        self, notice_type: str, notice_numbers: dict, azure_blob: AzureBlob
    ) -> None:
        notification_title = ""
        posts = []

        try:
            if notice_type == self.ACADEMY:
                notification_title = "학사 공지사항"
                posts = self.fetch_academy_posts()
            elif notice_type == self.AI:
                notification_title = "인공지능 혁신융합대학사업단 공지사항"
                posts = self.fetch_ai_posts()
            elif notice_type == self.COMPUTER:
                notification_title = "컴퓨터학부 공지사항"
                posts = self.fetch_computer_posts()
            elif notice_type == self.NOTICE:
                notification_title = "학교 공지사항"
                posts = self.fetch_notice_posts()
            elif notice_type == self.SEMINAR:
                notification_title = "컴퓨터학부 세미나"
                posts = self.fetch_seminar_posts()
            elif notice_type == self.SWEDU:
                notification_title = "소프트웨어교육원 공지사항"
                posts = self.fetch_swedu_posts()

            await self.send_posts(
                notification_title, posts, notice_numbers[notice_type]
            )
        except Exception as exception:
            await self.send_error_message(notification_title, exception)

        try:
            posts_json = self.convert_posts_to_json(posts)
            azure_blob.upload_blob(f"{notice_type}.json", posts_json)
        except Exception as exception:
            await self.send_error_message(notification_title, exception)

        notice_numbers[notice_type] = posts[-1]["number"]
