#!/usr/bin/env python
"""PeeweeCookieJar
This code is based on the Scrapy Cookie implementation.
This File contains the peewee model of an cookie.
In Addition the Cookiejar is able to save all cookies and implements some management features.

"""

import time,copy
import cookielib
from cookielib import CookieJar, IPV4_RE
import datetime
import logging

from scrapy.utils.httpobj import urlparse_cached
from scrapy.utils.python import to_native_str

import BaseModel
from synchronized import *

from peewee import *

__author__ = "Lukas Pupka-Lipinski"
__copyright__ = "Copyright 2018, PersistentPeeweeCookie"
__credits__ = [""]
__license__ = "GPL"
__version__ = "1.0.5"
__maintainer__ = "Lukas Pupka-Lipinski"
__email__ = "support@lpl-mind.de"
__status__ = "Dev"

class PersistentCookie(cookielib.Cookie, BaseModel.BaseModel):
    """
    This class is used to apply a cookie via a mysql server.
    A cookie can be reused if application is restarted.
    """
    comment = TextField(null=True)
    comment_url = TextField(null=True)
    domain = TextField(null=True)
    name = TextField(null=True)
    path = TextField(null=True)
    value = TextField(null=True)
    rest = TextField(null=True)

    expires = DateTimeField(default=datetime.datetime.now,null=True)

    discard = BooleanField(default=True,null=True)
    domain_initial_dot = BooleanField(default=True,null=True)
    domain_specified = BooleanField(default=True,null=True)
    path_specified = BooleanField(default=True,null=True)
    port_specified = BooleanField(default=True,null=True)
    rfc2109 = BooleanField(default=True,null=True)
    secure = BooleanField(default=True,null=True)

    port = IntegerField(default=0,null=True)
    version = IntegerField(default=0,null=True)
    accountid = BigIntegerField(default=0, null=False)

    def __init__(self,*args, **kwargs):
        """
        Creates a cookie in mysql space
        :param args: cookie parameter
        :param kwargs: cookie parameter
        """
        if len(args)>=1:
            BaseModel.BaseModel.__init__(self, [],
                                         version=int(args[0]) if args[0] is not None else args[0],
                                         name=args[1],
                                         value=args[2],
                                         port=args[3],
                                         port_specified=args[4],
                                         domain=args[5],
                                         domain_specified=args[6],
                                         domain_initial_dot=args[7],
                                         path=args[8],
                                         path_specified=args[9],
                                         secure=args[10],
                                         expires=datetime.datetime.fromtimestamp(int(args[11])) if args[11] is not None or type(args[11]) is not types.BooleanType else None,
                                         discard=args[12],
                                         comment=args[13],
                                         comment_url=args[14],
                                         rest=args[15],
                                         accountid=PeeweeCookieJar.accountid)

            if args[3] is None and args[4] is True:
                raise ValueError("if port is None, port_specified must be false")
        else:
            kwargs['accountid']=PeeweeCookieJar.accountid
            BaseModel.BaseModel.__init__(self,args,kwargs)

    def is_expired(self, now=None):
        """
        Repleace the is_expired method.
        :param now: current time
        :return: True if expired
        """
        if now is None: now = time.time()

        if (self.expires is not None):
            unixtime = time.mktime(self.expires.timetuple())
        else:
            unixtime=0
        if (unixtime <= now):
            return True
        return False

#change the standard used cookie ti mysqlcookie
cookielib.Cookie = PersistentCookie

