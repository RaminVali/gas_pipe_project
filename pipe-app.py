#This is my webapp visualising and exploring the available USA Gas Pipeline incident data

import streamlit as st
import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.offline import init_notebook_mode
import plotly.express as px

st.write("""

# Exploring USA Gas Pipeline Accident Data
The United States maintains over 3.2 million kilometres of natural gas distribution mains and pipelines, over 500,000 kilometres of gas transmission and gathering pipelines, over 180,000 kilometres hazardous liquid pipelines, and 114 active liquid natural gas
plants that are connected to natural gas transmission and distribution 
 systems [[1]](https://www.ncsl.org/research/energy/state-gas-pipelines.aspx#:~:text=The%20United%20States%20maintains%20about,gas%20transmission%20and%20distribution%20systems.).

The pipeline system includes:

 * __Transmission lines__ to transport large quantities of natural gas or hazardous liquids over long distances from gathering lines or storage facilities to distribution centers,
   storage facilities, power plants, industrial customers and municipalities.
    Most transmission pipelines are located underground.
 
 * __Distribution lines__ to move gas to industrial customers. Smaller distribution lines connect businesses and homes.
  Distribution lines usually are installed in underground utility easements along streets. Gas pipeline *commodities* include natural gas, hydrogen gas, propane gas and synthetic gas. Almost all gas gathering lines are for natural gas. Distribution and transmission are mostly for natural gas, but include some propane and hydrogen.
 
In this project we explore the incident data provided by the **Pipeline and Hazardous Materials Safety Administration** [(PHMSA)](https://www.phmsa.dot.gov/data-and-statistics/pipeline/distribution-transmission-gathering-lng-and-liquid-accident-and-incident-data) to explore the locations, causes and associated casualties of gas pipeline incidents in the United States over the last 10 years. We utilise [plotly](https://plotly.com/) to make interactive visualisations of the data. 

""")

st.write("""
# Pipeline Geographical Locations 
The figures below show the geographical locations of the gas pipelines. The data associated with these can viwed by hovering over the individual shape. 
The pipeline representations are in three parts, the __Transmission lines__, the __Distribution lines__, and finally the __Gulf of Mexico lines__. 
""")
# Loading the converted shape files. The shape files have to be converted from their geometric multiline representations to lat/lon 
# representations of the two ends of each of the segments. The algorithm to do this is in the previous versions of the code in the github repository. 
# You can simply uncomment each cell and have the .pkl variable constructed again. It just takes a little bit fo time, hence the 
# loading of the variable to save time.  
geo_df_trans = pd.read_pickle('geo_df_trans.pkl') #Gas transmission lines file
geo_df = pd.read_pickle('geo_df.pkl') # Gas distribution lines file, its the largest
geo_df_mx = pd.read_pickle('geo_df_mx.pkl') #Gas pipelines in the Gulf of Mexico

#Plotting the dataframe we made with lats, lons and names etc form the HGL, Inter/Intra and Gulf of Mexico shape files, 
# we manipulate the hoverdata to display what we like.


# # #--------------------------------------
# #Inter/Intra State Pipelines
fig = px.line_geo(geo_df,lat = geo_df.lats, lon = geo_df.lons, hover_name = geo_df.Operator_Name, locationmode="USA-states", scope="usa",
                 hover_data={'lats':False, #remove latitude form hover data
                             'lons':False, #remove longitude form hover data
                             'Category':False, #remove category from hover data
                            },
                               color = 'Category' )
fig.update_traces(line_color='#293d6e', line_width=0.25) #updating the default lines used for HGL piepes
# #--------------------------------------

#HGL Transmission Lines
#plotting the shape file onto the USA map using plotly
fig2 = px.line_geo(geo_df_trans,lat = geo_df_trans.lats, lon = geo_df_trans.lons, hover_name = geo_df_trans.Pipe_Name, locationmode="USA-states", scope="usa",
                 hover_data={'lats':False, #remove latitude form hover data
                             'lons':False, #remove longitude form hover data
                             'Operator_Name': True, 
                             'Category':False, #remove category from hover data
                            },
                               color = 'Category')
fig2.update_traces(line_color='#000000', line_width=.75) #updating the default lines used for HGL piepes
# #

