'''
    Name: Jack \n
    CS230: 5 \n
    Data: TRASH SCHEDULES BY ADDRESS (CSV) \n
    URL:
    \n
    Description: Welcome to my streamlit website.
    This website analyzes data from the Analyze Boston database
    on trash schedules by address, and visualizes it in an easily
    understandable manner. in addition, it helps citizens find out
    when their trash (with map location) is recycled.\n \n
    Pictured below is the dataset used for this project.
'''
'''
Complaint
    In addition, I have a MASSIVE COMPLAINT ABOUT THE CSV FILES USED.
    I basically picked my CSV as soon as it was mentioned in class and most options were already taken up. So I had to
    Take the trash option. You see. Compared to other options. There is so much quantity of data, but the data
    happens to have very little to really work with in terms of columns. 
    The Trash Schedule has nearly 400,000 rows! Thats a lot of data! But! Unlike something like the cannabis registry,
    Really just has 2 things to work with, Trash Day, And Locational information. It is very hard to creatively create
    applications for the data in comparison. Next. 400,000 Rows. This leads to problem 2. Github has a 25mb upload limit.
    My CSV file cannot be uploaded unless shortened. Or I find a workaround, which I am currently at a deadend with.
    Also. It makes any commands that need to go through the data go really slow. A simple command that turns a column of the DF into a list
    takes 10 seconds to print. 
    So the data given is in comparison to other datasets, creatively constrictive (which also effects visualization options)
    Cannot be uploaded easily to github WHICH IS NECESSARY TO GET THE EXTRA CREDIT.
    Plus its so much slower to work with
    
    Feedback: Make all the data in later year projects checked for size and data. Because as it is, how fast you pick
    Even by a few seconds, will make your job 10 times harder then other 
'''
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import fuzzywuzzy as fz
from fuzzywuzzy import process
import pydeck as pdk
#Need to download
path = ""C:/Users/nenoc/Downloads/pythonProject1/""
df = pd.read_csv(path + "data2.csv")
#This is the part where I make a dictionary to count each repeated city.
#By Mailing Neighbourhood, Recollect Date, Trashday, PWD District.
st.set_page_config(page_title="Trash Hub",layout="wide")
image = ("https://cdn.discordapp.com/attachments/664672681286828045/1186168819249577994/garbage-truck.png?ex=659244cc&is=657fcfcc&hm=8c39726978f03bcda5cadd48791a594434092da7cfcef0bcfe81dc4f707457b2&")
st.image(image,caption = 'Track Trash Today!',use_column_width=False)

def counting(column = "mailing_neighborhood"):
    tempdict = {}
    tempdf = df.dropna()
    for i in tempdf[column]:
        if i in tempdict:
            tempdict[i] += 1
        else:
            tempdict[i] = 1
    count_nan = len(df[column]) - df[column].count()
    return tempdict,count_nan
    #returns a count of all in the column, and also returns the total nan.

def validnum(num):
    try:
        floatn = float(num)
        return True
    except ValueError:
        return False
def listify(column = "full_address"):
    templist = []
    for i in df[column]:
        templist.append(i)
    return templist
#Create Program to return trash schedule by address or ZIPCode.
#Valid Num is necessary to create because isnumeric does not account for - signs unfortunately.
def bringschedule(entry):
    if validnum(entry):
        entry = float(entry)
        tempdf = df.loc[df['zip_code'] == entry]
    else:
        templist = listify("full_address")
        #application of outside package
        result = process.extract(entry,templist,limit=1)
        fazu = result[0][0]
        tempdf = df.loc[df["full_address"]==fazu]
    return tempdf
#Uses validnum to decide if a input is a zipcode or address. Zipcodes are easy but they have a lot of duplicates, so it returns a bunch of subs.
#However, We just want the closest address. So we use Fuzzy Wuzzy package (for extra credit) to find the closest one.
#See, Fuzzy wuzzy is a pain to deal with though, since it effectively compares the entry to each row (By which I have like 400k rows)
#To check which is the closest by giving them a number to each of them based on matchingness and returning that.
#Limit means it only returns one. And the [0][0] is because it not only gives the right address that you want, but also the score it used to come to the conclusion.
def zipmapping(zip, zoom):
    sampledata = zip[["y_coord", "x_coord", "full_address", "zip_code", "state", "trashday"]]
    layer = pdk.Layer('ScatterplotLayer', data=sampledata, get_position='[x_coord, y_coord]', auto_highlight=True, get_radius=30, get_fill_color=[200, 50, 0, 250], pickable=True,)
    hover = {"html": "Address: {full_address}, {state}, {zip_code}<br/>Trashday(s): {trashday}",
             "style": {"backgroundColor": "white", "color": "black"},}
    defaultview = pdk.ViewState(latitude=sampledata['y_coord'].mean(), longitude=sampledata['x_coord'].mean(), zoom=zoom)
    deck = pdk.Deck(layers=[layer], initial_view_state=defaultview, map_style='mapbox://styles/mapbox/streets-v11', tooltip=hover,)
    st.pydeck_chart(deck)
