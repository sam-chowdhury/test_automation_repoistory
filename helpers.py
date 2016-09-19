import sys
import time
import os
import smtplib
import random
from pprint import pprint
import json
import jsonschema
import requests

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import TimeoutException

# pylint: disable=import-error
import elements
import urls

# Send a query to the dev db (or prod if specified)
# Returns a dict of one row's fields and values
def queryDB(query, host='prod', db='hydra'):

    import pymysql

    if host == 'dev':
        host_name = 'mysql.dev.hungryfi.sh'
        user = 'db_access_dev'
        passwd = 'ChocolatierEast80'
    elif (host == 'prod') or (host == 'www'):
        host_name = 'slave.mysql.dfw.rsp.hungryfi.sh'  # '192.168.100.132'
        user = 'qa_access'
        passwd = 'LeatherTailor71'
    elif (host == 'stg') or (host == 'staging'):
        host_name = '192.168.100.94'
        user = 'qa_access'
        passwd = 'LeatherTailor71'
    else:
        print("Error: Usage = queryDB(query, host='dev'|'prod', db=____(e.g. hfm_core)")

    conn = pymysql.connect(host_name, user, passwd, db)
    cursor = conn.cursor()

    # Querify!
    # print("Executing query:", query)
    # print("on database:", db)
    # print("on server:", host)
    cursor.execute(query)

    # Grab the first row
    f_one = cursor.fetchone()

    # Get the list of columns
    fields = []
    for i in range(len(cursor.description)):
        fields.append(cursor.description[i][0])

    # For each column, store its value
    db_vals = {}
    if f_one is not None:
        for i in range(len(fields)):
            db_vals[fields[i]] = f_one[i]
    else:
        pass
        # print("Zero rows returned for", query)

    cursor.close()
    conn.close()
    return db_vals

# Send a query to the prod db (or dev if specified)
# Returns a dict of all rows' fields and values
def queryDBMultiple(query, db='prod'):

    import pymysql

    if (db == 'dev'):
        host='mysql.dev.hungryfi.sh'
        user='db_access_dev'
        passwd='ChocolatierEast80'
        db='hfm_core'
    elif (db == 'devffinder'):
        host='mysql.dev.hungryfi.sh'
        user='db_access_dev'
        passwd='ChocolatierEast80'
        db='ffinder'
    elif (db == 'prod'):
        host= '192.168.100.132' # 'slave.mysql.dfw.rsp.hungryfi.sh'
        user='qa_access'
        passwd='LeatherTailor71'
        db='ffinder'
    elif (db == 'prodhydra'):
        host= '192.168.100.132' # 'slave.mysql.dfw.rsp.hungryfi.sh'
        user='qa_access'
        passwd='LeatherTailor71'
        db='hydra'
    else:
        print("Error: Usage = queryDBMultiple(query, db='dev'|'devffinder'|'prod')")

    conn = pymysql.connect(host, user, passwd, db)
    cur = conn.cursor()

    # Querify!
    # print("Executing query:", query)
    # print("on database:", db)
    # print("on server:", host)
    cur.execute(query)

    # Grab the first row
    f_one = cur.fetchall()

    # print(f_one)
    # Get the list of columns
    fields = []
    for i in range(len(cur.description)):
        fields.append(cur.description[i][0])

    # For each column, store its value
    db_vals = {}
    if f_one:
        for i in range(len(fields)):
            db_vals[fields[i]] = f_one[i]
    else:
        pass
        # print("Zero rows returned for", query)

    cur.close()
    conn.close()
    return f_one


# Use queryDB, but allow some time for a response.
# host=self.db_host
def queryWait(self, query, seconds=10):
    try:
        return WebDriverWait(self.driver, seconds).until(
            lambda q: queryDB(query, host=self.db_host),
            "Timed out while waiting for query: "+query
            )
    except TimeoutException:
        seconds_behind = str(queryDB("show slave status")['Seconds_Behind_Master'])
        if seconds_behind is not None:
            print("Slave is")
            print(seconds_behind+" seconds behind Master")
            print()
        else:
            print("Slave is having ISSUES.")
        self.db_host = 'prod'
        return WebDriverWait(self.driver, 2).until(
            lambda q: queryDB(query, host=self.db_host),
            "Timed out while waiting for query: "+query
            )

# Return available product families
def getProductFamily():
    product_families = []

    q = "SELECT product_family_id AS id,"
    q+= " product_family_name AS name"
    q+= " FROM ffinder.product_families"

    q_res = queryDBMultiple(q)

    return q_res


# check if HTTPS is in URL
def siteIsSecure(browser, site):
    browser.get('http://' + site)
    return browser.current_url.startswith('https')

# Send an email from NutraClickQA@gmail.com to toaddr
# Different from the function in FunnelFunctions
def sendEmail(toaddr, subject, message):
    fromaddr = 'NutraClickQA@gmail.com'
    message['Subject'] = subject

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    username = 'NutraClickQA'
    password = 'NutraClickQA1'
    server.login(username,password)
    server.sendmail(fromaddr, toaddr, message.as_string())
    server.quit()

# Take a screenshot and put it in a folder with thte rest
# 'C:\screenshots\'' or '/usr/local/src/test_cases/Python/screenshots/'
# Filename is: text+'.png'
def takeScreenshot(browser, file):

    browser.maximize_window()

    # Pick a folder based on my OS
    if sys.platform == "win32":
        folder = 'C:\screenshots\\'
    elif (sys.platform == "linux2") or (sys.platform == "linux"):
        folder = '/home/automation/screenshots/'
    else:
        print("Error in takeScreenshot. Unexpected sys.platform value: "+sys.platform)

    # If the folder doesn't exist yet, create it.
    if not os.path.exists(folder):
        os.makedirs(folder)
        # Fail out if I couldn't make the folder
        if not os.path.exists(folder):
            failOut(browser, "Folder creation fail!")

    filename = txt_filename = None

    # e.g. '/home/automation/screenshots/file.png'
    # filename = folder+file+'.png'
    filename = folder+'screenshot'+'.png'

    # Take the shot!
    print("Saving screenshot to "+filename)
    try:
        browser.get_screenshot_as_file(filename)
    except (UnexpectedAlertPresentException, WebDriverException) as e:
        print("Error getting screenshot. Msg = \n"+str(e))

    # e.g. '/home/automation/screenshots/file.html'
    # txt_filename = filename[:-3]+"html"
    txt_filename = folder+'page_source'+'.html'
    print("Saving page source to "+txt_filename)
    txt_file = open(txt_filename, "w")
    src = browser.page_source.encode('utf-8').decode('utf-8')
    for line in src:
        try:
            txt_file.write(line)
        except: # What Exception?
            pass
    txt_file.close()

    if filename is not None and txt_filename is not None:
        return [filename, txt_filename]

# Call this, with a message, when something has failed.
# Quit the driver, write the msg to a file, and sys.exit with the msg
def failOut(browser=None, msg=None):

    print("\nTest FAILED!")

    if msg is None:
        msg = "FAILED. failOut() was called without a message."

    if browser is not None:
        # Get screenshot and page source
        ss, ss_txt = takeScreenshot(browser, 'failOutFile')

        # Close the browser
        try:
            browser.quit()
        except AttributeError:
            print("Not quitting the browser in failOut(), because there isn't a browser to quit.")

    # Get the current year, week, and time
    import datetime
    utcnow = datetime.datetime.utcnow()
    yr = str(utcnow.year)
    wk = str(utcnow.isocalendar()[1])
    cur_time = time.ctime()

    # Open log file, write to file, close file
    txt_file = open('error_log_'+yr+'_'+wk+'.csv', 'a')
    txt_file.write('\n'+cur_time+','+','+','+msg)
    txt_file.close()

    print('\n\nfailOut: '+msg+'\n\n')

    sys.exit(msg)

# Not implemented
def updateLeadInfo():
    pass

