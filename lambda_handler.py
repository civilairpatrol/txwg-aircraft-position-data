import json, os, re, requests

def lambda_handler(event, context):
    assert context

    openSkyUrl = os.environ['openSkyUrl']   # https://opensky-network.org/api/states/all

    arcGisUrl = os.environ['arcGisUrl']     # https://services{x}.arcgis.com/{appID}/arcgis/rest/services/{layerName}/FeatureServer
    arcGisClientId = os.environ['arcGisClientId']   # Not Implemented
    arcGisClientSecret = os.environ['arcGisClientSecret']   # Not Implemented
    arcGisToken = os.environ['arcGisToken'] # ArcGIS Temporary Access Token for App Owner

    openSky = requests.get(openSkyUrl)
    openSkyJson = openSky.json()

    adds = []

    for aircraft in openSkyJson['states']:
        match = re.search("^CAP[0-9]{3,4}", aircraft[1])
        if match:
          callsign = aircraft[1].strip()
          long = aircraft[5]
          lat = aircraft[6]
          altitude = sanitize_attribute(aircraft[7])
          speed = sanitize_attribute(aircraft[9])
          verticalSpeed = sanitize_attribute(aircraft[11])
          adds += [{
              "geometry": {
                  "x": long,
                  "y": lat,
                  "spatialReference": {
                      "wkid": 4326
                  }
              },
              "attributes": {
                  "Callsign": callsign,
                  "Altitude": (altitude*3.28084),
                  "OnGround": aircraft[8],
                  "Speed": (speed*1.943844),
                  "Heading": aircraft[10],
                  "VerticalSpeed": (verticalSpeed*196.85039370078738),
                  "Squawk": aircraft[14]
              }
          }]

    if adds:
        payload = { 'f': 'json', 'token': arcGisToken, 'adds': json.dumps(adds) }
        r = requests.post(arcGisUrl + '/0/applyEdits', data=payload)

    print('LogScheduledEvent');
    print('Received event:', json.dumps(event));
    print('Response from ArcGIS:', json.dumps(r.text));

def sanitize_attribute(value):
  if value:
    return value
  else:
    return 0
