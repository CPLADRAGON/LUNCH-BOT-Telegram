import holidays
from datetime import date
import pytz

def test_holiday_logic():
    sg_holidays = holidays.country_holidays('SG')
    
    # Test cases: (Date, Expected Result)
    test_dates = [
        (date(2026, 1, 1), True),   # New Year (Holiday)
        (date(2026, 4, 11), False),  # Saturday (Weekend)
        (date(2026, 4, 12), False),  # Sunday (Weekend)
        (date(2026, 4, 13), True),   # Monday (Work day)
    ]
    
    for d, is_working in test_dates:
        is_holiday = d in sg_holidays
        is_weekend = d.weekday() >= 5
        result = not is_holiday and not is_weekend 
        
        # Invert for "Not working day"
        print(f"Date: {d} | Holiday: {is_holiday} | Weekend: {is_weekend} | Should Send Poll: {result}")

if __name__ == "__main__":
    test_holiday_logic()