# Update the lead's state and zip, based on country
# returns lead
def updateLocInfo(lead):
    if lead['country'] == 'US':
        pass
    elif lead['country'] == 'CA':
        lead['state'] = 'QC'
        lead['zip'] = 'H0H 0H0'
    elif lead['country'] == 'AU':
        lead['state'] = 'CHR'
        lead['zip'] = '6798'
        lead['phone'] = '055-555-5555'
    elif lead['country'] == 'GB':
        lead['state'] = 'Caernarfonshire and Merionethshire'
        lead['zip'] = 'EC1A 1BB'
        lead['phone'] = '01222555555'
    elif lead['country'] == 'BR':
        lead['state'] = 'Amazonas'
        lead['zip'] = '04559-001'
    else:
        sys.exit("'Country' parameter '"+str(lead['country'])+"' not understood by updateLocInfo().")
    return lead

# Not implemented
def updateCardInfo(lead):
    if lead['real']:
        print("\n\nSorry, can't use a real card quite yet.\n\n")
        # lead['cc_num']  =
        # lead['cc_month']=
        # lead['cc_year'] =
        # lead['cc_code'] =
    return lead



# For the quiet output option
def pleasePrint(msg):
    # For something to print always, i.e. with -QUIET   on, use print()
    # For something to print often,  i.e. with NEITHER  on, use pleasePrint()
    # For something to print rarely, i.e. with -VERBOSE on, use vPrint()
    # if (vals['verbose']) or (not vals['quiet']):
    print(msg)

# For the verbose output option
def vPrint(msg):
    # For something to print always, i.e. with -QUIET   on, use print()
    # For something to print often,  i.e. with NEITHER  on, use pleasePrint()
    # For something to print rarely, i.e. with -VERBOSE on, use vPrint()
    # if vals['verbose']:
    print(msg)


# Given an ID, hide it by setting style.display to 'none'
def hideElement(browser, _id):
    try:
        browser.execute_script("document.getElementById('" + _id + "').style.display = 'none';")
    except NoSuchElementException:
        browser.execute_script("document.getElementByName('" + _id + "').style.display = 'none';")

# Given an ID, unhide it by resetting style to ''
def unhideElement(browser, _id):
    try:
        browser.execute_script("document.getElementById('" + _id + "').style='';")
    except NoSuchElementException:
        browser.execute_script("document.getElementByName('" + _id + "').style='';")


# Used to validate webservice responses against expected scheme
def validateWebServiceResponse(url, scheme):
    '''
    Used to validate webservice responses against expected scheme
    '''
    from jsonschema import validate

    # make a request through a url
    req = requests.get(url)

    # load the text of the response
    d = json.loads(req.text)

    # validate against a scheme
    try:
        validate(d, scheme)
        logTest('Passed: Response validated against scheme!')
    except jsonschema.exceptions.ValidationError as ve:
        logTest('Failed! Response does not match scheme!' + str(ve))

    # check the response
    if d["status"] == "error":
        logTest('Failed: Received error response using url!')
    else:
        logTest('Passed: Received success response using url!')

    # print the response code
    print ('\nReponse code: \n' + json.dumps(d, indent=4, sort_keys = True) +
        '\nEnd of response code above\n')

    return d


############
## Funnel ##
############

# Query the DB to get a list of all funnels that should be tested
def getActiveFunnels():

    # @TODO: Add list parameter "query_lines". E.g.:
    # [
    # "  AND NOT (funnel_type_id = 7 AND (product_id = 186 OR product_id = 100))",
    # "  AND funnel_id NOT IN (1485, 1578)"
    # ]

    q  = "SELECT product_id, funnel_id"
    q += " FROM hydra.funnels"
    # 'Active' status
    q += " WHERE state=3"
    # No PSP or Homepage or Click to Call, but yes Mobile
    q += "  AND (funnel_type_id < 4 or funnel_type_id = 7)"
    # Never touch anything below this
    q += "  AND funnel_id >= 385"
    # # TECH-19513
    # if test_mode:
    #     q += "  AND funnel_id > 1038"
    # else:
    #     q += "  AND funnel_id < 1038"
    q += " ORDER BY product_id"
    # q += " JOIN ffinder.products p"
    # q += " AND f.product_id = p.product_id"
    # q += " AND p.country = 'US'"
    db_vals = queryDBMultiple(q, 'prod')

    active_funnels = {}

    # Add the funnels from the above query
    for pid_funnel in db_vals:

        # Ignore the Fury mobile funnels
        # if pid_funnel[0] not in [100, 181]:

        if pid_funnel[0] in active_funnels:
            # Product ID already in dict
            active_funnels[pid_funnel[0]].append(pid_funnel[1])
        else:
            # New product ID
            active_funnels[pid_funnel[0]] = [pid_funnel[1]]

    return active_funnels

