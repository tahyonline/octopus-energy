# Octopus Energy Meter Readings

Download smart meter data from Octopus Energy (UK) and
analyse the consumption patterns.

> I am not associated with Octopus Energy
> other than I am a consumer using their services.
> Please do not contact me with outages,
> or issues with billing or anything else... 😀

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

# Done
deactivate
```

## Configuration

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
Find **Developer settings** on the Your Settings page,
where you will find your API key, MPAN and serial numbers.

(Note that I have one meter, like probably most consumers.
If you have multiple meters and how that looks like,
please open an issue with the details.)

## Usage

The convenience script
```shell
./run.sh
```
will build the single page application (SPA)
and the local server,
then start it and launch the default browser
opening the analytics tool.


# OLD
When run the first time, the tool will download all historical
data going backwards in time.

Each subsequent run will only request any new data since the
end of the last available reported consumption interval.

Do not edit the CSV file that stores the data, as that might
throw off the logic.

The CSV file is named as `octopus-<MPAN>-<SERIAL>.csv` or
you can add a configuration parameter
to `config.json` like this:
```json
{
  "csv" : "<your filename>"
}
```

## Data Stored in CSV
Each row in the generated CSV will have the
- interval start
- interval end
- consumption (in kWh)

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

Minimise requirements, ideally nothing beyond the what is
in the core libraries + `requests`.

Low fault tolerance: report error and quit.

## Sources

API documentation: [https://developer.octopus.energy/docs/api/](https://developer.octopus.energy/docs/api/)

API URL: https://api.octopus.energy/
