import pandas as pd
import pycountry_convert

def country_name_to_country_code(row):
    if row.geo == 'Kosovo':
        return 'KSV'

    try:
        return pycountry_convert.country_name_to_country_alpha3(row.geo)
    except KeyError:
        return ""

def clean_data(csv_path):
    df = pd.read_csv(csv_path)
    df.replace(to_replace=r'Germany.*', value='Germany', regex=True, inplace=True)
    df.replace(to_replace=r'France.*', value='France', regex=True, inplace=True)
    df.replace(to_replace=r'Kosovo.*', value='Kosovo', regex=True, inplace=True)
    df.replace(to_replace=r'Former.*', value='Macedonia', regex=True, inplace=True)
    df.columns = map(str.lower, df.columns)
    df['code'] = df.apply(lambda row: country_name_to_country_code(row), axis=1)
    df['value'].replace(to_replace=r',', value='', regex=True, inplace=True)
    df['value'].replace(to_replace=r': ', value='', regex=True, inplace=True)
    df['category'] = df[df.columns[3]]
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['value'] = df['value'].fillna(0)
    return df

population = clean_data('data/population.csv')
road_motorways = clean_data('data/roads_motorways.csv')
by_road_user = clean_data('data/1_by_road_user.csv')
by_vehicle = clean_data('data/2_by_vehicle.csv')
by_age = clean_data('data/3_by_age.csv')
vehicle_stock = clean_data('data/vehicle_stock.csv')