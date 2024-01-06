from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def parse_date(date_str: str, default_date: datetime) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
    except Exception as e:
        logger.error(f"Could not parse date {date_str}. Using default date {default_date}")
        logger.error(e)
        return default_date