# # GULF OF MEXICO
fig3 = px.line_geo(geo_df_mx,lat = geo_df_mx.lats, lon = geo_df_mx.lons, hover_name = geo_df_mx.Operator_Name, locationmode="USA-states", scope="usa",
                 hover_data={'lats':False, #remove latitude form hover data
                             'lons':False, #remove longitude form hover data
                             'Category':False, #remove category from hover data
                              },
                              color = 'Category' )

fig3.update_traces(line_color='#8723e3', line_width=0.25) #updating the default lines used for HGL piepes



# # #--------------------------------------
# #Adding all the traces together in one map
fig.add_trace(fig2.data[0]) 
fig.add_trace(fig3.data[0]) 
# # #--------------------------------------

# #fig.update_layout()
fig.update_layout(title = 'USA Gas Pipelines',
                  hovermode="closest",
                  margin={"r":0,"t":0,"l":0,"b":0},
                  showlegend = False)

fig.update_geos(
    resolution=50,
    showland=True, landcolor="#b1f699",
    showlakes=True, lakecolor="LightBlue")

st.plotly_chart(fig)

st.write("""

We can see that the highest concentration of the pipelines is in the state of Texas, followed by the Gulf of Mexico region and Oklahoma.

# Loading and Filtering the Gas Transmission Lines Incident Data

Now that we have some knowledge about the location of the various types of gas pipelines,
we take a closer look at the incident data associated with these.
We start with the gas transmission pipelines. 

""")

#changed encoding by saving as csv file again, tab delimited
Gas_Dist_Accidents = pd.read_csv('data/incident_gas_transmission_gathering_jan2010_present.csv',low_memory=False) 


# Reading in the required columns form the text file. I have kept it as a text file so it is easy to modify for future uses. 
req_clmns = []
#importing the list of required columns form the text file
with open('data/Gas_Trans_required_columns.txt') as f: 
    lines = f.readlines()
f.close()

for l in lines:
    req_clmns.append(l.strip()) #getting rid of the "\n" escape character

Gas_Dist_Acc = Gas_Dist_Accidents[req_clmns]
# I have discovered some outliers that fall outside the continental USA, so I will explude those: 
Gas_Dist_Acc = Gas_Dist_Acc[(-140<Gas_Dist_Acc['LOCATION_LONGITUDE']) & (Gas_Dist_Acc['LOCATION_LONGITUDE']<-50)]
Gas_Dist_Acc = Gas_Dist_Acc[Gas_Dist_Acc['LOCATION_LATITUDE']<50]



#Grouping the dataframe by year and then state counts, and sorting it.
grouped_Year_State = Gas_Dist_Acc.groupby(['IYEAR','OPERATOR_STATE_ABBREVIATION']).count().sort_values(by = 'REPORT_NUMBER',  ascending=False).reset_index()

# The column report number (1 on 1 relationship) can be our incident count so:
grouped_Year_State.rename(columns = {'IYEAR':'Incident Year','OPERATOR_STATE_ABBREVIATION':'Incident State', 'REPORT_NUMBER':'No of Incidents'}, inplace=True)

st.write('''Here is a representation of the available data:  ''')

#Dispalying the dataframe on the webapp
st.dataframe(Gas_Dist_Acc)

st.write('''Over the last 10 years, 1512 incidents have ben recorded in the gas transmission pipelines.''')

# Plotting the data using plotly:
fig = px.bar(data_frame=grouped_Year_State, y = 'Incident Year', x = 'No of Incidents',
            color = 'Incident State', orientation='h', 
            color_discrete_sequence= px.colors.sequential.deep_r,
            title='Number of Gas Transmission Line Incidents in Past 10 Years by State') #remove latitude form pipe)

fig.update_layout(showlegend=True)
st.plotly_chart(fig)


st.write("""
## Exploring the Injuries, Fatalities and Cuases of Gas Transmission Line Incidents
### Fatalities and Injuries
""")

# Calculating the number of fatalities
fatality = Gas_Dist_Acc['FATAL'].value_counts().reset_index()
fatality.rename(columns={'index':'Fatalities'}, inplace = True)
fatality['deaths'] = fatality['Fatalities']*fatality['FATAL']
# print('The fatality count is:')
# print(fatality['deaths'].sum())
Deaths = fatality['deaths'].sum()

