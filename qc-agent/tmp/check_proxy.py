import urllib.request
import os

print("Proxies:", urllib.request.getproxies())
print("Environment HTTP_PROXY:", os.environ.get('HTTP_PROXY'))
print("Environment HTTPS_PROXY:", os.environ.get('HTTPS_PROXY'))
