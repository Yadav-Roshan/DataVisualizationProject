import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
from math import degrees, asin
import re
from datetime import datetime

def convertingToKML(df):
    f2 = open("KML-{}.kml".format(df["TrajectoryId"][0]),'w')
    f2.write(f"""<?xml version="1.0" encoding="UTF-8"?>
	    <kml xmlns="http://www.opengis.net/kml/2.2"
  	    xmlns:gx="http://www.google.com/kml/ext/2.2">
	    <name>{df['Origin'][0]} to {df['Destination'][0]}</name>    
		    <gx:Tour>
	        <name>{df['Origin'][0]} to {df['Destination'][0]}</name>
	   		    <gx:Playlist>\n""")
    st.write()
    for i in range(df.shape[0]):
        f2.write(f"""				  <gx:FlyTo>
		    	        <gx:duration>{df['Time Diff'][i]/20.0}</gx:duration>
			            <gx:flyToMode>smooth</gx:flyToMode>
			    	    <Camera>
			    	    <longitude>{df['Longitude'][i]}</longitude>
			    	    <latitude>{df['Latitude'][i]}</latitude>
		        	    <altitude>{df['Altitude(m)'][i]}</altitude>
		        	    <heading>{df['Course'][i]}</heading>
		          	    <tilt>{90.00 + df['tilt'][i]}</tilt>
						<roll>0</roll>
			            <altitudeMode>absolute</altitudeMode>
			            </Camera>
				    </gx:FlyTo>\n""")
    f2.write("""		  </gx:Playlist>
	  	    </gx:Tour></kml>""")
    f2.close()

def time_difference(t1, t2):
    return (pd.to_datetime(t2) - pd.to_datetime(t1)).total_seconds()
def mph_to_mps(speed):
    return speed*4/9
def tilt_calculator(d, met1, met2):
    try:
        tilt = degrees(asin((met2-met1)/d))
    except Exception:
        tilt = 0
    return tilt
def distance_travelled_from_last_point(mps, time):
    return mps*time

def scraping_function(url, origin, destination, id, flightid):
    url_extract = requests.get(url).text
    soup = BeautifulSoup(url_extract, 'lxml')
    table = soup.find('table', class_ = "prettyTable fullWidth")
    header = table.find('tr', class_ = "thirdHeader")
    header_details = header.find_all('th')
    header_csv = []
    for column in header_details:
        try:
            texts = column.find('span', class_="show-for-medium-up").text
        except Exception:
            texts = column.text
        header_csv.append(texts)
    for i in range(len(header_csv)):
        if 'Time' in header_csv[i]:
            header_csv[i] = 'Time'
        if header_csv[i] == 'meters':
            header_csv[i] = 'Altitude(m)'
    table_data = table.find_all('tr')
    table_data.pop(0)
    table_data.pop(0)
    table_data.pop(0)
    data_csv = []
    for row in table_data:
        try:
            columns = row.find_all('td')
            column_data = []
            for i in columns:
                try:
                    tds = i.find('span').text
                except Exception:
                    tds = i.text
                column_data.append(tds)
            if column_data[1] != '':
                column_data[3] = column_data[3].split(' ')[1][:-1]
                column_data[7] = column_data[7][:-1]
                if column_data[4] == '':
                    column_data[4] = str(data_csv[-1][4])
                    column_data[5] = str(data_csv[-1][5])
                    column_data[6] = str(data_csv[-1][6])
                for i in range(1, len(column_data)-1):
                    try:
                        column_data[i] = float(column_data[i].replace(',', ''))
                    except Exception:
                        column_data[i] = 0
                data_csv.append(column_data)
        except Exception:
            break
    header_csv.extend(['Time Diff', 'm/s', 'Dist from lp', 'tilt'])
    data_csv[0].extend([0,mph_to_mps(data_csv[0][5]), 0,0])
    df = pd.DataFrame(columns = header_csv)
    for i in range(1, len(data_csv)):
        time = time_difference(data_csv[i-1][0][4:], data_csv[i][0][4:])
        mps = mph_to_mps(data_csv[i][5])
        d = distance_travelled_from_last_point(mps, time)
        tilt = tilt_calculator(d, data_csv[i-1][6], data_csv[i][6])
        data_csv[i].extend([time, mps, d, tilt])
    for i in range(len(data_csv)):
        df.loc[i] = data_csv[i]
    df["TrajectoryId"] = id
    df["FlightId"] = flightid
    df['Origin'] = origin
    df['Destination'] = destination
    convertingToKML(df)
    return df
