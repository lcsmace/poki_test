from django.shortcuts import render
import pandas as pd
import folium
import requests 
import os
from django.conf import settings

def maps(request):


    state_geo = requests.get("https://raw.githubusercontent.com/python-visualization/folium-example-data/main/world_countries.json").json()
    
    project_directory = settings.BASE_DIR

    csv_path = os.path.join(project_directory, 'cadastradas_por_pais.csv')

    population = pd.read_csv(csv_path)

    # population_dict = population.set_index("country")["population"]
    
    
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
    fill_opacity=0.01,
    line_opacity=0.2,
    legend_name="População por país",
).add_to(m)

    context={
    'map': m._repr_html_()
}

    return render(request, 'maps.html', context)    