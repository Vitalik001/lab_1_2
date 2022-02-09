'''
main.py
'''
import argparse
import folium
from geopy.geocoders import Nominatim
from geopy import distance
from folium.plugins import MarkerCluster

parser = argparse.ArgumentParser(description='A tutorial of argparse!')
parser.add_argument('year', type=str, help='year of the map')
parser.add_argument('latitude', type=str, help='latitude of customer')
parser.add_argument('longitude', type=str, help='longitude of customer')
parser.add_argument('path', type=str, help='path to gile with locations')
args = parser.parse_args()
customer_coordinates=(args.latitude, args.longitude)


def get_lines_by_year(year, path):
    '''
    Returns all lines from file that containts (year)
    '''
    lines=set()
    new_year='('+year+')'
    with open(path, encoding="utf8", errors='ignore') as file:
        for line in file:
            if new_year in line:
                line=line.strip().split('\t')
                index=line[0].find('(')
                film=line[0][:index]
                line=[i for i in line if i!='']
                address=line[1]
                line=film+': '+address
                lines.add(line)
    return lines

def get_coordinates(place):
    '''
    returns coordinates of place
    >>> get_coordinates('Lviv, Ukraine')
    (49.841952, 24.0315921)
    '''
    plc=place
    if not place:
        return None
    try:
        geolocator = Nominatim(user_agent="my_request")
        location = geolocator.geocode(place)
        second_point=(location.latitude, location.longitude)
        return second_point
    except AttributeError:
        return get_coordinates(','.join(plc.split(',')[1:]))

def get_distance(coordinates1, coordinates2):
    '''
    returns distance between coordinates
    >>> get_distance((49.841952, 24.0315921), (34.0536909, -118.242766))
    9996.940305944334
    '''
    try:
        return distance.distance(coordinates1, coordinates2).km
    except AttributeError:
        return None


def get_10_films(films, user_coordinates):
    '''
    returns list with 10 nearest films to user
    >>> get_10_films({'"Wetten, dass..?" : Stadthalle, B�blingen,\
 Baden-W�rttemberg, Germany', '"Wetten, dass..?" : Messehalle,\
 Erfurt, Thuringia, Germany', '"Wetten, dass..?" : Rheinhalle,\
 D�sseldorf, North Rhine-Westphalia, Germany', '"Wetten, dass..?"\
 : Messehalle 1, Dresden, Saxony, Germany'}, (49.841952, 24.0315921))
    ['"Wetten, dass..?" : Messehalle 1, Dresden, Saxony, Germany :\
 (51.0493286, 13.7381437) : 742.737877303846', '"Wetten, dass..?" :\
 Messehalle, Erfurt, Thuringia, Germany : (50.9777974, 11.0287364)\
 : 931.6454618464014', '"Wetten, dass..?" : Stadthalle, B�blingen,\
 Baden-W�rttemberg, Germany : (51.0834196, 10.4234469) : 974.6285917231806',\
 '"Wetten, dass..?" : Rheinhalle, D�sseldorf, North Rhine-Westphalia,\
 Germany : (51.4789205, 7.5543751) : 1176.635889848888']
    '''
    coord=[]
    for film in films:
        coordinates=get_coordinates(film.split(':')[-1])
        dist=get_distance(coordinates, user_coordinates)
        film+=' : '+str(coordinates)+' : '+str(dist)
        if len(coord)<10:
            coord.append(film)
            continue
        coord=sorted(coord, key=lambda x: float(x.split(':')[-1]))
        if float(coord[-1].split(':')[-1])>dist:
            coord.pop()
            coord.append(film)
    return sorted(coord, key=lambda x: float(x.split(':')[-1]))



def create_map(user_coordinates, films):
    '''
    creates the map with markers of films
    '''
    cities=['Kyiv','Kharkiv','Donetsk','Odessa','Dnipro','Zaporizhzhya','Lviv','Kryvyi Rih']
    mapp=folium.Map(location=user_coordinates, zoom_start=3)
    group=folium.FeatureGroup(name='nearest Films')
    group2=folium.FeatureGroup(name='Ukraine cities')
    mapp.add_child(group)
    mapp.add_child(group2)
    marker_cluster2=MarkerCluster().add_to(group2)
    marker_cluster = MarkerCluster().add_to(group)
    for city in cities:
        folium.Marker(location=get_coordinates(city), popup=city,\
 icon=folium.Icon(color='darkblue', icon_color='white', icon='city',\
 angle=0, prefix='fa')).add_to(marker_cluster2)
    for film in films:
        latitude=float(film.split(':')[-2].strip().split(',')[0][1:])
        longitude=float(film.split(':')[-2].strip().split(',')[1][:-1])
        name=film.split(':')[0]
        folium.Marker(location=(latitude, longitude), popup=name+', '+args.year,\
 icon=folium.Icon(color='darkblue', icon_color='white', icon='film',\
 angle=0, prefix='fa')).add_to(marker_cluster)
    folium.Marker(location=user_coordinates, popup="It's me", \
icon=folium.Icon(color='red', icon_color='white', icon='male', angle=0, prefix='fa')).add_to(mapp)
    folium.TileLayer('cartodbdark_matter').add_to(mapp)
    folium.TileLayer('Stamen Terrain').add_to(mapp)
    mapp.add_child(folium.LayerControl())
    mapp.save('Map.html')
create_map(customer_coordinates, get_10_films(get_lines_by_year(args.year,\
 args.path), customer_coordinates))
