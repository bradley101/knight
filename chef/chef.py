import mechanicalsoup as ms
import os.path, os
import traceback
import getpass
import json
import pickle
import argparse
from time import sleep
from tabulate import tabulate
from sys import argv, exit

class ns:
    pass

home_dir = os.path.expanduser('~')
rc_file = '.chefrc'
base_url = 'https://www.codechef.com'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
session_limit_url = 'https://www.codechef.com/session/limit'
lang_codes = {
    '.cpp': '44',
    '.c': '11',
    '.java': '10',
    '.py': '116',
    '.cs': '27',
}
solution_results = {
    'runtime error(SIGFPE)': 'Runtime Error',
    'wrong answer': 'Wrong Answer',
    'compilation error': 'Compile Error',
    'time limit exceeded': 'Time Limit Exceeded',
    'accepted': 'Accepted'
}

nsi = ns()
nsi.username = None
nsi.password = None
nsi.browser = None
nsi.init_status = None
nsi.args = argv[1:]

parser = argparse.ArgumentParser(description="CLI Version for Codechef for dummies....")
parser.add_argument("-n", "--nologin", help="Perform some actions without logging in", action="store_true")
parser.add_argument("-l", "--list-contests", help="Lists all the active contests", action="store_true")
parser.add_argument("-s", "--submit", help="Submit a solution to a problem", nargs=2, metavar=('problem_code', 'solution_location'))
parser.add_argument("--history", help="List Submission history for a problem", nargs=1, metavar=('problem_code'))
# parser.add_argument()
nsi.arg = parser.parse_args()
nsi.parser = parser

def init():
    rc_file_path = os.path.join(home_dir, rc_file)
    if not os.path.isfile(rc_file_path):
        nsi.username = input('Enter username: ',)
        nsi.password = getpass.getpass(prompt='Enter password: ')

        with open(rc_file_path, 'w') as f:
            json.dump({'username': nsi.username, 'password': nsi.password}, f)

        print('Username and Password saved.')
    else:
        with open(rc_file_path, 'r') as f:
            config = json.load(f)
            nsi.username, nsi.password = config['username'], config['password']
    
    retrieve_session()
    prepare_browser(session = nsi.session)

    parse_arguments()


def parse_arguments():
    if len(nsi.args) == 0:
        nsi.parser.print_help()
        exit(0)
    if nsi.arg.list_contests:
        list_active_contests()
    if not nsi.arg.nologin:
        login()
    if nsi.arg.history:
        print_submission_details(*nsi.arg.history)
    if nsi.arg.submit:
        submit(*nsi.arg.submit)
        print_submission_details(nsi.arg.submit[0])
    


def submit(problem_code, solution_file):
    login()
    solution_file_path = os.path.abspath(solution_file)
    nsi.browser.open(base_url + '/submit/' + problem_code)
    form = nsi.browser.select_form('form[id="problem-submission"]')
    form.set('files[sourcefile]', solution_file_path)
    form.set('language', lang_codes[os.path.splitext(solution_file_path)[1]])
    nsi.browser.submit_selected()
    sleep(1)
    nsi.browser.refresh()
    print ('Successfully submited')

    pass


def print_submission_details(pc):
    sleep(0.5)
    nsi.browser.open(base_url + '/status/' + pc + ',' + nsi.username)
    sub_table = nsi.browser.get_current_page().find('table', class_='dataTable')
    header = []
    data = []
    for th in sub_table.find('thead').find('tr').find_all('th'):
        header.append(th.text.strip())
    # header = header[:-1]
    trs = sub_table.find('tbody').find_all('tr')
    for tr in trs:
        _ = []
        tds = tr.find_all('td')
        for idx, td in enumerate(tds):
            if idx == 3:
                rs_span = td.find('span')
                if 'title' in rs_span.attrs and rs_span.attrs['title'] != '':
                    _.append(td.find('span').attrs['title'])
                else:
                    _.append(''.join([str(__) for __ in rs_span.find_all(text=True, recursive=False)]))
            else:
                _.append(td.text.strip())
        # _ = _[:-1]
        data.append(_)
    
    print(tabulate(data, headers=header, tablefmt='pretty'))
    pass


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
    # print(tmp)
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


def list_active_contests():
    header = []
    contest_data = []
    nsi.browser.open('https://www.codechef.com/contests')
    sleep(0.1)
    present = nsi.browser.get_current_page().find('table', class_='dataTable')
    ths = present.find_all('th')
    for th in ths:
        header.append(th.find('a').text.strip())
    trs = present.find('tbody').find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        _data = []
        for td in tds:
            _data.append(td.text.strip())
        contest_data.append(_data)
    
    print(tabulate(contest_data, headers=header, tablefmt='pretty'))



def main():
    init()
    pass

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc())
        pass
    finally:
        persist()
