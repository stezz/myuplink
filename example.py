# Example usage
from myuplink import UplinkAPI

if __name__ == '__main__':
    api = UplinkAPI()
    group_id = api.get_me()
    device_id = api.get_device(group_id)
    data = api.get_outdoor_temp(device_id)
    api.plot_data(dataframes=[data], title='Outdoor temperature', labels=['temperature'])
    brine_in = api.get_brine_in_temp(device_id)
    brine_out = api.get_brine_out_temp(device_id)
    # Plot the brine in and out temperatures on the same graph
    api.plot_data(dataframes=[brine_in, brine_out], title='Brine temperature', labels=['brine in','brine out'])
    hot_water_charging = api.get_hot_water_charging(device_id)
    hot_water_top = api.get_hot_water_top(device_id)
    # Plot the hot water charging and top temperatures on the same graph
    api.plot_data(dataframes=[hot_water_charging, hot_water_top], title='Hot water temperature', labels=['charging','top'])
