import requests
import re
import csv
import sys
#import numpy as np
import pandas as pd

def show_progress(process_name,i,total):
    sys.stdout.write('\r%s: %d out of %d are processed' % (process_name,i,total))

def read_csv_file(file_name):
    with open(path+file_name,'r') as csv_file:
        pns=csv.reader(csv_file, delimiter=',')
        patent_numbers=[]
        for pn in pns:
            patent_numbers.append(pn)

    return patent_numbers

def get_patent(patent_number):
    url = 'https://patents.google.com/patent/US'+patent_number[0].replace(',','')+'/en'
    text = requests.get(url).text
    return text

def get_count(sign,text):
    try:
        count=text.count(sign)
    except:
        count=0
    return count

def find_date(event,text):
    index_end = []
    for m in re.finditer(event, text):
        index_end.append(m.end())
    try:
        date= date_pattern.findall(text[index_end[0] - 100:index_end[0]])[0]
    except:
        date:"no-date"
    return date

def get_patent_citation_number(sign,text):
    try:
        citation_index=text.index(sign)
        citation_number=citation_pattern.findall(text[citation_index:citation_index+ len(sign)+ 6])
        citation_number=int(citation_number[0][1:-1])
    except:
        citation_number=0

    return citation_number

def get_claim_number(sign,text):
    try:
        citation_index=text.index(sign)
        citation_number=clami_pattern.findall(text[citation_index:citation_index+ len(sign)+ 6])
        citation_number=int(citation_number[0][1:-1])
    except:
        citation_number=0

    return citation_number

def get_patent_classes(text):
    try:

        citation_index= cpc_class_pattern.finditer(text)
        end_index=[]
        for ind in citation_index:
            end_index.append(ind.end())

        cpc_classes=[]
        for ind in end_index:
            i=0
            while text[ind+i]!='<': i+=1
            cpc_classes.append(text[ind:ind+i])

        cpc_classes_picked=[]
        for i in range(len(cpc_classes)-1):
            if(cpc_classes[i][-2:]=='00'):
                cpc_classes[i]=cpc_classes[i][:-1]
            if (cpc_classes[i] not in cpc_classes[i+1]):
                cpc_classes_picked.append(cpc_classes[i])
        cpc_classes_picked.append(cpc_classes[-1])
    except:
        cpc_classes_picked=[]

    return cpc_classes_picked

def data_extraction(patent_numbers):
    df= pd.DataFrame(columns=column_titles)
    for i in range(len(patent_numbers)):
        show_progress('data extraction', i, len(patent_numbers))
        data = []
        patent_data = get_patent(patent_numbers[i])
        data.append(company_name)
        data.append((patent_numbers[i][0]))
        data.append(get_count('scheme="inventor"',patent_data)) #number_of_inventors
        data.append(find_date('Priority to', patent_data))       #first_priority_date
        data.append(find_date('Application filed',patent_data))  #application_file_date
        data.append(find_date('Publication of',patent_data))     #publication_date
        data.append(find_date('Application granted', patent_data)) #application_granted_date
        data.append(find_date('expiration<',patent_data))          #expiration_date
        data.append(get_patent_citation_number('>Citations',patent_data) + get_patent_citation_number('Family Cites Families',patent_data)) #patent_citations_number
        data.append(get_patent_citation_number('Non-Patent Citations',patent_data))  #non_patent_citation_number
        data.append(get_patent_citation_number('Families Citing this family',patent_data))  #number_cited_by
        data.append(get_count('similarDocuments',patent_data))  #number_of_similar_documents
        data.append(get_patent_citation_number('Child Applications',patent_data))  #child_applications_number
        data.append(get_patent_citation_number('Priority Applications',patent_data))  #priority_applications_number
        data.append(get_patent_citation_number('Applications Claiming Priority',patent_data)) #applications_claiming_priority_number
        data.append(len(get_patent_classes(patent_data)))  #patent_cpc_classes
        data.append(get_claim_number('"count"',patent_data))  #number_of_claims
        df = df.append(pd.Series(data, index=column_titles), ignore_index=True)
    return df

def write_to_csv(file_name,data):
    data.to_csv(path+file_name, sep=',')


######## settings
path='D:\\Projects\\Mahour\\'
patent_numbers_file='patent_numbers.csv'
patent_data_file='patent_data.csv'
dates=[]
date_pattern = re.compile(r"\d{4}\-\d{2}\-\d{2}")
citation_pattern=re.compile(r"\(\d.*\)")
cpc_class_pattern=re.compile(r"\d*(\"Code\">)")
clami_pattern=re.compile(r"\>\d.*\<")
number_of_data_type=16
company_name='Apple'

column_titles= ['Company','patent numbe','inventors', 'first priority date','file date','publication date',
                 'grant date','expiration date','patent citation','non patent citation','cited by','similar docs','child applications',
                'Applications Claiming Priority','priority application','cpc classes','claims']


#################      Main
patent_numbers= read_csv_file(patent_numbers_file)
data=data_extraction(patent_numbers)
write_to_csv(patent_data_file,data)