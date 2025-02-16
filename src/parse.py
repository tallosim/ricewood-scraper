import datetime
from bs4 import BeautifulSoup

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.renderers.json import JSONBlockOutput

WEEKDAYS = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
MONTHS = ["januar", "februar", "marts", "april", "maj", "juni", "juli", "august", "september", "oktober", "november", "december"]

def load_converter():
    '''Load the PDF converter'''

    config_parser = ConfigParser({"output_format": "json"})
    return PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service(),
    )


def replace_br_tags(cell: BeautifulSoup) -> BeautifulSoup:
    '''Replace all <br> tags with a space'''

    [tag.replace_with(" ") for tag in cell.find_all("br")]
    return cell


def parse_date(date: str) -> datetime.date:
    '''Parse a date in the format e.g. "21. februar 2025, Uge 8"'''

    parts = date.split(",")[0].split()
    if len(parts) != 3:
        raise ValueError(f"Date {date} is not in the expected format")

    day = int(parts[0].rstrip("."))
    month = MONTHS.index(parts[1].lower()) + 1
    year = int(parts[2])

    return datetime.date(year, month, day)


def parse_menu_page(page: JSONBlockOutput) -> dict | None:
    '''Parse a menu page and return a dictionary with the menu'''

    menu = {}

    # Find the weekday in the title
    weekday_soup = BeautifulSoup(page.children[0].html, "html.parser")
    weekday = weekday_soup.get_text()
    if not any(weekday.lower() == d for d in WEEKDAYS):
        return None

    menu["weekday"] = weekday

    # Find the date
    date_soup = BeautifulSoup(page.children[1].html, "html.parser")
    date = date_soup.find("p")
    if date is None:
        return None

    menu["date"] = parse_date(date.get_text()).isoformat()

    # Find the dishes
    dishes_soup = BeautifulSoup(page.children[2].html, "html.parser")
    if dishes_soup.find("table") is None or dishes_soup.find("table").find("tbody") is None:
        return None

    dishes = dishes_soup.find("table").find("tbody")
    menu["dishes"] = []
    for row in dishes.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) == 2:
            category = replace_br_tags(cells[0]).get_text()
            dish = replace_br_tags(cells[1]).get_text()
            if category and dish:
                menu["dishes"].append({"category": category, "dish": dish})

    return menu


def parse_menu_pdf(pdf_path: str) -> list[dict]:
    '''Parse the menu PDF and return a list of menu pages'''

    # Load the PDF converter
    converter = load_converter()

    # Convert the PDF to JSON
    pages = converter(pdf_path).children

    # Parse the menu pages and filter out any that are not valid
    parsed_pages = [parse_menu_page(page) for page in pages]
    parsed_pages = [page for page in parsed_pages if page is not None]

    return parsed_pages