# Calculating the number of injuries
injury = Gas_Dist_Acc['INJURE'].value_counts().reset_index()
injury.rename(columns={'index':'Injuries'}, inplace = True)
injury['injuries'] = injury['Injuries']*injury['INJURE']
# print('The injury count is:')
# print(injury['injuries'].sum())
Injuries = injury['injuries'].sum()

data = {'Death':fatality['deaths'].sum(),'Injury':injury['injuries'].sum()}
Casualties=pd.DataFrame(data,index=['Number of Casualties'])
st.table(Casualties)

st.write("""
We can see that over the last 10 years, a total of 31 deaths and 117 injuries have occured. Given that the transmission lines are generally not in populated areas and are not very widespread, this low count is expected. We will compare this with the far more extensive and widespread distribution network.

### Causes of the Gas Transmission Line Incidents
PHMSA has categorised the gas transmission line incident cause into 8 different major cause goups. Each cause group is divided into sub-cause. The figure 
below presents the causes of the gas transmission pipeline incidents in the last 10 years. The cause details and number of incidents for each can be viewed by hovering over each segment.
""")

Acc_Cause = Gas_Dist_Acc.groupby(['CAUSE','CAUSE_DETAILS']).count().reset_index()
Acc_Cause.rename(columns = {'REPORT_NUMBER':'Number of Incidents','CAUSE':'Accident Cause', 'CAUSE_DETAILS':'Details'}, inplace=True) #each incident has a report number so its count is incident count

Acc_Cause['Accident Cause'] = Acc_Cause['Accident Cause'].str.lower().str.title()
Acc_Cause['Details'] = Acc_Cause['Details'].str.lower().str.capitalize()
# #trying with plotly express
fig = px.bar(data_frame=Acc_Cause, y = 'Accident Cause', x = 'Number of Incidents', color = 'Details',
            color_discrete_sequence= px.colors.sequential.Bluyl_r, orientation='h', 
            title='Causes of Gas Transmission Line Incidents in Past 10 Years',hover_data={'Accident Cause':False}) #remove latitude form pipe)
fig.update_layout(showlegend=False)
st.plotly_chart(fig)

st.write('''We can see that the main cause for the incidents is equiment failure followed by corrosion failure. To get a 
better understanding of the share of each incident cause we can use a pie chart:
 ''')

fig = px.pie(Acc_Cause, values='Number of Incidents', names='Accident Cause',
             color_discrete_sequence= px.colors.sequential.Bluyl,
             title = 'Gas Distribution Indicent Cause Breakown')
st.plotly_chart(fig)

st.write(''' # Incidents in the Gas Distribution Network 
We now explore the incidents in the gas distribution network which is far more extensive than the transmission pipeline and affects
geographical locations with high population density. We will first explore the geographical locations
of the gas distribution pipelines in the last 10 years.
''')
# Working on Gas Distribution Accidents now:
#changed encoding by saving as csv file again, tab delimited
Gas_Dist_Accidents = pd.read_csv('data/incident_gas_distribution_jan2010_present.csv',low_memory=False) 
req_clmns =  []
with open('data/Gas_Dist_required_columns.txt') as f: #importing the list of required columns form the text file
    lines = f.readlines()
f.close()
for l in lines:
    req_clmns.append(l.strip()) #getting rid of the "\n" escape character
Gas_Dist_Acc = Gas_Dist_Accidents[req_clmns]
#There is an outlier in the longitude column (large negative number), so we find it 
# and drop that whole row so we can do the plotting 
drop_row_index = Gas_Dist_Acc['LOCATION_LONGITUDE'].idxmin() #getting the row index for the minimum oulier 
Gas_Dist_Acc.drop(Gas_Dist_Acc.index[drop_row_index])

# I have discovered some outliers that fall outside the continental USA, so I will explude those: 
Gas_Dist_Acc = Gas_Dist_Acc[(-140<Gas_Dist_Acc['LOCATION_LONGITUDE']) & (Gas_Dist_Acc['LOCATION_LONGITUDE']<-50)]
Gas_Dist_Acc = Gas_Dist_Acc[Gas_Dist_Acc['LOCATION_LATITUDE']<50]

st.write('''Over the last 10 years, 1314 incidents have been recorded in the gas distribution pipelines.''')


#Formatting  the hovertext
Gas_Dist_Acc['hover_text'] = Gas_Dist_Acc["LOCATION_CITY_NAME"].str.title()+", "+ Gas_Dist_Acc["LOCATION_STATE_ABBREVIATION"]+ ", "+"Cause: "+Gas_Dist_Acc['CAUSE'].str.lower().str.capitalize()+", " + Gas_Dist_Acc["IYEAR"].astype(str)

