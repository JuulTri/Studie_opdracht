#!/usr/bin/env python
# coding: utf-8

# # Groep 20&21 Case 2

# ##### team:  Julius Feenstra, Boris Kuipers, Giel Suweijn, Semih Önel

# ## alles inladen 

# In[1]:


#pip install streamlit


# In[2]:


import streamlit as st
import pandas as pd
import numpy as np
from pandas import json_normalize
import requests
import plotly.express as px
import plotly.graph_objects as go
pd.set_option('display.float_format', lambda x: '%.1f' % x)


# ## Data inladen

# #### Landbouw-data inladen (API)

# In[3]:


r1 = requests.get('https://opendata.cbs.nl/ODataApi/odata/84075NED/Landbouwproductie')
x1 = r1.json()
df1 = pd.DataFrame(x1['value'])

r2 = requests.get('https://opendata.cbs.nl/ODataApi/odata/84075NED/Perioden')
x2 = r2.json()
df2 = pd.DataFrame(x2['value'])

r3 = requests.get('https://opendata.cbs.nl/ODataApi/odata/84075NED/TypedDataSet')
x3 = r3.json()
df3 = pd.DataFrame(x3['value'])


# #### KNMI-data inladen 

# In[4]:


weer = pd.read_csv('result.csv')


# ## Data bewerken 

# #### Landbouw-data inladen (API)

# In[5]:


df1 = df1[["Key", "Title"]]
df1.columns = ['Landbouwproductie', 'producten']

df2.columns = ['Perioden', 'Jaar', "toevoeging", "Status"]


# In[6]:


data_stap1 = df3.merge(df1, on='Landbouwproductie')
data = data_stap1.merge(df2, on='Perioden')
data = data.drop(["ID", "Perioden", "Landbouwproductie", "toevoeging", "Status"], axis=1)
data = data[data['Jaar'] != '2021']
data.columns = ['Hoeveelheid' , 'Eenheid', 'Product', 'Jaar']


# In[7]:


weer.columns=['De Bilt', 'Datum','Wind','Temperatuur','Zon','Neerslag','Luchtvochtigheid %']
weer['Datum'] = pd.to_datetime(weer['Datum'], format='%Y%m%d')
weer["Jaar"] = weer['Datum'].dt.year


# In[8]:


Wind = weer.groupby(weer['Jaar'])['Wind'].agg(['mean', 'max', 'min', 'sum'])
Wind['type'] = 'Wind'
Temperatuur = weer.groupby(weer['Jaar'])['Temperatuur'].agg(['mean', 'max', 'min', 'sum'])
Temperatuur['type'] = 'Temperatuur'
Zon = weer.groupby(weer['Jaar'])['Zon'].agg(['mean', 'max', 'min', 'sum'])
Zon['type'] = 'Zon'
Neerslag = weer.groupby(weer['Jaar'])['Neerslag'].agg(['mean', 'max', 'min', 'sum'])
Neerslag['type'] = 'Neerslag'
Luchtvochtigheid = weer.groupby(weer['Jaar'])['Luchtvochtigheid %'].agg(['mean', 'max', 'min', 'sum'])
Luchtvochtigheid['type'] = 'Luchtvochtigheid %'

natuur = pd.concat([Wind, Temperatuur, Zon, Neerslag, Luchtvochtigheid], axis='rows')
natuur.reset_index(inplace=True)
natuur.columns = ['Jaar', 'Gemiddelde', 'Maximum', 'Minimum', 'Totaal', 'Type']


# ## De data

# In[9]:


data.head()


# In[10]:


weer.head()


# In[11]:


natuur.head()


# In[12]:


##Gegevens in Streamlit zetten


# In[13]:


st.title("Invloed van het weer op de landbouwoogst")


# In[14]:


st.header('De data van de landbouw')
st.dataframe(data)


# In[15]:


InputNatuur = st.sidebar.selectbox("type natuurverschijnsel", ("Wind", "Temperatuur", "Zon", "Neerslag", "Luchtvochtigheid %"))
NatuurSelect = natuur[natuur["Type"] == InputNatuur]
st.header('de data van het weer')
st.dataframe(NatuurSelect)


# In[16]:


InputData = st.sidebar.selectbox("de eenheid", ("1000 kg", "stuks", "1000 kg karkasgewicht"))
DataSelect = data[data["Eenheid"] == InputData]
st.header('De data van de landbouw')
st.dataframe(DataSelect)


# In[17]:


## Visualisaties in Streamlit zetten


# In[18]:


## Dropdown-menu


# In[19]:


aardappelen = data.loc[data['Product'] == "Pootaardappelen (totaal)"]
haver = data.loc[data['Product'] == "Haver"]
appels = data.loc[data['Product'] == "Appels"]
broccoli = data.loc[data['Product'] == "Broccoli"]
aardbeien = data.loc[data['Product'] == "Aardbeien, productie"]


# In[20]:


fig = go.Figure()

fig.add_trace(go.Bar(x=aardappelen['Jaar'],y=aardappelen['Hoeveelheid'],name='Aardappelen'))
fig.add_trace(go.Bar(x=haver['Jaar'],y=haver['Hoeveelheid'],name='Haver'))
fig.add_trace(go.Bar(x=appels['Jaar'],y=appels['Hoeveelheid'],name='Appels'))
fig.add_trace(go.Bar(x=broccoli['Jaar'],y=broccoli['Hoeveelheid'],name='Broccoli'))
fig.add_trace(go.Bar(x=aardbeien['Jaar'],y=aardbeien['Hoeveelheid'],name='Aardbeien'))

dropdown_buttons = [
    {'label': 'Aardappelen', 'method': 'update', 
    'args':[{'visible': [True,False,False,False,False]},
            {'title': 'Aardappelen'}]},
    {'label': 'Haver', 'method': 'update', 
    'args':[{'visible': [False,True,False,False,False]},
            {'title': 'Haver'}]},
    {'label': 'Appels', 'method': 'update', 
    'args':[{'visible': [False,False,True,False,False]},
            {'title': 'Appels'}]},
    {'label': 'Broccoli', 'method': 'update', 
    'args':[{'visible': [False,False,False,True,False]},
            {'title': 'Broccoli'}]},
    {'label': 'Aardbeien', 'method': 'update', 
    'args':[{'visible': [False,False,False,False,True]},
            {'title': 'Aardbeien'}]},
    
]

fig.update_layout({
    'updatemenus':[{
        'type': "dropdown",
        'x': 1.3,
        'y':0.5,
        'showactive': True,
        'active': 0,
        'buttons': dropdown_buttons,
    }]
})
fig.update_layout({
        'yaxis': {'range': [0, 24000]}},
title = 'Producten per jaar',
xaxis_title_text='Jaar',
yaxis_title_text='Hoeveelheid',
width = 1000, height = 500,
)
st.plotly_chart(fig, use_container_width=True)


# In[21]:


## Slider


# In[22]:


fig = px.histogram(data_frame=data, 
                   x = 'Hoeveelheid',
                   y= 'Product', 
                   animation_frame= 'Jaar'
                  )
fig.update_layout({
        'xaxis': {'range': [0, 100000]}},
title = 'Producten per jaar',
xaxis_title_text='Opbrengst',
yaxis_title_text='Soort product',
width = 1000, height = 500,
)
st.plotly_chart(fig, use_container_width=True)


# In[23]:


## Checkbox


# In[ ]:




