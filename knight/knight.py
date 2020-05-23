import mechanicalsoup as ms
import os.path, os
import traceback
import getpass
import json
import pickle
import argparse
import logging
import re
from datetime import datetime
from time import sleep
from tabulate import tabulate
from sys import argv, exit

class ns:
    pass

"""
Defining the constants here
"""

app_name = 'knight'
home_dir = os.path.expanduser('~')
if not os.path.exists(os.path.join(home_dir, '.' + app_name)):
    os.makedirs(os.path.join(home_dir, '.' + app_name, 'logs'))
home_dir = os.path.join(home_dir, '.' + app_name)
rc_file = '.knightrc'
log_conf_file = os.path.join(home_dir, 'log.conf')
log_file = os.path.join(home_dir, 'logs', app_name + '.' + str(datetime.today().strftime("%Y-%m-%d")) + '.log')
session_file = '.' + app_name + '.session.pkl'
base_url = 'https://www.codechef.com'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
session_limit_url = 'https://www.codechef.com/session/limit'
contest_url = 'https://www.codechef.com/contests'
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
# logging.basicConfig(filename=log_file, level=logging.INFO)
logger = logging.getLogger(app_name)
logger.setLevel(logging.DEBUG)
log_handler = logging.FileHandler(filename=log_file, encoding="utf-8")
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s"))
logger.addHandler(log_handler)

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
nsi.parser = parser

def init():
    """
    Program initialization code. Configures the browser with the existing session and 
    parses the arguments provided during runtime
    """
    logger.info('Parsing the arguments')
    nsi.arg = nsi.parser.parse_args()
    logger.debug('Arg = ' + str(nsi.arg))
    
    if len(nsi.args) == 0:
        logger.info('No arguments provided. Printing help (-h --help)')
        
        nsi.parser.print_help()

        logger.info('Exiting program. exit code 0')
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

    logger.info('Inside configure()')
    logger.debug('manual = ' + str(manual))

    rc_file_path = os.path.join(home_dir, rc_file)
    def input_u_p():
        logger.info('Promt for credentials')

        nsi.username = input('Enter username: ',)
        def prompt_pwd():
            nsi.password = getpass.getpass(prompt='Enter password: ')
            nsi.repassword = getpass.getpass(prompt='Re enter password: ')
            return nsi.password == nsi.repassword
        while not prompt_pwd():
            logger.info('Incorrect password entered')
            print('Passwords did not match. Please retry')
            pass
        

        logger.info('Opening rc_file for writing credentials')
        with open(rc_file_path, 'w') as f:
            json.dump({'username': nsi.username, 'password': nsi.password}, f)
        logger.info('Credentials changed')

        print('Username and Password saved.')
    
    if manual:
        logger.info('Username and password change called --config')
        input_u_p()

    if not manual and not os.path.isfile(rc_file_path):
        logger.info('First time configuration')
        input_u_p()    
    elif not manual:
        logger.info('Opening rc_file for reading credentials')
        with open(rc_file_path, 'r') as f:
            config = json.load(f)
            nsi.username, nsi.password = config['username'], config['password']
        logger.info('Reading for file successfull')

    nsi.is_configured = True
    pass


def parse_arguments():
    """
    Parses all the arguments and calls the appropriate function for the argument
    """
    logger.info('Parsing command line arguments')
    logger.debug('Arg = ' + str(nsi.arg))

    if nsi.arg.config:
        configure(manual=True)
    else:
        if nsi.arg.list_contests:
            list_active_contests()
        if not nsi.arg.nologin:
            login()
        if nsi.arg.user:
            print('Username: ' + nsi.username)
        if nsi.arg.submit:
            submit(*nsi.arg.submit)
            print_submission_details(nsi.arg.submit[0])
        if nsi.arg.logout:
            logout()
        if nsi.arg.history:
            print_submission_details(*nsi.arg.history)
    


def submit(problem_code, solution_file):
    """
    Submits a solution to Codechef to a Problem.

    Parameters:
        problem_code (str): Codechef problem code
        solution_file (str): String path to the solution file
    """
    logger.info('Inside submit()')

    login()
    
    solution_file_path = os.path.abspath(solution_file)
    logger.debug('Solution file path = ' + str(solution_file_path))

    submission_url = base_url + '/submit/' + problem_code
    _resp = nsi.browser.open(submission_url)
    logger.debug('Opening submission url = ' + str(submission_url))
    logger.debug('Response = ' + _resp)

    logger.info('Setting form elements')
    form = nsi.browser.select_form('form[id="problem-submission"]')
    form.set('files[sourcefile]', solution_file_path)
    form.set('language', lang_codes[os.path.splitext(solution_file_path)[1]])
    logger.debug('Final form: ' + form.print_summary())
    _resp = nsi.browser.submit_selected()
    logger.debug('Submission url response = ' + str(_resp))

    sleep(1)
    
    logger.info('Refresing browser')
    nsi.browser.refresh()
    print ('Successfully submited')
    logger.info('Exiting submit()')


def print_submission_details(pc):
    """
    Prints the submission history for a given problem code in Tabular format

    Parameters:
        pc (str): Problem code
    """
    logger.info('Inside print submission history')
    logger.debug('Problem code = ' + str(pc))

    sleep(0.5)
    hist_url = base_url + '/status/' + pc + ',' + nsi.username
    logger.debug('Opening url : ' + str(hist_url))

    _resp = nsi.browser.open(hist_url)
    
    logger.debug('Response: ' + str(_resp))
    logger.info('Parsing table for submission history')

    sub_table = nsi.browser.get_current_page().find('table', class_='dataTable')
    header = []
    data = []
    for th in sub_table.find('thead').find('tr').find_all('th'):
        header.append(th.text.strip())
    header = header[:-1]
    
    logger.debug('Headers = ' + str(header))
    
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
    
    logger.debug('Table body parsed = ' + str(data))
    logger.info('Printing table via tabulate()')
    print(tabulate(data, headers=header, tablefmt='pretty'))
    logger.info('Exiting print submission history')


