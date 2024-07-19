import streamlit as st
import pandas as pd # library for data analysis
import requests # library to handle requests
from bs4 import BeautifulSoup # library to parse HTML documents
import re # library for regular expressions
import plotly # library for plotting
import plotly.express as px # library for plotting
import pycountry_convert as pc # library to convert country names into codes for mapping
from plotly import graph_objs as go # library for plotting
import numpy as np # library for math
import json # library for dealing with JSON files
from scipy.stats import pearsonr   
import xlrd

st. set_page_config(layout="wide")

question=st.chat_input('Question')

def Answer(q):
    question=str(q)
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
        #df[b] = df[b].str.replace(r',', '')
        #df[b] = df[b].str.replace(r'$', '')
    except:
        pass


    try:
        df[a]=df[a].str.replace(r'\[.*\]','')
        df[a]=df[a].str.replace(r'\(.*\)','')
    except:
        pass

    df[b] = df[b].replace(r'^\s*$', np.nan, regex=True)

    df[b] = pd.to_numeric(df[b], errors="coerce")

    first=(df[b].iloc[0])
    last=(df[b].iloc[len(df[b])-1])
    secondlast=(df[b].iloc[len(df[b])-2])

    if (last/first)>1:
        df = df[:-1]
    if (secondlast/first)>1:
        df = df[:-2]


    fig=px.bar(df,x=a,y=b,title=question)
    st.plotly_chart(fig)


    if (df[a].eq('China')).any() == True or (df[a].eq('Brazil')).any() == True:
        # creating a function to convert the country names to alpha3 codes that plotly can process into a map
        df.rename(columns={ df.columns[0]: "Country" }, inplace = True)
        a=(df.columns[0])

        def convert(row):
            try: cn_code = pc.country_name_to_country_alpha3(row.Country, cn_name_format = "default")
            except: cn_code="VAT"

            return(cn_code)
        df["Alpha3"]= df.apply(convert,axis=1)

        # maping the data using plotly
        fig=go.Figure(data = go.Choropleth(locations=df["Alpha3"],z=df[b]))
        fig.update_layout(autosize=False,width=1200,height=600,)
        st.plotly_chart(fig)


    return(df[a],df[b])


st.title("AutoGraph🤖📊")
st.write("AutoGraph is a program where you ask it a question and AutoGraph answers your question with a graph (and sometimes a map)")
st.write("Here is the [link](https://www.youtube.com/watch?v=FAOurWy01pM) to the tutorial and some sample prompts")
st.text("")
st.text("Biggest cities in India")
st.text("Countries by Iron Production")
st.text("Best selling video games of all time")
st.text("Countries by Grape production & Countries by Wine production")

if not ("&" or "and") in str(question):
    a,b =Answer(question)

if ("&" or "and") in str(question):
    questions=str(question).split("&" or "and")
    a,b=Answer(questions[0])
    a2,c=Answer(questions[1])

    df1=pd.DataFrame()
    df1.insert(0, "a", a)
    df1.insert(1, str(questions[0]), b)
    df1['a']=df1['a'].astype(str)

    df2=pd.DataFrame()
    df2.insert(0, "a", a2)
    df2.insert(1, str(questions[1]), c)
    df2['a']=df2['a'].astype(str)

    df3=pd.merge(df1,df2, how='inner', on='a')

    fig = px.scatter(df3, x=str(questions[0]), y=str(questions[1]), hover_data=["a"])
    st.text("p value under 0.05 is statistically significant")
    st.text(pearsonr(df3[str(questions[0])],df3[str(questions[1])]))
    st.plotly_chart(fig)