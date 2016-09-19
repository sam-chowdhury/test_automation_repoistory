'''
List of URLs to use in different test cases

When editing this file, please make sure to review the appropriate section
to insert a new list or dictionary of values.
'''

##########
# Retail #
##########

# Retail site base URLs
retail_base_urls = {
    'FF' : 'https://www.forcefactor.com',
    'FM' : 'https://www.femmefactor.com',
    'PL' : 'https://www.peaklife.com',
    'PS' : 'https://www.probioslim.com',
    'SB' : 'https://www.stagesofbeauty.com'
}

# Terms URLS
terms_ext = '/terms'
terms_ext_2 = '/terms_and_conditions'

ff_terms_url = retail_base_urls['FF'] + terms_ext
fm_terms_url = retail_base_urls['FM'] + terms_ext
pl_terms_url = retail_base_urls['PL'] + terms_ext_2
ps_terms_url = retail_base_urls['PS'] + terms_ext
sb_terms_url = retail_base_urls['SB'] + terms_ext

all_terms_urls = [ff_terms_url, fm_terms_url, pl_terms_url, ps_terms_url, sb_terms_url]


# Email/Subscription URLS
subscription_url_ext = ['/opt-out/marketing-emails/', '/opt-out/newsletters/', '/opt-out/all/', '/email-preferences/']

subscription_urls_FF = [retail_base_urls['FF']+ext for ext in subscription_url_ext]
subscription_urls_PL = [retail_base_urls['PL']+ext for ext in subscription_url_ext]
subscription_urls_FM = [retail_base_urls['FM']+ext for ext in subscription_url_ext]
subscription_urls_PS = [retail_base_urls['PS']+ext for ext in subscription_url_ext]
subscription_urls_SB = [retail_base_urls['SB']+ext for ext in subscription_url_ext]

all_subscription_urls = [subscription_urls_FF, subscription_urls_PL, subscription_urls_SB,
                         subscription_urls_FM, subscription_urls_PS]


# Product Pages
ff_urls = ['/shirts', '/bundles', '/bundles/ultimate_recovery_2', '/bundles/daily_health', '/bundles/powerhousestack',
           '/test_x180', '/volcano', '/factor_2', '/force_factor', '/test_x180_alpha','/test_x180_ignite','/cannabol',
           '/brx_br_40', '/ramp_up', '/multivitamin','/omega3', '/glutamine', '/gainzzz', '/shaker_bottle']
pl_urls = ['/somnapure', '/somnapure_pm', '/sleep_book', '/puritea', '/prostate', '/testosterone',
           '/somnapure_clinical_strength','/joint']
sb_urls = ['/adaptive-tripeptide-serum', '/radiance', '/harmony', '/elegance', '/grace']
sb_prod_ext = ['/hydrate-treat/treatment-cream', '/cleanse/cleanser', '/cleanse/scrub', '/hydrate-treat/serum' ]
fm_urls = ['/body_fit', '/body_sleek', '/body_smart', '/body_bliss', '/body_beauty', '/body_pro']
ps_urls = ['/probioslim', '/psyllium-fiber', '/yacon-root', '/premium-bundle', '/weight-loss-bundle',
           '/digestive-enzyme-complex','/garcinia-cambogia']

prefix = '/products'
product_urls_FF = [retail_base_urls['FF']+prefix+ext for ext in ff_urls]
product_urls_PL = [retail_base_urls['PL']+prefix+ext for ext in pl_urls]
product_urls_FM = [retail_base_urls['FM']+prefix+ext for ext in fm_urls]
product_urls_PS = [retail_base_urls['PS']+prefix+ext for ext in ps_urls]
prefix = '/shop'
product_urls_SB = [retail_base_urls['SB']+prefix+ext for ext in sb_urls]

all_product_urls = [product_urls_FF, product_urls_PL, product_urls_SB, product_urls_FM, product_urls_PS]

# Checkout pages for entering customer info

checkout_ext    = '/pay'
checkout_ext_2  = '/checkout'

#######
# CRM #
#######

crm_base_url = 'https://www.bigfishcrm.com'

crm_urls = {'search'        : crm_base_url + '/search',
            'issues'        : crm_base_url + '/issues',
            'old new order' : crm_base_url + '/new_order'}

####################
# Additional Sites #
####################

'''
List of additional customer facing site.
Ticket to Retrieve full list: TECH-20126
'''

secure_sites_list = ['www.forcefactorignite.com']

psp_sites_list = ['www.thecleverowl.com/']

all_sites_list = [secure_sites_list, psp_sites_list]
