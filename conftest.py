"""
Sets configuration values for PyTest, including definitions of command-line arguments
"""
import sys
import os

import smtplib
import pytest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set up the lib directory
if sys.platform == "win32":
    LIB_PATH = 'C:\\qa-automation\\lib\\'
else:
    LIB_PATH = '/usr/local/bin/qa-automation/lib/'
if os.path.isdir(LIB_PATH):
    sys.path.append(os.path.abspath(LIB_PATH))
else:
    sys.exit('Missing symlink. Please see '
             'http://confluence.nutraclick.com/display/QA/Getting+Started')

# https://pytest.org/latest/example/simple.html
@pytest.fixture()
#pylint: disable=bad-whitespace
def pytest_addoption(parser):
    """ Definitions of command-line arguments """
    # Test running meta
    parser.addoption("--all_combos", default=False, action="store_true", help="run all combinations")
    parser.addoption("--runslow",    default=False, action="store_true", help="run slow tests")

    # Test running specifics
    parser.addoption("--os",         default='Windows') # For BrowserStack. e.g.: Windows, win7, osx, mac, android
    parser.addoption("--browser",    default='chrome') #,     choices=['chrome', 'firefox', 'ie'])
    parser.addoption("--resolution", default='1024x768')
    parser.addoption("--env",        default='www',                      help="environment" ,
                     choices=['www', 'prod', 'sandbox', 'staging'])

    parser.addoption("--funnel_id",  default='852',                      help="funnel ID")
    parser.addoption("--step",       default='0',                        help="current_step_number (0=p1, 1=p2...)")

    parser.addoption("--bstack",     default=False, action="store_true", help="on BrowserStack (instead of local)")
    parser.addoption("--bTest",      default=False, action="store_true", help="test BrowserStack connection")

    # Lead info
    parser.addoption("--loc",        default='US',                       help="lead's country")
    parser.addoption("--fname",      default='Test')
    parser.addoption("--lname",      default='Auto')
    parser.addoption("--age",        default=30, type=int)
    parser.addoption("--gender",     default='Male')
    parser.addoption("--looking_for",default='All of the above')
    parser.addoption("--address",    default='123 Fake St.')
    parser.addoption("--city",       default='Boston')
    parser.addoption("--state",      default='MA')
    parser.addoption("--zip_code",   default='02108')
    parser.addoption("--phone",      default='555-555-5555')
    parser.addoption("--email",      default='asdf@nutraclick.com')
    # CC
    parser.addoption("--real",       default=False, action="store_true", help="Use a real card")
    parser.addoption("--cc_type",    default='Visa')
    parser.addoption("--cc_num",     default='1234123412341234')
    parser.addoption("--cc_month",   default='11')
    parser.addoption("--cc_year",    default='2022')
    parser.addoption("--cc_code",    default='123')

    # Choices
    parser.addoption("--upsell_qty",         default=0, type=int)
    parser.addoption("--upsells_to_add",     default=0, type=int)
    parser.addoption("--upsells_to_remove",  default=0, type=int)
    parser.addoption("--bill_upsell_1", action="store_true", default=False)
    parser.addoption("--bill_upsell_2", action="store_true", default=False)
    parser.addoption("--conf_upsell_1", action="store_true", default=False)
    parser.addoption("--conf_upsell_2", action="store_true", default=False)

    parser.addoption("--misc",       default=None,                         help="anything")

    parser.addoption("--offer_id",   default=1,    type=int,              help="Enter offer ID, e.g. '1' ")
    parser.addoption("--offer_name", default='Factor 2 - Trial - (18/30)', help="Enter offer name, e.g. 'Factor 2 - Trial - (18/30)' ")


