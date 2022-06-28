import requests
from typing import Union,Optional
import json
from urllib import parse
import sys
import websocket

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
    def __init__(self,uid:int,cookie:str) -> None:
        self.id = uid
        self.cookie = cookie
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33',
            'Cookie':cookie
            }

    def getMyWork(self,pulished:str,_type:str,page:int,lang:str) -> dict:
        urldict = {
            "python":'https://code.xueersi.com/api/python/my?published={}&type={}&page={}&per_page=20',
            "cpp":'https://code.xueersi.com/api/compilers/my?published={}&type={}&page={}&per_page=20',
            "scratch":'https://code.xueersi.com/api/projects/my?published={}&type={}&page={}&per_page=20',
        }
        url = urldict[lang].format(pulished,_type,page)
        response = requests.get(url,headers=self.headers).text
        data = json.loads(response)
        return data
    
    def getMyWebCover(self) -> dict:
        """获取自己已发布的可以作为封面的作品
        """
        url = "https://code.xueersi.com/api/space/web_cover/web_projects"
        response = requests.get(url,headers=self.headers).text
        data = json.loads(response)
        return data

    def getMessages(self,category:int,page:int,subtype:Optional[str] = None) -> dict:
        """
        :category:1为评论,2为点赞与收藏,3为反馈与审核(此选项需填subtype参数),4为系统消息,5为关注
        :subtype:feedback为建议反馈,report为举报,audit为审核,all为全部
        """
        if category != 3:
            url = f'https://code.xueersi.com/api/messages?category={category}&page={page}&per_page=10'
        else:
            if subtype:
                if subtype != 'all' and subtype != '':
                    url = f'https://code.xueersi.com/api/messages?category=3&sub_type=&page={page}&per_page=10'
                else:
                    url = f'https://code.xueersi.com/api/messages?category=3&sub_type={subtype}&page={page}&per_page=10'
            else:
                raise ValueError('If you want to retrieve messages, the subtype parameter cannot be null')
        response = requests.get(url,headers=self.headers).text
        data = json.loads(response)
        return data

    def setSignatrue(self,text:str) -> None:
        payloads = {
            "signature":text
        }
        url = "https://code.xueersi.com/api/space/edit_signature"
        response = requests.post(url,headers=self.headers,json = payloads)

    def setRepresentative(self,topic_id:str,state:int) -> None:
        """
        :state:0为取消代表作,1为设为代表作
        """
        payloads = {
            "state":state,
            "topic_id":topic_id
        }
        url = "https://code.xueersi.com/api/space/set_representative_work"
        response = requests.post(url,headers=self.headers,json = payloads)

