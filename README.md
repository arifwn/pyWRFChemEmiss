pyWRFChemEmiss
==============

pyWRFChemEmiss is a WRF-Chem emission preparation tool.

You'll need python 2.7 and wx-python installed in order to use this application. The data source (.xlsx spreadsheets) are typically exported from GIS apps / emission inventory system.

Screenshots:

![screen shot 2014-06-18 at 11 50 02 am](https://cloud.githubusercontent.com/assets/1146705/3309828/5ae53f98-f6a7-11e3-8bd2-35c6a704a09c.png)

![screen shot 2014-06-18 at 11 50 20 am](https://cloud.githubusercontent.com/assets/1146705/3309831/6cbf0bf4-f6a7-11e3-8670-f28c056a94ff.png)


Here is what the .xlsx spreadsheet looks like. If the first line on your spreadsheets is header/column label, put "2" in the "starting rows field" to start processing from row 2. Each row represent a grid cell:

```
x      y      latitude   longitude    CO_EMISSION  NO3_EMISSION ...
0      0      -7.55      107.711      0.03            0.005
1      0      -7.55      107.712      0.02            0.004
...
```

- `x` is relative x coordinate of the grid in meter. UTM projection is used during conversion.
- `y` is relative y coordinate of the grid in meter
- `latitude` is the y coordinate of the grid in degrees
- `longitude` is the x coordinate of the grid in degrees
- `CO_EMISSION` is the emission data. If you're not using mol/km^2/hour as emission unit, put the conversion factor in the "conversion factor" field in the emis_converter.py.

You can put several pollutants at once using "Add Pollutant" button, and save your configuration with "save list" button. 

After converting the data using pyWRFChemEmiss, you can proceed to run WRF-Chem's convert_emiss.exe and continue with the WRF simulation workflow.

Note that I haven't tested this app against the latest version of WRF and WRF-Chem, so it may or may not work.
