# Set Up

## Web Driver

You will need a gecko / mozilla firefox web driver in order to run `download_data.py` as it automates a web browser to grab all the pertinent data.

The drivers can be found here: https://github.com/mozilla/geckodriver/releases

Place the driver in the root of this project and make sure the name of the driver in `.env` matches the name of your downloaded driver.

## Dependencies

Run `pip install -r requirements.txt` to install the necessary dependencies.

# Running

After setting up, run `download_data.py` to download the data to the `/data` folder.