#It makes the map. I See, Zipmapping is kind of an inaccurate name but I decided to keep it since I oringinally made it for zip but it also works for address.
#Its a simple, throw in a row, get a map dot for it, and we also find the mean of all the coords to find where the center of the map should be based on data.
#These few lines took an eternity.
def chart(chart_type, data, catnam, quantitynam, nulls):
    st.title('Trash Schedules Data')
    if chart_type == 'bar':
        color = st.color_picker('Select Bar Color', '#000000')
        st.bar_chart(data.set_index(catnam), color= color)
    elif chart_type == 'pie':
        x, y = plt.subplots()
        y.pie(data[quantitynam], labels=data[catnam], autopct='%1.1f%%', explode= [0.03 for vari in data[catnam]],textprops={'fontsize': 6})
        st.pyplot(x)
    else:
        st.warning("Invalid chart type. Please choose 'bar' or 'pie'.")
    st.write(f'The total number of nulls in the dataset is {nulls} \n and has thus been excluded.')

def graph(category, catnam, quantitynam, chart_type='bar'):
    tempdict, nulls = counting(category)
    tempdf = pd.DataFrame(list(tempdict.items()), columns=[catnam, quantitynam])
    chart(chart_type, tempdf, catnam, quantitynam,nulls)
#Can be crammed into chart() but this has the same effect.
#I kept on using the wrong dataset. and heatmap took forever.
def heatmap(df):
    # Much more efficient then running it through if statements and validnum()
    df['x_coord'] = pd.to_numeric(df['x_coord'])
    df['y_coord'] = pd.to_numeric(df['y_coord'])
    layer = pdk.Layer('HexagonLayer', data=df, get_position='[x_coord, y_coord]', auto_highlight=True,
                      elevation_scale=20, pickable=True, extruded=True, coverage=1,)
    #Uses Hexagon because the actual heatmap type was less distinctive.
    view_state = pdk.ViewState(latitude=df['y_coord'].mean(), longitude=df['x_coord'].mean(), zoom=10,)
    deck = pdk.Deck(layers=[layer], initial_view_state=view_state, map_style='mapbox://styles/mapbox/streets-v11')
    st.pydeck_chart(deck)


tab1,tab2,tab3,tab4 = st.tabs(["About", "Track trashdays","Boston's Trash Collection Data","Citations"])
#So. Streamlit. We need to first access the data through pd. AND ANALYZE THAT SHIT!
#Bar Chart can be used, alongside Pie Chart to see MA distribution.
#Trash Schedule should allow for people to search via address, and zipcode.

with tab1:
    st.title("Boston Trash Schedules")
    st.write( "Welcome to my streamlit website. This website analyzes data from the Analyze Boston database \n on trash schedules by address, and visualizes it in an easily understandable manner. in addition, it helps citizens find out \n when their trash (with map location) is recycled.\n \n Pictured below is the dataset used for this project.")

    #Make this dataframe sortable through asceding or descending by Column/
    #Filter Data by one Condition, as well as with 2+ and or.
    #Return highest or lowest value in a certain column. We cam do this with the bar chart, by counting which city has the most coverage.
    #Analyze data with pivot tables
    st.write(df)
#Make select list for days.

with tab2:
    st.header("Please Input Your Zipcode or Address")
    entry = st.text_input("If an address is unavailable, the closest alternative will be presented")
    zip = bringschedule(entry)
    zoom = st.slider('Zoom Level', min_value=8, max_value=16, value=12)
    zipmapping(zip,zoom)

#Should Return, based on selection, a map, data.


with tab3:
    #Can jerry rig to offer a sorted version.######
    selection = st.selectbox("Select Chart Type", ["bar", "pie"], index=0)
    graph("mailing_neighborhood","Mailing Neighborhoods","Quantity",selection)
    #Can use multiselect box to provide information analysis with graphs seperately.
#Can bring bar graphs based on listify, that being what is the distribution based on day, neighbourhood.
    #Focus on creating a map that takes lat and long from the df, based on day and neighborhood.
    st.write("Shown above is the coverage of Boston's Trash\n")
    temptable = (pd.pivot_table(df, index='mailing_neighborhood', values='state', aggfunc='count'))
    temptable = temptable.rename_axis("Mailing neighborhood") #To get rid of the underline
    temptable = temptable.rename(columns={'state': 'Locations'})
    st.dataframe(temptable,width=1000)
    st.write("Shown above is a Pivot Table, with sorting functionality, to see the exact quantities in each mailing neighborhood.\n From it, we can derive the amount of care taken into consideration for each of massachusetts' mailing neighborhoods, based on governmental trash coverage.")
    st.header("The Massachusett's Trash Heatmap")
    heatmap(df)
    st.write("Above is a visualization of coverage with regards to the massachusetts area, based on the data provided.")
with (tab4):
    choice = st.multiselect("Citations", options=["References", "Media"])
    if "References" in choice:
        st.header("References")
        st.write("https://github.com/nithishr/streamlit-data-viz-demo")
        st.write('https://deckgl.readthedocs.io/en/latest/layer.html')#Can be used for data analyze. Map stuff layer.
        st.write("https://docs.streamlit.io/library/api-reference/widgets")
        st.write("https://pypi.org/project/fuzzywuzzy/")
        st.write("https://www.youtube.com/watch?v=8G4cD7ofgCM")
    if "Media" in choice:
        st.header("Media")
        st.write("https://www.flaticon.com/free-icons/garbage-truck")
        st.write("https://data.boston.gov/dataset/trash-schedules-by-address/resource/fee8ee07-b8b5-4ee5-b540-5162590ba5c1")

    #Widgets, Page Design
    #Need to add legends, title, and color to graphs,
    #add one more graph