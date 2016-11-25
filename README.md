# PayPark

PayPark is an open-source Automated Parking System written in Python.

![PayPark Web Interface](/screenshots/paypark-dashboard.png?raw=true "PayPark Web Interface")

## Setup

Debian packaging will be the preferred way of deployment. Until that is setup
`pip` and native Debian python packages can be used.

### Dependencies

    sudo apt-get install python-pip
    sudo pip install -r requirements.txt

### Configuration

In the root directory of the project copy `paypark.ini.example` to `paypark.ini`
and set the `SECRET_KEY`.

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

PayPark is configured to support different SMS API services to send and
receive SMS messages:

- Twilio
- BulkSMS
