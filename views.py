from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from urllib.parse import quote, unquote
import pandas as pd
import requests
from bs4 import BeautifulSoup
import openpyxl
from io import BytesIO
import base64
import logging
from .models import ScrapedData

# Set up logging
logger = logging.getLogger(__name__)



def firstscreen(request):
    return render(request, 'scraper/firstscreen.html')

def index(request):
    return render(request, 'scraper/index.html')


def scrape(request):
    if request.method == 'POST':
        link = request.POST.get('link')
        if not link:
            return JsonResponse({'error': 'Invalid request'}, status=400)
        encoded_link = quote(link, safe='')
        return redirect(reverse('processing', args=[encoded_link]))

    return JsonResponse({'error': 'Invalid request'}, status=400)

def processing(request, link):
    decoded_link = unquote(link)
    return render(request, 'scraper/processing.html', {'link': decoded_link})

def generate_download_link(request, link):
    try:
        decoded_link = unquote(link)
        logger.info(f"Fetching data from URL: {decoded_link}")
        response = requests.get(decoded_link)
        response.raise_for_status()  # Raise an exception for HTTP errors

        soup = BeautifulSoup(response.content, 'html.parser')

        data = {
            'Title': [soup.title.string if soup.title else 'No Title'],
            'Headings': [heading.get_text() for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])],
            'Paragraphs': [para.get_text() for para in soup.find_all('p')],
            'Links': [link.get('href') for link in soup.find_all('a', href=True)],
            'TextContent': [text for text in soup.stripped_strings],
            'Tables': []
        }

        # Process tables
        tables = soup.find_all('table')
        for table in tables:
            table_data = []
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                table_data.append(cell_texts)
            if table_data:
                data['Tables'].append(table_data)

        flat_data = []
        for key, values in data.items():
            if key == 'Tables':
                for i, table in enumerate(values):
                    for row in table:
                        flat_data.append({'Type': f'Table {i+1}', 'Content': row})
            else:
                for value in values:
                    flat_data.append({'Type': key, 'Content': value})

        df = pd.DataFrame(flat_data)

        # Save scraped data to database
        scraped_data = ScrapedData.objects.create(url=decoded_link)
        for key, value in data.items():
            setattr(scraped_data, key.lower(), value)
        scraped_data.save()

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='ScrapedData')
            for i, table in enumerate(data['Tables']):
                # Check if the table has a header
                if len(table) > 1 and len(table[0]) == len(table[1]):
                    table_df = pd.DataFrame(table[1:], columns=table[0])  # Use first row as header
                else:
                    table_df = pd.DataFrame(table)
                table_df.to_excel(writer, index=False, sheet_name=f'Table {i+1}')

        file_data = base64.b64encode(output.getvalue()).decode('utf-8')
        request.session['file_data'] = file_data

        download_url = reverse('download_excel')
        logger.info(f"Download URL generated: {download_url}")
        return JsonResponse({'download_url': download_url})
    except Exception as e:
        logger.error(f"Error generating download link: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def download_excel(request):
    file_data = request.session.get('file_data')
    if not file_data:
        return JsonResponse({'error': 'File not found'}, status=404)

    output = BytesIO(base64.b64decode(file_data))
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=scraped_data.xlsx'
    return response

















































































#IT ALSO WORKS but it doesnt give the table...

'''# Create your views here.
# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from urllib.parse import quote, unquote
import pandas as pd
import requests
from bs4 import BeautifulSoup
import openpyxl
from io import BytesIO
import base64
import logging
from .models import ScrapedData

# Set up logging
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'scraper/index.html')

def scrape(request):
    if request.method == 'POST':
        link = request.POST.get('link')
        if not link:
            return JsonResponse({'error': 'Invalid request'}, status=400)
        encoded_link = quote(link, safe='')
        return redirect(reverse('processing', args=[encoded_link]))

    return JsonResponse({'error': 'Invalid request'}, status=400)

def processing(request, link):
    decoded_link = unquote(link)
    return render(request, 'scraper/processing.html', {'link': decoded_link})


def generate_download_link(request, link):
    try:
        decoded_link = unquote(link)
        logger.info(f"Fetching data from URL: {decoded_link}")
        response = requests.get(decoded_link)
        response.raise_for_status()  # Raise an exception for HTTP errors

        soup = BeautifulSoup(response.content, 'html.parser')

        data = {
            'Title': [soup.title.string if soup.title else 'No Title'],
            'Headings': [heading.get_text() for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])],
            'Paragraphs': [para.get_text() for para in soup.find_all('p')],
            'Links': [link.get('href') for link in soup.find_all('a', href=True)],
            'TextContent': [text for text in soup.stripped_strings]
        }

        flat_data = []
        for key, values in data.items():
            for value in values:
                flat_data.append({'Type': key, 'Content': value})

        df = pd.DataFrame(flat_data)

        # Save scraped data to database
        scraped_data = ScrapedData.objects.create(url=decoded_link)
        for key, value in data.items():
            setattr(scraped_data, key.lower(), value)
        scraped_data.save()

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='ScrapedData')
        
        file_data = base64.b64encode(output.getvalue()).decode('utf-8')
        request.session['file_data'] = file_data

        download_url = reverse('download_excel')
        logger.info(f"Download URL generated: {download_url}")
        return JsonResponse({'download_url': download_url})
    except Exception as e:
        logger.error(f"Error generating download link: {e}")
        return JsonResponse({'error': str(e)}, status=500)



def download_excel(request):
    file_data = request.session.get('file_data')
    if not file_data:
        return JsonResponse({'error': 'File not found'}, status=404)

    output = BytesIO(base64.b64decode(file_data))
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=scraped_data.xlsx'
    return response
'''







































































































































































































































