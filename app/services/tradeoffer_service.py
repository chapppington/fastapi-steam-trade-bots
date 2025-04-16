import requests
import re
import json
from typing import Dict, Tuple

class TradeOfferService:
    class TradeOfferError(Exception):
        pass

    @staticmethod
    def extract_partner_id(trade_url: str, session_id: str, login_secure: str) -> Tuple[str, str]:
        """Extract partner ID from trade URL and get their Steam ID."""
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "ru,ja;q=0.9,uk;q=0.8,fr;q=0.7,zh;q=0.6,en-US;q=0.5,en;q=0.4,zh-CN;q=0.3",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        }

        cookies = {
            "Steam_Language": "english",
            "sessionid": session_id,
            "steamLoginSecure": login_secure
        }

        response = requests.get(trade_url, headers=headers, cookies=cookies)
        if response.status_code != 200:
            raise TradeOfferService.TradeOfferError(f"Failed to get trade page: {response.status_code}")

        partner_id_match = re.search(r"var g_ulTradePartnerSteamID = '(\d+)';", response.text)
        if not partner_id_match:
            raise TradeOfferService.TradeOfferError("Could not find partner ID in response")

        return partner_id_match.group(1), response.text

    @staticmethod
    def get_partner_inventory(trade_url: str, partner_id: str, session_id: str, login_secure: str) -> Dict:
        """Get partner's inventory."""
        inventory_headers = {
            "accept": "text/javascript, text/html, application/xml, text/xml, */*",
            "accept-language": "ru,ja;q=0.9,uk;q=0.8,fr;q=0.7,zh;q=0.6,en-US;q=0.5,en;q=0.4,zh-CN;q=0.3",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-prototype-version": "1.7",
            "x-requested-with": "XMLHttpRequest",
            "Referer": trade_url,
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        cookies = {
            "Steam_Language": "english",
            "sessionid": session_id,
            "steamLoginSecure": login_secure
        }

        inventory_url = f"https://steamcommunity.com/tradeoffer/new/partnerinventory/?sessionid={session_id}&partner={partner_id}&appid=730&contextid=2"
        response = requests.get(inventory_url, headers=inventory_headers, cookies=cookies)
        
        if response.status_code != 200:
            raise TradeOfferService.TradeOfferError(f"Failed to get inventory: {response.status_code}")

        try:
            data = response.json()
            if 'rgInventory' not in data:
                raise TradeOfferService.TradeOfferError("No inventory data in response")
                
            return data['rgInventory']
        except json.JSONDecodeError:
            raise TradeOfferService.TradeOfferError("Invalid JSON response from inventory request")

    @staticmethod
    def create_trade_offer(partner_id: str, inventory: Dict, session_id: str, trade_token: str) -> Dict:
        """Create trade offer data structure."""
        trade_items = []
        for asset_id, item in inventory.items():
            trade_items.append({
                "appid": "730",
                "contextid": "2",
                "amount": "1",
                "assetid": item['id']
            })

        return {
            "sessionid": session_id,
            "serverid": 1,
            "partner": partner_id,
            "tradeoffermessage": "HELLO FROM FASTAPI YEEEE",
            "json_tradeoffer": {
                "newversion": True,
                "version": 2,
                "me": {
                    "assets": [],
                    "currency": [],
                    "ready": False
                },
                "them": {
                    "assets": trade_items,
                    "currency": [],
                    "ready": False
                }
            },
            "captcha": "",
            "trade_offer_create_params": {
                "trade_offer_access_token": trade_token
            }
        }

    @staticmethod
    def send_trade_offer(trade_url: str, trade_data: Dict, session_id: str, login_secure: str) -> Dict:
        """Send the trade offer to Steam."""
        headers = {
            "accept": "*/*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "Referer": trade_url,
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        cookies = {
            "Steam_Language": "english",
            "sessionid": session_id,
            "steamLoginSecure": login_secure
        }

        # Convert trade data to form data
        form_data = {}
        for key, value in trade_data.items():
            if isinstance(value, dict):
                form_data[key] = json.dumps(value)
            else:
                form_data[key] = str(value)

        response = requests.post(
            "https://steamcommunity.com/tradeoffer/new/send",
            headers=headers,
            cookies=cookies,
            data=form_data
        )

        if response.status_code != 200:
            raise TradeOfferService.TradeOfferError(f"Failed to send trade offer: {response.status_code}")

        try:
            result = response.json()
            return result
        except json.JSONDecodeError:
            raise TradeOfferService.TradeOfferError("Invalid JSON response from trade offer request")

    @staticmethod
    def process_trade_offer(trade_url: str, session_id: str, login_secure: str) -> Dict:
        """Process a complete trade offer."""
        try:
            # Extract partner ID from trade URL
            partner_id, _ = TradeOfferService.extract_partner_id(trade_url, session_id, login_secure)
            
            # Get partner's inventory
            inventory = TradeOfferService.get_partner_inventory(trade_url, partner_id, session_id, login_secure)
            
            # Extract trade token from URL
            trade_token = trade_url.split("token=")[-1]
            
            # Create trade offer data
            trade_data = TradeOfferService.create_trade_offer(partner_id, inventory, session_id, trade_token)
            
            # Send trade offer
            response = TradeOfferService.send_trade_offer(trade_url, trade_data, session_id, login_secure)
            
            return {
                "success": True,
                "partner_id": partner_id,
                "items_count": len(inventory),
                "response": response
            }
        except TradeOfferService.TradeOfferError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            } 
