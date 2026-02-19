import requests
from datetime import datetime
from credentials import Credentials
import smtplib
import time

FROM_EMAIL = Credentials.from_email
TO_EMAIL = Credentials.to_email
SMTP = Credentials.smtp_host
MY_PW = Credentials.pw

LATITUDE = 42.360081
LONGITUDE = -71.058884

def is_iss_in_radar():
    """Sends a request to get current ISS position AND checks if
    the current ISS position is within +5 and -5 of current position."""
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])
    iss_position = (iss_latitude, iss_longitude)
    print(f"ISS current pos:{iss_position}")
    current_position = (LATITUDE, LONGITUDE)
    print(f"My current pos: {current_position}")

    x_diff = current_position[0] - iss_position[0]
    y_diff = current_position[1] - iss_position[1]
    print(x_diff, y_diff)

    # Your position is within +5 or -5 degrees of the ISS position.
    if abs(x_diff) <= 5 and abs(y_diff) <= 5:
        print("ISS is overhead! O.O")
        return True
    else:
        print("ISS not currently in radar...")
        return False

def is_night():
    """Sends a request to get sunrise and sunset times of current location, fetches current time,
    returns True if the sun has set at the current time, or False if otherwise."""
    parameters = {
        "lat": LATITUDE,
        "lng": LONGITUDE,
        "formatted": 0
    }
    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

    time_now = datetime.now().hour
    if time_now <= sunrise or time_now >= sunset:
        print("It's dark out now.")
        return True
    else:
        print("It's too bright out still.")
        return False

def send_email():
    with smtplib.SMTP(SMTP) as connection:
        # TLS Transport Layer Security - Securing our connection to our email server
        connection.starttls()
        connection.login(user=FROM_EMAIL, password= MY_PW)
        connection.sendmail(
            from_addr=FROM_EMAIL,
            to_addrs=TO_EMAIL,
            msg=f"Subject: Look up!!!\n\n"
                f"Look up in the sky for possible ISS sighting! ;)")


while True:
    time.sleep(60)
    if is_iss_in_radar() and is_night():
        print("Look up in the sky!\n\nSending Email...")
        send_email()