# climate_modelling

- GUI folder contains linear regression model. To run:
  
  1. Install dependencies (tensorflow and wxPython)
  
     wxPython can be obtained from https://www.wxpython.org/pages/downloads/
     ```
     pip install -U wxPython
     ```
     should do the trick.
       
  2. Get data in .nc files
  3. Run gui.py
  4. Select data: click on '...', browse to the selected .nc file and then select the appropriate variable name, which is 'T2' for observational data and 'tas' for model data.

- gp folder contains gaussian process models. To run:

  1. Install GPy
  
     ```
     pip install GPy
     ```
     
     Documentation for GPy: https://pythonhosted.org/GPy/
     
  2. Run! gp_positional_temporal.py models the temperature at various locations, and gp_temporal.py models the temperature at      a single location.
  
- basemap_example folder contains a single example of using Basemap to combine country borders with a heat map.
