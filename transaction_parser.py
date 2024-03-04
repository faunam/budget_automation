from pandas import DataFrame
from enum import Enum

class Columns():
    def __init__(self):
        self.DATE = 'Date'
        self.DESCRIPTION = 'Description'
        self.AMOUNT = 'Amount'
        self.CATEGORY = 'Category'
        self.ACCOUNT = 'Account'

class Transactions: 
    def __init__(self, transaction_list=[], column_names=Columns()):
        # input: transactions list from creditkarma,
        # self.dict: dictionary of transactions, format: 
        #    {'col1': ['data1', 'data2'...], 'col2': ['data1', 'data2'...], ...}
        self.list = transaction_list
        self.dict = {}
        self.df = DataFrame()

        for name in vars(column_names).values():
            self.dict[name] = []

        for transaction in transaction_list:
            self.dict[column_names.DATE].append(transaction['date'])
            self.dict[column_names.DESCRIPTION].append(transaction['description'])
            self.dict[column_names.AMOUNT].append(transaction['amount']['value'])
            self.dict[column_names.CATEGORY].append(transaction['category']['name'])
            self.dict[column_names.ACCOUNT].append(transaction['account']['providerName'])

        self.df = DataFrame.from_dict(self.dict)

    def to_csv(self, filepath):
        # writes self.df to csv file
        self.df.to_csv(filepath)
