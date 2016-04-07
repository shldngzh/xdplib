#!/usr/local/bin/python
# xdzlib_beta.py
# Python 2.7
# Version 1.5 Beta
# Xiaodong Zhai (xz125@duke.edu)
import os, subprocess
import gzip
import time
import datetime
import numpy as np

#%%
def locate_file( product, 
                  date_start, 
                  date_end = None, 
                  data_frequency = '1sec', 
                  data_type = 'L2'): 
    '''
    to locate file in Ubuntu server
    
    product:
        contract name with expiration
    date_start and date_end:
        date span of data files
    data_frequency:
        what frequency data 
    data_type:
        what data file type to choose (L1, L2, olhc)
    
    returns  1) list of file path (type = np.array)
             2) list of file name (type = np.array)
    '''
    date_start = datetime.date(int(date_start[0:4]),
                               int(date_start[4:6]),
                               int(date_start[6:]))
    if date_end == None:
        date_end = date_start
    else:                          
        date_end = datetime.date(int(date_end[0:4]),
                                 int(date_end[4:6]),
                                 int(date_end[6:]))
                             
    delta = date_end - date_start
    
    lst_path = np.array([])
    lst_fname = np.array([])
    
    for i in range(delta.days + 1):
        date = date_start + datetime.timedelta(days=i)
        FilePath = '/data/fe/eldo/' + data_frequency + '/%s/%s/%s/' % (date.year,date.strftime('%Y%m%d')[4:6],date.strftime('%Y%m%d')[6:])
        FileName = '.'.join(['eldo', date.strftime('%Y%m%d'), product, data_frequency.lower(), data_type, 'txt.gz'])
        if os.path.isfile(FilePath+FileName):        
            lst_path = np.append(lst_path, FilePath)
            lst_fname = np.append(lst_fname, FileName)
        
    return lst_path, lst_fname
    
# %%
def read_data( lst_path, 
                lst_fname, 
                time_start=None, 
                time_end=None,
                saveBinFile=1 ):
    '''
    read data with (default) specific time span within a day, given files
    location and file names
    
    lst_path:
        lst of paths of data files
    
    lst_fname:
        lst of data files names
    
    returns a data file (np.array)
    '''
    data = np.array([])
    for i in np.arange(0, len(lst_fname)):
        
        if saveBinFile == 1:    tmp = load_npy(lst_path[i], lst_fname[i])
        else:                   tmp = np.loadtxt(lst_path[i]+lst_fname[i])
            
        if time_start == None:
            if len(data) == 0:  data = tmp
            else:               data = np.vstack([ data, tmp ])
            if i == (len(lst_fname) - 1) :  break
            else:                           continue
         
        date = lst_fname[i].split('.')[1]
        epoch_start = get_epoch(date+time_start)
        epoch_end   = get_epoch(date+time_end)
        tmp = tmp[(tmp[:,0]>=epoch_start) & (tmp[:,0]<=epoch_end)]
        if len(data) == 0:  data = tmp
        else:               data = np.vstack([ data, tmp ])
    return data

# %%
def get_data( product, 
               date_start, 
               date_end=None, 
               time_start=None, 
               time_end=None,
               data_frequency='1sec', 
               data_type='L2' ):
    '''
    integrated method to get data with specified product, date span, 
    time span, frequency and data type
    '''
    lst_path, lst_fname = locate_file(product, date_start, date_end, 
                                     data_frequency, data_type)
    return read_data(lst_path, lst_fname, 
                     time_start=time_start, time_end=time_end, saveBinFile=1)

# %%
def get_data_simple( product, 
                       date_start, 
                       date_end=None, 
                       time_start=None, 
                       time_end=None,
                       data_frequency='1sec', 
                       data_type='L2' ):
    '''
    simple read, without creating any binary file
    integrated method to get data with specified product, date span, 
    time span, frequency and data type
    '''
    lst_path, lst_fname = locate_file(product, date_start, date_end, 
                                     data_frequency, data_type)
    return read_data(lst_path, lst_fname, time_start, time_end, saveBinFile=0)

# %%
def load_npy( lst_path, 
               lst_fname, 
               overwrite=False, 
               heading=False, 
               verbose=False, 
               debug=False ):
    filename_txt = lst_path + lst_fname
    filename_spa = '/home/xiaodong/data/var/'
    filename_npy = (filename_spa + lst_fname).replace( 'txt.gz', 'npy.gz' )
    mat = np.array( [] )
    if not os.path.exists(filename_npy) or overwrite:
            if not os.path.exists(filename_txt):
                    if debug: print filename_txt, "not found"
                    return mat
            skiprows = 1 if heading else 0
            mat = np.loadtxt( filename_txt, skiprows=skiprows )
            if verbose: print filename_txt, mat.shape
            fh_out = gzip.open( filename_npy, 'wb')
            np.save( fh_out, mat )
            fh_out.close()
    fh_in = gzip.open( filename_npy, 'rb' )
    mat = np.load( fh_in )
    fh_in.close()
    if verbose: print filename_npy, mat.shape
    return mat
    
# %%
def get_epoch( input_date_and_time, pattern='%Y%m%d%H%M%S' ):
    '''
    make epoch time given time 
    
    input_time: str type 
    pattern: default = '%Y%m%d%H%M%S'
    
    return epoch(int)
    '''
    epoch = int(time.mktime(time.strptime(input_date_and_time,pattern)))
    return epoch 

# %%
def align_2data( data_1, data_2 ):
    '''
    align 2 data series, according to the same index like epoch time
    '''
    indx    = np.intersect1d(data_1, data_2)
    tag_1   = np.in1d(data_1[:,0], indx)
    tag_2   = np.in1d(data_2[:,0], indx)
    data_1  = data_1[tag_1]
    data_2  = data_2[tag_2]
    return data_1, data_2

# %%
def linreg( X, Y, plot=False ):
    ''' 
    OLS linear regression
    return:
        beta, constant, r_squared, resid
    
    example:
        x1 = np.array([1,2,3,4,5,6])
        x2 = np.array([3,2,4,2,8,6])
        y  = np.array([2,2,4,4,4,8])
        
        beta, cons, r2, resid = linreg( [x1, x2, x3], y )
    '''
    X = np.array(X).T
    A = np.column_stack([X, np.ones(len(X))])
    result = np.linalg.lstsq( A, Y)[0]
    beta = result[:-1]
    cons = result[-1]
    est = np.dot(X, beta) + cons
    r_squared = np.square(est - Y.mean()).sum() / np.square(Y.mean() - Y).sum()
    resid = Y - np.dot(X,beta)
    return beta, cons, r_squared, resid 


