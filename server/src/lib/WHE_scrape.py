import requests
import re

from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from io import BytesIO
from pdfminer.high_level import extract_text
from datetime import datetime

class WHE_Scrape:

    def __init__(self):
        self.URL = "https://wa-whatcomcounty.civicplus.com/Archive.aspx?AMID=43"
        self.html = requests.get(self.URL).text
        self.soup = BeautifulSoup(self.html, 'html.parser')
        
    def retrieve_pdf_data(self):
    # Finds all <a> tags in the html and extracts the links
    # that start with 'Archive.aspx?ADID'
        
        pdf_data = []
        for link in self.soup.find_all('a'):
            links = link.get('href')
        
            case_name = link.find_next('span').text.strip() if link.find_next('span') else None
            date = link.find_next_sibling('span').text.strip() if link.find_next_sibling('span') else None
            
            if links is not None and date is not None:
                link_list = links.split()
    
                for pdf_link in link_list:
                    if pdf_link.startswith('Archive.aspx?ADID'):
                        pdf_text = self.extract_text(pdf_link)

                        extracted_dates = self.extract_date(date)
                        hearing_date = extracted_dates['hearingDate']
                        decision_full_date = extracted_dates['decisionFullDate']
                        decision_year_only = extracted_dates['decisionYearOnly']

                        hearing_examiner = self.extract_hearing_examiner(pdf_text)['hearing_examiner_name']

                        pdf_data.append({
                            'link': pdf_link, 
                            'case_name': case_name, 
                            'hearing_date': hearing_date,
                            'decision_full_date': decision_full_date,
                            'decision_year_only': decision_year_only,
                            'hearing_examiner': hearing_examiner,
                            'pdf_text': pdf_text
                            })
        
        return pdf_data
    
    def extract_text(self, link):
        base_url = "https://wa-whatcomcounty.civicplus.com/"
        complete_link = base_url + link
        response = requests.get(complete_link)
        pdf_content = response.content
        
        text = extract_text(BytesIO(pdf_content)).strip()
        normalized_text = ' '.join(text.split())
        extracted_text = normalized_text.lower()
        
        return extracted_text
    
    def extract_date(self, date):
        hearing_date_pattern = r'Hearing Date (\d{1,2}[./]\d{1,2}[./]\d{2,4})'
        decision_date_pattern = r'Decision Date (\d{1,2}[./]\d{1,2}[./]\d{2,4})'
        decision_year_pattern = r'(\d{4})'

        hearing_date_match = re.search(hearing_date_pattern, date)
        decision_date_match = re.search(decision_date_pattern, date)
        decision_year_match = re.search(decision_year_pattern, date)

        hearing_date = self.format_date(hearing_date_match.group(1)) if hearing_date_match else 'Not listed.'
        decision_full_date = self.format_date(decision_date_match.group(1)) if decision_date_match else None
        decision_year_only = decision_year_match.group(1) if decision_year_match else 'Not listed.'

        return {
            'hearingDate': hearing_date, 
            'decisionFullDate': decision_full_date, 
            'decisionYearOnly': decision_year_only
            }
    
    def format_date(self, date):
        try:
            date_obj = datetime.strptime(date, '%m/%d/%Y')
        except ValueError:
            try:
                date_obj = datetime.strptime(date, '%m.%d.%y')
            except ValueError:
                return date
            
        formatted_date = date_obj.strftime('%B %d, %Y')
        return formatted_date

    def extract_hearing_examiner(self, pdf_text):
        pattern = r"DATED this [^\n]*?(\d{1,2}(?:st|nd|rd|th)? day of [A-Za-z]+\s+\d{4}[,.])[\s\S]*?([\w\s.]+),"
        match = re.search(pattern, pdf_text, re.IGNORECASE)
        
        if match:
            date = match.group(1)
            name_match = match.group(2)
            hearing_examiner_name = name_match.title().replace('.', '').replace('\n', '').replace('_', '').strip()
            return {'date': date, 'hearing_examiner_name': hearing_examiner_name}
        
        else:
            return {'hearing_examiner_name': 'Unable to locate.'}
                            
    def search_keyword(self, keyword):
        
        print(f'keyword: {keyword}')
        pdf_links = self.retrieve_pdf_data()
        search_results = []
        
        for link_info in pdf_links:
            pdf_text = link_info.get('pdf_text', '').lower()
            if keyword.lower() in pdf_text:
                print(f'keyword found in {link_info["case_name"]}')
                search_results.append(link_info)

        return search_results
    
    def get_metadata(self):
            
        base_url = "https://wa-whatcomcounty.civicplus.com/"
        
        try:
            # Creates a PyPDF2 reader object to extract the metadata
            link = 'Archive.aspx?ADID=15523'
            complete_link = base_url + link
            response = requests.get(complete_link)
            pdf_content = response.content

            pdf_reader = PdfReader(BytesIO(pdf_content))
            metadata = pdf_reader.metadata
            return metadata
        except:
            print("No metadata found.")

    def update_db(self):
        print("Updating database...")
        decision_list = []
        decisions = self.retrieve_pdf_data()
        for decision in decisions:
            decision_list.append(decision)
            print(decision_list)

whe_scrape = WHE_Scrape()