# Xes首页
class XesIndex:
    def __init__(self,cookie:str) -> None:
        self.Follows = self.follows(cookie)
        self.Index = self.modules(1,cookie)
        self.Classroom = self.modules(1,cookie)
        self.Teacher = self.modules(3,cookie)

    @classmethod
    def getHeaders(self,cookie:str) -> dict:
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

    class follows:
        def __init__(self,cookie:str):
            self.cookie = cookie
            self.headers = XesIndex.getHeaders(self.cookie)
            self.primary = self.getFollows()
        def getFollows(self):
            return json.loads(requests.get('https://code.xueersi.com/api/index/works/follows', headers=self.headers).text)
        def getLikes(self) -> int:
            return [i['likes'] for i in self.primary['data']]
        def getUnlikes(self) -> int:
            return [i['unlikes'] for i in self.primary['data']]
        def getFavorites(self) -> int:
            return [i['favorites'] for i in self.primary['data']]
        def getUserid(self) -> int:
            return [i['user_id'] for i in self.primary['data']]
        def getUsername(self) -> int:
            return [i['username'] for i in self.primary['data']]
        def getCommentsnum(self) -> int:
            return [i['comments'] for i in self.primary['data']]
        def getCreatedat(self) -> str:
            return [i['created_at'] for i in self.primary['data']]
        def getDeletedat(self) -> str:
            return [i['deleted_at'] for i in self.primary['data']]
        def getHiddencode(self) -> int:
            return [i['hidden_code'] for i in self.primary['data']]
        def getManual(self) -> int:
            return [i['manual_weight'] for i in self.primary['data']]
        def getModifiedat(self) -> str:
            return [i['modified_at'] for i in self.primary['data']]
        def getWorkname(self) -> str:
            return [i['name'] for i in self.primary['data']]
        def getLang(self) -> str:
            return [i['lang'] for i in self.primary['data']]
        def getID(self) -> int:
            return [i['id'] for i in self.primary['data']]
        def getOriginalid(self) -> int:
            return [i['original_id'] for i in self.primary['data']]
        def getScore(self) -> float:
            lst = []
            for i in self.primary['data']:
                try:
                    lst.append(i["popular_score"])
                except:
                    lst.append('NaN')
        def getIspublic(self) -> int:
            return [i['published'] for i in self.primary['data']]
        def getPublishedat(self) -> str:
            return [i['published_at'] for i in self.primary['data']]
        def getRemoved(self) -> int:
            return [i['removed'] for i in self.primary['data']]
        def getSourceview(self) -> int:
            return [i['source_code_views'] for i in self.primary['data']]
        def getThumbnail(self) -> str:
            return [i['thumbnail'] for i in self.primary['data']]
        def getTopic(self) -> str:
            return [i['topic_id'] for i in self.primary['data']]
        def getType(self) -> str:
            return [i['type'] for i in self.primary['data']]
        def getUpdatedat(self) -> str:
            return [i['updated_at'] for i in self.primary['data']]
        def getVersion(self) -> str:
            return [i['version'] for i in self.primary['data']]
        def getViews(self) -> int:
            return [i['views'] for i in self.primary['data']]

    class modules:
        def __init__(self,input_index:int,cookie:Optional[str] = None):
            """
            :param cookie:Cookie
            :param input_index:
                   1 -> 首页
                   2 -> 开眼课堂
                   3 -> 老师的作品
            """
            self.cookie = cookie
            self.headers = XesIndex.getHeaders(self.cookie)
            if input_index == 1:index1 = 0
            elif input_index == 2:index1 = 1
            else:index1 = 4
            self.primary = self.getModules()["data"][index1]["items"]

        def getModules(self) -> dict:
            url = "https://code.xueersi.com/api/index/works/modules"
            response = requests.get(url,headers=self.headers).text
            data = json.loads(response)
            return data
        def getLikes(self) -> int:
            return [i['likes'] for i in self.primary]
        def getUnlikes(self) -> int:
            return [i['unlikes'] for i in self.primary]
        def getFavorites(self) -> int:
            return [i['favorites'] for i in self.primary]
        def getUserid(self) -> int:
            return [i['user_id'] for i in self.primary]
        def getUsername(self) -> int:
            return [i['username'] for i in self.primary]
        def getCommentsnum(self) -> int:
            return [i['comments'] for i in self.primary]
        def getCreatedat(self) -> str:
            return [i['created_at'] for i in self.primary]
        def getDeletedat(self) -> str:
            return [i['deleted_at'] for i in self.primary]
        def getHiddencode(self) -> int:
            return [i['hidden_code'] for i in self.primary]
        def getManual(self) -> int:
            return [i['manual_weight'] for i in self.primary]
        def getModifiedat(self) -> str:
            return [i['modified_at'] for i in self.primary]
        def getWorkname(self) -> str:
            return [i['name'] for i in self.primary]
        def getLang(self) -> str:
            return [i['lang'] for i in self.primary]
        def getID(self) -> int:
            return [i['id'] for i in self.primary]
        def getOriginalid(self) -> int:
            return [i['original_id'] for i in self.primary]
        def getScore(self) -> float:
            lst = []
            for i in self.primary:
                try:
                    lst.append(i["popular_score"])
                except:
                    lst.append('NaN')
        def getIspublic(self) -> int:
            return [i['published'] for i in self.primary]
        def getPublishedat(self) -> str:
            return [i['published_at'] for i in self.primary]
        def getRemoved(self) -> int:
            return [i['removed'] for i in self.primary]
        def getSourceview(self) -> int:
            return [i['source_code_views'] for i in self.primary]
        def getThumbnail(self) -> str:
            return [i['thumbnail'] for i in self.primary]
        def getTopic(self) -> str:
            return [i['topic_id'] for i in self.primary]
        def getType(self) -> str:
            return [i['type'] for i in self.primary]
        def getUpdatedat(self) -> str:
            return [i['updated_at'] for i in self.primary]
        def getVersion(self) -> str:
            return [i['version'] for i in self.primary]
        def getViews(self) -> int:
            return [i['views'] for i in self.primary]

    class foryou:
        def __init__(self,cookie:str):
            self.cookie = cookie
            self.headers = XesIndex.getHeaders(self.cookie)
            self.primary = self.getFor_you()['data']['projects']
        def getFor_you(self):
            return json.loads(requests.get('https://code.xueersi.com/api/pai/projects/for_you', headers=self.headers).text)
        def getLikes(self) -> int:
            return [i['likes'] for i in self.primary]
        def getUnlikes(self) -> int:
            return [i['unlikes'] for i in self.primary]
        def getFavorites(self) -> int:
            return [i['favorites'] for i in self.primary]
        def getUserid(self) -> int:
            return [i['user_id'] for i in self.primary]
        def getUsername(self) -> int:
            return [i['username'] for i in self.primary]
        def getCommentsnum(self) -> int:
            return [i['comments'] for i in self.primary]
        def getCreatedat(self) -> str:
            return [i['created_at'] for i in self.primary]
        def getDeletedat(self) -> str:
            return [i['deleted_at'] for i in self.primary]
        def getHiddencode(self) -> int:
            return [i['hidden_code'] for i in self.primary]
        def getManual(self) -> int:
            return [i['manual_weight'] for i in self.primary]
        def getModifiedat(self) -> str:
            return [i['modified_at'] for i in self.primary]
        def getWorkname(self) -> str:
            return [i['name'] for i in self.primary]
        def getLang(self) -> str:
            return [i['lang'] for i in self.primary]
        def getID(self) -> int:
            return [i['id'] for i in self.primary]
        def getOriginalid(self) -> int:
            return [i['original_id'] for i in self.primary]
        def getScore(self) -> float:
            lst = []
            for i in self.primary:
                try:
                    lst.append(i["popular_score"])
                except:
                    lst.append('NaN')
        def getIspublic(self) -> int:
            return [i['published'] for i in self.primary]
        def getPublishedat(self) -> str:
            return [i['published_at'] for i in self.primary]
        def getRemoved(self) -> int:
            return [i['removed'] for i in self.primary]
        def getSourceview(self) -> int:
            return [i['source_code_views'] for i in self.primary]
        def getThumbnail(self) -> str:
            return [i['thumbnail'] for i in self.primary]
        def getTopic(self) -> str:
            return [i['topic_id'] for i in self.primary]
        def getType(self) -> str:
            return [i['type'] for i in self.primary]
        def getUpdatedat(self) -> str:
            return [i['updated_at'] for i in self.primary]
        def getVersion(self) -> str:
            return [i['version'] for i in self.primary]
        def getViews(self) -> int:
            return [i['views'] for i in self.primary]

