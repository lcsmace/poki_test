from django.shortcuts import render
import pandas as pd
import folium
import requests 
import os
from django.conf import settings
import io
import matplotlib.pyplot as plt
import ast




def maps(request):


    state_geo = requests.get("https://raw.githubusercontent.com/python-visualization/folium-example-data/main/world_countries.json").json()
    
    project_directory = settings.BASE_DIR

    csv_path = os.path.join(project_directory, 'cadastradas_por_pais.csv')

    population = pd.read_csv(csv_path)

    def get_lat_long(country):
        username = 'lcsmacedo'
        base_url = 'http://api.geonames.org/searchJSON'
        params = {
            'q': country,
            'username': username
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'geonames' in data and len(data['geonames']) > 0:
                location = data['geonames'][0]
                return location['lat'], location['lng']
        return None
    


    countries_list = population['country_name'].values 


    data_list = []


    for country in countries_list:    
    
        lat_long = get_lat_long(country)

        if lat_long:

            data_list.append({'country':country, 'coordinates':(
                lat_long[0],lat_long[1]
            )})


    df = pd.DataFrame(data_list)

    df.to_csv('countries_lat_long.csv', index= False)

    data = pd.read_csv('countries_lat_long.csv', converters={"coordinates": ast.literal_eval},)

    pie_charts_data = zip(population.num_people)

    fig = plt.figure(figsize=(0.5, 0.5))
    fig.patch.set_alpha(0)
    ax = fig.add_subplot(111)
    plots = []
    for sizes in pie_charts_data:
        ax.pie(sizes, colors=("#e6194b", "#19e6b4"))
        buff = io.StringIO()
        plt.savefig(buff, format="SVG")
        buff.seek(0)
        svg = buff.read()
        svg = svg.replace("\n", "")
        plots.append(svg)
        plt.cla()
    plt.clf()
    plt.close()

    # population_dict = population.set_index("country_name")["num_people"]
    
    
    # def my_color_function(feature):
        
    #     country_name = feature["properties"]["name"]

    #     population = population_dict.get(country_name, 0) 
     
    #     if population > 0:
    #         return "orange" 
    #     else:
    #         return "white"  
        
    m = folium.Map(
    tiles=folium.TileLayer(no_wrap=True)
)


#     folium.GeoJson(
#         state_geo,
#         style_function=lambda feature: {
#             "fillColor": my_color_function(feature),
#             "color": "black",
#             "weight": 2,
#             "dashArray": "5, 5",
#     },
# ).add_to(m)


    folium.Choropleth(
    geo_data=state_geo,
    name="choropleth",
    data=population,
    columns=["country_name", "num_people"],
    key_on="feature.properties.name",
    fill_color="OrRd",
    fill_opacity=0.5,
    line_opacity=0.2,
    nan_fill_color="purple",
    nan_fill_opacity=0,
    legend_name="Cadastradas por país",
).add_to(m)
    


    for i, coord in enumerate(data.coordinates):
        marker = folium.Marker(coord)
        icon = folium.DivIcon(html=plots[i])
        marker.add_child(icon)
        popup = folium.Popup(
            "{} <br>\n Population: {}".format(population.country_name[i],population.num_people[i])
        )
        marker.add_child(popup)
        m.add_child(marker)
    m.get_root()

    context={
    'map': m._repr_html_()
}

    return render(request, 'maps.html', context) 