# Creates "f" dict, with many details about a funnel
def getFunnelInfo(funnel_id):
    '''
        age_drop
        age_range
        age_type
        brand_abbr
        brand_name
        cc_name
        cc_type
        country
        delimiter
        domain
        email
        fname
        funnel_id
        gender
        htwtphysique
        p1_question

        p3_upsell1_name
        p3_upsell1_price
        p3_upsell2_name
        p3_upsell2_price
        p3_upsells

        p4_upsell1_price
        p4_upsell2_price
        p4_upsell3_price
        p4_upsell4_price
        p4_upsell5_price
        p4_upsell6_price
        p4_upsell7_price
        p4_upsell8_price
        p4_upsell_price_array

        payment_gateway
        pid
        prod_abbr
        prod_name
        shipping
        yes-checkbox
        zip_code

        d
    '''
    funnel_id = str(funnel_id)
    f = {'funnel_id': funnel_id,
         'email': 'nutraclickqa+'+funnel_id+'.'+str(time.time())+'@gmail.com'}

    req = requests.get('http://kermit.nutraclick.com/ws/hydra/get-funnel-info/?funnel_id='+funnel_id)
    d = json.loads(req.text)
    f['d'] = d

    funnel_type_ids = ['', 'Full Lander', 'Discounted Shipping Lander', 'One Step',
                       'Presale Article', 'Homepage Variation', 'Click to Call', 'Mobile Lander']
    page_type_ids =['', 'Lead Generation', 'Qualify', 'Billing', 'Upsell', 'Confirmation']

    f['pid'] = d['data']['product_id']
    f = getProductInfo(f)


    f['funnel_type_id'] = int(d['data']['funnel_type_id'])
    f['funnel_type'] = funnel_type_ids[f['funnel_type_id']]
    # Check for 1-step, and set the array value of the billing page.
    # f['one_step'] = False
    # if funnel_type_ids[int(d['data']['funnel_type_id'])] == 'One Step':
    #     f['one_step'] = True

    print()

    f['page_types'] = []
    f['page_fields'] = []

    '''
        f['page_fields'] = [
            [ # p1
                elements.first_name_field,
                elements.age_field
            ],
            [ # p2
                elements.address_field,
                elements.city_field
            ]
        ]
        print()
        # print( f['page_fields'][0][0][0] ) # first page, fields, first field
    '''

    # For each page
    for page in range(len(d['data']['pages'])):
        this_page = d['data']['pages'][page]
        f['page_fields'].append([])

        # Gather the list of types of pages that exist on this funnel
        f['page_types'].append( page_type_ids[int( this_page['page_type_id'])])

        input_types = ['lead_responses', 'billing_responses', 'misc']
        # For each type of input
        for input_type in input_types:
            # Assuming a given page even has inputs, and that input type is on this page
            if ('inputs' in this_page) and (input_type in this_page['inputs']):
                i_type = this_page['inputs'][input_type]
                # billing_responses has numbered dics, followed by an items list.
                if input_type == 'billing_responses':
                    # For each response (cc num, month, year, code) (there's never more than 10)
                    for i in range(10):
                        # (stop at the end of the list)
                        if str(i) in i_type:
                            # Get its input_name
                            f['page_fields'][page].append(i_type[str(i)]['input_name'])
                        else:
                            # The is is the items list
                            pass
                # Others just have an (un-numbered) list of dicts.
                else:
                    # For each response
                    for i in range(len(i_type)):
                        # Get its input_name
                        f['page_fields'][page].append(i_type[i]['input_name'])

    # There's lots of survey fields. Add them dynamically.
    def addSurveyField(survey):
        # survey_responses[42] --> 42
        survey_number = survey[17:-1]
        q  = "SELECT sq.name as question, sqbt.name as type, sc.name as answer"
        q += " FROM  hydra.survey_question_bundles sqb"
        q += " JOIN hydra.survey_questions sq USING (survey_question_id)"
        q += " JOIN hydra.survey_question_bundle_choices sqbc USING (survey_question_bundle_id)"
        q += " JOIN hydra.survey_choices sc USING (survey_choice_id)"
        q += " JOIN hydra.survey_question_bundle_types sqbt USING (survey_question_bundle_type_id)"
        q += " WHERE sqbc.sequence = 1"
        q += " AND sqb.survey_question_bundle_id = "+survey_number
        survey_data = queryDB(q)
        query_type_map = {'radio':'select-one', 'checkbox':'checkbox', 'open_response':'text'}
        elements.fields.append(elements.Field(survey,
                                              survey_data['question'],
                                              query_type_map[survey_data['type']],
                                              survey_data['answer'],
                                              mandatory=True))

    # Try to set the Element object for each of the web elements in f['page_fields']

    # For each page in the newly-created list of fields on pages, e.g.:
    # ['lead_responses[first_name]', 'lead_responses[age]', 'survey_reponses[1]']
    for page in f['page_fields']:
        # For each field on that page, e.g.:
        # lead_responses[first_name]
        for i in range(len(page)):

            # Ignore typo: "reponses" -> "responses"
            if "reponses" in page[i]:
                page[i] = page[i].replace("reponses", "responses")

            found = False
            # pprint(elements.fields)
            # print("\n\n\n")
            for e_list in [elements.fields, elements.inputs]:
                for elem_field in e_list:
                    # print(str(elem_field))
                    if page[i] == elem_field.name:
                        page[i] = elem_field
                        found = True
                if not found:
                    # print("\n\n"+page[i]+"\n\n")
                    if page[i].startswith('survey'):
                        # Query the db for it then try again
                        addSurveyField(page[i])
                        for element in e_list:
                            if page[i] == element.name:
                                page[i] = element
                                found = True
                        if not found:
                            print("Failed to add '"+page[i]+"' (from funnel "+f['funnel_id']+") to elements.fields")
                    else:
                        print("Couldn't find '"+page[i]+"' (from funnel "+f['funnel_id']+") in list")

    '''
        print("x")
        for x in f['page_fields']:
            print(x)
        print("x")

        f['fname'] = 0
        f['gender'] = 0
        f['age_drop'] = 0
        f['age_range'] = 0
        f['age_type'] = 0
        f['zip_code'] = 0
        f['htwtphysique'] = 0
        f['p1_question'] = 0
        f['yes-checkbox'] = 0

        if 'first_name' in f['p1_fields'] or 'lead_responses[first_name]' in f['p1_fields']:
            f['fname'] = 1
        if 'gender'     in f['p1_fields'] or 'lead_responses[gender]'     in f['p1_fields']:
            f['gender'] = 1
        if 'age'        in f['p1_fields'] or 'lead_responses[age]'        in f['p1_fields']:
            f['age_drop'] = 1
        if 'age_range'  in f['p1_fields'] or 'lead_responses[age_range]'  in f['p1_fields']:
            f['age_range'] = 1
        if 'age_type'   in f['p1_fields'] or 'lead_responses[age_type]'   in f['p1_fields']:
            f['age_type'] = 1
        if 'zip_code'   in f['p1_fields'] or 'lead_responses[zip_code]'   in f['p1_fields']:
            f['zip_code'] = 1
        if 'commit' in f['p1_fields']     or 'yes-checkbox'               in f['p1_fields']:
            f['yes-checkbox'] = 1
        if 'survey_reponses[10]' in f['p1_fields']:
            f['htwtphysique'] = 1
        if 'p1_question' in f['p1_fields']:
            f['p1_question'] = 1

        f['cc_name'] = 0
        f['cc_type'] = 0

        f['p3_upsells'] = 0
        f['p3_upsell1_name'] = 0
        f['p3_upsell1_price'] = 0
        f['p3_upsell2_name'] = 0
        f['p3_upsell2_price'] = 0
    '''

    try:
        f['shipping'] = float(d['data']['shipping_options'][0]['onetime_shipping'])
    except:  # What exception?
        sys.exit("Shipping Option is not set for this funnel! Please either set a shipping option or deactivate the funnel.")

    for i in range(8):
        f['p4_upsell'+str(i+1)+'_price'] = 0
    if 'Upsell' in f['page_types']:
        for i in range(len(d['data']['pages'][f['page_types'].index('Upsell')]['inputs']['billing_responses']['items'])):
            # e.g. f['p4_upsell3_price'] = 29.99
            f['p4_upsell'+str(i+1)+'_price'] = \
                           d['data']['pages'][f['page_types'].index('Upsell')]['inputs']['billing_responses']['items'][i]['onetime_price']
    f['p4_upsell_price_array'] = [ f['p4_upsell1_price'], f['p4_upsell2_price'], f['p4_upsell3_price'], f['p4_upsell4_price'], \
                                   f['p4_upsell5_price'], f['p4_upsell6_price'], f['p4_upsell7_price'], f['p4_upsell8_price'] ]

    # print(f['p4_upsell_price_array'])
    # print()
    # for x in sorted(f):
    #     print(x)
    # print()

    return f

# Adds information about the protuct to the "f" dict
# f should have 'pid' by now. Gets called by getFunnelInfo.
def getProductInfo(f):

    q = queryDB("SELECT * FROM ffinder.products WHERE product_id = "+f['pid'])

    brand_abbrevs = ['', 'FF', 'PL', 'SB', 'BC', 'FM', 'AV', 'PS', 'HE', 'SS']
    f['brand_abbr'] = brand_abbrevs[q['brand_id']]
    f['brand_name'] = q['name_brand']
    f['domain'] = q['url'] # -- e.g. "www.forcefactor.com"
    f['prod_name'] = q['name_main_product']
    f['prod_abbr'] = q['abbrev'] # -- e.g. "VN"
    f['shipping'] = q['base_shipping']
    f['country'] = q['country']
    f['delimiter'] = '.'
    if f['country'] == 'BR':
        f['delimiter'] = ','
    f['payment_gateway'] = 'Litle'
    if f['country'] == 'BR':
        f['payment_gateway'] = 'Worldpay'

    return f

# Given various options, return a URL to use
def buildUrl(domain, env, funnel_id, hydra_environment='production', current_step_number='0', lead_token=None):

    # Default result:
    # http://www.femmefactor.com/funnel/613?hydra_environment=production&current_step_number=0
    # With default lead:
    # http://www.femmefactor.com/funnel/613?hydra_environment=production&current_step_number=0&lead_token=7ad302c68609c8c4e2f86092f959b52fc76a45ed26381453c53c35
    funnel_id = str(funnel_id)
    if env == 'www':
        base_url = 'http://'+domain+'/funnel/'
    elif (env == 'staging') or (env == 'stg'):
        # [3:] lops off 'www'
        base_url = 'http://staging'+domain[3:]+'/funnel/'
    else:
        base_url = 'http://hydrafront.nutraclick.com/funnel/'

    full_url = base_url+funnel_id+'?hydra_environment='+hydra_environment+'&current_step_number='+current_step_number

    if lead_token is not None:
        # Default token
        if lead_token == 1 or lead_token is True:
            full_url += '&lead_token=7ad302c68609c8c4e2f86092f959b52fc76a45ed26381453c53c35'
        # Specified token
        else:
            full_url += '&lead_token='+lead_token

    # Override all of the above for the Terms address
    if current_step_number == 'terms':
        base_url = base_url[:-7]+'terms/'
        full_url = base_url+funnel_id


    print(full_url)
    return full_url