# Xes发现
class XesExplore():
    def __init__(self) -> None:
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33',
            }

    def getExplore(self,_type:str,page:int,lang:Optional[str] = None,tag:Optional[str] = None) -> dict:
        if not lang:
            lang = ''
        if not tag:
            tag = ''
        else:
            tag = parse.quote(tag)
        url = f'https://code.xueersi.com/api/works/{_type}?type={_type}&lang={lang}&tag={tag}&page={page}&per_page=50'
        response = requests.get(url,headers=self.headers).text
        data = json.loads(response)
        return data

    def getSearch(self,_type:str,page:int,keyword:str,lang:Optional[str] = None,order:Optional[str] = None):
        if (_type == "works" or _type == "videos") and order:
            order = order
        else:
            order = 'comprehensive'
        if _type == 'works' and lang:
            lang = lang
        else:
            lang = 'all'
        url = f'https://code.xueersi.com/api/search?keyword={parse.quote(keyword)}&search_type={_type}&order_type={order}&lang={lang}&page={page}&per_page=50'
        response = requests.get(url,headers=self.headers).text
        data = json.loads(response)
        return data

# Xes的操作、行为
class XesBehavior():
    def __init__(self,cookie:str) -> None:
        self.cookie = cookie
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33',
            'Cookie':cookie
            }

    def parseWorkURL(self,url:str) -> dict:
        url = parse.urlparse(url)
        parad = parse.parse_qs(url.query)
        return parad

    def getTopicID(self,workurl:str):
        urldata = self.parseWorkURL(workurl)
        pid = urldata['pid'][0]
        lang = urldata['lang'][0]
        if lang == 'scratch':
            topic_id = f'CS_{pid}'
        else:
            form = urldata['form'][0]
            if form == "cpp":
                topic_id = f'CC_{pid}'
            else:
                topic_id = f'CP_{pid}'
        return topic_id

    def doLike(self,workurl:str):
        urldata= self.parseWorkURL(workurl)
        pid = urldata['pid'][0]
        lang = urldata['lang'][0]
        if lang == "scratch":
            url = f'https://code.xueersi.com/api/projects/{pid}/like'
            payload = {
                "id":pid,
                "lang":"scratch"
            }
        else:
            form = urldata['form'][0]
            if form == "cpp":
                url = f'https://code.xueersi.com/api/compilers/{pid}/like'
                payload = {
                    "form":"cpp",
                    "id":pid,
                    "lang":"code"
                }
            else:
                url = f'https://code.xueersi.com/api/python/{pid}/like'
                payload = {
                    "form":form,
                    "id":pid,
                    "lang":"code"
                }
        response = requests.post(url,headers=self.headers,json = payload)

    def doCannellike(self,workurl:str):
        urldata= self.parseWorkURL(workurl)
        pid = urldata['pid'][0]
        lang = urldata['lang'][0]
        if lang == "scratch":
            url = f'https://code.xueersi.com/api/projects/{pid}/cancel_like'
            payload = {
                "id":pid,
                "lang":"scratch"
            }
        else:
            form = urldata['form'][0]
            if form == "cpp":
                url = f'https://code.xueersi.com/api/compilers/{pid}/cancel_like'
                payload = {
                    "form":"cpp",
                    "id":pid,
                    "lang":"code"
                }
            else:
                url = f'https://code.xueersi.com/api/python/{pid}/cancel_like'
                payload = {
                    "form":form,
                    "id":pid,
                    "lang":"code"
                }
        response = requests.post(url,headers=self.headers,json = payload)

    def doUnlike(self,workurl:str):
        urldata= self.parseWorkURL(workurl)
        pid = urldata['pid'][0]
        lang = urldata['lang'][0]
        if lang == "scratch":
            url = f'https://code.xueersi.com/api/projects/{pid}/unlike'
            payload = {
                "id":pid,
                "lang":"scratch"
            }
        else:
            form = urldata['form'][0]
            if form == "cpp":
                url = f'https://code.xueersi.com/api/compilers/{pid}/unlike'
                payload = {
                    "form":"cpp",
                    "id":pid,
                    "lang":"code"
                }
            else:
                url = f'https://code.xueersi.com/api/python/{pid}/unlike'
                payload = {
                    "form":form,
                    "id":pid,
                    "lang":"code"
                }
        response = requests.post(url,headers=self.headers,json = payload)

    def doCannelunlike(self,workurl:str):
        urldata= self.parseWorkURL(workurl)
        pid = urldata['pid'][0]
        lang = urldata['lang'][0]
        if lang == "scratch":
            url = f'https://code.xueersi.com/api/projects/{pid}/cancel_unlike'
            payload = {
                "id":pid,
                "lang":"scratch"
            }
        else:
            form = urldata['form'][0]
            if form == "cpp":
                url = f'https://code.xueersi.com/api/compilers/{pid}/cancel_unlike'
                payload = {
                    "form":"cpp",
                    "id":pid,
                    "lang":"code"
                }
            else:
                url = f'https://code.xueersi.com/api/python/{pid}/cancel_unlike'
                payload = {
                    "form":form,
                    "id":pid,
                    "lang":"code"
                }
        response = requests.post(url,headers=self.headers,json = payload)

    def doFavorite(self,workurl:str,state:int):
        topic_id = self.getTopicID()
        payload = {
            "state":state,
            "topic_id":topic_id
            }
        requests.post('https://code.xueersi.com/api/space/favorite',headers=self.headers,json = payload)

    def sendComment(self,workurl:str,text:str,targetid:int):
        """
        :param targetid:回复作品时targetid为0,回复作品下的评论时targetid为评论的id号
        """
        if len(text) > 200:
            raise ValueError("The length of the text argument cannot be greater than 200")
        topic_id = self.getTopicID(workurl)
        payload = {
            "appid":'1001108',
            "content":text,
            "target_id":targetid,
            "topic_id":topic_id
        }
        requests.post('https://code.xueersi.com/api/comments/submit',headers=self.headers,json=payload)
    
    def followUser(self,userid:int,state:int):
        payload = {
            "followed_user_id":str(userid),
            "state":state
        }
        requests.post('https://code.xueersi.com/api/space/follow',headers=self.headers,json=payload)

