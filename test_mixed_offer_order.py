#!/usr/bin/python3
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException

# pylint: disable=import-error
import helpers as h
import elements as e


def testCreateMixedOrder(browser):

    # get random subscription offer
    offer_name = h.getRandomSubscriptionOffer()

    # use offer name to build dictionary for this particular offer
    offer_dict = h.getOfferAttributes(offer_name)

    # if the offer is inactive then exit the test
    h.evaluateOfferResitrictions(offer_dict)

    # if user isn't logged in already log them in
    h.verifyCRMUserLoggedIn(browser)

    # go to the new order page
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

    # clear the search field
    e.crm_search.clearField()
    time.sleep(10)

    # typing in straight will bring up all straight sale
    e.crm_search.fillInField(val='straight')

    # we just want the first one to satisfy this test
    xp = '//*[@id="offer-list"]/table/tbody/tr[2]/td[5]/button'
    try:
        btn = browser.find_element_by_xpath(xp)
    except NoSuchElementException:
        h.failOut(browser, 'Failed to find button at xpath '+xp)
    btn.click()

    # recap and place order
    h.recapAndSubmitOfferOrder(browser)

    # get the order number
    order_id = h.queryOfferOrder(order_email)
    time.sleep(2)

    # verify number of offers in the order
    offers_count = h.getOffersInOrder(order_id)
    assert len(offers_count) == 2

    for log in h.test_log:
        print(log)