# Fill in all of the fields on this page
def fillAllFields(browser, funnel, step, lead=None, mobile=False):
    f = funnel
    fields_on_this_page = f['page_fields'][int(step)]

    # Check for multiple fields on a given sub-page
    if mobile:
        data_labels = []
        f_index = 0
        for field in fields_on_this_page:
            if field.name == 'lead_responses[state]':
                del fields_on_this_page[f_index]
            field.find(browser)
            data_labels.append(field.element.get_attribute('data-label'))
            f_index += 1

        seen = set()
        dupes = set()
        for dl in data_labels:
            if dl in seen:
                dupes.add(dl)
            else:
                seen.add(dl)
        for dupe in dupes:
            print('Dupe: '+dupe)

    for field in fields_on_this_page:
        # time.sleep(0.5)
        # print(field.name)
        # If it's not there, just go to the next one.
        # e.g., submit email with non-required phone number on the same page.
        try:
            field.find(browser)
        except NoSuchElementException:
            continue

        if lead is None:
            field.fillInField()
            # time.sleep(0.5)
            if mobile:
                data_label = field.element.get_attribute('data-label')
                if data_label is not None:
                    sub_page_btn = browser.find_element_by_id(data_label+'-btn')
                # If data_label is None, just use the previous sub_page_btn value.
                sub_page_btn.click()
                # time.sleep(0.5)

        else:
            field_name_fill_map = {
                'lead_responses[first_name]'    : lead['fname'],
                'lead_responses[last_name]'     : lead['lname'],
                'lead_responses[full_name]'     : lead['fname']+" "+lead['lname'],
                'lead_responses[country]'       : lead['loc'],
                'lead_responses[age]'           : lead['age'],
                'lead_responses[gender]'        : lead['gender'],
                'lead_responses[fname]'         : lead['fname'],
                'lead_responses[address]'       : lead['address'],
                'lead_responses[city]'          : lead['city'],
                'lead_responses[state]'         : lead['state'],
                'lead_responses[zip_code]'      : lead['zip_code'],
                'lead_responses[phone_number]'  : lead['phone'],
                'lead_responses[email_address]' : lead['email'],
                'lead_responses[real]'          : lead['real'],
                'lead_responses[cc_type]'       : lead['cc_type'],
                'lead_responses[cc_num]'        : lead['cc_num'],
                'lead_responses[cc_month]'      : lead['cc_month'],
                'lead_responses[cc_year]'       : lead['cc_year'],
                'lead_responses[cc_code]'       : lead['cc_code']
            }
            if field.name in field_name_fill_map:
                field.fillInField(field_name_fill_map[field.name])
                if mobile:
                    time.sleep(1)
                    data_label = field.get_attribute('data-label')
                    sub_page_btn = browser.find_element_by_id(data_label+'-btn')
                    sub_page_btn.click()
            else:
                # print(field.name)
                # print("oops")
                field.fillInField()
                if mobile:
                    time.sleep(1)
                    browser.find_element_by_class_name('next_btn').click()


# Try to find a checkbox to check, and check it
def agreeToTerms(browser):

    # Find it
    try:
        ckbox = browser.find_element_by_id("terms-agree")
    except NoSuchElementException:
        ckbox = None
    except ElementNotVisibleException:
        ckbox = None
    except StaleElementReferenceException:
        print("Ckbox has gone stale (not attached to the page right now).")
        ckbox = None
    except WebDriverException:
        print("Ckbox went hiding. Hunt it down!")
        ckbox = browser.find_element_by_class_name("check-bx")

    # Click it
    if ckbox is not None:
        print('Clicking "terms-agree" ckbox')
        try:
            ckbox.click()
        except WebDriverException:
            # time.sleep(2)
            try:
                ckbox.click()
            except (ElementNotVisibleException, WebDriverException):
                browser.execute_script("window.scrollTo(0, 0)")
                browser.execute_script("arguments[0].scrollIntoView(true);", ckbox)
                try:
                    ckbox.click()
                except WebDriverException:
                    print("p3 terms checkbox click fail.\nClicking the label instead.")
                    label = None
                    try:
                        label = browser.find_element_by_xpath("//div[@class='form']/div[4]/label")
                    except NoSuchElementException:
                        return

                    if label is not None:
                        try:
                            label.click()
                        except (ElementNotVisibleException, WebDriverException):
                            browser.execute_script("window.scrollTo(0, 0)")
                            browser.execute_script("arguments[0].scrollIntoView(true);", label)
                            label.click()
    return ckbox

# Given what type of page this is,
# figure out how to submit the page.
def getSubmitBtn(browser, page_type):
    if page_type == 'Lead Generation':
        btn = browser.find_element_by_class_name("lander-form-qualify-btn")
    elif page_type == 'Qualify':
        btn = browser.find_element_by_id("form-submit-btn")
    elif page_type == 'Billing':
        agreeToTerms(browser)
        btn = browser.find_element_by_id("form-rush-btn")
    elif page_type == 'Upsell':
        btn = browser.find_element_by_id("upsell-submit-btn")
    else:
        failOut(browser, "helpers.submitPage() doesn't recognize page_type "+page_type)

    return btn

# If there is an exit pop, get rid of it.
def exitPopCheck(browser):
    try:
        alert = browser.switch_to.alert
        pleasePrint('Alert = '+alert.text)
        alert.accept()
        pleasePrint("Closed exit pop.")
    except NoAlertPresentException:
        pass
        # vPrint("No exit pop.")

# Given what type of page this is,
# figure out how to submit the page, than do so.
def submitPage(browser, page_type):
    btn = getSubmitBtn(browser, page_type)
    btn.click()
    exitPopCheck(browser)

# Print a message if verisign or mcafee are missing
def securityCheck(browser):
    pleasePrint("Checking security...")
    # @TODO: Change from try/catch to assert
    try:
        browser.find_element_by_id("verisign")
    except NoSuchElementException:
        pleasePrint("No verisign here.")

    try:
        browser.find_element_by_id("mcafee")
    except NoSuchElementException:
        pleasePrint("No mcafee here.")

# Confirm, for all footer links:
# id, label, and href
# THIS IS CURRENTLY BROKEN
# It's just a direct copy from FunnelFunctions
def footerCheck(browser):

    # TECH-16923 - Remove all "Home" links from bottom of landers
    # The list of all such elements should be empty
    # .........................never mind. It's back.
    # try:
    #     assert len(browser.find_elements_by_id('foot-home')) == 0
    # except AssertionError:
    #     failOut(browser, 'A "home" link is in the footer, but shouldn\'t be.')

    # TECH-15533
    # SKIP site maps on the funnels
    # VERIFY lower case footers on Stages of Beauty
    # SKIP Brazilian href and labels
    terms = {
        'id': 'foot-terms',
        'label': 'TERMS',
        'BR_label': 'TERMOS',
        'href': '/terms/'+db_vars['itid']}
    refund = {
        'id': 'foot-refund',
        'label': 'REFUND & RETURN POLICY',
        'BR_label': 'POLITICA DE REEMBOLSO E DEVOLUCAO',
        'href': '/refund'}
    privacy = {
        'id': 'foot-privacy',
        'label': 'PRIVACY POLICY',
        'BR_label': 'POLITICA DE PRIVACIDADE',
        'href': '/privacy'}
    _copyright = {
        'id': 'foot-copyright',
        'label': 'COPYRIGHT INFO',
        'BR_label': 'INFORMACOES DE COPYRIGHT',
        'href': '/copyright'}
    contact = {
        'id': 'foot-contact',
        'label': 'CONTACT US',
        'BR_label': 'FALE CONOSCO',
        'href': '/contact'}
    footers = [terms, refund, privacy, _copyright, contact]

    for f in footers:

        # Set expectations
        expected_label = f['label']
        expected_href = f['href']
        # SB-TC has lowercase labels
        if prod.getProdID().startswith('30'):
            expected_label = expected_label.lower()
        # PL-SP has [ LABEL ] (except on upsell pages)
        if prod.getProdID().startswith('20'):
            expected_label = "[ "+expected_label+" ]"
        # Brazil hrefs (except terms) is prefixed with "/pt"
        if prod.getLocation() == 'BR':
            expected_label = f['BR_label']
            if f != terms:
                expected_href = "/pt"+expected_href

        # Temporarily skip BR funnels until bug is fixed (TECH-17239)
        if prod.getLocation() != 'BR':
            # Get actual values
            actual_label = browser.find_element_by_id(f["id"]).text
            actual_href = browser.find_element_by_id(f["id"]).get_attribute("href")

            # Compare expected to actual
            # Go a little easier on PL-SP
            if prod.getProdID().startswith('20'):
                assert actual_label in expected_label
            else:
                assert actual_label == expected_label
            assert actual_href.endswith(expected_href)

    # @TODO: Confirm that they open in pop-up windows
    # (likely clicking instead of via parsing their code)

