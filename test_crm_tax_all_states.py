#!/usr/bin/python3
import sys
import time

from selenium.common.exceptions import WebDriverException

# pylint: disable=import-error
import helpers as h

'''
Ticket for New Tax Rules: TECH-19908
Automation Ticket: TECH-19975
'''

def testCRMTax(browser):

    # set up test cases
    state_zips = {
        'AL':'35801', 'AK':'99501', 'AZ':'85001', 'AR':'72201', 'CA':'90001', 'CO':'80201', 'CT':'06101',
        'DE':'19901', 'DC':'20001', 'FL':'33124', 'GA':'30101', 'HI':'96801', 'ID':'83254', 'IL':'60101',
        'IN':'46201', 'IA':'52801', 'KS':'67201', 'KY':'41701', 'LA':'70112', 'ME':'04032', 'MD':'21201',
        'MA':'02155', 'MI':'49036', 'MN':'55801', 'MS':'39530', 'MO':'63010', 'MT':'59044', 'NE':'68901',
        'NV':'89501', 'NH':'03217', 'NJ':'08201', 'NM':'87198', 'NY':'12201', 'NC':'28315', 'ND':'58282',
        'OH':'44301', 'OK':'74101', 'OR':'97201', 'PA':'19001', 'RI':'02840', 'SC':'29020', 'SD':'57101',
        'TN':'37201', 'TX':'79601', 'UT':'84321', 'VT':'05751', 'VA':'24517', 'WA':'98004', 'WV':'25813',
        'WI':'53201', 'WY':'82941'
    }




    # create unique email
    # order_email = h.createOfferEmail()

    # if offer is BR get another offer
    offer_name = h.getRandomSubscriptionOffer()

    def isValidName(name):
        # bad strings that break automation
        not_allowed = ['(BR)', '(CA)', '(AU)', '(GB)', 'QATEST', '(i)', 'Cross Sell', 'Peal' ]
        for item in not_allowed:
            if item in name:
                return False
        return True

    while not isValidName(offer_name):
        offer_name = h.getRandomStraightSaleOffer()

    # check if I am already logged into CRM
    h.verifyCRMUserLoggedIn(browser)

    # go to the new order page
    h.navigateToCRMPage(browser)
    time.sleep(2)

    # get offer attributes
    offer_dict = h.getOfferAttributes(offer_name)

    # # go to the correct brand
    h.goToOfferBrand(browser, offer_dict)

    # search
    h.searchForOfferToCart(browser, offer_name)

    # add offer to cart
    h.addOfferToCart(browser, offer_name)

    # if this is a subscription then accept the offers
    h.acceptOfferTerms(browser, offer_dict)
    time.sleep(1)

    # update with new zip
    for state, zip_code in state_zips.items():
        crm_zip = browser.find_element_by_id('postal-code')
        crm_zip.clear()
        crm_zip.send_keys(zip_code)

        fname_field = browser.find_element_by_id('first-name')
        try:
            fname_field.click()
        except WebDriverException as e:
            msg = 'Failed to click first-name because\n'
            msg += str(e)
            h.failOut(browser, msg)

        time.sleep(2)

        h.verifyCRMTax(browser, offer_name, state, offer_dict)

    # for log in h.test_log:
    #     print (log)