tk = 0
st.title("DV Project")
flightid = st.text_input("Enter Flight ID")
if st.button('Submit'):
    tk = 1

if tk ==1:
    day, month, year = datetime.now().day, datetime.now().month, datetime.now().year
    weather_data = pd.read_csv(f"https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=VABO&station=VAAH&station=VAAU&station=VABB&station=VABJ&station=VABM&station=VABP&station=VABV&station=VAHS&station=VAID&station=VAJB&station=VAJJ&station=VAJL&station=VAJM&station=VAKJ&station=VAKP&station=VAKS&station=VANP&station=VAOZ&station=VAPO&station=VAPR&station=VARK&station=VARP&station=VASD&station=VASU&station=VAUD&station=VEAB&station=VEAT&station=VEBD&station=VEBI&station=VEBN&station=VEBS&station=VEBU&station=VECC&station=VECO&station=VECX&station=VEDG&station=VEDO&station=VEGK&station=VEGT&station=VEGY&station=VEHO&station=VEHX&station=VEIM&station=VEJH&station=VEJR&station=VEJS&station=VEJT&station=VEKO&station=VEKU&station=VELP&station=VELR&station=VEMN&station=VEMR&station=VEPT&station=VERB&station=VERC&station=VERP&station=VETZ&station=VIAG&station=VIAL&station=VIAR&station=VIBN&station=VIBR&station=VIBY&station=VICG&station=VIDD&station=VIDN&station=VIDP&station=VIGG&station=VIGR&station=VIJO&station=VIJP&station=VIJR&station=VIJU&station=VIKG&station=VIKO&station=VILD&station=VILH&station=VILK&station=VIPT&station=VISM&station=VISP&station=VISR&station=VITE&station=VITX&station=VIUT&station=VOAT&station=VOBG&station=VOBL&station=VOBM&station=VOBX&station=VOBZ&station=VOCB&station=VOCI&station=VOCL&station=VOCP&station=VODX&station=VOGA&station=VOGB&station=VOGO&station=VOHB&station=VOHS&station=VOHY&station=VOJV&station=VOKN&station=VOKU&station=VOMD&station=VOML&station=VOMM&station=VOMY&station=VOND&station=VOPB&station=VOPC&station=VORY&station=VOSH&station=VOSM&station=VOSR&station=VOTK&station=VOTP&station=VOTR&station=VOTV&station=VOVZ&data=all&year1={str(year)}&month1={str(month)}&day1=1&year2={str(year)}&month2={str(month)}&day2={str(day)}&tz=Etc%2FUTC&format=onlycomma&latlon=yes&elev=yes&missing=null&trace=null&direct=no&report_type=1&report_type=3&report_type=4")
    weather_data.to_csv("Weather Data.csv", index=False)
    imp_url = "https://uk.flightaware.com"
    ext_url = imp_url + "/live/flight/{}".format(flightid)
    ext_url_extract = requests.get(ext_url).text
    soup = BeautifulSoup(ext_url_extract, 'lxml')
    origin = re.findall(r"'origin', '[A-Z]+", str(soup))[0][-4:]
    destination = re.findall(r"'destination', '[A-Z]+", str(soup))[0][-4:]
    st.write("Flight from", origin, "to", destination)
    odf = pd.read_csv("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station="+str(origin)+"&data=all&year1=2022&month1="+str(month)+"&day1="+str(day)+"&year2=2023&month2="+str(month)+"&day2="+str(day)+"&tz=Etc%2FUTC&format=onlycomma&latlon=yes&elev=yes&missing=null&trace=null&direct=no&report_type=1&report_type=3&report_type=4")
    ddf = pd.read_csv("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station="+str(destination)+"&data=all&year1="+str((year-1))+"&month1="+str(month)+"&day1="+str(day)+"&year2="+str(year)+"&month2="+str(month)+"&day2="+str(day)+"&tz=Etc%2FUTC&format=onlycomma&latlon=yes&elev=yes&missing=null&trace=null&direct=no&report_type=1&report_type=3&report_type=4")
    odf = odf.drop(["mslp","gust","skyl4","ice_accretion_1hr","ice_accretion_3hr","ice_accretion_6hr","peak_wind_gust","peak_wind_drct","peak_wind_time","snowdepth", "skyc2","skyc3","skyc4","skyl2","skyl3"], axis = 1)
    ddf = ddf.drop(["mslp","gust","skyl4","ice_accretion_1hr","ice_accretion_3hr","ice_accretion_6hr","peak_wind_gust","peak_wind_drct","peak_wind_time","snowdepth", "skyc2","skyc3","skyc4","skyl2","skyl3"], axis = 1)
    odf = odf.dropna(subset = ['tmpf', 'dwpf', 'relh', 'sknt', 'alti', 'vsby', 'skyc1', 'feel'])
    ddf = ddf.dropna(subset = ['tmpf', 'dwpf', 'relh', 'sknt', 'alti', 'vsby', 'skyc1', 'feel'])
    odf['wxcodes'] = odf['wxcodes'].fillna('HZ')
    ddf['wxcodes'] = ddf['wxcodes'].fillna('HZ')
    odf['valid'] = pd.to_datetime(odf['valid'])
    odf['day'] = odf['valid'].dt.day
    odf['month'] = odf['valid'].dt.month
    odf['year'] = odf['valid'].dt.year
    odf['hr'] = odf['valid'].dt.hour
    odf['min'] = odf['valid'].dt.minute
    ddf['valid'] = pd.to_datetime(ddf['valid'])
    ddf['day'] = ddf['valid'].dt.day
    ddf['month'] = ddf['valid'].dt.month
    ddf['year'] = ddf['valid'].dt.year
    ddf['hr'] = ddf['valid'].dt.hour
    ddf['min'] = ddf['valid'].dt.minute
    odf.to_csv("Origin Weather.csv", index=False)
    ddf.to_csv("Destination Weather.csv", index = False)
    main_url = imp_url + "/live/flight/{}/history/".format(flightid)
    main_url_extract = requests.get(main_url).text
    soup = BeautifulSoup(main_url_extract, 'lxml')
    new_table = soup.find('table', class_ = "prettyTable fullWidth tablesaw tablesaw-stack")
    table_body = new_table.find_all('tr')[1:]
    while True:
        if 'Scheduled' in table_body[0].text:
            table_body.pop(0)
        else:
            break
    og = None
    if 'On The Way!' in table_body[0].text:
        x = re.findall(r'a href="[/a-zA-Z0-9]+', str(table_body[0]))[0][8:]
        og = scraping_function(imp_url+x+"/tracklog", origin, destination, 'OnGoing', flightid)
        og["FlightId"] = flightid
        og["Origin"] = origin
        og["Destination"] = destination
        og.to_csv("FlightData-Ongoing.csv", index=False)
        table_body.pop(0)
    flight_links = []
    for i in table_body:
        if origin in i.text and destination in i.text and 'Cancelled' not in i.text:
            x = re.findall(r'a href="[/a-zA-Z0-9]+', str(i))[0][8:]
            flight_links.append(x)
            if len(flight_links) == 5:
                break
    final_df = pd.DataFrame()
    for i in range(5):
        df = scraping_function(imp_url+flight_links[i]+"/tracklog", origin, destination, i+1, flightid)
        df["TrajectoryId"] = i+1
        df["FlightId"] = flightid
        final_df = pd.concat([final_df, df]).reset_index(drop=True)
    final_df.to_csv("FlightData.csv", index=False)
    st.write("Data Acquired, go to Power BI to see the visualizations.")