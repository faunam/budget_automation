from selenium import webdriver
from selenium.webdriver.common.by import By
import subprocess
import time
import json
import os
from dotenv import load_dotenv
from transaction_parser import Transactions

# scraping credit karma for transaction history

def setup_driver():
    # returns driver
    service = webdriver.ChromeService()
    # service = webdriver.ChromeService(service_args=['--log-level=ALL'], log_output=subprocess.STDOUT)
    options = webdriver.ChromeOptions()
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    options.add_argument("user-data-dir=selenium_user_data_new_new")
    options.add_experimental_option("detach", True)
    # options.headless = True
    driver = webdriver.Chrome(options=options, service=service)

    return driver

def login(driver):
    load_dotenv()
    driver.find_element(By.NAME, 'password').send_keys(os.getenv("PASSWORD"))
    time.sleep(1)
    driver.find_element(By.ID, 'Logon').click()

def write_json(data, filename):
    # data: json-encodable data, filename: str including extension
    with open(filename, 'w') as outfile:
        outfile.write(json.dumps(data))

def get_network_requests(network_log):
    # return list of request events meeting filter_fun criteria, if provided
    events = []
    for entry in network_log:
        event = json.loads(entry['message'])['message']
        if 'request' in event['params'] \
        and 'url' in event['params']['request'] \
        and event['params']['request']['url'] == "https://api.creditkarma.com/graphql":
            events.append(event)
    return events


def get_network_responses(driver, network_log):
    requests = get_network_requests(network_log)
    request_ids = [request['params']['requestId'] for request in requests]
    responses = {}
    skipped_request_ids = []

    for request_id in request_ids:
        try:
            response = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
            responses[request_id] = json.loads(response["body"])
        except:
            skipped_request_ids.append(request_id)

    write_json(requests, 'requests.json')
    write_json(responses, 'responses.json')
    # with open('network_log.json', 'w') as outfile:
    #     # avoid double encode
    #     outfile.write(json.dumps([json.loads(entry['message'])['message'] for entry in network_log]))
    return responses

def get_transactions(driver, network_log):
    # returns list of transaction dicts from ck
    # responses = []
    # with open('responses.json', 'r') as infile:
    #     responses = json.load(infile)
    responses = get_network_responses(driver, network_log)
    for response in responses.values():
        if bool('data' in response) \
        and bool('prime' in response['data']) \
        and 'transactionList' in response['data']['prime']:
            # list
            return response['data']['prime']['transactionList']['transactions']
        
    raise Exception('response error: transactions not found')

def test():
    url = 'https://www.creditkarma.com/auth/logon'
    driver = setup_driver()
    driver.get(url)
    time.sleep(2)
    login(driver)
    time.sleep(1)

    driver.get("https://www.creditkarma.com/networth/transactions")
    time.sleep(5)
    network_log = driver.get_log('performance') 
    
    transaction_list = get_transactions(driver, network_log)
    transactions = Transactions(transaction_list)
    transactions.to_csv('transactions.csv')


# test()