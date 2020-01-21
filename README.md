# SPP Collect Log
This is a Log Collector for IBM Spectrum Protect Plus.

## Installation
Clone this repo by using `git clone` command
Make sure you install all pre-req by using `pip install -r requirement.txt`

## Configuration
Export the variables $SPPUSER $SPPPWD $SPPHOST
```
export SPPUSER=<SPP Username>
export SPPPASS=<SPP User Password>
export SPPHOST=spp1.company.com
```
or you can added the switches --user --pass --host.

If you need more information please see use -h

## Test if it works
You can test by running `python spp_collect_log.py`
