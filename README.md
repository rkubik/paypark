# ParkPlus

ParkPlus is an open-source Automated Parking System written in Python.

![PayPark Web Interface](/paypark-web.png?raw=true "PayPark Web Interface")

## Setup

Debian packaging will be the preferred way of deployment. Until that is setup
`pip` and native Debian python packages can be used.

### Dependencies

    sudo apt-get install python-pip
    sudo pip install

### Configuration

In the root directory of the project create a file `paypark.ini`:

    SECRET_KEY=''
    TIMEZONE='American/Edmonton'
    LOCALE='en_US.utf8'
    COUNTRY_CODE='CA'
    CURRENCY_CODE='CAD'
    CURRENCY_SYMBOL='$'
    ACCOUNT_TOP_UP='500,1000,2000,3000,5000'

    SMS_SERVICE='twilio'
    TWILIO_NUMBER=''
    TWILIO_HOST='0.0.0.0'
    TWILIO_PORT=9000
    TWILIO_MSSID=''
    TWILIO_SID=''
    TWILIO_AUTH_TOKEN=''

    LICENSE_PLATE_MAX=5
    LICENSE_PLATE_PER_PAGE=10
    LICENSE_PLATE_REGEX='^[A-Z]{3}[0-9]{3}$'
    LICENSE_PLATE_HELP='Enter without spaces or hyphens (Example: AAA123)'

    PHONE_NUMBER_MAX=3
    PHONE_NUMBER_PER_PAGE=10
    PHONE_NUMBER_REGEX='^[0-9]{11}$'
    PHONE_NUMBER_HELP='Phone number with country code (Example: 12345678901)'

    HISTORY_PER_PAGE=10

    PAYMENT_SERVICE='stripe'
    STRIPE_API_KEY=''

    MAIL_SERVER='localhost'
    MAIL_USERNAME=''
    MAIL_PASSWORD=''
    MAIL_FROM_EMAIL='info@paypark.com'
    MAIL_FROM_NAME='PayPark Automated System'

### Running

Create and populate demo database:

    python db.py --init --demo

Run the web application:

    python app.py

Login to the web interface at `http://localhost:8085`:

    Email: demo@demo.com
    Password: demo

On another terminal, run the Twilio SMS API service:

    python sms.py

The Twilio SMS API service is the default PayPark SMS service. You do not
need a Twilio account to test and use the API service:

    curl --form 'Body=start 1000' --form 'From=12345678901' --form 'MessagingServiceSid=' localhost:9000
    {
        "error": "Missing: MessagingServiceSid"
    }

Make sure you enter a value for `MessagingServiceSid` in the config file.

    curl --form 'Body=start 1000' --form 'From=12345678901' --form 'MessagingServiceSid=12345' localhost:9000
    {
        "error": "Phone number not registered."
    }

In the web portal login as the demo user and add a phone number.

    curl --form 'Body=start 1000' --form 'From=12345678901' --form 'MessagingServiceSid=12345' localhost:9000
    <?xml version="1.0" encoding="UTF-8"?><Response><Message>Parking is free.</Message></Response>

## SMS API Services

PayPark is configured to support different SMS API services. Currently PayPark supports:

- Twilio