def login():
    """
    Logs in the user with username and password if already not logged in.
    Then checks if any other IP is logged in with the same username, and
    logs them out.
    """
    logger.info('Inside login')
    if not is_logged_in():
        logger.info('User not logged in')
        _frm = nsi.browser.select_form('form[id="new-login-form"]')
        nsi.browser['name'] = nsi.username
        nsi.browser['pass'] = nsi.password
        logger.info('Form credentials filled')
        # logger.debug(str(_frm.print_summary()))
        _resp = nsi.browser.submit_selected()
        logger.debug('Submit response: ' + str(_resp))
        _resp = nsi.browser.get_current_page().find(string = re.compile('Sorry'))
        logger.debug('Login failed check response: ' + str(_resp))
        if _resp is not None:
            print('Username or Password incorrect. Please use --config option to reset username and password')
            logger.info('Login failed')
            raise Exception("Login failed")

    check_session_limit()
    return True


def logout():
    """
    Logout the user if alredy logged in
    """
    logger.info('Inside logout()')
    if is_logged_in():
        _resp = nsi.browser.open(base_url + '/logout')
        logger.debug('Logout response: ' + str(_resp))
    logger.info('Exiting logout()')


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
    logger.info('Inside prepare browser')
    logger.debug('Checking browser objet: ' + str(nsi.browser))

    if nsi.browser == None:
        nsi.browser = ms.StatefulBrowser(session=session) if session != None else ms.StatefulBrowser()
    nsi.browser.set_user_agent(user_agent)
    logger.info('Opening session limit url')
    nsi.init_status = nsi.browser.open(session_limit_url)
    logger.debug('Response _resp = ' + str(nsi.init_status))
    while nsi.init_status.status_code not in [200, 403]:
        logger.info('Retrying..')
        sleep(0.5)
        nsi.init_status = nsi.browser.open(session_limit_url)
        logger.debug('Response _resp = ' + str(nsi.init_status))

    logger.info('Exiting prepare browser')


def persist():
    """
    Saves the browser session to a local file in home directory for later use.
    """

    if nsi.browser:
        with open(os.path.join(home_dir, session_file), 'wb') as f:
            pickle.dump(nsi.browser.session, f)
        return True


def retrieve_session():
    """
    Loads the session object from the session file (if present)
    nsi.session is used to store the session object if presnet else NoneType
    """

    logger.info('Inside retrieve session')
    nsi.session = None

    logger.info('Checking for session file')
    if os.path.exists(os.path.join(home_dir, session_file)):
        logger.info('Reading from session file')
        with open(os.path.join(home_dir, session_file), 'rb') as f:
            nsi.session = pickle.load(f)

        return True
    logger.info('Session file not found')
    return False


def check_session_limit():
    """
    Checks if the same user is logged in with some other session in some other 
    browsers. It parses the form and checks for input-type=checkbox with text other
    than 'Your current Session', checks them and submits the form to log them out
    """
    logger.info('Inside check session limit')
    page = nsi.browser.get_current_page()
    inps = page.findAll(lambda inp: inp.name == 'input' and inp.attrs['type'] == 'checkbox' and inp.parent.find('b').text == '')
    logger.debug('Logout search result: ' + str(len(inps)))

    if len(inps) > 0:
        nsi.browser.select_form('form[id="session-limit-page"]')
        for c in page.findAll(lambda inp: inp.name == 'input' and inp.attrs['type'] == 'checkbox' and inp.parent.find('b').text == ''):
            nsi.browser[c.attrs['name']] = c.attrs['value']
        _resp = nsi.browser.submit_selected()
        logger.debug('Submit response: ' + str(_resp))
    logger.info('Exiting check session limit')


def list_active_contests():
    """
    Prints the active contests data in Tabular format. It visits the contest page and
    parses the table to extract contest details and stores them in a list and uses the
    tabulate library to print it in table format
    """
    logger.info('Inside list active contests')
    header = []
    contest_data = []
    
    logger.info('Opening contest url: ' + contest_url)
    _resp = nsi.browser.open(contest_url)
    logger.debug('Response _resp = ' + str(_resp))

    sleep(0.1)

    logger.info('Parsing the contest table')
    present = nsi.browser.get_current_page().find('table', class_='dataTable')
    ths = present.find_all('th')
    for th in ths:
        header.append(th.find('a').text.strip())
    
    logger.info('Headers parsed')
    logger.debug('Headers = ' + str(header))

    trs = present.find('tbody').find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        _data = []
        for td in tds:
            _data.append(td.text.strip())
        contest_data.append(_data)
    
    logger.info('Table body parsed')
    logger.debug('Table body: ' + str(contest_data))
    logger.info('Priting table via tabulate()')
    print(tabulate(contest_data, headers=header, tablefmt='pretty'))
    logger.info('Exiting list active contests')



def main():
    """
    Entry point for the program. And calls the init function for the initialization
    """
    logger.info('In main()')
    logger.info('Calling init()')

    try:
        init()
    except Exception:
        logger.exception(traceback.format_exc())
    finally:
        persist()
    
    logger.info('Finished executing init()')

    with open(log_file, 'a') as f:
        f.write('-' * 100)
        f.write('\n')

    
    pass

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc())
        pass
    finally:
        persist()

