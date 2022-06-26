import requests
from typing import Union,Optional
import json
from urllib import parse

# Xes作品信息
class XesWork():
    def __init__(self,workurl:str,cookie:Optional[str] = None) -> None:
        self.headers = self.getHeaders(cookie)
        querys = self.parseWorkURL(workurl)
        self.workid = querys['pid'][0]
        self.worktype = querys['langType'][0]
        self.topicid = self.getTopicID()
        datas = self.getWorkData()
        self.islike = datas['islike']
        self.isunlike = datas['isunlike']
        self.isfavorite = datas['isfavorite']
        self.primary = datas['primary']
        self.smilar = self.getWorkSmilar()
        self.profile = self.getWorkProfile()
        self.overview = self.getOverview()
        self.original = self.getOriginal()

    def getHeaders(self,cookie:str):
        if cookie:
            headers = {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33',
                'Cookie':cookie
                }
        else:
            headers = {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33',
                }
        return headers

    def getTopicID(self) -> str:
        iddict = {
            "python":"CP_{}",
            "cpp":"CC_{}",
            "scratch":"CS_{}"
        }
        topicid = iddict[self.worktype].format(self.workid)
        return topicid

    def parseWorkURL(self,url:str) -> dict:
        url = parse.urlparse(url)
        parad = parse.parse_qs(url.query)
        return parad

    def extractData(self,urldict:dict,urlkey:int,formattext:object) -> dict:
        url = urldict[self.worktype][urlkey].format(formattext)
        data = requests.get(url,headers=self.headers).text
        targetdata = json.loads(data)
        return targetdata

    def getWorkData(self) -> dict:
        urldict = {
            "python":[
                'https://code.xueersi.com/api/compilers/v2/{0}?id={0}',
                'https://code.xueersi.com/api/compilers/{0}/is_like?id={0}&lang=code&form=python',
                'https://code.xueersi.com/api/compilers/{0}/is_unlike?id={0}&lang=code&form=python',
                'https://code.xueersi.com/api/space/is_favorite?topic_id={0}'
                ],
            "cpp":[
                'https://code.xueersi.com/api/compilers/v2/{0}?id={0}',
                'https://code.xueersi.com/api/compilers/{0}/is_like?id={0}&lang=code&form=cpp',
                'https://code.xueersi.com/api/compilers/{0}/is_unlike?id={0}&lang=code&form=python',
                'https://code.xueersi.com/api/space/is_favorite?topic_id={0}'
                ],
            "scratch":[
                'https://code.xueersi.com/api/projects/v2/{0}?id={0}',
                'https://code.xueersi.com/api/projects/{0}/is_like?id={0}&lang=scratch',
                'https://code.xueersi.com/api/projects/{0}/is_unlike?id={0}&lang=scratch',
                'https://code.xueersi.com/api/space/is_favorite?topic_id={0}'
                ]
        }
        primarydata = self.extractData(urldict,0,self.workid)
        islike = self.extractData(urldict,1,self.workid)
        isunlike = self.extractData(urldict,2,self.workid)
        isfavorite = self.extractData(urldict,3,self.topicid)
        targetdict = {"primary":primarydata,"islike":islike,"isunlike":isunlike,"isfavorite":isfavorite}
        return targetdict
    
    def getWorkSmilar(self) -> dict:
        workname = self.primary['data']['name']
        userid = self.primary['data']['user_id']
        url = f"https://code.xueersi.com/api/pai/projects/similar?topic_id={self.topicid}&name={parse.quote(workname)}&lang={self.worktype}&user_id={userid}"
        response = requests.get(url,headers=self.headers).text
        return json.loads(response)

    def getWorkProfile(self) -> dict:
        userid = self.primary['data']['user_id']
        url = f"https://code.xueersi.com/api/space/profile?user_id={userid}"
        response = requests.get(url,headers=self.headers).text
        return json.loads(response)

    def getOverview(self) -> dict:
        url = f"https://code.xueersi.com/api/comments/overview?appid=1001108&topic_id={self.topicid}"
        response = requests.get(url,headers=self.headers).text
        return json.loads(response)

    def getOriginal(self) -> dict:
        originalid = self.primary['data']['original_id']
        urldict = {
            "python":'https://code.xueersi.com/api/python/get_original_project?lang=code&form=python&original_id={}',
            "cpp":'https://code.xueersi.com/api/compilers/get_original_project?lang=code&form=cpp&original_id={}',
            "scratch":'https://code.xueersi.com/api/projects/get_original_project?lang=scratch&form=&original_id={}'
        }
        url = urldict[self.worktype].format(originalid)
        response = requests.get(url,headers=self.headers).text
        return json.loads(response)

    def getComments(self,order:str,page:int) -> dict:
        url = f'https://code.xueersi.com/api/comments?appid=1001108&topic_id={self.topicid}&parent_id=0&order_type={order}&page={page}&per_page=15'
        response = requests.get(url,headers=self.headers).text
        return json.loads(response)

    def getAssets(self) -> dict:
        url = self.primary['data']['assets']['assets_url']
        response = requests.get(url,headers=self.headers).text
        return json.loads(response)


    def getLikes(self) -> int:
        return self.primary['data']['likes']
    def getUnlikes(self) -> int:
        return self.primary['data']['unlikes']
    def getFavorites(self) -> int:
        return self.primary['data']['favorites']
    def getUserid(self) -> int:
        return self.primary['data']['user_id']
    def getUsername(self) -> int:
        return self.primary['data']['username']
    def getCommentsnum(self) -> int:
        return self.primary['data']['comments']
    def getCreatedat(self) -> str:
        return self.primary['data']['created_at']
    def getDeletedat(self) -> str:
        return self.primary['data']['deleted_at']
    def getDescription(self) -> str:
        return self.primary['data']['description']
    def getCover(self) -> str:
        return self.primary['data']['first_frame']
    def getHiddencode(self) -> int:
        return self.primary['data']['hidden_code']
    def getManual(self) -> int:
        return self.primary['data']['manual_weight']
    def getModifiedat(self) -> str:
        return self.primary['data']['modified_at']
    def getWorkname(self) -> str:
        return self.primary['data']['name']
    def getLang(self) -> str:
        return self.primary['data']['lang']
    def getID(self) -> int:
        return self.primary['data']['id']
    def getSource(self) -> str:
        return self.primary['data']['created_source']
    def getOriginalid(self) -> int:
        return self.primary['data']['original_id']
    def getScore(self) -> float:
        return self.primary['data']['popular_score']
    def getIspublic(self) -> int:
        return self.primary['data']['published']
    def getPublishedat(self) -> str:
        return self.primary['data']['published_at']
    def getRemoved(self) -> int:
        return self.primary['data']['removed']
    def getSourceview(self) -> int:
        return self.primary['data']['source_code_views']
    def getTags(self) -> list:
        return self.primary['data']['tags'].split(" ")
    def getTemplate(self) -> int:
        return self.primary['data']['template_project_id']
    def getThumbnail(self) -> str:
        return self.primary['data']['thumbnail']
    def getTopic(self) -> str:
        return self.primary['data']['topic_id']
    def getType(self) -> str:
        return self.primary['data']['type']
    def getUpdatedat(self) -> str:
        return self.primary['data']['updated_at']
    def getAvater(self) -> str:
        return self.primary['data']['user_avater']
    def getVersion(self) -> str:
        return self.primary['data']['version']
    def getViews(self) -> int:
        return self.primary['data']['views']
    def getXml(self) -> str:
        return self.primary['data']['xml']
    def getXmlpath(self) -> str:
        return self.primary['data']['xml_path']
    def isLike(self) -> bool:
        return self.islike
    def isUnlike(self) -> bool:
        return self.isunlike
    def isFavorite(self) -> bool:
        return self.isfavorite
    

