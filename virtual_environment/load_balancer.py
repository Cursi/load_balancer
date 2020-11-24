from datetime import datetime
import sys
import requests

import asyncio
import aiohttp

EXPECTED_NUMBER_OF_ARGUMENTS = 4
NUMBER_OF_REQUESTS = None
BASE_URL = None
POLICY_ID = None

ERROR_INVALID_NUMBER_OF_REQUESTS = 1
ERROR_INVALID_URL = 2
ERROR_HTTP_REQUEST = 3
ERROR_HEROKU_INSTANCE_WAKEUP = 4
ERROR_INVALID_POLICY_ID = 5

HTTP_OK_STATUS_CODE = 200
ERROR_EXIT_CODE = 1

NUMBER_OF_SERVICES = 5

cloudServices = {
    "asia": ["0", "1"],
    "emea": ["0"],
    "us": ["0", "1"]
}

cloudServicesBaseLatencies = {
    "asia": 520,
    "emea": 330,
    "us": 370
}

# Prints load balances command line usage
def PrintUsage():
    print("Usage: python <NUMBER_OF_REQUESTS> <FORWARDING_UNIT_BASE_URL> <POLICY_ID>")

# Prints the occured error message based on the code given through the execution
def PrintError(error_code):
    if error_code == ERROR_INVALID_NUMBER_OF_REQUESTS:
        print("NUMBER_OF_REQUESTS is not an integer!")
    elif error_code == ERROR_INVALID_URL:
        print("FORWARDING_UNIT_BASE_URL is not a valid URL!")
    elif error_code == ERROR_HTTP_REQUEST:
        print("HTTP request to FORWARDING_UNIT_BASE_URL did not respond with " + HTTP_OK_STATUS_CODE + "!")
    elif error_code == ERROR_HEROKU_INSTANCE_WAKEUP:
        print("Couldn't wake up all heroku instances!")
    elif error_code == ERROR_INVALID_POLICY_ID:
        print("POLICY_ID is not valid, should be 1, 2, 3, 4 or 5!")

# Returns the forwarding unit URL that will be GET requested 
def GetComputedURL(region=None, serverValue=None, isSpecificRequest=False):
    if isSpecificRequest == False:
        return BASE_URL + "/work"
    elif serverValue == None:
        return BASE_URL + "/work/" + region
    else:
        return BASE_URL + "/work/" + region + "/" + serverValue

# Wakes up heroku instances from idle
def WakeUpHerokuInstances():
    print("Waking up heroku instances...")

    for key in cloudServices:
        for serverValue in cloudServices[key]:
            currentWakeUpRequestURL = GetComputedURL(region=key, serverValue=serverValue, isSpecificRequest=True)
            
            response = requests.get(url = currentWakeUpRequestURL) 
            if response.status_code != HTTP_OK_STATUS_CODE:
                PrintError(ERROR_HEROKU_INSTANCE_WAKEUP)
                exit(ERROR_EXIT_CODE)
            else:
                print("Instance " + serverValue + " from " + key + " is UP!")

# Awaits for the async GET responses
async def AsyncGET(url):
    global max_response_time
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Sends all the requests to the service with lowest latency, EMEA 0
def GetSingleTrafficCoroutines():
    print("Running single traffic policy...")
    computedURL = GetComputedURL("emea", "0", True)
    print("Forwarding " + str(NUMBER_OF_REQUESTS) + " requests to " + computedURL)

    return [AsyncGET(computedURL) for _ in range(NUMBER_OF_REQUESTS)]

# Sends equally distributed requests to all 5 services
def GetEqualyDistributedCoroutines():
    print("Running equaly distributed traffic policy...")
    print("Forwarding " + str(NUMBER_OF_REQUESTS) + " requests to all services")

    coroutines = []

    for key in cloudServices:
        for serverValue in cloudServices[key]:
            currentRequestURL = GetComputedURL(region=key, serverValue=serverValue, isSpecificRequest=True)
            coroutines += [AsyncGET(currentRequestURL) for _ in range(int(NUMBER_OF_REQUESTS / NUMBER_OF_SERVICES))]

    return coroutines