class XesCloud:
    def __init__(self,name):
        """
        :param name:Variable Name
        """
        if isinstance(name,str):
            self.name = name
        else:
            raise TypeError("变量名只能用字符串")

    def getCookies(self):
        cookies = ""
        if len(sys.argv) > 1:
            try:
                cookies = json.loads(sys.argv[1])["cookies"]
            except:
                print("未登录")
                sys.exit(0)
        return cookies

    def getID(self):
        cookie = self.getCookies()
        id = ''
        for i in cookie.split(";"):
            id = i[8:] if i[1:7] == "stu_id" else id
        return id

    def open(self) -> None:
        self.ws = websocket.create_connection(f'wss://api.xueersi.com/codecloudvariable/ws:80',timeout=10)

    def close(self) -> None:
        try:
            self.ws.close()
        except NameError:
            raise Exception("连接不存在,您没有建立过连接,请使用open函数建立连接\neg.\ncloud=XesCloud('num')\ncloud.open()")

    def create(self) -> None:
        message = {
            "method": "create",
            "user": str(self.getID()),
            "project_id": "20547605",
            "name": "☁ "+self.name,
            "value": 0
        }
        try:
            self.ws.send(json.dumps(message))
        except NameError:
            raise Exception("连接不存在,您没有建立过连接,请使用open函数建立连接\neg.\ncloud=XesCloud('num')\ncloud.open()")

    def remove(self) -> None:
        message = {
            "method": "delete",
            "name": "☁ "+self.name,
            "project_id": "20547605",
            "user": str(self.getID())
        }
        try:
            self.ws.send(json.dumps(message))
        except NameError:
            raise Exception("连接不存在,您没有建立过连接,请使用open函数建立连接\neg.\ncloud=XesCloud('num')\ncloud.open()")

    def write(self,value) -> None:
        """
        :param value:Value
        """
        message = {
            "method":"set",
            "user":str(self.getID()),
            "project_id":"20547605",
            "name":"☁ "+self.name,
            "value":value
        }
        try:
            self.ws.send(json.dumps(message))
        except NameError:
            raise Exception("连接不存在,您没有建立过连接,请使用open函数建立连接\neg.\ncloud=XesCloud('num')\ncloud.open()")
        self.close()

    def read(self) -> int:
        self.ws = websocket.create_connection(f'wss://api.xueersi.com/codecloudvariable/ws:80',timeout=10)
        message = {"method": "handshake", 
            "user": str(self.getID()),
            "project_id": "20547605"
        }
        dic = {}
        try:
            while True:
                self.ws.send(json.dumps(message))
                r = self.ws.recv()
                print(r)
                value = str(json.loads(r)['value'])
                name = str(json.loads(r)['name'])
                if name in dic:
                    break
                dic[name] = value
            try:
                return int(dic["☁ "+self.name])
            except:
                raise Exception("变量不存在")
        except NameError:
            raise Exception("连接不存在,您没有建立过连接,请使用open函数建立连接\neg.\ncloud=XesCloud('num')\ncloud.open()")

class XesSubmit():
    def __init__(self,cookie) -> None:
        self.cookie = cookie
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33',
            'Cookie':cookie
            }

    def submitFeedback(self,text:str,_type:str,contact:str = '',images:list = []):
        payload = {
            "contact":contact,
            "content":text,
            "images":images,
            "score":0,
            "source_type":_type
        }
        requests.post('https://code.xueersi.com/api/index/feedback/submit',headers=self.headers,json=payload)

    def submitReport(self):
        pass
