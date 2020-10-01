import sys
import os
import dmit
import xarray as xr
import configparser
import netCDF4 as nc
import numpy as np
import grib

import logging
log = logging.getLogger("dmic.log")
log.setLevel(logging.DEBUG)

b_t2m = False
b_u10 = False
b_v10 = False

class convert:

    def __init__(self, gribfile, leveltype, outfile):

        if leveltype=='sf':
            ini_grib = grib.cf_grib_definitions.gribparameter2cfnaming_sf
        else:
            log.error('Sorry! But '+leveltype+' is not implemented yet')
            log.error('Possible options for --leveltype is: sf\n exiting')
            sys.exit(0)

        # Call object
        grib_reader = grib.read(leveltype)

        # Get coordinates
        lats, lons, latdim, londim = grib_reader.get_grid(gribfile)

        # we have to divide calls to grib_reader.read() between same parameter, multiple levels OR
        # multiple parameters, same level.
        grib_dic = {}
        for key in ini_grib:
            keylist = key.split('_')
            lvl = str(keylist[1])

            if lvl not in grib_dic.keys():
                grib_dic[lvl] = {}
            
            grib_dic[lvl][key] = ini_grib[key]



        # This works but creates NaN for all values with missing level (eg parid 33 does not have values at level 2)
        i=0
        for key in grib_dic.keys():
            ds_grib = grib_reader.read(gribfile, leveltype, grib_dic[key])
            # if i==0: ds = ds_grib
            # if i>0: ds = xr.merge([x, ds_grib])
            # x = ds_grib
            i+=1

            coord_names = list(ds_grib.coords)
            dim_names   = list(ds_grib.dims)
            var_names   = list(ds_grib.data_vars)
        
            k=0
            for var in var_names:

                level = ds_grib[var].coords['level'].values[0]
                
                if var == 'air_temperature' and level==2:
                    b_t2m = True
                    t2m = np.array(ds_grib[var].values, dtype=np.float32)
                if var == 'eastward_wind' and level==10:
                    b_u10 = True
                    u10 = np.array(ds_grib[var].values, dtype=np.float32)
                if var == 'northward_wind' and level==10:
                    b_v10 = True
                    v10 = np.array(ds_grib[var].values, dtype=np.float32)

                k+=1

        

        ncf = nc.Dataset(outfile,'w')
        ncdim_time = ncf.createDimension("time", None)
        ncdim_lat = ncf.createDimension("latitude", latdim)
        ncdim_lon = ncf.createDimension("longitude", londim)

        # 'f4' = float (ordinary, bot python float which is 64bit)
        # 'i4' = "i4" represents a 32 bit integer

        if b_t2m:
            ncvar_t2m = ncf.createVariable('air_temperature_2m', 'f4', ('time','latitude','longitude'), zlib=True)
            ncvar_t2m[:,:,:] = t2m[:,0,:,:]
            ncvar_t2m.units = 'K'
            ncvar_t2m.long_name = 'air_temperature_2m'
        if b_u10:
            ncvar_u10 = ncf.createVariable('eastward_wind_10m', 'f4', ('time','latitude','longitude'), zlib=True)
            ncvar_u10[:,:,:] = u10[:,0,:,:]
            ncvar_u10.units = 'm/s'
            ncvar_u10.long_name = 'eastward_wind_10m'
        if b_v10:
            ncvar_v10 = ncf.createVariable('nortward_wind_10m', 'f4', ('time','latitude','longitude'), zlib=True)
            ncvar_v10[:,:,:] = v10[:,0,:,:]
            ncvar_v10.units = 'm/s'
            ncvar_v10.long_name = 'nortward_wind_10m'

        

        ncf.close()



        # ds.to_netcdf(outfile)
            
        # Read gribfile
        # ds_grib = grib_reader.read(gribfile, leveltype, grib_dic)
        # print(ds_grib)

        # i = 0
        # for key in grib_dic.keys():
        #     ds_grib = grib_reader.read(gribfile, leveltype, grib_dic[key])

        #     ds_grib.to_netcdf(outfile+'.'+str(i))

        #     i+=1

        #     if i==0: # For first iteration we create the netcdf file
        #         ncf = nc.Dataset('out.nc','w')
        #         ncdim_time = ncf.createDimension("TIME", None)
            

        
        return
