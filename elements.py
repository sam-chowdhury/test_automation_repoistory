import sys

from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

import helpers as h

'''
pages: [
    {
        NAMES:VALUES
        elements: {
            buttons: [
                VALUES
            ]
        }
        inputs: {
            lead_responses: [
                {
                    NAMES:VALUES
                }
            ]
            misc: [
                {
                    NAMES:VALUES
                }
            ]
            billing_responses: {
                #: {
                    NAMES:VALUES
                }
                items: [
                    {
                        NAMES:VALUES
                    }
                ]
            }
        }
    }
]
'''

# FunnelPage has Elements
class WebElement(object):
    def __init__(self, name, id_, xpath=None): # The underscore avoids name collision
        self.name = name
        self.id = id_
        self.xpath = xpath

    def __repr__(self):
        return '%s(%r)' % (self.__class__, self.__dict__)

    # Set the element's "element" attribute
    def find(self, browser):
        # print('Looking for '+self.name)
        try:
            # print('Looking for id '+self.id)
            self.element = browser.find_element_by_id(self.id)
        except NoSuchElementException:
            try:
                # print('Looking for name '+self.name)
                self.element = browser.find_element_by_name(self.name)
            except NoSuchElementException:
                try:
                    # print('Looking for n[] '+self.name+"[]")
                    self.element = browser.find_element_by_name(self.name+"[]")
                    # print ('this')
                except NoSuchElementException:
                    # print('Is there an xpath?')
                    if self.xpath is not None:
                        # print('Yes there is. looking for xpath '+self.xpath)
                        try:
                            self.element = browser.find_element_by_xpath(self.xpath)
                        except NoSuchElementException:
                            h.failOut(browser, "Couldn't find xpath "+self.xpath)
                    else:
                        h.failOut(browser, "Couldn't find by name, and element does not have an xpath: "+self.name)

# Inputs are WebElements that might be fields or buttons.
class Input(WebElement):
    def __init__(self, name, id_, input_type='text', value='', mandatory=True, xpath=None):
        WebElement.__init__(self, name, id_, xpath)
        self.type = input_type
        self.value = value
        self.mandatory = mandatory
        self.xpath = xpath


# Fields are a specific kind of Input WebElement.
class Field(Input):
    def __init__(self, name, id_, field_type='text', value='', mandatory=True, xpath=None):
        Input.__init__(self, name, id_, field_type, value, mandatory, xpath)
        '''
            if mandatory:
                if bad_entries:
                    bad_entries.append('')
                else:
                    bad_entries = ['']
        '''
    # def findField(self, browser):
    #     WebElement.find(self, browser)

    # Assert its 'type' attribute
    def checkField(self):
        # print('Checking type of '+self.name)
        assert self.element.get_attribute('type') == self.type

    # Insert a value into the field
    def fillInField(self, val='x'):
        # print('Filling in '+self.name)
        if val == 'x':
            val = self.value
        # Don't try to interact with hidden elements
        if self.element.get_attribute('type') in ['hidden', 'checkbox']:
            print("Field "+self.name+" is either hidden or a checkbox. Ignoring.")
        else:
            # Some fields need to be cleared before typing into them.
            if self.name in ['lead_responses[first_name]', 'lead_responses[phone]',
                             'lead_responses[city]', 'lead_responses[zip_code]', 'lead_responses[cc_name]']:
                # print('Clearing '+self.name)
                self.clearField()

            # print(self.name+' = '+self.value)
            self.element.send_keys(val)

    # Reset a field to empty
    def clearField(self):
        # print('Clearing '+self.name)
        if self.name == 'cc_type':
            if self.element.get_attribute('type') in ['hidden', 'checkbox']:
                return True
        if self.type != "select-one":
            # print(self.type)
            # ...text is easy
            self.element.clear()
        else:
            # ...dropdowns are harder.
            # Locate the Select element
            element = Select(self.element)
            # Find the first option (e.g. "Please select")
            to_select = element.options[0].text
            # Select the first option
            element.select_by_visible_text(to_select)


# class Button(Input)

##########
# Fields #
##########

