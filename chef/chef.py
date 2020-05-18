import mechanicalsoup as ms
import os.path, os
import traceback
import getpass
import json
import pickle
import argparse
import logging
from time import sleep
from tabulate import tabulate
from sys import argv, exit

class ns:
    pass

"""
Defining the constants here
"""

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

"""
Adding global variables to a namespace so it can be used and changed inside functions
"""
nsi = ns()
nsi.username = None
nsi.password = None
nsi.browser = None
nsi.init_status = None
nsi.args = argv[1:]
nsi.is_configured = False

"""
Defining our argument parser
"""
parser = argparse.ArgumentParser(description="CLI Version for Codechef for dummies....")
parser.add_argument("-n", "--nologin", help="Perform some actions without logging in", action="store_true")
parser.add_argument("-l", "--list-contests", help="Lists all the active contests", action="store_true")
parser.add_argument("-s", "--submit", help="Submit a solution to a problem", nargs=2, metavar=('problem_code', 'solution_location'))
parser.add_argument("--history", help="List Submission history for a problem", nargs=1, metavar=('problem_code'))
parser.add_argument("-u", "--user", help="Get current logged in user", action="store_true")
parser.add_argument("--config", help="Configure and change username and password", action="store_true")
parser.add_argument("--logout", help="Logout current user", action="store_true")
# parser.add_argument()
nsi.arg = parser.parse_args()
nsi.parser = parser

def init():
    """
    Program initialization code. Configures the browser with the existing session and 
    parses the arguments provided during runtime
    """

    if len(nsi.args) == 0:
        nsi.parser.print_help()
        exit(0)

    configure()
    retrieve_session()
    prepare_browser(session = nsi.session)

    parse_arguments()


def configure(manual = False):
    """
    Configures our program with Codechef username and password and stores them in a 
    JSON file in home dir

    Parameters:
        manual (boolean): If true, program asks for username and password and changes
            the existing one.
            If false (default), program loads the existing username and password from
            the file (if present) or asks for new username and password
    """

    rc_file_path = os.path.join(home_dir, rc_file)
    def input_u_p():
        nsi.username = input('Enter username: ',)
        nsi.password = getpass.getpass(prompt='Enter password: ')

        with open(rc_file_path, 'w') as f:
            json.dump({'username': nsi.username, 'password': nsi.password}, f)

        print('Username and Password saved.')
    
    if manual:
        input_u_p()

    if not manual and not os.path.isfile(rc_file_path):
        input_u_p()    
    elif not manual:
        with open(rc_file_path, 'r') as f:
            config = json.load(f)
            nsi.username, nsi.password = config['username'], config['password']
    
    nsi.is_configured = True
    pass


def parse_arguments():
    """
    Parses all the arguments and calls the appropriate function for the argument
    """
    
    if nsi.arg.list_contests:
        list_active_contests()
    if not nsi.arg.nologin:
        login()
    if nsi.arg.history:
        print_submission_details(*nsi.arg.history)
    if nsi.arg.logout:
        logout()
    if nsi.arg.user:
        print('Username: ' + nsi.username)
    if nsi.arg.config:
        configure(manual=True)
    if nsi.arg.submit:
        submit(*nsi.arg.submit)
        print_submission_details(nsi.arg.submit[0])
    


def submit(problem_code, solution_file):
    """
    Submits a solution to Codechef to a Problem.

    Parameters:
        problem_code (str): Codechef problem code
        solution_file (str): String path to the solution file
    """

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
    """
    Prints the submission history for a given problem code in Tabular format

    Parameters:
        pc (str): Problem code
    """

    sleep(0.5)
    nsi.browser.open(base_url + '/status/' + pc + ',' + nsi.username)
    sub_table = nsi.browser.get_current_page().find('table', class_='dataTable')
    header = []
    data = []
    for th in sub_table.find('thead').find('tr').find_all('th'):
        header.append(th.text.strip())
    header = header[:-1]
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
        _ = _[:-1]
        data.append(_)
    
    print(tabulate(data, headers=header, tablefmt='pretty'))
    pass


def login():
    """
    Logs in the user with username and password if already not logged in.
    Then checks if any other IP is logged in with the same username, and
    logs them out.
    """

    if not is_logged_in():
        nsi.browser.select_form('form[id="new-login-form"]')
        nsi.browser['name'] = nsi.username
        nsi.browser['pass'] = nsi.password
        nsi.browser.submit_selected()
    check_session_limit()
    return True


def logout():
    """
    Logout the user if alredy logged in
    """

    if is_logged_in():
        nsi.browser.open(base_url + '/logout')


def is_logged_in():
    """
    Checks if the user is already logged in in the previous session
    It find the HTML document for the word 'Logout' and if present,
    the user is logged in, else not
    """

    tmp = nsi.browser.get_current_page().findAll(text='Logout')
    # print(tmp)
    if tmp:
        return True
    return False


def prepare_browser(session = None):
    """
    Initialises the browser with existing session (if present).
    Then opens the session limit page to check for existing logged in sessions.

    Parameters:
        session (bs4.BeautifulSoup.Session): Any existing session object to init.
    """

    if nsi.browser == None:
        nsi.browser = ms.StatefulBrowser(session=session) if session != None else ms.StatefulBrowser()
    nsi.browser.set_user_agent(user_agent)
    nsi.init_status = nsi.browser.open(session_limit_url)
    
    while nsi.init_status.status_code not in [200, 403]:
        sleep(0.5)
        nsi.init_status = nsi.browser.open(session_limit_url)
    # print(nsi.browser.get_url())


def persist():
    """
    Saves the browser session to a local file in home directory for later use.
    """

    if nsi.browser:
        with open(os.path.join(home_dir, '.chefsession.pkl'), 'wb') as f:
            pickle.dump(nsi.browser.session, f)
        return True


def retrieve_session():
    """
    Loads the session object from the session file (if present)
    nsi.session is used to store the session object if presnet else NoneType
    """

    nsi.session = None
    if os.path.exists(os.path.join(home_dir, '.chefsession.pkl')):
        with open(os.path.join(home_dir, '.chefsession.pkl'), 'rb') as f:
            nsi.session = pickle.load(f)

        return True
    return False


def check_session_limit():
    """
    Checks if the same user is logged in with some other session in some other 
    browsers. It parses the form and checks for input-type=checkbox with text other
    than 'Your current Session', checks them and submits the form to log them out
    """

    page = nsi.browser.get_current_page()
    inps = page.findAll(lambda inp: inp.name == 'input' and inp.attrs['type'] == 'checkbox' and inp.parent.find('b').text == '')

    if len(inps) > 0:
        nsi.browser.select_form('form[id="session-limit-page"]')
        for c in page.findAll(lambda inp: inp.name == 'input' and inp.attrs['type'] == 'checkbox' and inp.parent.find('b').text == ''):
            nsi.browser[c.attrs['name']] = c.attrs['value']
        nsi.browser.submit_selected()


def list_active_contests():
    """
    Prints the active contests data in Tabular format. It visits the contest page and
    parses the table to extract contest details and stores them in a list and uses the
    tabulate library to print it in table format
    """

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
    """
    Entry point for the program. And calls the init function for the initialization
    """
    
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
