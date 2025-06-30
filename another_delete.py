import folium

# Coins calculés
coins = [
    (3.96619, 9.79869),
    (3.96619, 9.80249),
    (3.96259, 9.80249),
    (3.96259, 9.79869)
]

# Carte centrée
m = folium.Map(location=[3.96439, 9.80059], zoom_start=17)

# Dessiner polygone
folium.Polygon(locations=coins, color="blue", weight=3, fill=True, fill_opacity=0.1).add_to(m)

# Ajout point central
folium.Marker([3.96439, 9.80059], popup="Centre du campus").add_to(m)

m.save("ucac_icam_campus.html")