#                      name,                           id,            type,        default_input, optionals
# p1, p2 basic fields
first_name    = Field('lead_responses[first_name]',   'first-name',  'text',      'Test')
last_name     = Field('lead_responses[last_name]',    'last-name',   'text',      'Auto')
full_name     = Field('lead_responses[full_name]',    'full-name',   'text',      'Test Auto')
gender        = Field('lead_responses[gender]',       'gender',      'select-one','Male')
age           = Field('lead_responses[age]',          'age',         'select-one','30')
age.good_entries           = ['20', '30', '40', '50']
age.bad_entries            = ['a', '10', '9999']
email_address = Field('lead_responses[email_address]','email_address','email',    'asdf@nutraclick.com')
email_address.good_entries = ['asdf@nutraclick.com']
email_address.bad_entries  = ['asdf']
phone_number  = Field('lead_responses[phone_number]', 'phone_number','tel',       '5555555555')
phone_number.good_entries  = ['555-555-5555']
phone_number.bad_entries   = ['asdf']
address       = Field('lead_responses[address]',      'address',     'text',      '123 Fake St.')
address.good_entries       = ['123 Fake St.']
address.bad_entries        = ['']
address_2     = Field('lead_responses[address_2]',    'address_2',   'text',      '',           mandatory=False)
city          = Field('lead_responses[city]',         'city',        'text',      'Anytown')
city.good_entries          = ['Anytown']
city.bad_entries           = ['']
state         = Field('lead_responses[state]',        'state',       'select-one','MA')
state.good_entries         = ['MA']
state.bad_entries          = ['0']
zip_code      = Field('lead_responses[zip_code]',     'zip-code',    'tel',       '02108')
zip_code.good_entries      = ['12345', '123451234', '12345-1234', '12345 1234']
zip_code.bad_entries       = ['1234', '123456', '12345- 1234', '12345123', '1234512345']
country       = Field('lead_responses[country]',      'country',     'select-one','US',         mandatory=False)

# BR
street_number = Field('lead_responses[street_number]', None,         'tel',       '24')
address_2     = Field('lead_responses[address_2]',     None,         'text',      '401',        mandatory=False)
street_3      = Field('lead_responses[street_3]',      None,         'text',      'Downtown')

# Survey responses
sr_6          = Field('survey_responses[6]',    'survey-question-height',       'select-one', '5')
sr_7          = Field('survey_responses[7]',    'survey-question-height_inches','select-one', '9')
sr_10         = Field('survey_responses[10]',   'survey-question-weight',       'tel',        '150')
sr_11         = Field('survey_responses[11]',   'survey-question-goal-weight',  'tel',        '200')
sr_cp         = Field(None, 'survey-question-what_is_your_current_physique_',               'select-one', 'Lean, Thin')
sr_gp         = Field(None, 'survey-question-what_type_of_physique_do_you_want_to_achieve_','select-one', 'Fit, Lean')

commit        = Field('commit',                       'yes-checkbox','checkbox',  'unchecked',  mandatory=False)

# p3 checkboxes
trial         = Field('billing_responses[items][1]',   None,        'checkbox', 'checked') # Trial
ups_1         = Field('billing_responses[items][2]',   None,        'checkbox', 'unchecked', mandatory=False) # Upsell 1
ups_2         = Field('billing_responses[items][3]',   None,        'checkbox', 'unchecked', mandatory=False) # Upsell 2

# p3 entry fields
cc_name       = Field('billing_responses[cc_name]',   'cc-name',     'text',      'Testcc Autocc')
cc_type       = Field('billing_responses[cc_type]',   'cc-type',     'select-one','Visa')
cc_number     = Field('billing_responses[cc_number]', 'cc-number',   'tel',       '1234123412341234')
cc_month      = Field('billing_responses[cc_month]',  'cc-month',    'select-one','11')
cc_year       = Field('billing_responses[cc_year]',   'cc-year',     'select-one','2020')
cc_code       = Field('billing_responses[cc_code]',   'cc-code',     'tel',       '123')

# List of fields
fields = [
    first_name, last_name, full_name, gender, age, email_address, phone_number, address, address_2, city, state,
    zip_code, country, street_number, address_2, street_3, sr_6, sr_7, sr_10, sr_11, sr_cp, sr_gp, commit, trial,
    ups_1, ups_2, cc_name, cc_type, cc_number, cc_month, cc_year, cc_code
]


