from hashlib import sha1
import time
import aiohttp
import asyncio
import aiofiles
from pyquery import PyQuery as pq
import js2py
import js2py.pyjs
import random
import os
import json
from .templates import Templates
import typing
import pathlib
import base64


class Studio:
    YT_STUDIO_URL = "https://studio.youtube.com"
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
    #utylee
    #USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0'
    #<<<
    TRANSFERRED_BYTES = 0
    CHUNK_SIZE = 64*1024

    def __init__(self, cookies: dict = {'SESSION_TOKEN': '', 'VISITOR_INFO1_LIVE': '', 'PREF': '', 'LOGIN_INFO': '', 'SID': '', '__Secure-3PSID': '.', 'HSID': '',
                 'SSID': '', 'APISID': '', 'SAPISID': '', '__Secure-3PAPISID': '', 'YSC': '', 'SIDCC': ''}):
        self.SAPISIDHASH = self.generateSAPISIDHASH(cookies['SAPISID'])
        #utylee
        self.SAPISIDHASH = '1696614203_08d6778d0f71d13d69b7dfaf5078d8a05ecdd2bf'
        # <<<
        self.cookies = cookies
        self.Cookie = " ".join(
            [f"{c}={cookies[c]};" if not c in ["SESSION_TOKEN", "BOTGUARD_RESPONSE"] else "" for c in cookies.keys()])
        # utylee
        self.Cookie = 'SESSION_TOKEN=AZHt5fVoyl9Nwt_LIuVHLkflhUSEyfATBRBnvyygLoMEayZ8yz_-xrneg3ZIqJUpGmc9Umqip-jtTgNprkxL3dnyD4aqLYhVErTtSBJ8U6_hz2zH_Kz5WEhn0m6pWfW_HssZ97R3w4pEa4RnPQt17gtwOSkuB6xw-w==;SID=bwiKQMZfuxg7qreyQqrz1gq2E9xI-JO3qFdagM8gybBPLo0_RzHD1VaKtnMyvlADGLeZxA.; __Secure-1PSIDTS=sidts-CjEB3e41hY2Mxb5T4ffJ9Sh-xKKuUYYV_lX4VIzHN_MtK6t6g9fSCyg5R9ZEzpjBZkpbEAA; __Secure-3PSIDTS=sidts-CjEB3e41hY2Mxb5T4ffJ9Sh-xKKuUYYV_lX4VIzHN_MtK6t6g9fSCyg5R9ZEzpjBZkpbEAA; __Secure-1PSID=bwiKQMZfuxg7qreyQqrz1gq2E9xI-JO3qFdagM8gybBPLo0_ZbxMp1a9Z3Ql3od5Hi7hHg.; __Secure-3PSID=bwiKQMZfuxg7qreyQqrz1gq2E9xI-JO3qFdagM8gybBPLo0_XYofBQPupBUR1kI6JmAZtA.; HSID=AvRqTmK7fNVPLmkOZ; SSID=AiT7NzqdSkPkgnX6L; APISID=p8f9ZyUEhhWnSFrA/AE-xTaQa4FiTT8zdl; SAPISID=IRlK7NG2h-QJvKUE/AaU6oW8D_Zvs8CIzg; __Secure-1PAPISID=IRlK7NG2h-QJvKUE/AaU6oW8D_Zvs8CIzg; __Secure-3PAPISID=IRlK7NG2h-QJvKUE/AaU6oW8D_Zvs8CIzg; YSC=AfLUyGAH_Rk; VISITOR_INFO1_LIVE=S9vhK1gLDOA; VISITOR_PRIVACY_METADATA=CgJLUhICGgA%3D; LOGIN_INFO=AFmmF2swRgIhAPQPWVkIyV_SzRTFl8N1yUE1lOk6KPkntT3EXTFHTf2aAiEA3XSg0fEId_FEVBD39osX7J3xsIgmd_DNCHJq5uKOMRI:QUQ3MjNmemxJcHhtMC1MaG1xQXhYTktBQVNfcS1VRjVMenowaksyTFc1V2YyN3ZiSVZ3cHdvUXhKcHNyRlYzZUFETHhEc1RNZmhGQmpUN2lmcHlUVWdNRG5UYTJXanUtZ096SU4wTE9EelR5LUZPLUdYczlvRjVVYnBQVURFWGYwdDJIaW5mYWg1VkRsaHNhWlZHWTUzcTRna2JYbjhKcmNn; SIDCC=ACA-OxNCN0GYvdfy3LiDS_cH836RxVmjoqGTCldlB9B_bgMZL-TGmESVD6twRuhpxWDVxq79yA; __Secure-1PSIDCC=ACA-OxOp0RQ821KCHnOKpEfr2_QItkHCSwbmJqjQFnEm_8rXfhvYEfREIchAY2bZqnrS-Bch; __Secure-3PSIDCC=ACA-OxMGF0hAWmJJ334pSQ1JFuRtbFn5PKjQLvEWYIoJwMEwIQlfxjEW9LX84iP8_JmwBOQDPQ'
        
        #self.Cookie = ' __Secure-1PSIDTS=sidts-CjEB3e41hUqHXsLCEW8MojEnzgMH5PsnGx2Z6cEQt3Yps4t7yTUSTalkNmhL6jvOAoF7EAA; __Secure-3PSIDTS=sidts-CjEB3e41hUqHXsLCEW8MojEnzgMH5PsnGx2Z6cEQt3Yps4t7yTUSTalkNmhL6jvOAoF7EAA; HSID=AYsPqIwfM4y6X5OSd; SSID=AF-uBwGGxVaNTVXpK; APISID=ilo39lLM4LjHn6f2/A7-4EQUMzXHEYv9ZT; SAPISID=_l0ZLupo82lDRlFa/AcvlTdLrc_wz4u71w; __Secure-1PAPISID=_l0ZLupo82lDRlFa/AcvlTdLrc_wz4u71w; __Secure-3PAPISID=_l0ZLupo82lDRlFa/AcvlTdLrc_wz4u71w; SID=bwiKQOGCqXerLlhtmwgGrJirLwsQ3ucuqSawRSXSaSfv95V5hvYfFkmV-w0SKBVkKOitKQ.; __Secure-1PSID=bwiKQOGCqXerLlhtmwgGrJirLwsQ3ucuqSawRSXSaSfv95V5DNV4i5bskvUfg4u6QUzDwQ.; __Secure-3PSID=bwiKQOGCqXerLlhtmwgGrJirLwsQ3ucuqSawRSXSaSfv95V59b6Tfvdc7-bS_zsNibyZrw.; YSC=_x21LqBM7Uo; VISITOR_INFO1_LIVE=wMjtQpZ97oI; VISITOR_PRIVACY_METADATA=CgJLUhICGgA%3D; LOGIN_INFO=AFmmF2swRQIhAK5GO0SE1qGGdQ6WJEPclj-0xPnoOwlrcZmnTPq8DHWGAiAKvL0F3wPlQ4aLHuNwfyEan0ef0_2KCqEqBANmhwyb9w:QUQ3MjNmeFFHS0E1TlB0bUJPZFdIMVZ6VHZpV1V3cHVUWGdHUXVpUGlUQnlHUXFLUGhCVGlQRVhZVi1LYU5SMXF2YnBaQ2NrM1d3OFBZbTdlNG5LckZYdUlMOC1hZzFYLTlLc2ZsTTd1eDZGd3RyRE5PQ280M1liSHljRmxKdVZ3QXVRSGdZVktJVmxuMnlzSXV0ZEdiUjRmOFNna2tfUUN3; SIDCC=ACA-OxPsF1h7YlZ15-ZUs3KrhJkPh8ykAP7a5JQC3IydpBDgC_kYQdCZuwT-6haiKOpIAOI5aA; __Secure-1PSIDCC=ACA-OxOUOECYUxK4iaA5iSQ2cKX31i7M7u6719FdsoOmUwiI2aiy3Zkp67Xub--t6tC4wpRJWQ; __Secure-3PSIDCC=ACA-OxMs8QJ_XpoD1oAdXjpPw1QKDdpTTlrtwYwM-R4vYPyVzwqA3MTZ9HQW8K6KsiC5WbBQDA; SESSION_TOKEN=AZHt5fXwqt10l-SLDNcZA3tC5OYamxdpcOhyEdS5RT2lBCO9911c-FD5BZpVh5OVxaBhbdRipIBWoVPOHf6YIyqvqh95YZS5CTMJASiUGp_P0G3TEJQUk9QlvihiOE83Sr0fTXg9lBTN9K7sKELNFBm6Nl1jIr8P2Ec='

        # <<<
        self.HEADERS = {
            'Authorization': f'SAPISIDHASH {self.SAPISIDHASH}',
            'Content-Type': 'application/json',
            'Cookie': self.Cookie,
            'X-Origin': self.YT_STUDIO_URL,
            'User-Agent': self.USER_AGENT
        }
        # utylee
        # self.HEADERS = {
        #     'Authorization': f'SAPISIDHASH {self.SAPISIDHASH}',
        #     'Accept-Language' : 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
        #     'Content-Type': 'application/json',
        #     'Cookie': self.Cookie,
        #     'X-Origin': self.YT_STUDIO_URL,
        #     'User-Agent': self.USER_AGENT
        # }

        # <<<
        self.session = aiohttp.ClientSession(headers=self.HEADERS)
        self.loop = asyncio.get_event_loop()
        self.config = {}
        self.js = js2py.EvalJs()
        self.js.execute("var window = {ytcfg: {}};")

    def __del__(self):
        self.loop.create_task(self.session.close())

    def generateSAPISIDHASH(self, SAPISID) -> str:
        hash = f"{round(time.time())} {SAPISID} {self.YT_STUDIO_URL}"
        sifrelenmis = sha1(hash.encode('utf-8')).hexdigest()
        return f"{round(time.time())}_{sifrelenmis}"

    async def getMainPage(self) -> str:
        page = await self.session.get(self.YT_STUDIO_URL)
        return await page.text("utf-8")

    async def login(self) -> bool:
        """
        Login to your youtube account
        """
        page = await self.getMainPage()
        # utylee
        #print(page)
        # >>
        _ = pq(page)
        script = _("script")
        if len(script) < 1:
            raise Exception("Didn't find script. Can you check your cookies?")
        # utylee
        # print(f'len:{len(script)}')
        print(f'{self.cookies}')
        import re
        # for iii in range(len(script)):
        #     ttt = script[iii].text
        #     print(f'script {iii}: {ttt}')
        # print(page)
        with open('page.html', 'w+') as ff:
            ff.write(page)
        # >>
        script = script[0].text
        # utylee
        # print(script)
        print(self.HEADERS)
        # >>
        self.js.execute(
            f"{script} window.ytcfg = ytcfg;")

        INNERTUBE_API_KEY = self.js.window.ytcfg.data_.INNERTUBE_API_KEY
        CHANNEL_ID = self.js.window.ytcfg.data_.CHANNEL_ID
        DELEGATED_SESSION_ID = self.js.window.ytcfg.data_.DELEGATED_SESSION_ID

        if INNERTUBE_API_KEY == None or CHANNEL_ID == None:
            raise Exception(
                "Didn't find INNERTUBE_API_KEY or CHANNEL_ID. Can you check your cookies?")
        self.config = {'INNERTUBE_API_KEY': INNERTUBE_API_KEY,
                       'CHANNEL_ID': CHANNEL_ID, 'data_': self.js.window.ytcfg.data_}
        self.templates = Templates({
            'channelId': CHANNEL_ID,
            'sessionToken': self.cookies['SESSION_TOKEN'],
            'botguardResponse': self.cookies['BOTGUARD_RESPONSE'] if 'BOTGUARD_RESPONSE' in self.cookies else '',
            'delegatedSessionId': DELEGATED_SESSION_ID
        })

        return True

    def generateHash(self) -> str:
        harfler = list(
            '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
        keys = ['' for i in range(0, 36)]
        b = 0
        c = ""
        e = 0

        while e < 36:
            if 8 == e or 13 == e or 18 == e or 23 == e:
                keys[e] = "-"
            else:
                if 14 == e:
                    keys[e] = "4"
                elif 2 >= b:
                    b = round(33554432 + 16777216 * random.uniform(0, 0.9))
                c = b & 15
                b = b >> 4
                keys[e] = harfler[c & 3 | 8 if 19 == e else c]
            e += 1

        return "".join(keys)

    async def fileSender(self, file_name):
        async with aiofiles.open(file_name, 'rb') as f:
            chunk = await f.read(self.CHUNK_SIZE)
            while chunk:
                if self.progress != None:
                    self.TRANSFERRED_BYTES += len(chunk)
                    self.progress(self.TRANSFERRED_BYTES,
                                  os.path.getsize(file_name))

                self.TRANSFERRED_BYTES += len(chunk)
                yield chunk
                chunk = await f.read(self.CHUNK_SIZE)
                if not chunk:
                    break

    async def uploadFileToYoutube(self, upload_url, file_path):
        self.TRANSFERRED_BYTES = 0

        uploaded = await self.session.post(upload_url,  headers={
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8'",
            "x-goog-upload-command": "upload, finalize",
            "x-goog-upload-file-name": f"file-{round(time.time())}",
            "x-goog-upload-offset": "0",
            "Referer": self.YT_STUDIO_URL,
        }, data=self.fileSender(file_path), timeout=None)
        _ = await uploaded.text("utf-8")
        _ = json.loads(_)
        return _['scottyResourceId']

    async def uploadVideo(self, file_name, title=f"New Video {round(time.time())}", description='This video uploaded by github.com/yusufusta/ytstudio', privacy='PRIVATE', draft=False, progress=None, extra_fields={}):
        """
        Uploads a video to youtube.
        """
        self.progress = progress
        frontEndUID = f"innertube_studio:{self.generateHash()}:0"

        uploadRequest = await self.session.post("https://upload.youtube.com/upload/studio",
                                                headers={
                                                    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8'",
                                                    "x-goog-upload-command": "start",
                                                    "x-goog-upload-file-name": f"file-{round(time.time())}",
                                                    "x-goog-upload-protocol": "resumable",
                                                    "Referer": self.YT_STUDIO_URL,
                                                },
                                                json={'frontendUploadId': frontEndUID})

        uploadUrl = uploadRequest.headers.get("x-goog-upload-url")
        scottyResourceId = await self.uploadFileToYoutube(uploadUrl, file_name)

        _data = self.templates.UPLOAD_VIDEO
        _data["resourceId"]["scottyResourceId"]["id"] = scottyResourceId
        _data["frontendUploadId"] = frontEndUID
        _data["initialMetadata"] = {
            "title": {
                "newTitle": title
            },
            "description": {
                "newDescription": description,
                "shouldSegment": True
            },
            "privacy": {
                "newPrivacy": privacy
            },
            "draftState": {
                "isDraft": draft
            },
        }
        _data["initialMetadata"].update(extra_fields)

        upload = await self.session.post(
            f"https://studio.youtube.com/youtubei/v1/upload/createvideo?alt=json&key={self.config['INNERTUBE_API_KEY']}",
            json=_data
        )

        return await upload.json()

    async def deleteVideo(self, video_id):
        """
        Delete video from your channel
        """
        self.templates.setVideoId(video_id)
        delete = await self.session.post(
            f"https://studio.youtube.com/youtubei/v1/video/delete?alt=json&key={self.config['INNERTUBE_API_KEY']}",
            json=self.templates.DELETE_VIDEO
        )
        return await delete.json()

    async def listVideos(self):
        """
        Returns a list of videos in your channel
        """
        list = await self.session.post(
            f"https://studio.youtube.com/youtubei/v1/creator/list_creator_videos?alt=json&key={self.config['INNERTUBE_API_KEY']}",
            json=self.templates.LIST_VIDEOS
        )
        return await list.json()

    async def getVideo(self, video_id):
        """
        Get video data.
        """
        self.templates.setVideoId(video_id)
        video = await self.session.post(
            f"https://studio.youtube.com/youtubei/v1/creator/get_creator_videos?alt=json&key={self.config['INNERTUBE_API_KEY']}",
            json=self.templates.GET_VIDEO
        )
        return await video.json()

    async def createPlaylist(self, title, privacy="PUBLIC") -> dict:
        """
        Create a new playlist.
        """
        _data = self.templates.CREATE_PLAYLIST
        _data["title"] = title
        _data["privacyStatus"] = privacy

        create = await self.session.post(
            f"https://studio.youtube.com/youtubei/v1/playlist/create?alt=json&key={self.config['INNERTUBE_API_KEY']}",
            json=_data
        )
        return await create.json()

    async def editVideo(self, video_id, title: str = "", description: str = "", privacy: str = "", thumb: typing.Union[str, pathlib.Path, os.PathLike] = "", tags: typing.List[str] = [], category: int = -1, monetization: bool = True, playlist: typing.List[str] = [], removeFromPlaylist: typing.List[str] = []):
        """
        Edit video metadata.
        """
        self.templates.setVideoId(video_id)
        _data = self.templates.METADATA_UPDATE
        if title != "":
            _title = self.templates.METADATA_UPDATE_TITLE
            _title["title"]["newTitle"] = title
            _data.update(_title)

        if description != "":
            _description = self.templates.METADATA_UPDATE_DESCRIPTION
            _description["description"]["newDescription"] = description
            _data.update(_description)

        if privacy != "":
            _privacy = self.templates.METADATA_UPDATE_PRIVACY
            _privacy["privacy"]["newPrivacy"] = privacy
            _data.update(_privacy)

        if thumb != "":
            _thumb = self.templates.METADATA_UPDATE_THUMB
            image = open(thumb, 'rb')
            image_64_encode = base64.b64encode(image.read()).decode('utf-8')

            _thumb["videoStill"]["image"][
                "dataUri"] = f"data:image/png;base64,{image_64_encode}"
            _data.update(_thumb)

        if len(tags) > 0:
            _tags = self.templates.METADATA_UPDATE_TAGS
            _tags["tags"]["newTags"] = tags
            _data.update(_tags)

        if category != -1:
            _category = self.templates.METADATA_UPDATE_CATEGORY
            _category["category"]["newCategoryId"] = category
            _data.update(_category)

        if len(playlist) > 0:
            _playlist = self.templates.METADATA_UPDATE_PLAYLIST
            _playlist["addToPlaylist"]["addToPlaylistIds"] = playlist
            if len(removeFromPlaylist) > 0:
                _playlist["addToPlaylist"]["deleteFromPlaylistIds"] = removeFromPlaylist
            _data.update(_playlist)

        if len(removeFromPlaylist) > 0:
            _playlist = self.templates.METADATA_UPDATE_PLAYLIST
            _playlist["addToPlaylist"]["deleteFromPlaylistIds"] = removeFromPlaylist
            _data.update(_playlist)

        _monetization = self.templates.METADATA_UPDATE_MONETIZATION
        _monetization["monetizationSettings"]["newMonetization"] = monetization
        _data.update(_monetization)

        update = await self.session.post(
            f"https://studio.youtube.com/youtubei/v1/video_manager/metadata_update?alt=json&key={self.config['INNERTUBE_API_KEY']}",
            json=_data
        )
        return await update.json()