# Confirm that mobile users arrive to a zoomed-out page and are able to zoom
def mobileCheck(browser):
    # Confirm that mobile users arrive to a zoomed-out page
    assert "maximum-scale=1" not in browser.page_source
    assert "initial-scale=1" not in browser.page_source
    # Confirm that mobile users are able to zoom
    assert "user-scalable=0" not in browser.page_source

# Confirm that the right pixels exist, given pid and page (TECH-16391)
def pixelCheck(browser, page):
    q  = "SELECT *"
    q += " FROM fbait.pixels_new"
    q += " WHERE product_id = "+str(db_vars['pid'])
    q += " AND page = "+str(page)
    q += " AND network_id IS NULL"
    res = queryDB(q, host='prod', db='fbait')
    if res is not None:
        print(''.join(res['code'][:-10].split()))
        # assertIn(''.join(res['code'][:-10].split()), ''.join(browser.page_source.split()))
        assert ''.join(res['code'][:-10].split()) in ''.join(browser.page_source.split())
        vPrint("Pixel confirmed")

# Check for 'Mixed content' or 'insecure' in the console log
def consoleLogCheck(browser):
    url = browser.current_url
    log = browser.get_log('browser')
    for entry in log:
        # msg = entry['message']
        if 'Mixed content' in entry['message'] or 'insecure' in entry['message']:
            failOut(browser, entry)

# Return the ID of the funnel that this one was cloned from
# or '0' if it wasn't cloned
def getParentFunnel(itid):
    q  = "SELECT e.secondary_entity_id FROM hydra.events e"
    q += " JOIN hydra.funnels f ON (e.secondary_entity_id = f.funnel_id)"
    q += " WHERE e.event_action_id = 6 AND e.entity_key_id = 1 AND e.entity_id = "+itid
    q_result = queryDB(q, host='prod', db='hydra')
    try:
        parent = str(q_result['secondary_entity_id'])
        return parent
    # If there is no parent, set the parent to 0.
    except: # What Exception?
        return '0'

# Check if this is one of the funnels that have no "phone" field
def hasPhone(funnel_id):
    no_phone_funnels = ['406', '432', '433', '506', '581']
    if funnel_id in no_phone_funnels:
        return False

    # Recursively query to see if any of its anscestors are on the list
    # Stop querying if the ID gets below 385
    while funnel_id >= '385':
        if funnel_id in no_phone_funnels:
            return False
        funnel_id = getParentFunnel(funnel_id)

    # If we haven't yet returned False (which will be the usual case), then it does have a Phone field.
    return True



#########
## CRM ##
#########


test_log = []

def logTest(x):
    print(x)
    test_log.append(x)


# Log into CRM
def openAndLoginCRM(browser, level='rep'):

    browser.get(urls.crm_base_url)
    logTest('Logging into CRM using ' + str(level))

    # Find login fields
    try:
        elements.crm_user_name.find(browser)
    except NoSuchElementException:
        logTest('Failed! Could not find user name field')

    try:
        elements.crm_password.find(browser)
    except NoSuchElementException:
        logTest('Failed! Could not find password field!')

    # Change credentials if manager
    if level == 'manager':
        elements.crm_user_name.fillInField(val='ha-qau')
        elements.crm_password.fillInField(val='Test2test2016')

    else:
        # Fill in credentials
        elements.crm_user_name.fillInField()
        elements.crm_password.fillInField()

    # Click submit button
    try:
        browser.find_element_by_xpath('//*[@id="content"]/form/p/input').click()
    except NoSuchElementException:
        logTest('Failed! Could not find submit button.')

    browser.maximize_window()

# Figure out if you are already logged into the CRM.
# Returns boolean
def isCRMUserLoggedIn(browser):

    # go to the search page
    browser.get('https://www.bigfishcrm.com/search')
    time.sleep(1)

    if "Logged in" in browser.page_source:
        return True
    return False

# If logged in, do nothing. If not, then log in.
def verifyCRMUserLoggedIn(browser):
    if not isCRMUserLoggedIn(browser):
        openAndLoginCRM(browser, level='rep')

# Go to specific CRM page
def navigateToCRMPage(browser, page='new new order'):

    # need to update with manager navigation

    logTest('Navigating to ' + str(page) + '...')

    if page in urls.crm_urls:
        url = urls.crm_urls[page]
        browser.get(url)
    elif page == 'new new order':
        browser.find_element_by_xpath('//*[@id="link"]/a[8]').click()
    else:
        err_msg = 'Could not find the CRM page ' + page + ' you were trying to go to, acceptable choices include: search, issues, old new order, new new order'
        logTest(err_msg)
        failOut(browser, err_msg)
    # print(browser.current_url)

# Get offer id is offer name is provided
def getOfferIDFromName(offer_name):
    q  = "SELECT o.offer_id AS offer_id"
    q += " FROM ffinder.offers o"
    q += " WHERE o.name= " + "'" + offer_name + "'"

    q_res = queryDB(q, host='prod', db= 'ffinder')
    offer_id = q_res['offer_id']

    return offer_id

# Get offer name from id
def getOfferNameFromID(offer_id):
    q  = "SELECT o.name AS offer_name"
    q += " FROM ffinder.offers o"
    q += " WHERE o.offer_id= " + str(offer_id)

    q_res = queryDB(q, host='prod', db= 'ffinder')
    offer_name = q_res['offer_name']

    return offer_name

# Returns a dictionary of offer attributes useful to create an order
def getOfferAttributes(offer_name):

    country_abrev = {'(CA)' : 'CA',
                     '(BR)' : 'BR',
                     '(AU)' : 'AU',
                     '(GB)' : 'GB'}


    # Query for the offer based on the case and return the restrictions
    q  = "SELECT b.brand_abbrev AS brand,"
    q += " o.offer_type_id AS offer_type,"
    q += " b.brand_name AS brand_name,"
    q += " o.offer_status_id AS offer_status,"
    q += " p.country AS country"
    q += " FROM ffinder.offers o"
    q += " JOIN ffinder.products p USING (product_family_id)"
    q += " JOIN ffinder.brands b USING (brand_id)"
    q += " WHERE o.name = " + '"' + str(offer_name) + '"'

    for country, abrev in country_abrev.items():
        if country in offer_name:
            q += " AND p.country= " + "'" + abrev + "'"

    q += " ORDER BY o.offer_status_id ASC"

    q_res = queryDB(q, host='prod', db= 'ffinder')

    # Create offer dictionary
    offer_dict = {}
    for column, value in q_res.items():
        offer_dict[column] = value

    return (offer_dict)