# Sends distributed requests based on the base latency of each service
def GetBaseLatencyDistributedCoroutines():
    print("Running base latency distributed traffic policy...")
    coroutines = []

    totalBaseLatency = 0
    for baseLatency in cloudServicesBaseLatencies:
        totalBaseLatency += cloudServicesBaseLatencies[baseLatency]
        
    weights = {}
    totalWeights = 0

    for key in cloudServices:
        weights[key] = totalBaseLatency / cloudServicesBaseLatencies[key]
        totalWeights += weights[key]
    
    percentages = {}

    for key in cloudServices:
        percentages[key] = round(weights[key] / totalWeights * 100) / 100

    for key in cloudServices:
        for serverValue in cloudServices[key]:
            currentNumberOfRequests = round(NUMBER_OF_REQUESTS * percentages[key] / len(cloudServices[key]))
            print("Forwarding " + str(currentNumberOfRequests) + " requests to " + key + " " + serverValue)
            currentRequestURL = GetComputedURL(region=key, serverValue=serverValue, isSpecificRequest=True)
            coroutines += [AsyncGET(currentRequestURL) for _ in range(currentNumberOfRequests)]

    return coroutines

# Sends all the requests to the service with lowest latency, EMEA 0
def GetRandomTrafficCoroutines():
    print("Running random traffic policy...")
    computedURL = GetComputedURL()
    print("Forwarding " + str(NUMBER_OF_REQUESTS) + " requests to " + computedURL)

    return [AsyncGET(computedURL) for _ in range(NUMBER_OF_REQUESTS)]

# Sends all the requests to the service with lowest latency, EMEA 0
def GetRegionalRandomTrafficCoroutines():
    print("Running regional random traffic policy...")
    print("Forwarding " + str(NUMBER_OF_REQUESTS) + " requests to all services")

    coroutines = []

    for key in cloudServices:
        currentRequestURL = GetComputedURL(region=key, isSpecificRequest=True)
        coroutines += [AsyncGET(currentRequestURL) for _ in range(int(NUMBER_OF_REQUESTS / len(cloudServices)))]

    return coroutines

# Starts one of the load balancing policy based on command line argument and prints elapsed time for all requests
def StartLoadBalancer():
    print("Load balancing " + str(NUMBER_OF_REQUESTS) + " requests to " + BASE_URL + "\n")
    WakeUpHerokuInstances()
    print()

    loop = asyncio.get_event_loop()

    if POLICY_ID == 1:
        coroutines = GetSingleTrafficCoroutines()
    elif POLICY_ID == 2:
        coroutines = GetEqualyDistributedCoroutines()
    elif POLICY_ID == 3:
        coroutines = GetBaseLatencyDistributedCoroutines()
    elif POLICY_ID == 4:
        coroutines = GetRandomTrafficCoroutines()
    elif POLICY_ID == 5: 
        coroutines = GetRegionalRandomTrafficCoroutines()

    start=datetime.now()
    results = loop.run_until_complete(asyncio.gather(*coroutines))
    print("\nElapsed time for all requests: " + str(round((datetime.now() - start).total_seconds() * 1000)))

if __name__ == "__main__":
    if len(sys.argv) == EXPECTED_NUMBER_OF_ARGUMENTS:
        BASE_URL = sys.argv[2].strip("/")
        try:
            NUMBER_OF_REQUESTS = int(sys.argv[1])
            try:
                POLICY_ID = int(sys.argv[3])
                if POLICY_ID >= 1 and POLICY_ID <= 5:
                    try:
                        if requests.get(url = BASE_URL).status_code == HTTP_OK_STATUS_CODE:
                            StartLoadBalancer()
                        else:
                            PrintError(ERROR_HTTP_REQUEST)
                    except:
                        PrintError(ERROR_INVALID_URL)
                else:
                    PrintError(ERROR_INVALID_POLICY_ID)
            except:
                PrintError(ERROR_INVALID_POLICY_ID)
        except:
            PrintError(ERROR_INVALID_NUMBER_OF_REQUESTS)
    else:
        PrintUsage()