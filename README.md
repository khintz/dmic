# DMIC
Sometimes you need to convert files from one another. This is a collection of tools to avoid replicating code.

### Install
**pip install dmic**

## Usage
**dmic -h** : *gives help message*
**dmic [command]** : *see below*
Possible commands are:
**grib2nc** : *convert a gribfile to netcdf*

### Flags
**-v**, **--verbose** : *verbose mode*
**-i**, **--input** : *input file*
**-o**, **--output** : *output file*
**-V**, **--version** : *show version number*

### Examples
*dmic -v grib2nc -i 001.grib -o 001.nc*

### CF Convention
...

##### Requirements and disclaimer
dmic has *not* been tested on windows, but works for macOS Catalina and Ubuntu18.04 and above. dmic is build using python and requires python3.6 or newer. dmic has not been tested with python2 (because why should it?)
