import re
import cloudscraper


USERNAME = "PocketSagepocketsage"
PASSWORD = "pa??zSRJpgk5YXTX"
REGION = "eu"


def getStore():
  s = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False})

  url = "https://auth.riotgames.com/api/v1/authorization"

  payload = {
    "client_id": "play-valorant-web-prod",
    "nonce": "1",
    "redirect_uri": "https://playvalorant.com/opt_in",
    "response_type": "token id_token"
    }
  headers = {
    'Content-Type': 'application/json',
  }

  response = s.request("POST", url, headers=headers, json=payload)


  payload = {
    "type": "auth",
    "username": USERNAME,
    "password": PASSWORD,
    "remember": True,
    "language": "en_US"
  }
  headers = {
    'Content-Type': 'application/json',
  }

  response = s.request("PUT", url, headers=headers, json=payload)

  data = response.json()
  pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
  data = pattern.findall(data['response']['parameters']['uri'])[0]
  access_token = data[0]


  url = "https://auth.riotgames.com/userinfo"

  payload = ""
  headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + access_token
  }

  response = s.request("GET", url, json=payload, headers=headers)
  PUUID = response.json()["sub"]



  url = "https://entitlements.auth.riotgames.com/api/token/v1"

  payload = ""
  headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + access_token
  }

  response = s.request("POST", url, data=payload, headers=headers)
  entitlement = response.json()["entitlements_token"]

  print("Token: " + access_token)
  print("PUUID: " + PUUID)
  print("Entitlement: " + entitlement)








  url = "https://pd.{}.a.pvp.net/store/v2/storefront/{}".format(REGION, PUUID)

  payload = ""
  headers = {
      "X-Riot-Entitlements-JWT": entitlement,
      "Authorization": "Bearer " + access_token
  }

  response = s.request("GET", url, data=payload, headers=headers)

  offers = response.json()["SkinsPanelLayout"]["SingleItemOffers"]

  output = ""
  for offer in offers:
    data = s.get("https://valorant-api.com/v1/weapons/skinlevels/" + offer).json()["data"]
    output += data["displayName"] + "<img src='" + data["displayIcon"] + "'></br>"
    print(data["displayName"] + "</br>")
  return output