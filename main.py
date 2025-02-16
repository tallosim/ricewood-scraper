import os
import json
import argparse
import logging

from src.download import download
from src.parse import parse_menu_pdf

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

def main():
	parser = argparse.ArgumentParser(description='Download the menu for a given year and week')

	parser.add_argument('--year', type=int, help='The year of the menu')
	parser.add_argument('--week', type=int, help='The week of the menu')
	parser.add_argument('--output-dir', default='menus', help='The directory to save the menu PDFs')
	parser.add_argument('--output-file', default='menu_{year}_{week}.json', help='The file to save the parsed menu to')

	args = parser.parse_args()


	logger.info("Downloading menu for year %s, week %s", args.year, args.week)
	file_name = download(args.year, args.week, args.output_dir)
	logger.info("Downloaded to %s", file_name)

	logger.info("Starting to parse menu")
	menu = parse_menu_pdf(file_name)
	logger.info("Successfully parsed menu")
	
	output_file = args.output_file.format(year=args.year, week=args.week)
	output_path = os.path.join(args.output_dir, output_file)
	logger.info("Saving menu to %s", output_path)
	with open(output_path, 'w') as file:
		json.dump(menu, file, indent=4, ensure_ascii=False)

if __name__ == '__main__':
	main()