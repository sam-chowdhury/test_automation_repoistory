'''
Doc summary
What does this test cover?
'''

###########
# IMPORTS #
###########
# Un-comment the ones you need

# import os
# import sys
# import time
# import random
# import re
# import json

# from pprint import pprint

# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# from selenium.common.exceptions import NoSuchElementException
# from selenium.common.exceptions import ElementNotVisibleException
# from selenium.common.exceptions import TimeoutException
# from selenium.common.exceptions import WebDriverException
# from selenium.common.exceptions import StaleElementReferenceException

# pylint: disable=import-error
import helpers as h

'''
    ##############
    # DECORATORS #
    ##############
    # Un-comment all that apply

    ## duration ##
    # @pytest.mark.slow
    # @pytest.mark.fast

    ## frequency ##
    # @pytest.mark.daily
    # @pytest.mark.weekly

    ## target category ##
    # @pytest.mark.funnel
    # @pytest.mark.zedo
    # @pytest.mark.crm

    ## brand ##
    # @pytest.mark.forcefactor
    # @pytest.mark.peaklife
    # @pytest.mark.stagesofbeauty
    # @pytest.mark.femmefactor
    # @pytest.mark.smartbiotics
    # @pytest.mark.healthexperts

    # # skip the given test function if eval(condition) results in a True value.  Evaluation happens within the module global context. Example: skipif('sys.platform == "win32"') skips the test if we are on the win32 platform. see http://pytest.org/latest/skipping.html
    # @pytest.mark.skipif(condition)
    # # mark the the test function as an expected failure if eval(condition) has a True value. Optionally specify a reason for better reporting and run=False if you don't even want to execute the test function. If only specific exception(s) are expected, you can list them in raises, and if the test fails in other ways, it will be reported as a true failure. See http://pytest.org/latest/skipping.html
    # @pytest.mark.xfail(condition, reason=None, run=True, raises=None, strict=False)
    # # call a test function multiple times passing in different arguments in turn. argvalues generally needs to be a list of values if argnames specifies only one name or a list of tuples of values if argnames specifies multiple names. Example: @parametrize('arg1', [1,2]) would lead to two calls of the decorated test function, one with arg1=1 and another with arg1=2.see http://pytest.org/latest/parametrize.html for more info and examples.
    # @pytest.mark.parametrize(argnames, argvalues)
    # # mark tests as needing all of the specified fixtures. see http://pytest.org/latest/fixture.html#usefixtures
    # @pytest.mark.usefixtures(fixturename1, fixturename2, ...)
    # # mark a hook implementation function such that the plugin machinery will try to call it first/as early as possible.
    # @pytest.mark.tryfirst
    # # mark a hook implementation function such that the plugin machinery will try to call it last/as late as possible.
    # @pytest.mark.trylast



    # Available fixtures:
    # browser, env, funnel_id, step, bstack, test,
    # lead, loc, age, gender, fname, lname, address, city, state, zip_code, phne, email, looking_for
    # real, cc_type, cc_num, cc_month, cc_year, cc_code
    # upsell_qty, upsells_to_add, upsells_to_remove, bill_upsell_!, bill_upsell_2, conf_upsell_1, conf_upsell_2,
    # misc, offer_id, offer_name
'''
def testName(browser, env, funnel_id, step):

    # Gather info
    f = h.getFunnelInfo(funnel_id)
    url = h.buildUrl(f['domain'], env, funnel_id, current_step_number=step)

    # Open the page!
    browser.get(url)

    # Test something
    assert 1 == 1
