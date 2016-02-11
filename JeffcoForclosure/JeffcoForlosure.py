#Tested with python 2.6

import urllib2
import mechanize as mech
import lxml.html
from lxml import etree



def Jeffco_search_url():
#TODO need to add cookies, and check if we are already there
    """
    accesses the page to do a search for forclosure properties
    returns browser object on search page.
    """
    jeffco_start_url = 'http://gts.co.jefferson.co.us/'
    br = mech.Browser()
    #br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6')]
    br.open(jeffco_start_url)
    br.select_form(name="aspnetForm")
    br.submit()
    return br

def jeffco_search(search_page, reset_form, foreclosure_number, 
                  grantors_name, owners_name, zipcode, street, subdivision, 
                  status, ned_from_date, ned_to_date, sold_from_date, 
                  sold_to_date):
#TODO add other search fields, date in important for upcoming sales.
#TODO need to make sure the form is blank
    """
    Search Jeffco forclosure list
    return browser object
    """
    #if reset_form:
        #re = search_page.submit(name="ctl00$ContentPlaceHolder1$btnReset")
        
    search_page.select_form(name="aspnetForm")
    search_page['ctl00$ContentPlaceHolder1$txtForeclosureNumber'] = \
               foreclosure_number
    search_page['ctl00$ContentPlaceHolder1$txtGrantorsName'] = grantors_name
    search_page['ctl00$ContentPlaceHolder1$txtOwersName'] = owners_name
    search_page['ctl00$ContentPlaceHolder1$txtZipCode'] = zipcode
    search_page['ctl00$ContentPlaceHolder1$txtStreet'] = street
    search_page['ctl00$ContentPlaceHolder1$txtSubdivision'] = subdivision
    prop_status = search_page.form.possible_items("ctl00$ContentPlaceHolder1$ddStatus")
    search_page.form.set(True, prop_status[prop_status.index(status)] , \
                "ctl00$ContentPlaceHolder1$ddStatus")
    search_page['ctl00$ContentPlaceHolder1$txtNedDate1'] = ned_from_date
    search_page['ctl00$ContentPlaceHolder1$txtNedDate2'] = ned_to_date
    search_page['ctl00$ContentPlaceHolder1$txtCurrentScheduledSaleDateFrom'] = \
               sold_from_date
    search_page['ctl00$ContentPlaceHolder1$txtCurrentScheduledSaleDateTo'] = \
               sold_to_date
    search_page.submit(name="ctl00$ContentPlaceHolder1$btnSearch")
    return search_page

def jeffco_number_results(result_page):
    # only gets the forclosure numbers from the first page. 
    page_xml = lxml.html.parse(result_page.response())
    #get the number of records returned from search
    number_results_ele ='//*[@id="ctl00_ContentPlaceHolder1_Label1"]'
    #parse and return the string "Your Search Returned 398 Records."
    return page_xml.xpath(number_results_ele)[0].text.rsplit(' ')[3]
    
    
def jeffco_parse_results(result_page):
    """
    Returns 1 page of forclosure search results as a list of tuples
    http://gts.co.jefferson.co.us/SearchDetails.aspx?id=320024312&fn=J1001745
    """
    number_record = jeffco_number_results(result_page)
    page_xml = lxml.html.parse(result_page.response())
    result_table_el = '//*[@id="ctl00_ContentPlaceHolder1_gvSearchResults"]'
    result_table = page_xml.xpath(result_table_el)
    fnum = []
    forclosure_num = lambda row: row[0].text_content()
    #gets last part of link
    # http://gts.co.jefferson.co.us/SearchDetails.aspx?id=320024312&fn=J1001745"
    f_link = lambda row: row[0][0].get('href')
    first_last_and = lambda row: row[1].text_content()
    street = lambda row: row[2].text_content()
    zipcode = lambda row: row[3].text_content()
    subdivision = lambda row: row[4].text_content()
    balance_due = lambda row: row[5].text_content()
    status = lambda row: row[6].text_content()
    for row in result_table[0]:
        #make sure we are in the data and not in colum headings or other
        if row[0].text_content()[0]=='J':
            fnum.append((forclosure_num(row), f_link(row), first_last_and(row), street(row), 
                         zipcode(row), subdivision(row), balance_due(row), 
                         status(row)))
#TODO need to decide how best to look up the property record from the forclosure
#     The property scedule number nor the parcil id are part of the forclosure info
#     maybe the plus 4 zipcode
    return fnum, result_table

def jeffco_more_results(result_page):
    """
    checks if there is another page of search results
    """
    
    

#tests
br = Jeffco_search_url()
br = jeffco_search(br,True,'','','','','','','Sold','','','10/13/2009', '10/13/2010')
x, y = jeffco_parse_results(br)



#print(br.response().read())

#br['ctl00$ContentPlaceHolder1$ddStatus']= '"selected=""sold""'
#print(results.response().read())