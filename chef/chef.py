import mechanicalsoup as ms
import os.path
import getpass
import json
import pickle
from time import sleep

class ns:
    pass

home_dir = os.path.expanduser('~')
rc_file = '.chefrc'
base_url = 'https://www.codechef.com'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
session_limit_url = 'https://www.codechef.com/session/limit'

nsi = ns()
nsi.username = None
nsi.password = None
nsi.browser = None
nsi.init_status = None


def init():
    rc_file_path = os.path.join(home_dir, rc_file)
    if not os.path.isfile(rc_file_path):
        nsi.username = input('Enter username: ',)
        nsi.password = getpass.getpass(prompt='Enter password: ')

        with open(rc_file_path, 'w') as f:
            json.dump({'username': nsi.username, 'password': nsi.password}, f)

        print('Username and Password changed.')
    else:
        with open(rc_file_path, 'r') as f:
            config = json.load(f)
            nsi.username, nsi.password = config['username'], config['password']
    
    retrieve_session()
    prepare_browser(session = nsi.session)
    login()
    sleep(0.5)
    print(nsi.browser.get_url())



def login():
    if not is_logged_in():
        nsi.browser.select_form('form[id="new-login-form"]')
        nsi.browser['name'] = nsi.username
        nsi.browser['pass'] = nsi.password
        nsi.browser.submit_selected()
    check_session_limit()
    return True


def is_logged_in():
    tmp = nsi.browser.get_current_page().findAll(text='Logout')
    print(tmp)
    if tmp:
        return True
    return False


def prepare_browser(session = None):
    if nsi.browser == None:
        nsi.browser = ms.StatefulBrowser(session=session) if session != None else ms.StatefulBrowser()
    nsi.browser.set_user_agent(user_agent)
    nsi.init_status = nsi.browser.open(session_limit_url)
    
    while nsi.init_status.status_code not in [200, 403]:
        sleep(0.5)
        nsi.init_status = nsi.browser.open(session_limit_url)
    # print(nsi.browser.get_url())


def persist():
    with open(os.path.join(home_dir, '.chefsession.pkl'), 'wb') as f:
        pickle.dump(nsi.browser.session, f)
    return True


def retrieve_session():
    nsi.session = None
    if os.path.exists(os.path.join(home_dir, '.chefsession.pkl')):
        with open(os.path.join(home_dir, '.chefsession.pkl'), 'rb') as f:
            nsi.session = pickle.load(f)

        return True
    return False


def check_session_limit():
    page = nsi.browser.get_current_page()
    inps = page.findAll(lambda inp: inp.name == 'input' and inp.attrs['type'] == 'checkbox' and inp.parent.find('b').text == '')

    if len(inps) > 0:
        nsi.browser.select_form('form[id="session-limit-page"]')
        for c in page.findAll(lambda inp: inp.name == 'input' and inp.attrs['type'] == 'checkbox' and inp.parent.find('b').text == ''):
            nsi.browser[c.attrs['name']] = c.attrs['value']
        nsi.browser.submit_selected()


def main():
    init()
    persist()
    pass

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    finally:
        persist()
