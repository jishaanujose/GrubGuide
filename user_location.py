import requests

def get_current_location():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        location = {
                "ip": data.get("ip"),
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country"),
                "loc": data.get("loc"),  # latitude,longitude
            }
        return location
    except Exception as e:
        return {"error": str(e)}