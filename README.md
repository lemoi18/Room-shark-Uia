# Room Reservation Automation Script



## This is now deprecated since UIA changed their booking system.
This Python script automates the process of booking a room via the university's web interface, utilizing Selenium for browser automation. The script logs in via Feide, selects the appropriate date and time, and submits the reservation request for a specified room.

## Features

- Automated login via Feide.
- Room reservation based on provided date, time, and duration.
- Headless browser operation for use on servers without a GUI.
- Logging to both console and file for easier debugging.

## Requirements

- Python 3.x
- The following Python libraries:
  - selenium
  - argparse
  - requests
  - pyvirtualdisplay
- ChromeDriver (Ensure the correct version of ChromeDriver is installed and added to your PATH)

## Installation

1. Clone the repository:
   git clone [https://github.com/yourusername/room-reservation-automation.git](https://github.com/lemoi18/Room-shark-Uia.git)
   cd Room-shark-Uia

2. Install the required Python packages:
   pip install -r requirements.txt

3. Download and install ChromeDriver:
   - Ensure that the version of ChromeDriver matches your installed version of Chrome.
   - Add the chromedriver to your system's PATH.


## Usage

Run the script from the command line with the following options:

python main.py <username> <password> --starttime <start_time> --room <room_id> --duration <duration_hours>

### Command-Line Arguments

- <username>: Your Feide username.
- <password>: Your Feide password.
- --starttime: Start time for the reservation (either 8 or 12).
- --room: The ID of the room you wish to book (e.g., A3055).
- --duration: Duration of the reservation in hours (default is 4).

### Example

To book room A3055 starting at 8 AM for 4 hours:
python TimeEdit.py your_username your_password --starttime 8 --room A3055 --duration 4

## Logging

Logs are saved in a file named debug.log in the script's directory. This log file will include detailed information on the script's execution, including any errors encountered.

## Troubleshooting

- Ensure that ChromeDriver is compatible with your installed Chrome version.
- If the script fails to find an element, it may be due to changes in the web interface. Review the relevant sections of the script and update the element selectors as needed.
- Review debug.log for detailed error messages and stack traces.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
