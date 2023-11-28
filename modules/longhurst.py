# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 12:17:40 2023

@author: Markel Gómez Letona

Module with utility functions to work with Longhurst provinces. 

Depends on the pyshp, shapely and pandas packages.
_______________________________________________________________________________

"""

import shapefile # this is 'pyshp'
import shapely as sy
from pandas import read_csv

## Read Longhurst province 
fpath = 'rawdata/longhurst/Longhurst_world_v4_2010'
try:
    sf = shapefile.Reader(fpath)
except Exception as e: # ShapefileException is not recognised?
    if 'Unable to open' in str(e):
        print("Shapefile of Longhurst provinces (Longhurst_world_v4_2010) not " 
              "found!"
              "\n\nCheck that it is correctly named or that it is in the "
              "correct location (rawdata/longhurst/)."
              "\n\nOtherwise, download data from:"
              "\n\nhttps://www.marineregions.org/downloads.php#longhurst"
              "\n\nPlace file (longhurst_v4_2010.zip) in the "
              "rawdata/longhurst/ folder of the project and unzip it.")
    else:
        print("Error when reading Longhurst shapefile:\n\n" + str(e))
            

## Read shapefile's geometry
shapes = sf.shapes()

## Get the records:
records = sf.records()


## Read metadata of Longhurst provinces

# The source file is provided in: https://www.marineregions.org/sources.php#longhurst
# It's .xls file. Here the .csv file is the same but without the pre-header 
# lines and without the empty columns between data columns.
fpath = 'rawdata/longhurst/Longhurst_Province_Summary.csv'
try:
    lmeta = read_csv(fpath, sep=';', header=0)
except FileNotFoundError:
    print("No such file or directory: " + fpath,
          "\n\nThe source file can be obtained in: https://www.marineregions.org/sources.php#longhurst"
          "\n\nRemove pre-header lines and empty columns between data columns,"
          " and convert to ';'-separated .csv")


## Utility functions


def find_longhurst(x, y, out='code'):   
    """
    Find the Longhurst province to which a point of x,y coordinates belongs.
    
    https://www.marineregions.org/downloads.php#longhurst

    Parameters
    ----------
    x : FLOAT
        LONGITUDE of point. Must be a float or coercible to float.
    y : FLOAT
        LATITUDE of point. Must be a float or coercible to float.
    out : STRING, optional
        Output type, one of 'code' (province code) or 'name' (full name of 
        province). The default is 'code'.

    Returns
    -------
    The Longhurst province code or full name for coordinates x,y. If a point
    does not belong to any province (e.g., land) 'NOT_IN_PROV' is returned.

    """
    x = float(x)
    y = float(y)
    
    # the for + break loop has basically the same running time than the while 
    # loop
    is_in_poly = False
    for i in range(len(shapes)):
        
        # Get shape (province) i:
        bshp = shapes[i]

        # Get coordinates of point:
        scoords = (x, y)
        
        # Check if point is in province:
        is_in_poly = sy.geometry.Point(scoords).within(sy.geometry.shape(bshp))
        
        # If found, exist loop already (avoids checking all provinces needlessly):
        if is_in_poly: break

    
    # When the province is found, the while loop is existed.
    # The province of the sample will be i
    if is_in_poly:
        lp = {'code': records[i][0], 'name': records[i][1]}
    else:
        lp = {'code': 'NOT_IN_PROV', 'name': 'Point not in Longhurst province. Likely land, or unassigned area close to Antarctica.'}
    
    return(lp[out])


def longhurst_meta(prov=None):
    """
    Returns metadata associated to the specific Longhurst province. If no input
    is provided, the entire metadata table is returned.
    
    Summary values by Mathias Taeger and David Lazarus, Museum für Naturkunde, 
    Berlin. 26.3.2010. https://www.marineregions.org/sources.php#longhurst

    Parameters
    ----------
    prov : STRING, optional
        Longhurst province code for which metadata is to be retrieved. The
        default is None, i.e., returns a dataframe with the metadata of all 
        provinces.

    Returns
    -------
    Dictionary with the metadata for the specified Longhurst province:
        'PROVCODE' : Longhurst province code.
        'PROVDESCR' : Longhurst province full name.
        'Biome' : 'C'=coastal, 'P'=polar, 'T'=trade winds, 'W'=westerlies.
        'productivity_gC_m2_d' : integrated primary productivity, gC·m-2·d-1.
        'prod_class' : productivity class, 1-5:
                       very low (1) = <0.4
                       low (2) = <0.8
                       middle (3) = <1.2
                       high (4) = <1.6
                       very high (5) = >1.6
         'chl_mg_m2' : integrated Chl-a, mg·m-2.
         'chl_class' : Chl-a class, 1-5:
                       very low (1) = <5
                       low (2) = <10
                       middle (3) = <15
                       high (4) = <20
                       very high (5) = >25
         'photic_depth_m' : depth of photic layer, m.
         'photic_class' : photic layer class, 1-5:
                          very low (1) = <30
                          low (2) = <40
                          middle (3) = <50
                          high (4) = <60
                          very high (5) = >60            
         'mld_sigma_m' : mixed layer depth, m.
         'mld_class' : mixed layer depth class, 1-5:
                       very low (1) = <20
                       low (2) = <40
                       middle (3) = <60
                       high (4) = <80
                       very high (5) = >80                
         'temp_0_celsius' : temperature at 0 m depth, celsius.
         'temp_50_celsius' : temperature at 50 m depth, celsius.
         'temp_diff' : temperature difference between 0 and 50 m depth, celsius.
         
         If no input is provided, a dataframe is returned with the same
         variables for all provinces.

    """
    if prov==None:
        # If no input, return entire table
        provmeta = lmeta
    else:
        # Return metadata for specified province
        df = lmeta.loc[lmeta['PROVCODE']==prov, :]
        if df.shape[0]==0:
            raise ValueError("invalid province code") 
        else:
            provmeta = df.squeeze().to_dict()
        
    return(provmeta)
    