class PeeweeCookieJar(CookieJar):
    """
    Cookie jar with scrapy wrapper and sqlcookie
    """
    accountid=0

    def __init__(self,accountid, policy=None, check_expired_frequency=10000):
        """
        creates a cookie jar
        :param accountid: A jar bounded to a Fbworker account ID
        :param policy: policy used
        :param check_expired_frequency: expired frequency check time
        """
        logging.getLogger('MysqlCookieJar').debug("Init CookieJar")
        CookieJar.__init__(self,policy)

        self.check_expired_frequency = check_expired_frequency
        self.processed = 0

        PeeweeCookieJar.accountid=accountid

        try:
            BaseModel.db.create_tables([PersistentCookie])

            BaseModel.db.commit()
        except OperationalError, ex:
            logging.getLogger('MysqlCookieJar').debug("SqlCookie table already exists!")
        except Exception, ex:
            logging.getLogger('MysqlCookieJar').error(ex)

            logging.getLogger('MysqlCookieJar').debug("Read cookies")
        try:
            for cookie in PersistentCookie.select().where(PersistentCookie.accountid == accountid):
                self.__set_cookie(cookie)
                logging.getLogger('MysqlCookieJar').debug("Found cookie "+str(cookie))
        except Exception, ex:
            logging.getLogger('MysqlCookieJar').error(ex)

    def _cookie_from_cookie_tuple(self, tup, request):

        return CookieJar._cookie_from_cookie_tuple(self, tup, request)

    def extract_cookies(self, response, request):

        if type(response)==WrappedResponse and type(request)==WrappedRequest:
            return CookieJar.extract_cookies(self,response,request)

        else:
            wreq = WrappedRequest(request)
            wrsp = WrappedResponse(response)
            return CookieJar.extract_cookies(self,wrsp, wreq)

    def add_cookie_header(self, request):
        wreq = WrappedRequest(request)
        self._policy._now = self._now = int(time.time())

        # the cookiejar implementation iterates through all domains
        # instead we restrict to potential matches on the domain
        req_host = urlparse_cached(request).hostname
        if not req_host:
            return

        if not IPV4_RE.search(req_host):
            hosts = potential_domain_matches(req_host)
            if '.' not in req_host:
                hosts += [req_host + ".local"]
        else:
            hosts = [req_host]

        cookies = []
        for host in hosts:
            if host in self._cookies:
                cookies += self._cookies_for_domain(host, wreq)

        attrs = self._cookie_attrs(cookies)
        if attrs:
            if not wreq.has_header("Cookie"):
                wreq.add_unredirected_header("Cookie", "; ".join(attrs))

        self.processed += 1
        if self.processed % self.check_expired_frequency == 0:
            # This is still quite inefficient for large number of cookies
            self.clear_expired_cookies()

    @property
    def _cookies(self):
        return CookieJar._cookies(self)

    def clear_session_cookies(self, *args, **kwargs):
        return CookieJar.clear_session_cookies(self,*args, **kwargs)

    def clear(self):
        return CookieJar.clear(self)

    def __iter__(self):
        return iter(self)

    def __len__(self):
        return len(self)

    def set_policy(self, pol):
        return super(PeeweeCookieJar, self).set_policy(self, pol)

    def make_cookies(self, response, request):
        if type(response) == WrappedResponse and type(request) == WrappedRequest:
            return CookieJar.make_cookies(self, response, request)

        else:
            wreq = WrappedRequest(request)
            wrsp = WrappedResponse(response)
            return CookieJar.make_cookies(self,wrsp, wreq)

    def set_cookie(self, cookie):
        obj=CookieJar.set_cookie(self,cookie)
        cookie.save()
        return obj

    def set_cookie_if_ok(self, cookie, request):
        obj=CookieJar.set_cookie_if_ok(self,cookie, WrappedRequest(request))
        cookie.save()
        return obj

    def __set_cookie(self, cookie):
        return CookieJar.set_cookie(self,cookie)

def potential_domain_matches(domain):
    """Potential domain matches for a cookie

    >>> potential_domain_matches('www.example.com')
    ['www.example.com', 'example.com', '.www.example.com', '.example.com']

    """
    matches = [domain]
    try:
        start = domain.index('.') + 1
        end = domain.rindex('.')
        while start < end:
            matches.append(domain[start:])
            start = domain.index('.', start) + 1
    except ValueError:
        pass
    return matches + ['.' + d for d in matches]

class WrappedRequest(object):
    """Wraps a scrapy Request class with methods defined by urllib2.Request class to interact with CookieJar class

    see http://docs.python.org/library/urllib2.html#urllib2.Request
    """

    def __init__(self, request):
        self.request = request

    def get_full_url(self):
        return self.request.url

    def get_host(self):
        return urlparse_cached(self.request).netloc

    def get_type(self):
        return urlparse_cached(self.request).scheme

    def is_unverifiable(self):
        """Unverifiable should indicate whether the request is unverifiable, as defined by RFC 2965.

        It defaults to False. An unverifiable request is one whose URL the user did not have the
        option to approve. For example, if the request is for an image in an
        HTML document, and the user had no option to approve the automatic
        fetching of the image, this should be true.
        """
        return self.request.meta.get('is_unverifiable', False)

    def get_origin_req_host(self):
        return urlparse_cached(self.request).hostname

    # python3 uses attributes instead of methods
    @property
    def full_url(self):
        return self.get_full_url()

    @property
    def host(self):
        return self.get_host()

    @property
    def type(self):
        return self.get_type()

    @property
    def unverifiable(self):
        return self.is_unverifiable()

    @property
    def origin_req_host(self):
        return self.get_origin_req_host()

    def has_header(self, name):
        return name in self.request.headers

    def get_header(self, name, default=None):
        return to_native_str(self.request.headers.get(name, default),
                             errors='replace')

    def header_items(self):
        return [
            (to_native_str(k, errors='replace'),
             [to_native_str(x, errors='replace') for x in v])
            for k, v in self.request.headers.items()
        ]

    def add_unredirected_header(self, name, value):
        self.request.headers.appendlist(name, value)

class WrappedResponse(object):

    def __init__(self, response):
        self.response = response

    def info(self):
        return self

    # python3 cookiejars calls get_all
    def get_all(self, name, default=None):
        return [to_native_str(v, errors='replace')
                for v in self.response.headers.getlist(name)]
    # python2 cookiejars calls getheaders
    getheaders = get_all


