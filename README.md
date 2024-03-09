# MyUpLink internal API access
This is a simple tool to access MyUpLink internal APIs that are better than the official ones provided by NIBE.

## Usage
Create a `.env` file in your root like

```bash
UPLINK_USERNAME = yourusername
UPLINK_PASSWORD = yourpassword
```

Then you can use it like this (also contained in the `example.py` file):

```python
from myuplink import UplinkAPI

if __name__ == '__main__':
    api = UplinkAPI()
    group_id = api.get_me()
    device_id = api.get_device(group_id)
    categories = api.get_categories(group_id)
    data = api.get_outdoor_temp(device_id)
    df = api.save_to_pickle(data)
    api.plot_data(df)
```