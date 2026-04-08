import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lunch_bot import is_last_working_day_of_month
from datetime import date

def test_last_working_day():
    print("Testing Monthly Reset Logic...")
    
    # Test April 2026 (April 30 is Thursday, last working day)
    d1 = date(2026, 4, 30)
    print(f"Is {d1} last working day? {is_last_working_day_of_month(d1)}")
    
    # Test April 29
    d2 = date(2026, 4, 29)
    print(f"Is {d2} last working day? {is_last_working_day_of_month(d2)}")

    # Test May 2026 (May 31 is Sunday, May 29 is Friday - last working day)
    d3 = date(2026, 5, 29)
    print(f"Is {d3} last working day? {is_last_working_day_of_month(d3)}")
    
    d4 = date(2026, 5, 30)
    print(f"Is {d4} last working day? {is_last_working_day_of_month(d4)}")

if __name__ == "__main__":
    test_last_working_day()
