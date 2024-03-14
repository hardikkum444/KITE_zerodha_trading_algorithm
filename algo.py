import requests
import getpass
import csv
import json

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def get_creds():
    print("Getting credentials...")
    userid = input("userid --> ")
    print("Password input...")
    passwd = getpass.getpass("password --> ")
    print("Twofa input...")
    oauth = getpass.getpass("twofa --> ")

    return userid, passwd, oauth

# this entire code is to get the enctoken, not for logging in!
def login(userid, passwd, oauth):
    session = requests.Session()
    response = session.post('https://kite.zerodha.com/api/login', data={
        "user_id": userid,
        "password": passwd
    })

    # JSON data???
    if response.ok and response.json().get('data'):
        request_id = response.json()['data']['request_id']
        user_id = response.json()['data']['user_id']
    else:
        raise Exception(f"{RED}Failed to login. Please check your credentials.{RESET}")

    response = session.post('https://kite.zerodha.com/api/twofa', data={
        "request_id": request_id,
        "twofa_value": oauth,
        "user_id": user_id
    })
    encToken = response.cookies.get('enctoken')
    if encToken:
        print(encToken)
        return encToken
    else:
        raise Exception(f"{RED}Failed to get authentication token.{RESET}")

class kite:

    # this is me calling a default const for kite
    def __init__(self,enctoken):
        self.headers = {"Authorization": f"enctoken {enctoken}"}
        self.session = requests.session()
        self.root_url = "https://api.kite.trade"
        self.response = self.session.get(self.root_url, headers=self.headers)
        print(f"{GREEN}Your connection is up and ready... {RESET}")
        print(f"{RED}Response from the server --> {RESET}", self.response.text)

    def profile(self):
        profile = self.session.get(f"{self.root_url}/user/profile", headers=self.headers).json()["data"]
        final = json.dumps(profile)
        return final

    def margins(self):
        margins = self.session.get(f"{self.root_url}/user/margins", headers=self.headers).json()["data"]
        return margins

    def positions(self):
        positions = self.session.get(f"{self.root_url}/portfolio/positions", headers=self.headers).json()["data"]
        return positions

    def holdings(self):
        holdings = self.session.get(f"{self.root_url}/portfolio/holdings", headers=self.headers).json()["data"]
        return holdings

    def stockDump(self):
        stockDump = self.session.get(f"{self.root_url}/instruments", headers=self.headers)
        if stockDump.ok:
            csv_data = stockDump.text
            with open('data.csv', 'w') as file:
                file.write(csv_data)
            print(f"{RED}csv dump of tradable stocks has been saved!{RESET}")
        else:
            print("falied to get csv data")

    def auctions(self):
        auctions = self.session.get(f"{self.root_url}/portfolio/holdings/auctions", headers=self.headers).json()["data"]
        return auctions

    # orders
    
    # def place_order(self, variety, exchange, trading_symbol, transaction_type, quantity, product, order_type, price=None, validity=None, disclosed_quantity=None, trigger_price=None, squareoff=None, stoploss=None, trailing_stoploss=None, tag=None ):
    #     req_parameters = locals()
    #     del req_parameters["self"]
    #     for k in list(req_parameters.keys()):
    #         if req_parameters[k] is None:
    #             del req_parameters[k]
    #     order_id = self.session.post(f"{self.root_url}/orders/{variety}",data=req_parameters, headers=self.headers).json()["data"]["order_id"]

    #     return order_id
    def place_order(self, variety, exchange, tradingsymbol, transaction_type, quantity, product, order_type, price=None,
                    validity=None, disclosed_quantity=None, trigger_price=None, squareoff=None, stoploss=None,
                    trailing_stoploss=None, tag=None):
        params = locals()
        del params["self"]
        for k in list(params.keys()):
            if params[k] is None:
                del params[k]
        order_id = self.session.post(f"{self.root_url}/orders/{variety}",
                                     data=params, headers=self.headers).json()["data"]["order_id"]
        return order_id

def main():
    opt = input("Do you have enctoken? (y/n)")
    if opt == 'y':
            enctoken = input("please enter enctoken --> ")
    else:
        userid, passwd, oauth = get_creds()
        enctoken = login(userid, passwd, oauth)
    
    kiteapp = kite(enctoken = enctoken)

    print(f"{GREEN}User_profile:{RESET}")
    print(kiteapp.profile())

    print(f"{GREEN}Margins:{RESET}")
    print(kiteapp.margins())

    print(f"{GREEN}Positions:{RESET}")
    print(kiteapp.positions())

    print(f"{GREEN}Holdings:{RESET}")
    print(kiteapp.holdings())

    print(f"{GREEN}Historical data:{RESET}")
    kiteapp.stockDump()

    print(f"{GREEN}Auctions:{RESET}")
    print(kiteapp.auctions())

    print("placing order")

    order = kiteapp.place_order(variety="amo",
                         exchange="NSE",
                         tradingsymbol="IDEA",
                         transaction_type="BUY",
                         quantity=1,
                         product="NRML",
                         order_type="MARKET",
                         price=None,
                         validity=None,
                         disclosed_quantity=None,
                         trigger_price=None,
                         squareoff=None,
                         stoploss=None,
                         trailing_stoploss=None,
                         tag="Hardiks_trade")
    print(order)


if __name__ == "__main__":
    main()
