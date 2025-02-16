import os
import requests
from bs4 import BeautifulSoup

def download(year: int, week: int, output_dir: str = 'menus') -> str:
	'''Download the menu for a given year and week'''

	# Download the menu page for the given year and week
	page_url = f'https://ricewood.dk/menu/?year={year}&uge={week}'
	page = requests.get(page_url)
	if page.status_code != 200:
		raise Exception('Failed to download page')
	
	# Find the URL of the PDF menu
	soup = BeautifulSoup(page.content, 'html.parser')
	menu_url = 'https://ricewood.dk' + soup.find('div', class_='menu_pdf').find('a')['href']

	# Download the PDF menu
	menu = requests.get(menu_url)
	if menu.status_code != 200:
		raise Exception('Failed to download menu')
	
	# Save the PDF menu to a file
	file_name = os.path.join(output_dir, f'menu_{year}_{week}.pdf')
	os.makedirs(output_dir, exist_ok=True)
	with open(file_name, 'wb') as file:
		file.write(menu.content)

	return file_name