from http.server import BaseHTTPRequestHandler, HTTPServer
import concurrent.futures
import logging
import time
from coinbase.wallet.client import Client

hostName = "localhost"
serverPort = 8080

passphrase = '5wx3wsqwi5q'
b64secret = 'H38KtFytazVZZDVFHRHz9GwruaACjkPpPV6WBflNEalp6SZd8wyEP4xuC2ctuT5avdO3Yfr2vE4aKqTPRJjwAQ=='
key = 'ca4a4b9d543f18c5da1ee9995bfb56ef'

def get_current_price(key, b64secret):
    '''Returns current price'''

    client = Client(key, b64secret, api_version='YYYY-MM-DD')
    currency_code = 'USD'  # can also use EUR, CAD, etc.
    # Make the request
    price = client.get_spot_price(currency=currency_code)
    return price.amount

class MyServer(BaseHTTPRequestHandler):
    price = get_current_price(key, b64secret)
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Coinbase Server</title></head>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>Currency Rate: %s</p>" % self.price, "utf-8"))
        self.wfile.write(bytes("<p>Last Buy: </p>", "utf-8"))
        self.wfile.write(bytes("<p>Last Sell: </p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))


def serverThread():
    while(True):
        webServer = HTTPServer((hostName, serverPort), MyServer)
        logging.info("Server started http://%s:%s" % (hostName, serverPort))

        try:
            webServer.serve_forever()
        except :
            pass

    webServer.server_close()
    logging.info("Server stopped.")
  

def logThread():
    while True:
        time.sleep(2.0)
        logging.info('hi from log thread')

if __name__ == "__main__":        

    logging.basicConfig(level=logging.INFO)
       
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Run Server
        executor.submit(serverThread)
        # Run A Parallel Thread
        executor.submit(logThread)