fig = go.Figure(data = go.Scattergeo(
                    lat=Gas_Dist_Acc.LOCATION_LATITUDE, lon=Gas_Dist_Acc.LOCATION_LONGITUDE,
                    text=Gas_Dist_Acc['hover_text'], 
                    mode = 'markers',
                    marker = dict(
                    size = 4,
                    opacity = 0.8,
                    reversescale = True,
                    autocolorscale = False,
                    symbol = 'circle', 
                    line = dict(
                        width=1,
                        color='rgba(219, 15, 15)'
                    ),
                    colorscale = 'Hot_r',
                    cmin = 2010,
                    color = Gas_Dist_Acc.IYEAR,
                    cmax = Gas_Dist_Acc.IYEAR.max(),
                    colorbar_title="Incident Year")))

fig.update_layout(
        title = 'Gas distribution line incidents in the last 10 years',
        geo_scope='usa',
        hovermode="closest",
        margin={"r":0,"t":0,"l":10,"b":0},
        showlegend = True
    )
fig.update_geos(
    resolution=50,
    showland=True, landcolor="#b1f699",
    showlakes=True, lakecolor="LightBlue")

st.plotly_chart(fig)

st.write('''As can be seen from the figure above the majority of the gas distribution line incidents happen in the major 
population centres in the USA. It is beneficial to have a more detailed view of the number of incidents in each state over the
span of 10 years.''')
grouped_Year_State = Gas_Dist_Acc.groupby(['IYEAR','LOCATION_STATE_ABBREVIATION']).count().sort_values(by = 'NAME',  ascending=False).reset_index()

#creating a data frame as the output of the groupby. The product of the groupby is a series, 
# so you do a to_frame to get the df and then reset the index to get a proper index
# The column NAME (1 on 1 relationship) can be our incident count so:

grouped_Year_State.rename(columns = {'IYEAR':'Incident Year','LOCATION_STATE_ABBREVIATION':'Incident State', 'NAME':'No of Incidents'}, inplace=True)
#Sorting based on year
grouped_Year_State=grouped_Year_State.sort_values("Incident Year") # Make sure you sort the time horizon column in ascending order
#plotting using plotly:
fig = px.bar(data_frame=grouped_Year_State, y ='No of Incidents' , x = 'Incident State',
            color = 'Incident Year', orientation='v', 
            color_continuous_scale=px.colors.sequential.OrRd_r,
            title='Number of Gas Distribution Incidents in Past 10 Years by State') #remove latitude form pipe)

fig.update_layout(showlegend=True)
st.plotly_chart(fig)

st.write('''The figure above is not very telling and difficult to interpret even with the hover text.
 So we do a choropleth map for every year. So we will try another method of presenting the data. We can use an animated choropleth map that displays the density of incidents per year for each state[[2]](https://towardsdatascience.com/simplest-way-of-creating-a-choropleth-map-by-u-s-states-in-python-f359ada7735e) 
''')
fig = px.choropleth(grouped_Year_State,
                    locations='Incident State', 
                    locationmode="USA-states", 
                    scope="usa",
                    color='No of Incidents',
                    color_continuous_scale="agsunset_r", 
                    animation_frame='Incident Year' #make sure 'Incident Year' is string type and sorted in ascending order
                    )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig)

st.write('''
## Explorting the Injuries, Fatalities and Cuases of the Gas Transmission Network Incidents
### Fatalities and Injuries
 ''')

# Calculating the number of fatalities
fatality = Gas_Dist_Acc['FATAL'].value_counts().reset_index()
fatality.rename(columns={'index':'Fatalities'}, inplace = True)
fatality['deaths'] = fatality['Fatalities']*fatality['FATAL']
# print('The fatality count is:')
# print(fatality['deaths'].sum())
Deaths = fatality['deaths'].sum()

# Calculating the number of injuries
injury = Gas_Dist_Acc['INJURE'].value_counts().reset_index()
injury.rename(columns={'index':'Injuries'}, inplace = True)
injury['injuries'] = injury['Injuries']*injury['INJURE']
# print('The injury count is:')
# print(injury['injuries'].sum())
Injuries = injury['injuries'].sum()

