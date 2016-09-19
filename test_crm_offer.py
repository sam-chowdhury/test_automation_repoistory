#!/usr/bin/python3
import sys
import time
import requests
# pylint: disable=import-error
import helpers as h
# import elements as e
import random
import itertools
import json
import pymysql
from jenkinsapi.jenkins import Jenkins
# from pprint import pprint

# Test a single offer
def testSingleOfferOrder(browser, offer_id):

    try:
        offer_name = h.getOfferNameFromID(offer_id)
    except:
        h.failOut(browser, 'Enter a valid offer id!')
    h.logTest('Test Description: Create order with offer ' + str(offer_name))

    # use offer name to build dictionary for this particular offer
    offer_dict = h.getOfferAttributes(offer_name)

    # if the offer is inactive then exit the test
    h.evaluateOfferResitrictions(offer_dict)

    # if user isn't logged in already log them in
    h.verifyCRMUserLoggedIn(browser)

    # go tot the new order page
    h.navigateToCRMPage(browser)
    time.sleep(2)

    # create unique email
    order_email = h.createOfferEmail()

    # go to the correct brand
    h.goToOfferBrand(browser, offer_dict)

    # search for offer
    h.searchForOfferToCart(browser, offer_name)

    # get offer country
    h.getOfferCountry(browser, offer_name)

    # fill in the customer fields
    h.fillInCustomerFields(browser, offer_name, order_email)

    # add offer to cart
    h.addOfferToCart(browser, offer_name)

    # accept terms if its a subscription
    h.acceptOfferTerms(browser, offer_dict)

    # recap and place order
    h.recapAndSubmitOfferOrder(browser)

    # find the order
    h.queryOfferOrder(order_email)

    for log in h.test_log:
        print(log)



'''
\qa-automation\pytest>py.test -s --offer test_crm_subscription_offer.py
============================= test session starts =============================
platform win32 -- Python 3.4.3 -- py-1.4.29 -- pytest-2.7.2
rootdir: \qa-automation\pytest, inifile:
collected 1 items


========================== 1 passed in 5.38 seconds ===========================

\qa-automation\pytest>
'''
