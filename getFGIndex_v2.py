### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta
# from botocore.vendored import requests
import requests

## Functionality Helper Functions ###
def parse_float(n):
    """
    Securely converts a non-numeric value to float.
    """
    try:
        return float(n)
    except ValueError:
        return float("nan")
        
def get_btcprice():
    """
    Retrieves the current price of bitcoin in dollars from the alternative.me Crypto API.
    """
    bitcoin_api_url = "https://api.alternative.me/v2/ticker/bitcoin/?convert=USD"
    response = requests.get(bitcoin_api_url)
    response_json = response.json()
    price_dollars = parse_float(response_json["data"]["1"]["quotes"]["USD"]["price"])
    return price_dollars
    
def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']
    
def get_slot(intent_request, slotName):
    slots = get_slots(intent_request)
    if slots is not None and slotName in slots and slots[slotName] is not None:
        return slots[slotName]['value']['interpretedValue']
    else:
        return None    

def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']

    return {}

def elicit_intent(intent_request, session_attributes, message):
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitIntent'
            },
            'sessionAttributes': session_attributes
        },
        'messages': [ message ] if message != None else None,
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


def close(intent_request, session_attributes, fulfillment_state, message):
    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [message],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }
### Intents Handlers ###
def convert_dollars(intent_request):
    """
    Performs dialog management and fulfillment for converting from dollars to bitcoin.
    """
    # Gets slots' values
    session_attributes = get_session_attributes(intent_request)
    slots = get_slots(intent_request)
    amount = get_slot(intent_request, 'amount')
    # Get the current price of bitcoin in dolars and make the conversion from dollars to bitcoin.
    btc_value = parse_float(amount) / get_btcprice()
    btc_value = round(btc_value, 4)
    text = """Thank you for your information;
            you can get {} Bitcoins for your ${} dollars.
            """.format( btc_value, amount )
    message =  {
            'contentType': 'PlainText',
            'content': text
        }
    fulfillment_state = "Fulfilled"    
    return close(intent_request, session_attributes, fulfillment_state, message)  

### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    # Get the name of the current intent
    intent_name = intent_request['sessionState']['intent']['name']
    # Dispatch to bot's intent handlers
    if intent_name == "getFGIndex":
        return convert_dollars(intent_request)
    raise Exception("Intent with name " + intent_name + " not supported")

### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    return dispatch(event)