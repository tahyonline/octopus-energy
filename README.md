# Octopus Energy Meter Readings

Download smart meter data from Octopus Energy (UK) and
store them in a CSV file.

The CSV file can be used as a data source for Excel or
another tool.
Do not edit the CSV file, as when the 

## Installation

Clone the repo and install the requirements,
ideally into a virtual environment:
```shell
# Clone the repo
git clone https://github.com/tahyonline/octopus-energy.git
cd octopus-energy

# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip3 install -r requirements.txt
```

## Configuration

### Simple: For Single Meters

Copy the `config-template.json` file to
`config.json` and put in your API key.

```json
{
  "url": "https://api.octopus.energy",
  "apikey": "<your secret api key that you never disclose to anyone>",
  "mpan": "<your meter point number",
  "serial": "<your meter serial number"
}
```

The `apikey`, `mpan` and `serial` parameters are available
on the [Octopus Energy](https://octopus.energy) customer portal.
On the **Accounts** page, click on **Personal details**
right under your name.
Find **Developer settings** on the "Your Settings" page,
where you will find your API key, MPAN and serial numbers.

The CSV file is named as `octopus-<MPAN>-<SERIAL>.csv` by default,
or you can add a configuration parameter
to `config.json` like this:
```json
{
  "csv" : "<your filename>"
}
```

### Advanced: For Multiple Meters

Create the `config.json` file as follows:

```json
{
  "accounts": [
    {
      "name": "Advanced Electricity",
      "url": "<fully specified API URL>",
      "apikey": "<your API key>",
      "csv": "<your CSV file name>"
    }
  ]
}
```

The URL must conform to the Octopus Energy API specification:
- For electricity meters: `https://api.octopus.energy/v1/electricity-meter-points/<MPAN>/meters/<SERIAL>/consumption`
- For gas meters:  `https://api.octopus.energy/v1/gas-meter-points/<MPAN>/meters/<SERIAL>/consumption`
Replace `<MPAN>` and `<SERIAL>` with the codes for your meters.

A default file name is not used, the `csv` parameter must be specified
and **should be different** for the meters,
as otherwise it will be overwritten with the data of the last account in the list.

If both simple and advanced configurations are in the file,
the advanced takes precedence and the simple is ignored.

## Usage

```shell
cd octopus-energy
source venv/bin/activate
python3 octopus.py
```
When run the first time, the tool will download all historical
data going backwards in time.

Each subsequent run will only request any new data since the
end of the last available reported consumption interval.

Do not edit the CSV file that stores the data, as that might
throw off the logic.


## Data Stored in CSV
If used with Excel, the CSV file should be added as a data source.
This ensures that it is not updated by Excel and the tool
can find the last date and time for incremental updates.

Each row in the generated CSV will have the
- interval start (date and time)
- interval end (date and time)
- consumption (kWh)

The interval start and end dates are as returned from
the API, which appears to not stick to one timezone,
or take into account the timezone in the request.

Instead, the timezone will alternate between UTC, denoted as
`Z` and BST, marked as `+01:00`. Here is an example for an
interval that happened to span the daylight saving change:

`"2020-03-29T00:30:00Z","2020-03-29T02:00:00+01:00",0.1`

This interval is not 1.5 hours long, only happens to start
at 00:30GMT and end at 01:00GMT, which is 02:00BST.

## Use Case and Development Objectives

Download and keep a record of energy usage for own analytics
purposes.

Minimise requirements, ideally nothing beyond what is
in the core libraries + `requests`.

Low fault tolerance: report error and quit.

## Sources

API documentation: [https://developer.octopus.energy/docs/api/](https://developer.octopus.energy/docs/api/)

API URL: https://api.octopus.energy/