# Evaluate offers for BR and inactive restrictions
def evaluateOfferResitrictions(offer_dict):

    # If the offer is not active, quit.
    if offer_dict['offer_status'] == 2:
        err_msg = ' Failed! This offer is not active and cannot be added!'
        logTest(err_msg)
        sys.exit(err_msg)

    # If the offer is not active, quit.
    if offer_dict['country'] == 'BR':
        err_msg = 'Failed! BR offers can\'t be automated yet.'
        logTest(err_msg)
        sys.exit(err_msg)

# Create unique email for CRM order
def createOfferEmail():

    return 'qaautomation+' + str(int(time.time())) + '@nutraclick.com'

# Get Countries offer is offered in
def getOfferCountry(browser, offer_name):

    # Because offer association uses a tree structure, querying the DB is useless.
    # To find out if the offer is international, we need to change the country.
    # Search for the Add to Cart button until we confirm that it isn't there.
    # Default country is United States

    countries = ['United States', 'Australia', 'Brazil', 'Canada', 'United Kingdom']

    elements.crm_country.find(browser)
    for country in countries:
        elements.crm_country.fillInField(val=country)
        time.sleep(1)
        if hasACartButton(browser, offer_name):
            return country

    msg = 'Could not find offer in any country!'
    logTest(msg)
    failOut(browser, msg)

# Fill in CRM customer information
def fillInCustomerFields(browser, offer_name, order_email):

    # use country to fill in the rest of the fields
    country = getOfferCountry(browser, offer_name)

    # zip code auto populates city and state
    for field in elements.crm_customer_info_fields:

        # Skipping type for now
        if field == elements.crm_cc_type:
            continue

        try:
            # find field
            field.find(browser)
        except NoSuchElementException:
            logTest('Failed! Field cannot be found!')

        # country specific can be changed by zip
        if field == elements.crm_zip:
            if country == 'Australia':
                field.fillInField(val='VIC 3000')
            elif country == 'United Kingdom':
                field.fillInField(val='EC1A 1BB')
                state = browser.find_element_by_id('state').send_keys('Berkshire')
            elif country == 'Canada':
                field.fillInField(val='A1C 1A4')
            elif country == 'Brazil':
                field.fillInField(val='04559-001')
            else:
                field.fillInField()
        elif field == elements.crm_email:
            field.fillInField(val=order_email)
            # print(order_email)
        else:
            field.fillInField()

    # Brazil also requires an additional billing that only shows after you move away from zip
    # Putting it here so it happens after all other fields
    # Will also want to do this for crm_card_type
    if country == 'Brazil':
        try:
            # Find
            elements.crm_cpf.find(browser)
        except NoSuchElementException:
            logTest('CPF field cannot be found!')
        try:
            # Fill in
            elements.crm_cpf.fillInField()
        except:
            logTest('Failed to fill in CPF field!')

# Navigates to correct brand based on offer
def goToOfferBrand(browser, offer_dict):

    brand = offer_dict['brand']
    crm_brand_navigation    = ('FM', 'FF', 'PL', 'PS', 'SB')

    positions = []
    for pos, abbrev in enumerate(crm_brand_navigation):
        if abbrev == brand:
            positions.append(pos)

    for position in positions:
        btn_position = position + 1
        print ("btn_position = "+str(btn_position))
        brand_btn_xpath = '//*[@id="brand-selection"]/ul/li[' + str(btn_position) + ']/img'
        print("brand_btn_xpath = "+brand_btn_xpath)
        logTest('Navigating to brand ' + str(brand))
        try:
            brand_btn = browser.find_element_by_xpath(brand_btn_xpath)
        except NoSuchElementException:
            logTest('Couldn\'t find brand button. Trying again after 10 seconds...')
            time.sleep(10)
            try:
                brand_btn = browser.find_element_by_xpath(brand_btn_xpath)
            except NoSuchElementException:
                err_msg = 'Could not find brand button for brand ' + brand
                logTest(err_msg)
                failOut(browser, err_msg)

        try:
            brand_btn.click()
        except ElementNotVisibleException:
            err_msg = 'Could not click brand button for brand ' + brand
            logTest(err_msg)
            failOut(browser, err_msg)

        time.sleep(2)

# Searches for offer name
def searchForOfferToCart(browser, offer_name):

    try:
        logTest('Searching for offer ' + offer_name)
        elements.crm_search.find(browser)

        # fill in offer name
        elements.crm_search.fillInField(offer_name)
        time.sleep(1)

    except NoSuchElementException:
        err_msg = 'Failed! Count not find ' + offer_name + ' in New Order Page!'
        logTest(err_msg)
        failOut(browser, err_msg)

# Search for cart button
def hasACartButton(browser, offer_name):

    add_cart_xpath = getCRMCartButtonXPATH(offer_name)

    try:
        browser.find_element_by_xpath(add_cart_xpath)
        return True
    except NoSuchElementException:
        return False

# get a list for offers that contain the same name
def getOfferNameMatches(offer_name):

    # One offer can contain the same string as another offer's full name.
    # In the CRM New Order page, offers are ordered by type, name, offer_id

    q  = "SELECT o.name AS name"
    q += " FROM ffinder.offers o"
    q += " LEFT JOIN ffinder.offer_schemes os USING (offer_scheme_id)"
    q += " LEFT JOIN ffinder.offer_association_rules_x_offers USING (offer_id)"
    q += " WHERE 1"
    q += " AND offer_association_rule_x_offer_id IS NOT NULL"
    q += " AND o.name like '%" + offer_name + "%'"
    q += " ORDER by o.offer_type_id, name, offer_id"

    q_res = queryDBMultiple(q)

    matches = []
    for name in q_res:
        matches.extend(name)

    match_index = 0
    for match in matches:
        match_index += 2
        if match == offer_name:
            return match_index

def getCRMCartButtonXPATH(offer_name):

    match_index = getOfferNameMatches(offer_name)
    add_cart_xpath = '//*[@id="offer-list"]/table/tbody/tr[' + str(match_index) + ']/td[5]/button'

    return add_cart_xpath

# Add offer to cart
def addOfferToCart(browser, offer_name):

    logTest('Adding offer to cart..')

    add_cart_xpath = getCRMCartButtonXPATH(offer_name)
    try:
        add_btn = browser.find_element_by_xpath(add_cart_xpath)
    except NoSuchElementException:
        logTest('Could not find add to cart button!')
    add_btn.click()
    time.sleep(2)

# If Offer is subscription type, look for and accept terms
def acceptOfferTerms(browser, offer_dict):

    if offer_dict['offer_type'] == 1:
        try:
            logTest('Accepting offer terms...')
            browser.find_element_by_xpath('//*[@id="modal-add-offer"]/div[3]/div/button[2]').click()
            time.sleep(2)
        except NoSuchElementException:
            logTest('Failed! Offer is a subscription and could not find terms!')


# Recap and submit CRM order
def recapAndSubmitOfferOrder(browser):

    # order recap
    logTest('Recapping order...')
    try:
        place_order_btn = browser.find_element_by_id('place-order')
    except NoSuchElementException:
        err_msg = 'Failed! Could not find order recap button!'
        logTest(err_msg)
        failOut(browser, err_msg)
    try:
        place_order_btn.click()
    except ElementNotVisibleException as e:
        err_msg = 'Failed! Order recap button is not visible!'
        err_msg += "\n"+str(e)
        logTest(err_msg)
        failOut(browser, err_msg)
    time.sleep(2)

    # place order
    logTest('Placing order...')
    try:
        order_recap_btn = browser.find_element_by_xpath('//*[@id="modal-order-recap"]/div[3]/div[2]/button[2]')
    except NoSuchElementException:
        logTest('Failed! Could not find Place Order button!')
        # failOut(browser, )
    try:
        order_recap_btn.click()
    except ElementNotVisibleException:
        logTest('Failed! Place Order button is not visible!')
        # failOut(browser, err_msg)
    time.sleep(3)

