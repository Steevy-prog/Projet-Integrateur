import folium
import openrouteservice

# Initialize client
client = openrouteservice.Client(key="5b3ce3597851110001cf6248e40949eb54be42528efcacd8356dfa98")

# Coordinates: [longitude, latitude]
coords = [
    [4.0776000, 9.7076000],   # Start
    [4.0812000, 9.7098000]    # End
]

# Request route
route = client.directions(
    coords,
    profile='foot-walking',
    format='geojson'  # Important!
)

# Extract the geometry (a list of [lon, lat] points)
geometry = route['features'][0]['geometry']['coordinates']

# Convert to [lat, lon] for folium
locations = [list(reversed(coord)) for coord in geometry]

# Plot on folium
m = folium.Map(location=locations[0], zoom_start=17)
folium.PolyLine(locations, color="blue", weight=5).add_to(m)

# Add markers
folium.Marker(locations[0], tooltip="Start").add_to(m)
folium.Marker(locations[-1], tooltip="End").add_to(m)

# Save to HTML
m.save("route_map.html")
print("✅ Map saved as route_map.html")