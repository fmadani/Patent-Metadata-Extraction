import requests
import re
import sys
import html2text
#import pdb
import csv



def url_first_page_query(company_name,date_start, date_end):
    url="http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=0&p=1&f=S&l=50&Query=%28AN%2F"+company_name+"+AND+ISD%2F"+date_start+"-%3E"+date_end+"%29&d=PTXT"
    return url

def url_other_page_query(company_name,date_start, date_end,page_number):
    url = "http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=0&f=S&l=50&d=PTXT&OS=+%28AN%2F" + company_name + "+AND+ISD%2F" + date_start + "-%3E" + date_end + "%29&RS=%28AN%2F" + company_name + "+AND+ISD%2F" + date_start + "-%3E" + date_end + "%29&Query=+%28AN%2F" + company_name + "+AND+ISD%2F" + date_start + "-%3E" + date_end + "%29&TD=17063&Srch1=%28" + company_name + ".ASNM.+AND+%40PD%3E%3D" + date_start + "%3C%3D" + date_end + "%29&NextList" + str(
        page_number) + "=Next+50+Hits"
    return url

def patents_total_number_extraction(url,char):
    text = requests.get(url,headers=headers).text
    index_end=[]
    #pdb.set_trace()
    for m in re.finditer(char,text):
        index_end.append(m.end())

    total_number_of_patents=int(re.findall('\d+',text[index_end[0]:index_end[0]+15])[0])
    return total_number_of_patents

def patent_number_found(url):
    text = requests.get(url,headers=headers).text
    text = h.handle(text) # h is defined in the setting. h convert html to text.
    patent_numbers.extend(pattern.findall(text))

def patent_number_extraction():
    for i in range(1, int(total_number_of_patents / 50) + 2):
        sys.stdout.write('\rnumber is %d out of %d' % (i * 50, total_number_of_patents))
        if i == 1:
            url = url_first_page_query(company_name, date_start, date_end)
            patent_number_found(url)
        else:
            page_number = i
            url = url_other_page_query(company_name, date_start, date_end, page_number)
            patent_number_found(url)

def save_to_csv(file_name,field_name,data):
    with open(path+file_name,'w') as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n')

        writer.writerow([field_name])
        for item in data:
            writer.writerow([item])



#############            Settings
date_start='20090101'           #Enter dates in form of yyyyddmm without any other character
date_end='20183112'
company_name='apple'
path='D:\\Projects\\Mahour\\'
character_indicate_total_number_of_patents="out of "

page_number=0
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}

h = html2text.HTML2Text()
h.ignore_links = False

pattern = re.compile(r"\d\s\|\s\[(.*)\]") #pattern of patent numbers like " | [D38,345,543]"

file_name_to_save_patent_numbers='patent_numbers.csv'


total_number_of_patents=patents_total_number_extraction(url_first_page_query(company_name,date_start,date_end),character_indicate_total_number_of_patents)
patent_numbers=[]


####### Main Module
patent_number_extraction()
save_to_csv(file_name_to_save_patent_numbers,'patent number',patent_numbers)