# Query db for CRM order
def queryOfferOrder(order_email):

    time.sleep(5)

    q  = "SELECT o.order_id AS order_id"
    q += " FROM ffinder.orders o"
    q += " JOIN ffinder.leads l USING (lead_id)"
    q += " WHERE l.email_address =" + " " + "'" + order_email + "'"

    q_res = queryDB(q, host='prod', db='ffinder')
    logTest('Created order with ' + str(q_res))

    return q_res['order_id']


# list of offers in order
def getOffersInOrder(order_id):

    # get the offers we used in this order
    q = "SELECT o.name "
    q +=" FROM ffinder.offers o"
    q +=" JOIN ffinder.offers_x_orders oxo USING (offer_id)"
    q +=" WHERE oxo.order_id = " + str(order_id)

    q_res = queryDBMultiple(q)
    logTest('Offers in this order include: ' + str(q_res))
    return q_res

# Return a list of straight sale offer name, change count to specify how many
def getRandomStraightSaleOffers(count=2):

    active_offers_list = []

    q = "SELECT o.name AS offer_name"
    q += " FROM ffinder.offers o"
    q += " LEFT JOIN ffinder.offer_schemes os USING (offer_scheme_id)"
    q += " LEFT JOIN ffinder.offer_association_rules_x_offers USING (offer_id)"
    q += " WHERE 1"
    q += " AND offer_association_rule_x_offer_id IS NOT NULL"
    q += " AND o.offer_status_id = 1"
    q += " AND o.offer_type_id = 2"

    q_res = queryDBMultiple(q)

    for row in q_res:
        active_offers_list.extend(row)

    # pick random offers from the list
    offers = random.sample(set(active_offers_list),count)
    return offers

# Returns a single random straight sale offer
def getRandomStraightSaleOffer():

    offers = getRandomStraightSaleOffers(count=1)
    offer_name = offers[0]
    return offer_name


# Returns list of random subscription offers,change count to specify how many
def getRandomSubscriptionOffers(count=2):

    # Create a list of active offers
    active_offers_list = []

    q = "SELECT o.name AS offer_name"
    q += " FROM ffinder.offers o"
    q += " LEFT JOIN ffinder.offer_schemes os USING (offer_scheme_id)"
    q += " LEFT JOIN ffinder.offer_association_rules_x_offers USING (offer_id)"
    q += " WHERE 1"
    q += " AND offer_association_rule_x_offer_id IS NOT NULL"
    q += " AND o.offer_status_id = 1"
    q += " AND o.offer_type_id = 1"

    q_res = queryDBMultiple(q)

    for row in q_res:
        active_offers_list.extend(row)

    # pick a random offer from the list
    offers = random.sample(set(active_offers_list),count)
    return offers

# Returns a single random subscription offer
def getRandomSubscriptionOffer():

    offers = getRandomSubscriptionOffers(count=1)
    offer_name = offers[0]
    return offer_name

# Return offer price and shipping
def getOfferPriceAndShipping(offer_dict, offer_name):

    # the price of the sale of a
    q = "SELECT oi.shipping AS shipping, (i.price/100) AS price"
    q+= " FROM ffinder.offers o"
    q+= " JOIN ffinder.offers_x_offer_components oxoc using (offer_id)"
    q+= " JOIN ffinder.offer_components oc using (offer_component_id)"
    q+= " JOIN ffinder.offer_component_types oct using (offer_component_type_id)"
    q+= " JOIN ffinder.offer_items oi using (offer_item_id)"
    q+= " JOIN ffinder.offer_schemes_x_offer_schedules osxos using (offer_scheme_id)"
    q+= " JOIN ffinder.offer_schedules oscd"
    q+= " ON osxos.offer_schedule_id = oscd.offer_schedule_id"
    q+= " JOIN ffinder.items i using (item_id)"
    q+= " WHERE o.name= " + '"' + offer_name + '"'
    q+= " AND o.offer_status_id = 1"

    # subscription offers have multiple items but are priced at 0
    if offer_dict['offer_type'] == 1:
        q+= " AND oct.name = 'trial'"

    q+= " GROUP BY i.sku"

    q_res = queryDB(q, host='prod', db= 'ffinder')

    offer_prices = {}
    for column, value in q_res.items():
        offer_prices[column] = float(value)

    return offer_prices


# Returns the text for the subotal value in CRM
def getCRMSubtotalValue(browser):

    try:
        subtotal = browser.find_element_by_id('subtotal').get_attribute('innerHTML').strip('$')
        logTest('Subtotal: ' + subtotal)
    except NoSuchElementException:
        logTest('Could not find subtotal value!')
    return float(subtotal)


# Compare CRM actual subtotal vs. expected price of offer
def verifyCRMSubtotal(browser):
    # NEEDS update for multiple offers
    # get the offer price and shipping from DB
    offer_prices = getOfferPriceAndShipping(offer_dict, offer_name)
    expected_subtotal = offer_prices['price']
    expected_shipping = offer_prices['shipping']

    try:
        assert actual_subtotal == expected_subtotal
        logTest('Actual price shown ' + str(actual_subtotal) + ' equals expected price of offer ' + str(expected_subtotal))
    except AssertionError:
        failed.append(offer_name + ' in ' + state+' Failed actual price shown ' + str(actual_subtotal) + ' does not equal expected price of offer ' + str(expected_shipping))

#  Compare CRM actual shipping vs. expected price of offer
def verifyCRMShipping(browser):

    # NEEDS update for multiple offers
    # get the offer price and shipping from DB
    offer_prices = getOfferPriceAndShipping(offer_dict, offer_name)
    expected_subtotal = offer_prices['price']
    expected_shipping = offer_prices['shipping']

    try:
        assert actual_shipping == expected_shipping
        logTest('Actual price shown ' + str(actual_shipping) + ' equals expected shipping ' + str(expected_shipping))
    except AssertionError:
        failed.append(offer_name + ' in ' + state + ' ' + zip_code +' Failed actual price shown ' + str(actual_shipping) + ' does not equal expected shipping ' + str(expected_shipping))

# Returns the text for the tax value in CRM
def getCRMTaxValue(browser):
    ## NEEDS update for multiple offers

    try:
        tax = browser.find_element_by_id('tax').get_attribute('innerHTML').strip('$')
        logTest('Tax: ' + tax)
    except NoSuchElementException:
        logTest('Failed! Could not get tax value!')

    return float(tax)

# Returns the text for the shipping value in CRM
def getCRMShippingValue(browser):

    try:
        shipping = browser.find_element_by_id('shipping').get_attribute('innerHTML').strip('$')
        logTest('Shipping: ' + shipping)
    except NoSuchElementException:
        logTest('Could not get shipping value!')

    return float(shipping)

# Returns the text for the total value in CRM
def getCRMTotalValue(browser):

    try:
        total = browser.find_element_by_id('total').get_attribute('innerHTML').strip('$')
        logTest('Total: ' + total)
    except NoSuchElementException:
        logTest('Could not get total value!')

    return float(total)