####################
# Non-field inputs #
####################

#                        name,  id,                  type
p1_submit_btn    = Input(None,  None,               'submit') # , class='lander-form-qualify-btn'
p2_submit_btn    = Input(None, 'form-submit-btn',   'submit')
p3_submit_btn    = Input(None, 'form-rush-btn',     'submit')
p4_submit_btn    = Input(None, 'upsell-submit-btn', 'submit')
p4_no_thanks_btn = Input(None, 'upsell-submit-btn', 'submit') # , class='no_thanks'

# List of non-field inputs
inputs = [
    p1_submit_btn, p2_submit_btn, p3_submit_btn, p4_submit_btn, p4_no_thanks_btn
]


#################################
# Non-field, non-input elements #
#################################

#                                 name,                 id
# All pages
txtkn               = WebElement('_txtkn',              None)
current_step_number = WebElement('current_step_number', None)
foot_home           = WebElement(None,                 'foot-home')
foot_terms          = WebElement(None,                 'foot-terms') # , class='legal-link'
foot_refund         = WebElement(None,                 'foot-refund') # , class='legal-link'
foot_privacy        = WebElement(None,                 'foot-privacy') # , class='legal-link'
foot_copyright      = WebElement(None,                 'foot-copyright') # , class='legal-link'
foot_contact        = WebElement(None,                 'foot-contact') # , class='legal-link'
USI_overlayDiv      = WebElement(None,                 'USI_overlayDiv')
flashChatDiv        = WebElement(None,                 'flashChatDiv')
tracking_debug_toggle          = WebElement(None,      'tracking_debug_toggle')
tracking_debug_container       = WebElement(None,      'tracking_debug_container')
tracking_debug_inner_container = WebElement(None,      'tracking_debug_inner_container')
tracking_debug_inner_container = WebElement(None,      'tracking_debug_inner_container')
funnel_debug_data_dump         = WebElement(None,      'funnel_debug_data_dump')
all_pages_elements = [
    txtkn, current_step_number,
    foot_home, foot_terms, foot_refund, foot_privacy, foot_copyright, foot_contact,
    USI_overlayDiv, flashChatDiv,
    tracking_debug_toggle, tracking_debug_container,
    tracking_debug_inner_container, tracking_debug_inner_container,
    funnel_debug_data_dump
]

# p1
p1_form       = WebElement('form', 'form')
verisign      = WebElement(None,   'verisign')
mcafee        = WebElement(None,   'mcafee')
a_spot_list_1 = WebElement(None,   'a-spot-list-1')
a_spot_list_2 = WebElement(None,   'a-spot-list-2')
a_spot_list_3 = WebElement(None,   'a-spot-list-3')
a_spot_list_4 = WebElement(None,   'a-spot-list-4')
a_spot_list_5 = WebElement(None,   'a-spot-list-5')
a_spot_list_6 = WebElement(None,   'a-spot-list-6')
a_spot_list_7 = WebElement(None,   'a-spot-list-7')
a_spot_list_8 = WebElement(None,   'a-spot-list-8')
bspot         = WebElement(None,   'bspot')
p1_elements = [
    p1_form, verisign, mcafee,
    a_spot_list_1, a_spot_list_2, a_spot_list_3, a_spot_list_4,
    a_spot_list_5, a_spot_list_6, a_spot_list_7, a_spot_list_8,
    bspot
]

# p2
p2_form       = WebElement('form', 'form')
questions     = WebElement(None,   'questions') # section
choice_1      = WebElement(None,   'choice-1') # input
choice_box_1  = WebElement(None,   'choice-box-1') #label
choice_2      = WebElement(None,   'choice-2')
choice_box_2  = WebElement(None,   'choice-box-2')
choice_3      = WebElement(None,   'choice-3')
choice_box_3  = WebElement(None,   'choice-box-3')
choice_4      = WebElement(None,   'choice-4')
choice_box_4  = WebElement(None,   'choice-box-4')
main_form     = WebElement(None,   'main-form') # section
p2_elements = [
    p2_form, questions,
    choice_1, choice_box_1, choice_2, choice_box_2, choice_3, choice_box_3, choice_4, choice_box_4, main_form
]

