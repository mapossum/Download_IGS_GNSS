Year = 2023
jDay = 64
StartHour = 22
Duration = 5
Station = "FAA100PYF_R"  #TAHITI AIRPORT

import requests # get the requsts library from https://github.com/requests/requests
import gzip, math, os

# overriding requests.Session.rebuild_auth to mantain headers when redirected
class SessionWithHeaderRedirection(requests.Session):
    AUTH_HOST = 'urs.earthdata.nasa.gov'
    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)

   # Overrides from the library to keep headers when redirected to or from
   # the NASA auth host.
    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url

        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)

            if (original_parsed.hostname != redirect_parsed.hostname) and \
                    redirect_parsed.hostname != self.AUTH_HOST and \
                    original_parsed.hostname != self.AUTH_HOST:

                del headers['Authorization']
        return

# create session with the user credentials that will be used to authenticate access to the data
username = "mapossum"
password = "G30gr@phy"

session = SessionWithHeaderRedirection(username, password)

# the url of the file we wish to retrieve
         #"https://cddis.nasa.gov/archive/gnss/data/highrate/YYYY/DDD/FOLDER/HH/STATION_YYYYDDDHHMM_15M_01S_MO.crx.gz"
baseurl = "https://cddis.nasa.gov/archive/gnss/data/highrate/{0}/{1}/23d/{2}/{3}_{0}{1}{2}{4}_15M_01S_MO.crx.gz"


finalfilename = "{}_{}{}_{}_{}.crx".format(Station,Year,(str(jDay).zfill(3)),(str(StartHour).zfill(2)),(str(Duration).zfill(2)))
print(finalfilename)
oFile = open(finalfilename, "ab")

for hr in range(StartHour,StartHour+Duration+1):
    cDay = jDay + math.floor(hr/24)
    hrc = ((str(hr % 24).zfill(2)))
    for m in range(0, 60, 15):
        #print(m)
        url = baseurl.format(Year,(str(cDay).zfill(3)),(str(hrc).zfill(2)), Station, (str(m).zfill(2)))
        print(url)

        # extract the filename from the url to be used when saving the file
        filename = url[url.rfind('/')+1:]  

        try:
            # submit the request using the session
            response = session.get(url, stream=True)
            print(response.status_code)

            # raise an exception in case of http errors
            response.raise_for_status()  

            # save the file
            with open(filename, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    fd.write(chunk)

        except requests.exceptions.HTTPError as e:
            # handle any errors here
            print(e)

  
        with gzip.open(filename, 'rb') as f:
            file_content = f.read()
            oFile.write(file_content)
            #if you want the individual 15 minute files as well 
            with open(filename.replace(".gz",""), 'wb') as fd:
                fd.write(file_content)
            

        os.remove(filename)

oFile.close()

os.system("CRX2RNX.exe " + finalfilename)  
                