# https://pytest.org/latest/example/simple.html
@pytest.yield_fixture(scope = 'session')
def browser(request):
    ''' Specify bstack, browser name, browser version, and resolution '''
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    using_bstack = request.config.getoption("--bstack")
    brows = request.config.getoption("--browser")
    op_sys = request.config.getoption("--os")
    res = request.config.getoption("--resolution")

    # BrowserStack
    if using_bstack:

        '''
            desired_cap = {'os': 'Windows', 'os_version': '7',  'browser': 'Chrome',
                'browser_version': '43.0', 'resolution': '2048x1536'}
            desired_cap = {'os': 'Windows', 'os_version': 'XP', 'browser': 'IE',
                'browser_version': '7.0', 'resolution': '800x600'}
            desired_cap = {'os': 'Windows', 'os_version': '8.1','browser': 'Firefox',
                'browser_version': '39.0', 'resolution': '1024x768'}

            desired_cap = {'os': 'OS X', 'os_version': 'Yosemite',     'browser': 'Safari',
                'browser_version': '8.0', 'resolution': '1024x768'}
            desired_cap = {'os': 'OS X', 'os_version': 'Snow Leopard', 'browser': 'Safari',
                'browser_version': '5.1', 'resolution': '1024x768'}

            desired_cap = {'platform': 'MAC', 'browserName': 'iPhone', 'device': 'iPhone 5'}
            desired_cap = {'platform': 'MAC', 'browserName': 'iPad',   'device': 'iPad Air'}

            desired_cap = {'platform': 'ANDROID', 'browserName': 'android', 'device': 'Samsung Galaxy S5'}
            desired_cap = {'platform': 'ANDROID', 'browserName': 'android', 'device': 'Google Nexus 5'}
            desired_cap = {'platform': 'ANDROID', 'browserName': 'android', 'device': 'Samsung Galaxy Tab 4 10.1'}

            800x600, 1024x768, 1280x800, 1280x1024, 1366x768, 1440x900,
            1680x1050, 1600x1200, 1920x1200, 1920x1080, 2048x1536
        '''

        def change_browser():
            if brows.lower().startswith('chrome'):
                desired_cap['browser'] = 'Chrome'
                desired_cap['browser_version'] = '43.0'
            elif brows.lower().startswith('ff'):
                desired_cap['browser'] = 'Firefox'
                desired_cap['browser_version'] = '38.0'


        if op_sys.lower().startswith('win'):
            desired_cap = {'os': 'Windows', 'os_version': '7',
                           'browser': 'Chrome', 'browser_version': '43.0', 'resolution': res}
            if op_sys.lower().endswith('xp'):
                desired_cap['os_version'] = 'XP'
            elif op_sys.lower().endswith('7'):
                desired_cap['os_version'] = '7'
            elif op_sys.lower().endswith('8'):
                desired_cap['os_version'] = '8'
            elif op_sys.lower().endswith('8.1'):
                desired_cap['os_version'] = '8.1'
            change_browser()

        elif op_sys.lower().startswith('os'):
            desired_cap = {'os': 'OS X', 'os_version': 'Yosemite',
                           'browser': 'Safari', 'browser_version': '8.0', 'resolution': res}
            if op_sys.lower().endswith('Yosemite'):
                desired_cap['os_version'] = 'Yosemite'
                desired_cap['browser_version'] = '5.1'
            change_browser()

        elif op_sys.lower().startswith('mac'):
            desired_cap = {'platform': 'MAC', 'browserName': 'iPhone', 'device': 'iPhone 5'}

        elif op_sys.lower().startswith('android'):
            desired_cap = {'platform': 'ANDROID', 'browserName': 'android', 'device': 'Samsung Galaxy S5'}

        desired_cap['browserstack.local'] = True

        driver = webdriver.Remote(
            desired_capabilities=desired_cap,
            command_executor='http://samchowdhury1:UMxDHgQgHq3LJM5U8Qpa@hub.browserstack.com:80/wd/hub'
        )

    # Chrome
    elif brows.lower() in ('chrome', 'gc'):
        path_to_chromedriver = LIB_PATH+'chromedriver'
        if sys.platform == "win32":
            path_to_chromedriver += '.exe'
        chrome_opts = Options()
        chrome_opts.add_argument("log-level=0")
        chrome_opts.add_argument("test-type")
        # https://code.google.com/p/chromedriver/issues/detail?id=799
        chrome_opts.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        # enable browser logging
        dc = DesiredCapabilities.CHROME
        dc['loggingPrefs'] = { 'browser':'ALL' }
        # pylint: disable=redefined-variable-type
        driver = webdriver.Chrome(executable_path=path_to_chromedriver,
                                  chrome_options=chrome_opts,
                                  desired_capabilities=dc
                                  # service_args=["--verbose", "--log-path=C:\\qc1.log"]
                                 )

    elif brows.lower() in ('firefox', 'ff'):
        driver = webdriver.Firefox()
    else:
        sys.exit('\nSory, I don\'t recognize that browser quite yet.\n')

    yield driver
    driver.quit()

@pytest.fixture
def env(request):
    ''' choices=['www', 'prod', 'sandbox', 'staging'] '''
    return request.config.getoption("--env")
@pytest.fixture
def funnel_id(request):
    ''' . '''
    return request.config.getoption("--funnel_id")
@pytest.fixture
def step(request):
    ''' current_step_number (0=p1, 1=p2...) '''
    return request.config.getoption("--step")
@pytest.fixture
def bstack(request):
    ''' on BrowserStack (instead of local) '''
    return request.config.getoption("--bstack")
@pytest.fixture
def bTest(request):
    ''' test BrowserStack connection '''
    return request.config.getoption("--bTest")

