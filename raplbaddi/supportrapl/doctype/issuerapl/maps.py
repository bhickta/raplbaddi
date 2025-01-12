import frappe
import googlemaps
import abc
import geopy.distance


class MapClient(abc.ABC):
    def get_distance(origins: list[str], destinations: list[str]):
        pass

class GoogleMapClient(MapClient):
    def __init__(self) -> None:
        self.api_key = frappe.db.get_single_value('Google Settings', 'api_key')
        self.client = googlemaps.Client(key=self.api_key)
        self.set()

    def _get_lat_lng_distance(self, coords_1, coords_2):
        return geopy.distance.geodesic(coords_1, coords_2).kilometers

    def set(self):
        self.distance_matrix = self.client.distance_matrix

    def road_distance(self, origin, destination):
        try:
            # Get the distance matrix with driving mode
            distance_matrix = self.distance_matrix(origin, destination, mode="driving")
            
            # Validate the response structure
            if 'rows' in distance_matrix and distance_matrix['rows']:
                elements = distance_matrix['rows'][0].get('elements', [])
                if elements and 'distance' in elements[0]:
                    # Extract the distance in meters and convert to kilometers
                    distance = elements[0]['distance']['value'] // 1000
                    return distance
                else:
                    return 0
            else:
                return 0
        except Exception as e:
            return 0