# Compare CRM actual tax vs. expected price of offer
def verifyCRMTax(browser, offer_name, state, offer_dict):
    '''
    Compares actual and expected tax values.
    '''

    # set up
    tax_rate = 0

    # Rates gathered on 6/28/16 from http://taxfoundation.org/article/state-and-local-sales-tax-rates-2016
    state_tax_rates = {
        'CA' : 0.09,
        'GA' : 0.06,
        'IL' : 0.08,
        'MA' : 0.0625,
        'MD' : 0.06,
        'MO' : 0.0835,
        'NC' : 0.0675,
        'OH' : 0.0675,
        'SD' : 0.065,
        'TX' : 0.0825,
        'PA' : 0.06,
        'NJ' : 0.07,
        'NY' : 0.08,
        'FL' : 0.07
    }

    # what is the tax rate?
    if state in state_tax_rates:
        tax_rate = state_tax_rates[state]

    stages_only_states = ['PA', 'NY', 'NJ', 'FL']
    if state in stages_only_states and offer_dict['brand'] != 'SB':
        tax_rate = 0.00

    # IL is weird
    non_stages_1_states = ['IL']
    if state in non_stages_1_states and offer_dict['brand'] != 'SB':
        tax_rate = 0.01

    shipping_taxable_states = [
        'AL','AR','CO','CT','FL','GA','HI','IL','IN','KS','KY','MI',
        'MN','MO','MS','NC','ND','NE','NJ','NM','NV','NY','OH','PA',
        'RI','SC','SD','TN','TX','VA','VT','WA','WI','WV','WY']

    shipping_taxable = True if state in shipping_taxable_states else False

    # get the offer price and shipping from DB
    offer_prices = getOfferPriceAndShipping(offer_dict, offer_name)
    expected_subtotal = offer_prices['price']
    expected_shipping = offer_prices['shipping']

    # verify the tax on the item
    if shipping_taxable == True:
        expected_tax = (expected_shipping + expected_subtotal) * tax_rate
    else:
        expected_tax = expected_subtotal * tax_rate

    # tax value on screen
    actual_tax = getCRMTaxValue(browser)

    # compare expected tax and actual tax
    try:
        assert actual_tax == round(expected_tax,2)
        logTest('Actual tax shown ' + str(actual_tax) + ' equals expected tax ' + str(round(expected_tax,2)))
    except AssertionError:
        print(offer_name + ' in ' + state + ' Failed actual tax shown ' + str(actual_tax) + ' does not equal expected tax ' + str(round(expected_tax,2)))



############
## Retail ##
############

def createRetailOrder(browser, brand, product_urls):
    added_to_cart = False

    while not added_to_cart:
        logTest('Getting '+brand+' product link...')
        url = random.choice(product_urls)

        logTest('\nOpening ' + url)
        browser.get(url)
        time.sleep(1)

        added_to_cart = addRetailProductToCart(browser)

    openRetailCheckoutPage(browser, brand=brand)
    checkoutFromRetailSite(browser)

    for log in test_log:
        print (log)

# Adds product to cart from ID
def addRetailProductToCart(browser):

    added_to_cart = False

    # Add the product
    logTest('Looking for add to cart button...')

    try:
        browser.find_element_by_name('add_item').click()
    except NoSuchElementException:
        try:
            browser.find_element_by_id('add-item').click()
        except NoSuchElementException:
            try:
                browser.find_element_by_id('add_item1').click()
            except NoSuchElementException:
                logTest('Could not find add to cart button!')

    time.sleep(2)
    if 'View Cart (1)' in browser.page_source or 'ITEMS (1)' in browser.page_source:
        added_to_cart = True

    return added_to_cart

# Open retail checkout page
def openRetailCheckoutPage(browser, brand=None):
    logTest('Going to checkout page...')
    time.sleep(2)
    checkout_url = []
    if brand == 'SB' or brand == 'PL':
        checkout_url = urls.retail_base_urls[brand]+urls.checkout_ext_2
    else:
        checkout_url = urls.retail_base_urls[brand]+urls.checkout_ext

    browser.get(checkout_url)
    time.sleep(1)

# On a retail site, fill in all the fields in elements.retail_payment_fields
def fillInRetailPaymentFields(browser):

    offer_email = createOfferEmail()
    # fill in retail payment form
    logTest('Filling in payment fields..')
        # Fill in customer fields
    for field in elements.retail_fields:
        field.find(browser)
        field.clearField()
        if field == elements.retail_email:
            field.fillInField(val=offer_email)
        else:
            field.fillInField()

    return offer_email

# Submit Retail Checkout Page
def submitRetailCheckoutPage(browser):
    # time.sleep(3)
    logTest('Submitting checkout page...')
    time.sleep(3)
    submit_btn = browser.find_element_by_id('submit')
    try:
        submit_btn.click()
    except WebDriverException as e:
        failOut(browser, '\nFailed while trying to click retail submit btn. Err msg:\n'+str(e))
    time.sleep(3)

# Get retail order
def getRetailOrderID(offer_email):

    logTest('Querying for Order ID...')
    query  = "SELECT order_id FROM ffinder.orders o"
    query += " JOIN ffinder.leads l USING (lead_id)"
    query += " WHERE l.email_address =" + "'" + offer_email + "'"
    q_res = queryDB(query, host='prod', db='ffinder')

    if len(q_res) > 0:
        logTest("Order created: " + str(q_res))
    else:
        logTest("Failed! Could not retrive order id for email " + offer_email)

# Checkout process for retail sites
def checkoutFromRetailSite(browser):

    # must have something in cart for this to work
    # must be already on the checkout page
    offer_email = fillInRetailPaymentFields(browser)
    submitRetailCheckoutPage(browser)
    getRetailOrderID(offer_email)

# Checks quantity field exists, user can click on field, default value of field, dropdown options or input capability
def retailQuantityChecks(browser):

    logTest('Checking quantity field...')

    qty = elements.retail_qty
    qty.find(browser)

    # user can click on quantity
    try:
        qty.element.click()
    except ElementNotVisibleException:
        failOut(browser, 'Failed! Could not click on quantity field')

    # Checks default value in quantity field
    try:
        assert qty.element.get_attribute('value') == '1'
    except AssertionError:
        failOut(browser, 'Failed! Default value was not 1!')

    # if its a dropdown it should have value 1 - 5 in that order
    if qty.element.get_attribute('type') != 'text':
        option_html ='''<optionvalue="1">1</option>
                        <optionvalue="2">2</option>
                        <optionvalue="3">3</option>
                        <optionvalue="4">4</option>
                        <optionvalue="5">5</option>'''

        expected_options = option_html.replace(" ", "").strip()
        actual_options = qty.element.get_attribute('innerHTML').replace(" ", "").strip()

        assert actual_options == expected_options
    # its a text field, clear the field, insert random integer from 1 - 10
    else:
        qty.clearField()
        expected_value = random.randint(1, 10)
        qty.fillInField(val=expected_value)

    logTest('Finished checking quantity field!')

################
## Commission ##
################


# Query DB for a random commission period
def getRandomCommissionPeriod():
    # commission period 2 data does not exist
    commission_periods = []

    q = "SELECT commission_period_id AS period_id"
    q += " FROM ffinder.commission_periods"
    q += " WHERE commission_period_id !=2"
    q_res = queryDBMultiple(q)

    for row in q_res:
        commission_periods.extend(row)

    # pick a random commission period from the list
    random_period = random.choice(commission_periods)

    return random_period

# Return a dictionary of values and query for commission period attibutes
def getCommissionPeriodCalParameters(period_id):

    # create a dictionary of values and query for commission period attibutes
    params = {'Min Call Count for Incentive' : '',
             'Refund Rate Multiplier' : '',
             'Cross-sell Rate Multiplier' :'',
             'Cross-sell Rate Multiplier' : '',
             'Save Rate Multiplier' : '',
             'Conversion Rate Multiplier' : '',
             'Max Average Disposition Time for' : '',
             'Outbound Call Divider' : ''}

    # query for calculation attributes
    for name, value in params.items():
        q = "SELECT cm.value as value"
        q += " FROM ffinder.commission_periods cp"
        q += " JOIN ffinder.commission_metrics cm using (commission_period_id)"
        q += " JOIN ffinder.commission_fact_types cft using (commission_fact_type_id)"
        q += " WHERE cft.name = '" + name + "'"
        q += " AND cp.commission_period_id =" + str(period_id)
        q_res = queryDB(q, host='prod', db= 'ffinder')

        value = float(q_res['value'])
        params[name] = value

    return params

# Return commission period start, end dates
def getCommissionPeriodStartEndDates(period_id):

    dates = {}
    # query for start and end date for a given period
    q = "SELECT start_date, end_date"
    q += " FROM ffinder.commission_periods cp"
    q += " WHERE cp.commission_period_id =" + str(period_id)
    q_res = queryDB(q, host='prod', db= 'ffinder')

    for column, value in q_res.items():
        dates[column] = value.strftime('%Y-%m-%d')

    return dates


if __name__ == '__main__':
    pprint(getFunnelInfo('500'))
