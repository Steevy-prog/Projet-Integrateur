import folium

3.971656, 9.790969
3.969675, 9.792060
3.970051, 9.792535


# Coins calculés
coins = [
    (3.971340, 9.790578),
    (3.971656, 9.790969),
    (3.970051, 9.792535),
    (3.969675, 9.792060)
]

# Carte centrée
m = folium.Map(location=[3.96439, 9.80059], zoom_start=17)

# Dessiner polygone
folium.Polygon(locations=coins, color="blue", weight=3, fill=True, fill_opacity=0.1).add_to(m)

# Ajout point central
folium.Marker([3.96439, 9.80059], popup="Centre du campus").add_to(m)

m.save("ucac_icam_campus.html")