@pytest.fixture
def lead(request):
    ''' . '''
    return {
        'loc'     : request.config.getoption("--loc"),
        'age'     : request.config.getoption("--age"),
        'gender'  : request.config.getoption("--gender"),
        'fname'   : request.config.getoption("--fname"),
        'lname'   : request.config.getoption("--lname"),
        'address' : request.config.getoption("--address"),
        'city'    : request.config.getoption("--city"),
        'state'   : request.config.getoption("--state"),
        'zip_code': request.config.getoption("--zip_code"),
        'phone'   : request.config.getoption("--phone"),
        'email'   : request.config.getoption("--email"),
        'real'    : request.config.getoption("--real"),
        'cc_type' : request.config.getoption("--cc_type"),
        'cc_num'  : request.config.getoption("--cc_num"),
        'cc_month': request.config.getoption("--cc_month"),
        'cc_year' : request.config.getoption("--cc_year"),
        'cc_code' : request.config.getoption("--cc_code")
    }

@pytest.fixture
def loc(request):
    ''' . '''
    return request.config.getoption("--loc")
@pytest.fixture
def age(request):
    ''' . '''
    return request.config.getoption("--age")
@pytest.fixture
def gender(request):
    ''' . '''
    return request.config.getoption("--gender")
@pytest.fixture
def fname(request):
    ''' . '''
    return request.config.getoption("--fname")
@pytest.fixture
def lname(request):
    ''' . '''
    return request.config.getoption("--lname")
@pytest.fixture
def address(request):
    ''' . '''
    return request.config.getoption("--address")
@pytest.fixture
def city(request):
    ''' . '''
    return request.config.getoption("--city")
@pytest.fixture
def state(request):
    ''' . '''
    return request.config.getoption("--state")
@pytest.fixture
def zip_code(request):
    ''' . '''
    return request.config.getoption("--zip_code")
@pytest.fixture
def phone(request):
    ''' . '''
    return request.config.getoption("--phone")
@pytest.fixture
def email(request):
    ''' . '''
    return request.config.getoption("--email")
@pytest.fixture
def looking_for(request):
    ''' . '''
    return request.config.getoption("--looking_for")

@pytest.fixture
def real(request):
    ''' Use a real card '''
    return request.config.getoption("--real")
@pytest.fixture
def cc_type(request):
    ''' . '''
    return request.config.getoption("--cc_type")
@pytest.fixture
def cc_num(request):
    ''' . '''
    return request.config.getoption("--cc_num")
@pytest.fixture
def cc_month(request):
    ''' . '''
    return request.config.getoption("--cc_month")
@pytest.fixture
def cc_year(request):
    ''' . '''
    return request.config.getoption("--cc_year")
@pytest.fixture
def cc_code(request):
    ''' . '''
    return request.config.getoption("--cc_code")

@pytest.fixture
def upsell_qty(request):
    ''' . '''
    return request.config.getoption("--upsell_qty")
@pytest.fixture
def upsells_to_add(request):
    ''' . '''
    return request.config.getoption("--upsells_to_add")
@pytest.fixture
def upsells_to_remove(request):
    ''' . '''
    return request.config.getoption("--upsells_to_remove")
@pytest.fixture
def bill_upsell_1(request):
    ''' . '''
    return request.config.getoption("--bill_upsell_1")
@pytest.fixture
def bill_upsell_2(request):
    ''' . '''
    return request.config.getoption("--bill_upsell_2")
@pytest.fixture
def conf_upsell_1(request):
    ''' . '''
    return request.config.getoption("--conf_upsell_1")
@pytest.fixture
def conf_upsell_2(request):
    ''' . '''
    return request.config.getoption("--conf_upsell_2")

@pytest.fixture
def misc(request):
    ''' . '''
    return request.config.getoption("--misc")

@pytest.fixture
def offer_id(request):
    ''' Enter offer ID, e.g. '10' '''
    return request.config.getoption("--offer_id")
@pytest.fixture
def offer_name(request):
    ''' Enter offer name, e.g. 'Factor 2 - Trial - (18/30)' '''
    return request.config.getoption("--offer_name")

# Examples
@pytest.fixture(scope="module")
def smtp(request):
    ''' . '''
    smtp_conn = smtplib.SMTP("merlinux.eu")
    def fin():
        print("teardown smtp")
        smtp_conn.close()
    request.addfinalizer(fin)
    return smtp_conn  # provide the fixture value

# https://pytest.org/latest/example/simple.html
def pytest_runtest_setup(item):
    if 'slow' in item.keywords and not item.config.getoption("--runslow"):
        pytest.skip("need --runslow option to run")

@pytest.fixture
def all_combos(request):
    ''' . '''
    return request.config.getoption("--all_combos")
@pytest.fixture
def runslow(request):
    ''' . '''
    return request.config.getoption("--runslow")
