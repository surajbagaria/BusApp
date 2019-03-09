import urllib.request
import ssl

endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'

API_KEY = 'AIzaSyBf2CZVNafcGGeYFzG7w5JBOcFY6cHN6-4'

origin = input('Where are you?').replace(' ','+')
destination = input('Where you want to go?').replace(' ', '+')

nav_request = 'origin={} &destination={} &key={}'.format(origin, destination, API_KEY)
gcontext = ssl.SSLContext()
request = endpoint + nav_request

response = urllib.request.urlopen(request, context=gcontext).read()
directions = json.loads(response)
print(directions)
