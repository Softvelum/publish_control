import base64
import md5

from time import gmtime, strftime

id = "ID_1"
ip = "127.0.0.1"
password = "defaultpassword"
stream_name ="/live/stream"

m = md5.new()
m.update(id + stream_name + password + ip)

base64hash = base64.b64encode(m.digest())

urlsignature = "id=" + id + "&sign=" + base64hash + "&ip=" + ip

base64urlsignature = base64.b64encode(urlsignature)

initial_url = "rtsp://127.0.0.1/live/stream"
signedurlwithvalidinterval = initial_url + "?publishsign=" + base64urlsignature

print signedurlwithvalidinterval