# p3
p3_form               = WebElement('form',            'form')
lead_token_hash       = WebElement('lead_token_hash', 'lead_token_hash')
lead_id               = WebElement(None,              'lead_id')
main_billing          = WebElement(None,              'main-billing')
accepted_cards_images = WebElement(None,              'accepted-cards-images')
cvv_cvc_link          = WebElement(None,              'cvv-cvc-link')
row_1                 = WebElement(None,              'row-1')
row_2                 = WebElement(None,              'row-2')
fmf_book_price        = WebElement(None,              'fmf-book_price')
verisign              = WebElement(None,              'verisign')
mcafee                = WebElement(None,              'mcafee')
subtotal              = WebElement(None,              'subtotal')
shipping              = WebElement(None,              'shipping')
tax                   = WebElement(None,              'tax')
total                 = WebElement(None,              'total')
terms                 = WebElement(None,              'terms')
p3_elements = [
    p3_form, lead_token_hash, lead_id, main_billing, accepted_cards_images, cvv_cvc_link, row_1, row_2,
    fmf_book_price, verisign, mcafee, subtotal, shipping, tax, total, terms
]

# p4
upsell_container_1 = WebElement(None, 'upsell-container-1') # div (through 'upsell-container-x')
upsell_container_2 = WebElement(None, 'upsell-container-2') # div (through 'upsell-container-x')
add_to_order       = WebElement(None, 'add-to-order') #div
cvv_cvc_link       = WebElement(None, 'cvv-cvc-link')
terms              = WebElement(None, 'terms')
p4_elements = [
    upsell_container_1, upsell_container_2, add_to_order, cvv_cvc_link, terms
]


#################
# Retail Fields #
#################

#                           name,            id,                type,            default_input, optionals
retail_first_name   = Field('first_name',   'first-name',       'text',          'Test')
retail_last_name    = Field('last_name',    'last-name',        'text',          'Auto')
retail_zip_code     = Field('zip_code',     'zip-code',         'tel',           '02108')
retail_phone        = Field('phone_number', 'phone',            'tel',           '123-456-7878')
retail_email        = Field('email_address','email',            'text',          'qaautomation@nutraclick.com')
retail_cc_name      = Field('cc_name',      'cc-name',          'text',          'Testcc Autocc')
retail_cc_type      = Field('cc_type',      'cc-type',          'select-one',    'Visa')
retail_cc_number    = Field('cc_number',    'cc-number',        'tel',           '1234123412341234')
retail_cc_month     = Field('cc_month',     'cc-month',         'select-one',    '11')
retail_cc_year      = Field('cc_year',      'cc-year',          'select-one',    '2020')
retail_cc_code      = Field('cc_code',      'cc-code',          'tel',           '123')
retail_qty          = Field('add_qty',      'add_qty'           'select-one')

retail_fields = [
    retail_first_name, retail_last_name, city, state, address, retail_zip_code,
    retail_phone, retail_cc_type, retail_cc_name, retail_cc_number,
    retail_cc_month, retail_cc_year, retail_cc_code, retail_email
]
for retail_field in retail_fields:
    fields.append(retail_field)


###############
# CRM Fields ##
###############


# Log In Fields
#                     name,        id,              type,         default
crm_user_name = Field('user_name', 'user_name',     'text',       'ha-qa')
crm_password  = Field('password',  'password',      'text',       'test1test')


# Customer Information Fields
#                     name,        id,              type,         default_input,           optionals
crm_zip       = Field(None,        'postal-code',   'text',       '02108-0000')
crm_phone     = Field(None,        'phone-number',  'tel',        '1234567878')
crm_country   = Field(None,        'country',       'select-one', 'United States')
crm_address_1 = Field(None,        'address-1',     'text',       '24 School Street')
crm_address_2 = Field(None,        'address-2',     'text',       '4th Floor',             mandatory=False)
crm_email     = Field(None,        'email-address', 'text',       'qaautomation@nutraclick.com', mandatory=False)

