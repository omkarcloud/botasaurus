from time import sleep
import traceback
import random
from bs4 import BeautifulSoup
import requests
import re
from urllib.error import ContentTooShortError
from http.client import RemoteDisconnected
from urllib.error import ContentTooShortError, URLError

NETWORK_ERRORS = [RemoteDisconnected, URLError,
                  ConnectionAbortedError, ContentTooShortError,  BlockingIOError]

def istuple(el):
    return type(el) is tuple

def is_errors_instance(instances, error):
    for i in range(len(instances)):
        ins = instances[i]
        if isinstance(error, ins):
            return True, i
    return False, -1

def retry_if_is_error(func, instances=None, retries=2, wait_time=None):
    tries = 0
    errors_only_instances = list(
        map(lambda el: el[0] if istuple(el) else el, instances))

    while tries < retries:
        tries += 1
        try:
            created_result = func()
            return created_result
        except Exception as e:
            is_valid_error, index = is_errors_instance(
                errors_only_instances, e)

            if not is_valid_error:
                raise e

            traceback.print_exc()

            if istuple(instances[index]):
                instances[index][1]()

            if tries == retries:
                raise e

            print('Retrying')

            if wait_time is not None:
                sleep(wait_time)
def extract_links_from_html(html):
    soup = BeautifulSoup(html, features="html.parser")
    xs = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'http' in href:
            xs.append(href)

    return xs


def extract_links_from_text(text):
    result = re.search("(?P<url>https?://[^\s]+)", text).group("url")
    return [result]


API = 'https://www.1secmail.com/api/v1/'


def extractids(req):
    idList = []
    for i in req:
        for k, v in i.items():
            if k == 'id':
                mailId = v
                idList.append(mailId)
    return idList


# ["1secmail.com","1secmail.org","1secmail.net","bheps.com","dcctb.com","kzccv.com","qiott.com","wuuvo.com"]
domainList = None


def get_domains():
    global domainList
    if domainList is None:
        domainList = requests.get(
            "https://www.1secmail.com/api/v1/?action=getDomainList").json()
    return domainList


class TempMail():

    def generate_email(username):
        # ['1secmail.com', '1secmail.net', '1secmail.org']
        domain = random.choice(get_domains())

        email = f'{username}@{domain}'
        return email

    def extract(email):
        ls = email.split('@')
        login = ls[0]
        domain = ls[1]
        return login, domain

    def deleteMailbox(email):
        login, domain = TempMail.extract(email)
        url = 'https://www.1secmail.com/mailbox'
        data = {
            'action': 'deleteMailbox',
            'login': f'{login}',
            'domain': f'{domain}'
        }

        requests.post(url, data=data)

    def get_domains():
        return get_domains()

    def get_email_link(email):
        def run():
            login, domain = TempMail.extract(email)
            reqLink = f'{API}?action=getMessages&login={login}&domain={domain}'
            req = requests.get(reqLink).json()

            if len(req) == 0:
                print('No messages')
                assert False

            id = extractids(req)[-1]

            msgRead = f'{API}?action=readMessage&login={login}&domain={domain}&id={id}'
            req = requests.get(msgRead).json()

            html = req['htmlBody']
            
            if html == '':
                links = extract_links_from_text(req['textBody'])
            else:
                links = extract_links_from_html(html)
            has_no_links = len(links) == 0

            if has_no_links:
                print(req)

            return links[0]

        retry_if_is_error(
            run, NETWORK_ERRORS + [AssertionError], 5, 5)
        link = run()
        return link

    def get_body(email):
        def run():
            login, domain = TempMail.extract(email)
            reqLink = f'{API}?action=getMessages&login={login}&domain={domain}'
            req = requests.get(reqLink).json()

            if len(req) == 0:
                print('No messages')
                assert False

            id = extractids(req)[-1]

            msgRead = f'{API}?action=readMessage&login={login}&domain={domain}&id={id}'
            req = requests.get(msgRead).json()

            html = req['htmlBody']
            
            if html == '':
                return req['textBody']
            else:
                return  html

        retry_if_is_error(
            run, NETWORK_ERRORS + [AssertionError], 
            # 1
            5
            , 5)
        data = run()
        return data

    def get_email_link_and_delete_mailbox(email):
        link = TempMail.get_email_link(email)
        TempMail.deleteMailbox(email)
        return link 

if __name__ == '__main__':
    link = TempMail.get_email_link("shyam@1secmail.com")
    print(link) 


    # email = TempMail.generate_email('temp')
    # print(email)
    # print(TempMail.get_email_link_and_delete_mailbox(email))