data = {'Death':fatality['deaths'].sum(),'Injury':injury['injuries'].sum()}
Casualties=pd.DataFrame(data,index=['Number of Casualties'])
st.table(Casualties)

st.write('''
As can be seen from the table above, the injury/fatality rate is larger than
the Gas Transmission lines injury/fatality, so this warrants a closer look.
It is beneficial to combine the fatalities and the injuries into a new column "Casualties".
The reason for the larger number of casualties, is that the gas distribution network has a 
considerable presence in locations with higher population densities. As a result, 
the casualties are higher when there is an incident.

In terms of causes, it can be seen that natural force damage due to earth movement followed
by unknown causes contribute to the highest casualties in the last 10 years. 
 ''')
Casualties = Gas_Dist_Acc[(Gas_Dist_Acc['FATALITY_IND']=='YES')|(Gas_Dist_Acc['INJURY_IND']=='YES')]
Casualties_by_State = Casualties.groupby(['LOCATION_STATE_ABBREVIATION', 'CAUSE', 'CAUSE_DETAILS']).sum()
Casualties_by_State= Casualties_by_State.reset_index()
Casualties_by_State.rename(columns = {'LOCATION_STATE_ABBREVIATION':'State',
                                    'FATAL':'Number_Fatalities',
                                    'CAUSE': 'Cause',
                                    'CAUSE_DETAILS': 'Cause Details',
                                    'INJURE':'Number_Injuried'}, inplace=True)


Casualties_by_State['Cause'] = Casualties_by_State['Cause'].str.lower().str.capitalize()
Casualties_by_State['Cause Details'] = Casualties_by_State['Cause Details'].str.lower().str.capitalize()
Casualties_by_State['Casualties'] = Casualties_by_State['Number_Fatalities']+Casualties_by_State['Number_Injuried']
fig = px.bar(data_frame=Casualties_by_State, y ='Casualties' , x ='State' , color ='Cause' , #hover_data='CAUSE_DETAILS',
            color_discrete_sequence= px.colors.sequential.Jet, orientation='v',
            hover_data={'Cause Details'},
            title='Casualties of Gas Distribution Line Incidents in Past 10 Years')
fig.update_layout(showlegend=True)
st.plotly_chart(fig)

st.write(''' As can be seen form the figure above, th State of New York has the highest number of casualties
for gas distribution pipe related incidents in the last 10 years. We can compare that with the incident data for the 
same gas distribution pipeline, where the State of California had the highest number. We can also use a map to show the worst 
States in terms of the total casualties in the last 10 years:
''')
Casualties_by_State =Casualties_by_State.groupby(['State']).sum().reset_index() #grouping based on States only for the heatmap
#Plotting the heatmap
fig = px.choropleth(Casualties_by_State,
                    locations='State', 
                    locationmode="USA-states", 
                    scope="usa",
                    color='Casualties',
                    color_continuous_scale="speed", 
                    )

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig)

st.write(''' 
# Conclusions

In this project we explored the incident data provided by the Pipeline and Hazardous Materials Safety Administration [(PHMSA)](https://www.phmsa.dot.gov/data-and-statistics/pipeline/distribution-transmission-gathering-lng-and-liquid-accident-and-incident-data)
 and found some insights related to the locations, causes and associated casualties of gas pipeline incidents in the United States
over the last 10 years. We utilised [plotly](https://plotly.com/) to make interactive
visualisations of the data to help us understand the available data better. 

Causes, casualties, and incident locations are inherently different between gas transmission and gas distribution pipelines. 

The former has a lower casualty count as its not distributed among the areas with large
 population, naturally the highest number of incidents occur in Texas, Oklahoma 
 and Gulf of Mexico where the transmission lines are more prevalent. The number 
 of incidents per year is steady around 100. The major causes for gas transmission 
 lines are equipment failure, mainly as a result of malfunctioning control and relief equipment, 
 followed by corrosion issues. 

Gas distribution pipeline incidents on the other hand occur in the locations with much 
larger population density. As a result, their casualty rates are higher. 
The pipeline network itself is much more widespread as well, contributing to the 
higher incident and casualty rate. California has the highest number of gas distribution 
incidents in the last 10 years followed by New York; however, in terms of casualties, 
the State of New York has the highest number of casualties. The main contributor to the 
incidents resulting in casualties is natural force damage due to earth movement.
''')