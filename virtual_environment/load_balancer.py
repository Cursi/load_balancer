import sys
import json
import requests

EXPECTED_NUMBER_OF_ARGUMENTS = 3
NUMBER_OF_REQUESTS = None
BASE_URL = None

ERROR_INVALID_NUMBER_OF_REQUESTS = 1
ERROR_INVALID_URL = 2
ERROR_HTTP_REQUEST = 3

HTTP_OK_STATUS_CODE = 200

def PrintUsage():
    print("Usage: python <NUMBER_OF_REQUESTS> <FORWARDING_UNIT_BASE_URL>")

def PrintError(error_code):
    if error_code == ERROR_INVALID_NUMBER_OF_REQUESTS:
        print("NUMBER_OF_REQUESTS is not an integer!")
    elif error_code == ERROR_INVALID_URL:
        print("FORWARDING_UNIT_BASE_URL is not a valid URL!")
    elif error_code == ERROR_HTTP_REQUEST:
        print("HTTP request to FORWARDING_UNIT_BASE_URL did not respond with " + HTTP_OK_STATUS_CODE + "!")

def StartLoadBalancer():
    print("We're good to go with " + str(NUMBER_OF_REQUESTS) + " requests to " + BASE_URL)

if __name__ == "__main__":
    if len(sys.argv) == EXPECTED_NUMBER_OF_ARGUMENTS:
        BASE_URL = sys.argv[2]

        try:
            NUMBER_OF_REQUESTS = int(sys.argv[1])
            try:
                if requests.get(url = BASE_URL).status_code == HTTP_OK_STATUS_CODE:
                    StartLoadBalancer()
                else:
                    PrintError(ERROR_HTTP_REQUEST)
            except:
                PrintError(ERROR_INVALID_URL)
        except:
            PrintError(ERROR_INVALID_NUMBER_OF_REQUESTS)
    else:
        PrintUsage()