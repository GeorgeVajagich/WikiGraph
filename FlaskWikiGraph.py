import pandas as pd # library for data analysis
import requests # library to handle requests
from bs4 import BeautifulSoup # library to parse HTML documents   
import re # library for regular expressions
import plotly # library for plotting
import plotly.express as px # library for plotting
import pycountry_convert as pc # library to convert country names into codes for mapping
from plotly import graph_objs as go # library for plotting
import numpy as np # library for math
from flask import Flask, render_template # library for website
from flask import request
import json # library for dealing with JSON files

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/graph",methods=["GET","POST"])
def graph():
    question=request.form['Question']
    search = question + 'wikipedia'
    url = 'https://www.google.com/search?q='

    headers = {
        'Accept' : '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82',
    }

    parameters = {'q': search}

    content = requests.get(url, headers = headers, params = parameters).text
    soup = BeautifulSoup(content, 'html.parser')

    search = soup.find(id = 'search')
    first_link = search.find('a')

    wikiurl=(first_link['href'])
    table_class="wikitable sortable jquery-tablesorter"
    response=requests.get(wikiurl)

    soup = BeautifulSoup(response.text, 'html.parser')
    table=soup.find('table',{'class':"wikitable"})

    df=pd.read_html(str(table))
    df=pd.DataFrame(df[0])



    if df.columns[0]=="Rank" or df[df.columns[0]].iloc[0]==1 or df[df.columns[0]].iloc[0]=="1." or df[df.columns[0]].iloc[0]=="—":
        df=df.drop(df.columns[0], axis=1)
    
    if type(df[df.columns[1]].iloc[0])==str:
        if any(chr.isdigit() for chr in df[df.columns[1]].iloc[0])==False:
            df=df.drop(df.columns[1], axis=1)


    a=(df.columns[0])
    b=(df.columns[1])


    if df[a][0]=="World":
        df=df.drop(index=0)

    try:
        df[b]=df[b].str.replace(r'\[.*\]','')
        df[b] = df[b].str.replace(r'\D+', '')
    except:
        pass
    
    try:
        df[a]=df[a].str.replace(r'\[.*\]','')
        df[a]=df[a].str.replace(r'\(.*\)','')
    except:
        pass

    df[b] = df[b].replace(r'^\s*$', np.nan, regex=True)

    df[b]= df[b].astype(float)

    first=(df[b].iloc[0])
    last=(df[b].iloc[len(df[b])-1])
    secondlast=(df[b].iloc[len(df[b])-2])

    if (last/first)>1:
        df = df[:-1]
    if (secondlast/first)>1:
        df = df[:-2]


    fig=px.bar(df,x=a,y=b)   
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    
    if (df[a].eq('China')).any() == True or (df[a].eq('Brazil')).any() == True:
        # creating a function to convert the country names to alpha3 codes that plotly can process into a map
        df.rename(columns={ df.columns[0]: "Country" }, inplace = True)
        def convert(row):
            try: cn_code = pc.country_name_to_country_alpha3(row.Country, cn_name_format = "default")
            except: cn_code="VAT" 
        
            return(cn_code)
        df["Alpha3"]= df.apply(convert,axis=1)
    
        # maping the data using plotly
        fig=go.Figure(data = go.Choropleth(locations=df["Alpha3"],z=df[b]))
        fig.update_layout(autosize=False,width=1200,height=600,)
        
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
    return render_template('home.html', graphJSON=graphJSON)
        
     