# Customer Payment Information Fields
#                     name,        id,              type,         default_input,           optionals
crm_cc_type   = Field(None,        None,            'select-one', 'Visa')
crm_cc_card   = Field(None,        'card-number',   'text',       '41111111111111111')
crm_cc_exp    = Field(None,        'expiration',    'text',       '0120')
crm_cc_cvv    = Field(None,        'cvv',           'text',       '123')
crm_campaign  = Field(None,        'campaign',      'select-one', 'Declines')
crm_cpf       = Field(None,        'cpf',           'text',       '11111111111')

# CRM Offer Panel fields
crm_search    = Field(None,              'search',           None)

crm_fields = [
    crm_user_name,crm_password, crm_zip, crm_phone, crm_country, crm_address_1, crm_address_2, crm_email,
    crm_cc_type, crm_cc_card, crm_cc_exp, crm_cc_cvv, crm_campaign, crm_cpf
]
for crm_field in crm_fields:
    fields.append(crm_field)

crm_customer_info_fields = [
    first_name, last_name, crm_zip, crm_address_1, crm_address_2,
    crm_phone, crm_cc_type, crm_cc_card, crm_cc_exp, crm_cc_cvv,
    crm_email, crm_campaign
]

#################
# CRM Elements ##
#################

# CRM Brand Navigation
crm_brand_navigation = ('FM', 'FF', 'PL', 'PS', 'SB')


# CRM Offer Selection Pane
#                                name,          id,     optionals
crm_add_cart        = WebElement(None,          None,   xpath='//*[@id="offer-list"]/table/tbody/tr[2]/td[5]/button]')
crm_accept_terms    = WebElement(None,          None,   xpath='//*[@id="modal-add-offer"]/div[3]/div/button[2]')


# CRM Price Section Elements
#                                name,          id,     xpath
crm_order_recap     = WebElement(None,          None,   xpath='//*[@id="place-order"]/button')
crm_place_order     = WebElement(None,          None,   xpath='//*[@id="modal-order-recap"]/div[3]/div[2]/button[2]')
crm_process_date    = WebElement(None,          'process-date')
crm_order_recap     = WebElement('Order Recap', 'place-order')
crm_place_order     = WebElement('Place Order', 'process-date')
crm_subtotal        = WebElement(None,          None,   xpath='//*[@id="summary-totals"]/div[2]/div[2]')
crm_shipping        = WebElement(None,          None,   xpath='//*[@id="summary-totals"]/div[3]/div[2]')
crm_tax             = WebElement(None,          None,   xpath='//*[@id="summary-totals"]/div[4]/div[3]')
crm_total           = WebElement(None,          None,   xpath='//*[@id="summary-totals"]/div[5]/div[3]')

crm_elements = [
    crm_add_cart, crm_accept_terms, crm_process_date, crm_order_recap,
    crm_place_order, crm_subtotal, crm_shipping, crm_tax, crm_total
]

crm_recap_values = [
    crm_subtotal, crm_shipping, crm_tax, crm_total
]



# List of lists of all non-field, non-input elements
elements_lists = [
    all_pages_elements, p1_elements, p2_elements, p3_elements, p4_elements, crm_elements
]

# List of all non-field, non-input elements
elements = []
elements.append(elements_list[:] for elements_list in elements_lists)

############
# Combined #
############
# List of lists of ALL elements
all_elements_lists = [
    fields, inputs, elements
]
# List of ALL elements
all_elements = []
all_elements.append(all_elements_list[:] for all_elements_list in elements_lists)



if __name__ == '__main__':
    # test_element = Element('element_name', 'element_id', 'element_type', 'element_value', False)
    # print(str(test_element))

    # test_input = Input('input_name', 'input_id', 'input_type', 'input_value', False)
    # print(str(test_input))

    # test_field = Field('field_name.name', 'field_id', 'field_type', 'field_value', False)
    # print()
    # for x in sorted(test_field.__dict__):
    #     print(x,": ",test_field.__dict__[x])
    # print()

    print()
    # for x in sorted(zip_field.__dict__):
    #     print(x,": ",zip_field.__dict__[x])
    # for x in sorted(elements):
        # print(x,": ",elements[x])
    print(all_elements)
    print()
