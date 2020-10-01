#!/bin/env python
"""
Meteorological Tool for converting between file formats
"""
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
import os
import sys
import time
import logging
import docopt

import grib2nc

version = '0.0.2'
__doc__ += """
Usage:
  {filename} [grib2nc] [options]
  {filename} (-h | --help)
  {filename} --version

Commands:
  grib2nc                       Convert grib file to netCDF4

Options:
  -i, --infile <STRING>         File or directory with files, usually gribfiles. If directory use with --idir
  -o, --outfile <STRING>        Specify output file [default: mapp.nc]
  -l, --leveltype <STRING>      Which type of level should be converted: sf, pl, ml [default: sf]
  -h, --help                    Show this screen.
  -q, --quiet                   Print no info.
  -v, --verbose                 Print info.
  -d, --debug                   Print detailed info.
  --logfile <FILE>              Write full log to file
  -V, --version                 Show version

Examples:
  Convert gribfile to netcdf file
    dmic -v grib2nc -i <gribfile> -o <netcdffile>

For Dev:
  dmic -i -o

History:
   October 2020: Created (KAH)
""".format(filename=os.path.basename(__file__), version=version)

if len(sys.argv) < 2:
    sys.exit('Input missing: try with -h or --help')

args = docopt.docopt(__doc__, version=str(version))

log = logging.getLogger("dmic.log")
log.setLevel(logging.DEBUG)

formatstr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
shortformatstr = '%(message)s'
formatter = logging.Formatter(formatstr)
shortformatter = logging.Formatter(shortformatstr)

if args['--logfile']:
    fh = logging.FileHandler(args['--logfile'])
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    log.addHandler(fh)

if args['--quiet']:
    args['--verbose'] = args['--debug'] = 0

ch = logging.StreamHandler()
if args['--debug']:
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
elif args['--verbose']:
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
else:
    ch.setLevel(logging.WARNING)
    ch.setFormatter(shortformatter)

log.addHandler(ch)

log.info('%s started' % os.path.basename(__file__))
log.debug('docopt args=%s' % str(args).replace('\n', ''))


infile  = args['--infile']
outfile = args['--outfile']


def main():

    if args['grib2nc']:
        log.info("Converting GRIB file to netCDF4")

        leveltype = args['--leveltype']

        grib2nc.convert(infile,leveltype,outfile)

    
    return

  
if __name__=='__main__': main()