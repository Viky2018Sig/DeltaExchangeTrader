import hashlib
import hmac
import requests
import time
from typing import Dict, Any, Optional

class DeltaExchangeAPI:
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.india.delta.exchange"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'python-delta-trader/1.0',
            'Content-Type': 'application/json'
        })

    def _generate_signature(self, method: str, timestamp: str, path: str, query_string: str = '', payload: str = '') -> str:
        message = method + timestamp + path + query_string + payload
        message_bytes = message.encode('utf-8')
        secret_bytes = self.api_secret.encode('utf-8')
        signature = hmac.new(secret_bytes, message_bytes, hashlib.sha256).hexdigest()
        return signature

    def _request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None, auth: bool = True) -> Dict[str, Any]:
        url = self.base_url + path
        timestamp = str(int(time.time()))
        query_string = ''
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        payload = ''
        if data:
            payload = requests.models.PreparedRequest().prepare_body(data, None, None)[0].decode('utf-8') if data else ''

        headers = {}
        if auth:
            signature = self._generate_signature(method, timestamp, path, query_string, payload)
            headers.update({
                'api-key': self.api_key,
                'timestamp': timestamp,
                'signature': signature
            })

        response = self.session.request(method, url, params=params, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_products(self, contract_types: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if contract_types:
            params['contract_types'] = contract_types
        return self._request('GET', '/v2/products', params=params, auth=False)

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        return self._request('GET', f'/v2/tickers/{symbol}', auth=False)

    def get_tickers(self, contract_types: Optional[str] = None, underlying_asset_symbols: Optional[str] = None, expiry_date: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if contract_types:
            params['contract_types'] = contract_types
        if underlying_asset_symbols:
            params['underlying_asset_symbols'] = underlying_asset_symbols
        if expiry_date:
            params['expiry_date'] = expiry_date
        return self._request('GET', '/v2/tickers', params=params, auth=False)

    def get_positions(self) -> Dict[str, Any]:
        return self._request('GET', '/v2/positions/margined')

    def place_order(self, product_id: int, size: int, side: str, order_type: str, limit_price: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        data = {
            'product_id': product_id,
            'size': size,
            'side': side,
            'order_type': order_type,
            **kwargs
        }
        if limit_price:
            data['limit_price'] = limit_price
        return self._request('POST', '/v2/orders', data=data)

    def cancel_order(self, order_id: int) -> Dict[str, Any]:
        data = {'id': order_id}
        return self._request('DELETE', '/v2/orders', data=data)

    def get_orders(self, product_id: Optional[int] = None, state: str = 'open') -> Dict[str, Any]:
        params = {'state': state}
        if product_id:
            params['product_id'] = product_id
        return self._request('GET', '/v2/orders', params=params)