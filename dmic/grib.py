import sys
import pygrib
import warnings
import numpy as np
import datetime as dt
import configparser
import xarray as xr
from dmit import regrot


import logging
log = logging.getLogger("dmic.log")
log.setLevel(logging.DEBUG)

class read:


    def __init__(self, leveltype):

        if leveltype=='sf':
            pass
        else:
            log.error('Sorry! But '+leveltype+' is not implemented yet')
            log.error('Possible options for --leveltype is: sf\n exiting')
            sys.exit(0)

        return


    def get_grid(self, gribfile, using_pygrib_derived_coords=False):
        """Get grid from gribfile.
        This function will always try to return regular coordinates.

        Parameters
        ----------
        gribfile : str
            path to gribfile
        using_pygrib_derived_coords : boolean (optional)
            Default: False, if true, force to use pygrib derived coordinates

        Returns
        -------
        lat : 1d-array
            flattened array with latitudes
        lon : 1d-array
            flattened array with longitudes
        """
        gr = pygrib.open(gribfile)

        g = gr[1]

        latdim = g.Nj
        londim = g.Ni

        if not using_pygrib_derived_coords:
            try:
                latFirst = g.latitudeOfFirstGridPointInDegrees
                lonFirst = g.longitudeOfFirstGridPointInDegrees
                latLast = g.latitudeOfLastGridPointInDegrees
                lonLast = g.longitudeOfLastGridPointInDegrees
                dy = g.jDirectionIncrementInDegrees
                dx = g.iDirectionIncrementInDegrees
                latPole = g.latitudeOfSouthernPoleInDegrees
                lonPole = g.longitudeOfSouthernPoleInDegrees

                lons, lats = np.meshgrid(np.linspace(
                    lonFirst, lonLast, londim), np.linspace(latFirst, latLast, latdim))

                if not latPole==0 and not lonPole==0:
                    log.info('Found rotated coordinates - converting to regular coordinates')
                    lons, lats = regrot.rot_to_reg(lonPole,latPole,lons,lats)

            except RuntimeError:
                using_pygrib_derived_coords = True
                warnings.warn('Falling back to pygrib derived coordinates')
                lats, lons = g.latlons()
                using_pygrib_derived_coords=True
        if using_pygrib_derived_coords:
            lats, lons = g.latlons()

        data_date = g.dataDate
        data_time = g.dataTime

        starttime = dt.datetime.strptime(('%i-%.2i')%(data_date,data_time),'%Y%m%d-%H%M')

        gr.close()

        return lats.flatten(), lons.flatten(), latdim, londim

    # def read_cfgrib(self, grib_file):

    #     indicatorOfParameter = 11
    #     typeOfLevel = 'heightAboveGround'
    #     level = 2
    #     ds_grib = xr.open_dataset(grib_file, engine='cfgrib',
    #                         backend_kwargs=dict(read_keys=['indicatorOfParameter'],
    #                         filter_by_keys={'indicatorOfParameter': indicatorOfParameter, 'typeOfLevel': typeOfLevel, 'level': level}))
    #     print(ds_grib)

    #     return
    

    #def read(self, gribfile, indicatorOfParameters, level, type_of_level, indicator_of_type_of_level):
    def read(self, gribfile, leveltype, ini_grib):
        """Get fields from gribfile.
        This function will always try to return whatever is found in the gribfile.
        Therefore this can fail for very large gribfiles. If so, and until we support large gribfiles
        use the grib_filter tool from eccodes to reduce the input.

        Time, latitude and longitude dimensions are assumed to be the same for all fields. However, the gribfile can
        hold several times, as long as all fields do.

        Parameters
        ----------
        gribfile : str
            path to gribfile

        Returns
        -------
        ds : xarray-dataset
            xarray dataset with the fields found
        """

        gr = pygrib.open(gribfile)

        init = True
    
        # First find out the number of time dimensions in this file
        timestamps = []
        levels = []
        msg = 0
        for g in gr:
            data_date = g.dataDate
            data_time = g.dataTime
            timestamps.append(dt.datetime.strptime(('%i-%.2i')%(data_date,data_time),'%Y%m%d-%H%M'))
            levels.append(g.level)
            if init:
                latdim = gr[1].Nj
                londim = gr[1].Ni
                init=False

        Nt = len(list(set(timestamps)))
        Nlev = len(list(set(levels)))
        No_msg = gr.tell()

        gr.seek(0) # Resets iterator to beginning of file

        #print(ini_grib)
        found_names = []
        dim_dict = {}
        for g in gr:
            ini_id    = str(g.indicatorOfParameter)+'_' \
                        + str(g.level)+'_'\
                        + str(g.indicatorOfTypeOfLevel)+'_' \
                        + str(g.typeOfLevel)

            #print(g.indicatorOfParameter,g.level,g.indicatorOfTypeOfLevel,g.typeOfLevel)
            
           # print(ini_id)

            try:
                cfname = ini_grib[ini_id]
                #print(cfname)
                #log.info('Found variable: '+cfname)
            except KeyError:
                #log.warning("parameterId: "+parid+" was not found in grib.ini")
                continue

            if not cfname in dim_dict.keys():
                found_names.append(cfname)
                dim_dict[cfname] = {}
            if not g.indicatorOfTypeOfLevel in dim_dict[cfname].keys():
                dim_dict[cfname][g.indicatorOfTypeOfLevel] = {}
            if not g.typeOfLevel in dim_dict[cfname][g.indicatorOfTypeOfLevel].keys():
                dim_dict[cfname][g.indicatorOfTypeOfLevel][g.typeOfLevel] = {}
                dim_dict[cfname][g.indicatorOfTypeOfLevel][g.typeOfLevel]['level'] = []

            # Make sure levels are only counted once if Nt>1
            if not g.level in dim_dict[cfname][g.indicatorOfTypeOfLevel][g.typeOfLevel]['level']:
                dim_dict[cfname][g.indicatorOfTypeOfLevel][g.typeOfLevel]['level'].append(g.level)


        # Now we have a dictionary with dimensions of the inputs. We can not allocate and actually
        # read the input data. So we rewind the iterator once again.

        gr.seek(0) # Resets iterator to beginning of file
        
        ds_grib = xr.Dataset()

        if leveltype=='sf': 
            indicatorOfTypeOfLevel = 'sfc'
            typeOfLevel            = 'heightAboveGround'
        if leveltype=='ml': 
            indicatorOfTypeOfLevel = 'ml'
            typeOfLevel            = 'hybrid'
        if leveltype=='pl': 
            indicatorOfTypeOfLevel = '103'
            typeOfLevel            = 'heightAboveSea'

        for name in dim_dict.keys():
            Nlev = len(dim_dict[name][indicatorOfTypeOfLevel][typeOfLevel]['level'])
            ds_grib[name] = (['time', 'level', 'latitude', 'longitude'], np.zeros([Nt, Nlev, latdim, londim]))

        # Done allocating, now we read the data 

        index_counter = {}
        for name in found_names:
            index_counter[name] = {'k_nt': 0, 'k_nlev': 0}

        init=True
        coords = {'time': [], 'level': [], 'latitude': [], 'longitude': []}

        for g in gr:
            ini_id    = str(g.indicatorOfParameter)+'_' \
                        + str(g.level)+'_'\
                        + str(g.indicatorOfTypeOfLevel)+'_' \
                        + str(g.typeOfLevel)

            try:
                cfname = ini_grib[ini_id]
            except KeyError:
                continue
            
            #print(cfname)

            data_time = dt.datetime.strptime(('%i-%.2i')%(g.dataDate,g.dataTime),'%Y%m%d-%H%M')
            coords['time'].append(data_time)
            coords['level'].append(g.level)

            x = xr.DataArray(g.values, dims=[' latitude', 'longitude']) #.expand_dims(['time','level'])

            kt = index_counter[cfname]['k_nt']
            nt = index_counter[cfname]['k_nlev']

            ds_grib[cfname][kt,nt,:,:] = x

            # Increment level
            index_counter[cfname]['k_nlev']+=1
            
            # Increment time 
            if not init and data_time != prev_time:
                index_counter[cfname]['k_nt']+=1

            init=False
            prev_time = data_time

        coords['time'] = list(set(coords['time']))
        coords['level'] = list(set(coords['level']))

        ds_grib = ds_grib.assign_coords( {'time': ('time', coords['time']), 
                                'level': ('level', coords['level'])})

        log.info('In total '+str(No_msg)+' grib messages was iterated through')

        gr.close()

        return ds_grib



class cf_grib_definitions:
    # Follows CF v75 (15 september 2020) convention and DMI grib parameters
    # https://cfconventions.org/Data/cf-standard-names/75/build/cf-standard-name-table.html


    gribparameter2cfnaming_sf = { '11_2_sfc_heightAboveGround': 'air_temperature',
                                  '33_10_sfc_heightAboveGround': 'eastward_wind',
                                  '34_10_sfc_heightAboveGround': 'northward_wind'}

    
    