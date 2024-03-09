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

    def get_outdoor_temp(self, device_id, days=30):
        return self.fetch_data(device_id, '4', days)

    def get_brine_in_temp(self, device_id, days=30):
        return self.fetch_data(device_id, '13', days)

    def get_brine_out_temp(self, device_id, days=30):
        return self.fetch_data(device_id, '14', days)

    def get_hot_water_charging(self, device_id, days=30):
        return self.fetch_data(device_id, '12', days)


    def get_hot_water_top(self, device_id, days=30):
        return self.fetch_data(device_id, '11', days)

    def get_return_line_temp(self, device_id, days=30):
        return self.fetch_data(device_id, '10', days)

    def get_supply_line_temp(self, device_id, days=30):
        return self.fetch_data(device_id, '8', days)


    def save_to_pickle(self, data, filename='cache.pkl'):
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert('Europe/Helsinki')
        df.set_index('timestamp', inplace=True)
        if os.path.exists(filename):
            df_old = pd.read_pickle(filename)
            df_combined = pd.concat([df_old, df]).drop_duplicates(keep=False)
            df_combined.to_pickle(filename)
        else:
            df.to_pickle(filename)
        return df

    def plot_data(self, data):
        data.plot(y='value')
        plt.ylabel(data['unit'].iloc[0])
        plt.show()
