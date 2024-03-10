import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import urllib.parse as urlparse

class UplinkAPI:
    def __init__(self):
        self.api_url = 'https://internalapi.myuplink.com/'
        self.token_url = f'{self.api_url}oauth/token'
        self.session = requests.Session()
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.load_env_variables()
        self.authenticate()


    def use_cache(prefix):
        "Decorator to cache data to disk and load it from disk if it exists."
        def decorator(func):
            def wrapper(self, device_id, days=30):
                if not os.path.exists('cache'):
                    os.mkdir('cache')
                filename = f'cache/{prefix}.pkl'
                data = func(self, device_id, days)
                df = pd.DataFrame(data)
                df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert('Europe/Helsinki')
                df.set_index('timestamp', inplace=True)
                if os.path.exists(filename):
                    print(f'Loading data from cache: {filename}')
                    df_old = pd.read_pickle(filename)
                    print(f'Old data: {df_old.shape[0]} rows')
                    print(f'New data: {df.shape[0]} rows')
                    df_combined = pd.concat([df_old, df])
                    df_result = pd.DataFrame(df_combined.to_dict(), index=df_combined.index.unique())
                    print(f'Combined data: {df_result.shape[0]} rows')
                    df_result.to_pickle(filename)
                    return df_result
                else:
                    print(f'Saving data to cache: {filename}')
                    df.to_pickle(filename)
                return df
            return wrapper
        return decorator

    def load_env_variables(self):
        load_dotenv()
        self.username = os.getenv('UPLINK_USERNAME')
        self.password = os.getenv('UPLINK_PASSWORD')

    def authenticate(self):
        data = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
            'client_id': 'My-Uplink-Web'
        }
        response = self.session.post(self.token_url, data=data, headers=self.headers)
        self.token = json.loads(response.text)['access_token']
        self.headers['Authorization'] = f'Bearer {self.token}'

    def get_me(self):
        me = urlparse.urljoin(self.api_url, 'v3/groups/me')
        response = self.session.get(me, headers=self.headers)
        return json.loads(response.text)[0]['id']

    def get_device(self, group_id):
        devices_url = urlparse.urljoin(self.api_url, f'v2/groups/{group_id}/devices')
        response = self.session.get(devices_url, headers=self.headers)
        return json.loads(response.text)[0]['id']

    def get_categories(self, group_id):
        categories_url = urlparse.urljoin(self.api_url, f'v2/group/{group_id}/categories/all?chart=history')
        response = self.session.get(categories_url, headers=self.headers)
        categories = json.loads(response.text)['parameters']
        return {category['parameterName']: category['parameterId'] for category in categories}

    def fetch_data(self, device_id, parameter_id, days=30):
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
        data_url = urlparse.urljoin(self.api_url, f'v2/devices/{device_id}/points/{parameter_id}/{start_date.strftime("%Y-%m-%d %H:%M:%S")}/{end_date.strftime("%Y-%m-%d %H:%M:%S")}/average/none')
        response = self.session.get(data_url, headers=self.headers)
        return json.loads(response.text)

    @use_cache('outdoor_temp')
    def get_outdoor_temp(self, device_id, days=30):
        return self.fetch_data(device_id, '4', days)

    @use_cache('brine_in_temp')
    def get_brine_in_temp(self, device_id, days=30):
        return self.fetch_data(device_id, '13', days)

    @use_cache('brine_out_temp')
    def get_brine_out_temp(self, device_id, days=30):
        return self.fetch_data(device_id, '14', days)

    @use_cache('hot_water_charging')
    def get_hot_water_charging(self, device_id, days=30):
        return self.fetch_data(device_id, '12', days)

    @use_cache('hot_water_top')
    def get_hot_water_top(self, device_id, days=30):
        return self.fetch_data(device_id, '11', days)

    @use_cache('return-line-temp')
    def get_return_line_temp(self, device_id, days=30):
        return self.fetch_data(device_id, '10', days)

    @use_cache('supply-line-temp')
    def get_supply_line_temp(self, device_id, days=30):
        return self.fetch_data(device_id, '8', days)

    def plot_data(self, labels, title, dataframes):
        ax = None
        for (label, df) in zip(labels, dataframes):
            # Plot each DataFrame on the same axes (ax) and assign a label for the legend
            ax = df.plot(y='value', ax=ax, label=f'{label}', grid=True)
        plt.title(title)
        plt.ylabel(dataframes[0]['unit'].iloc[0])
        plt.legend()
        plt.show()

