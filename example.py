# Example usage
from myuplink import UplinkAPI

if __name__ == '__main__':
    api = UplinkAPI()
    group_id = api.get_me()
    device_id = api.get_device(group_id)
    categories = api.get_categories(group_id)
    data = api.get_outdoor_temp(device_id)
    df = api.save_to_pickle(data)
    api.plot_data(df)