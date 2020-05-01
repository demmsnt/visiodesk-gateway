import json
import requests
import hashlib
import logging
from requests.cookies import RequestsCookieJar
from requests.auth import AuthBase


class BearerAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        logging.getLogger("BearerAuth").debug("Authorization=Bearer " + self.token)
        r.headers["Authorization"] = "Bearer " + self.token
        return r


class VisiobasClient:
    def __init__(self, host, port, verify=True):
        """
        :param host: server host
        :param port: server port
        :param verify: verify ssl certificate
        """
        self.host = host
        self.port = port
        self.token = None
        self.user_id = None
        self.session = None
        self.logger = logging.getLogger(__name__)
        self.auth = None
        self.verify = verify

    def get_addr(self):
        return "{}:{}".format(self.host, self.port)

    def get(self, url, headers=None, cookies=None) -> list or dict:
        return self.__extract_response_data(
            self.__request('get', url, headers, cookies=cookies))

    def delete(self, url, headers=None, cookies=None) -> list or dict:
        return self.__extract_response_data(
            self.__request('delete', url, headers, cookies))

    def post(self, url, data, headers=None, cookies=None) -> list or dict:
        return self.__extract_response_data(
            self.__request('post', url, data, headers, cookies))

    def __get_session(self):
        self.session = self.session if self.session is not None else requests.Session()
        return self.session

    # TODO add request attempt if response is 401 - Autorization issue, then try perform rq_login and send request one more time
    def __request(self, method, url, data=None, headers=None, cookies=None):
        session = self.__get_session()
        if method == 'get':
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug("GET: {}".format(url))
            response = session.get(url, headers=headers, cookies=cookies, auth=self.auth, verify=self.verify)
        elif method == 'post':
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug("POST: {} data: {}".format(url, data))
            response = session.post(url, data, headers=headers, auth=self.auth, verify=self.verify)
        # elif method == 'delete':
        #     response = session.delete(url, headers=headers, auth=self.auth)
        else:
            raise Exception('Unsupported http method: {}'.format(method))
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("Response: {} data: {}".format(url, response))
        return response

    def rq_check_auth_token(self) -> bool:
        """
        Request verification user token\n
        :param token: token to verify
        :type token: str
        :return: token verification result
        """
        url = "{}/secure/check".format(self.get_addr().format())
        data = self.get(url)
        return data["success"] is True

    def rq_login(self, login, password):
        """
        Request login and keep login token and user_id\n
        :param login: plain text login
        :type login: str
        :param password: md5 hashed password
        :type password: str
        :return: 'token' and 'user_id'
        """
        self.logger.debug("login: {}, password: ...".format(login))
        url = "{}/auth/rest/login".format(self.get_addr())
        data = json.dumps({
            "login": login,
            "password": password
        })
        # js = {
        #     "login": login,
        #     "password": hashlib.md5(password.encode()).hexdigest()
        # }
        headers = {
            "Content-type": "application/json;charset=UTF-8"
        }

        data = self.post(url, data, headers)
        # data = self.__extract_response_data(response)
        self.__set_credentials(data["token"], data["user_id"])
        return data

    def rq_logout(self):
        """
        Request logout\n
        :return:
        """
        if not self.token:
            raise ValueError("login token expected")

        url = "{}/auth/secure/logout".format(self.get_addr())
        # headers = {
        #     "Authorization": "Bearer {}".format(self.token)
        # }
        #
        # cookies = RequestsCookieJar()
        # cookies.set("user.token", self.token)
        # cookies.set("user.user_id", str(self.user_id))
        # return self.get(url, headers=headers, cookies=cookies)
        return self.get(url)
        # response = requests.get(url, headers=headers)
        # data = self.__extract_response_data(response)
        # return response

    def rq_children(self, reference=""):
        """
        Request get children all certain object (reference)
        :param reference: optional object reference string, by default output only root objects
        :type reference: str
        :return: list of children objects (by default root objects)
        """
        url = "{}/vbas/arm/get/{}".format(self.get_addr(), reference) if not reference \
            else "{}/vbas/arm/get/objects".format(self.get_addr())
        return self.get(url)

    def __set_credentials(self, token, user_id):
        self.token = token
        self.user_id = user_id
        self.auth = BearerAuth(self.token)

    def __extract_response_data(self, response) -> dict:
        if response.status_code == 200:
            result = response.json()
            if result["success"] is True:
                return result["data"] if "data" in result else {}
            else:
                err = "Failed extract response result, error: {}".format(result["error"])
                self.logger.error(err)
                raise ValueError(err)
        else:
            raise ValueError("Expected status code 200, response={}".format(response))
            # raise requests.HTTPError(response=response)