# Xes用户信息
class XesUser():
    def __init__(self,userid = Union[int,str],cookie:Optional[str] = None) -> None:
        self.headers = self.getHeaders(cookie)
        self.userid = userid
        datas = self.getUserData()
        self.primary = datas['primary']
        self.index = datas['index']
        self.webcover = datas['webcover']
        contact = self.getUserContact()
        self.favorite = contact['favorite']
        self.follow = contact['follow']
        self.fans = contact['fans']
        self.medal = contact['medal']

    def getHeaders(self,cookie:str):
        if cookie:
            headers = {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33',
                'Cookie':cookie
                }
        else:
            headers = {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33',
                }
        return headers

    def extractData(self,urldict:dict,urlkey:str,formattext:object) -> dict:
        url = urldict[urlkey].format(formattext)
        data = requests.get(url,headers=self.headers).text
        targetdata = json.loads(data)
        return targetdata

    def extractContact(self,urldict:dict,urlkey:str,format1:object,format2:object) -> dict:
        url = urldict[urlkey].format(format1,format2)
        data = requests.get(url,headers=self.headers).text
        targetdata = json.loads(data)
        return targetdata

    def getUserData(self) -> dict:
        urldict = {
            "primary":"https://code.xueersi.com/api/space/profile?user_id={}",
            "index":"https://code.xueersi.com/api/space/index?user_id={}",
            "webcover":"https://code.xueersi.com/api/space/web_cover?user_id={}"
        }
        primary = self.extractData(urldict,"primary",self.userid)
        index = self.extractData(urldict,"index",self.userid)
        webcover = self.extractData(urldict,"webcover",self.userid)
        targetdict = {"primary":primary,"index":index,"webcover":webcover}
        return targetdict

    def getUserContact(self,page:int) -> dict:
        urldict ={
            "favorite":"https://code.xueersi.com/api/space/favorites?user_id={}&page={}&per_page=20",
            "follow":"https://code.xueersi.com/api/space/follows?user_id={}&page={}&per_page=10",
            "fans":"https://code.xueersi.com/api/space/fans?user_id={}&page={}&per_page=10",
            "medal":"https://code.xueersi.com/api/incentive/medals?user_id={}&page={}&per_page=15"
        }
        favorite = self.extractContact(urldict,"favorite",self.userid,page)
        follow = self.extractContact(urldict,"follow",self.userid,page)
        fans = self.extractContact(urldict,"fans",self.userid,page)
        medal = self.extractContact(urldict,"medal",self.userid,page)
        targetdict = {"favorite":favorite,"follow":follow,"fans":fans,"medal":medal}
        return targetdict

    def getUserWork(self,page:int,order:str) -> dict:
        url = f"https://code.xueersi.com/api/space/works?user_id={self.userid}&page={page}&per_page=20&order_type={order}"
        response = requests.get(url,headers=self.headers).text
        data = json.loads(response)
        return data

# Xes自己的信息
class XesOneself():
    def __init__(self) -> None:
        pass

# Xes首页
class XesIndex():
    def __init__(self) -> None:
        pass

# Xes发现
class XesExplore():
    def __init__(self) -> None:
        pass

# Xes的操作、行为
class XesBehavior():
    def __init__(self) -> None:
        pass
