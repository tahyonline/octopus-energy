# Octopus Energy Meter Readings

Download smart meter data from Octopus Energy (UK)

## Installation

Clone the repo and install the requirements,
ideally into a virtual environment:
````shell
# Clone the repo
git clone https://github.com/tahyonline/octopus-energy.git
cd octopus-energy

# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip3 install -r requirements.txt
````

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

## Use Case and Development Objectives

Download and keep a record of energy usage for own analytics
purposes.

Minimise requirements, ideally nothing beyond the what is
in the core libraries + `requests`.

Low fault tolerance: report error and quit.

## Sources

API documentation: [https://developer.octopus.energy/docs/api/](https://developer.octopus.energy/docs/api/)

API URL: https://api.octopus.energy/
