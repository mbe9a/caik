'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

import skrf as rf
from skrf import micron
from skrf.media import Freespace
from skrf.calibration import OnePort
from copy import deepcopy
from unipath import Path
from matplotlib import pyplot as plt
from pylab import * # this is sloppy
from IPython.html.widgets import interactive
import cai



# conversion between masks representations: mask and decimal and hex if preferred
# ( binary is an intermediary form).
# def dec2bin(dec, rank):
#     '''
#     convert decimal to binary with given width
#     '''
#     binary = binary_repr(int(dec), width=(2**rank)**2)
#     return binary

def hex2bin(hex_dec, rank):
    '''
    convert hexadecimal to binary with given width
    '''
    dec = int(hex_dec, base = 0)
    binary = binary_repr(int(dec), width = (2**rank)**2)
    return binary
    
# def dec2mask(dec,rank,**kw):
#     '''
#     translates a decimal representaion into a binary mask (numpy array) 
#     '''
#     binary = dec2bin(dec=dec,rank=rank)
#     return array([int(k) for k in binary ]).reshape((2**rank,2**rank),**kw)

def hex2mask(hex_dec,rank,**kw):
    '''
    translates a decimal representation into a binary mask (numpy array)
    '''
    binary = hex2bin(hex_dec = hex_dec, rank = rank)
    return array([int(k) for k in binary ]).reshape((2**rank,2**rank),**kw)
    
# def bin2dec(binary):
#     '''
#     convert binary to decimal
#     '''
#     return int('0b'+''.join(binary),base=0)

def bin2hex(binary):
    '''
    convert binary to hexadecimal
    '''
    return hex(int('0b'+''.join(binary),base = 0))
    
# def mask2dec(mask):
#     '''
#     translates a mask to its decimal representation
#     '''
#     flat = mask.flatten().astype('str')
#     return bin2dec(flat)

def mask2hex(mask):
    '''
    translates a mask to its hexadecimal representation
    '''
    flat = mask.flatten().astype('str')
    return hex(bin2dec(flat))

# creation of mask sets for a given rank
def gen_had_masks(rank, invert = False):
    '''
    generate a list  hadamard masks for a given rank 
    
    
    the masks returned are binary numpy.arrays's.
    there will be N=(2**rank)**2 masks. 
    '''
    if invert:
        matrixList = cai.list2bn(rank, cai.inverse_ML(cai.createH(rank,'111-',[])))
    else:
        matrixList = cai.list2bn(rank, cai.createH(rank,'111-',[]))
    return array([[int(k) for k in matrix] for matrix in matrixList]).reshape(((2**rank)**2,(2**rank)**2))

    
def gen_raster_masks(rank, invert=False):
    '''
    generate a list  raster masks for a given rank 
    
    the masks returned are binary numpy.arrays's.
    there will be N=rank**2 masks. 
    '''
    length = (2**rank)**2
    if invert:
        pixel = 0
        arr = array([[1 for x in range(0,length)] for y in range(0,length)])
    else:
        pixel = 1
        arr = array([[0 for x in range(0,length)] for y in range(0,length)])
    count = 0
    for mask in arr:
        mask[count] = pixel
        count += 1
    return arr

def gen_masks(kind, rank, invert=False):
    '''
    generate set of masks of given `kind` and rank. possibly inverted
    '''
    kw =dict(rank=rank, invert=invert)
    if kind == 'hadamard':
        return gen_had_masks(**kw)
    elif kind == 'raster':
        return gen_raster_masks(**kw)
    else:
        raise ValueError('bad kind')
    
# def gen_decs(kind, rank, invert=False):
#     '''
#     generate decimal representations for a given kind of mask set and rank
    
#     '''
#     masks = gen_masks(kind=kind, rank=rank, invert=invert)
#     return [mask2dec(k) for k in masks]

def gen_hexs(kind, rank, invert = False):
    '''
    generate decimal representation for a given kind of mask set and rank

    '''
    masks = gen_masks(kind = kind, rank = rank, invert = invert)
    return [mask2hex(k) for k in masks]


class Decoder(object):
    def __init__(self, base_dir, cal=None, cal_each_mask=False):
        '''
        A Decoder for a Vector Coded Aperture Measurment System
        
        Parameters
        -----------
        base_dir : str, or `unipath.Path`
            the base directory which holds all data
            
        cal: `skrf.Calibration` object or None
            the calibration template that is copied for each mask's
            calibration. The `measurements` attribute provided by
            the calibraition template is never used, only the `ideals`.
            if None, then no calibration is performed
        
        cal_each_mask : bool
            should a calibration be performed for each mask? If True, this
            requires that `cal` represents a calibration template, for
            which the `measurements` are provided for each mask dir
        '''
        self.base_dir = Path( base_dir)
        self.cal = cal
        self.cal_each_mask = cal_each_mask
        # determine rank 
        max_hex = max([int(d, base=0) for d in self.hexs.keys()])
        self.rank = int(sqrt(len('{0:b}'.format(max_hex))))
        
        self.frequency = rf.ran(str(self.hexs.values()[0])).values()[0].frequency
        
            
        
    @property
    def hexs(self):
        '''
        list of decimal values for each mask
        
        A dictionary with key:values as string:Path for each dec value
        '''
        return {str(k.name):k for k in self.base_dir.listdir()}
    
    
            
    def pixel2hexs(self, m, n, half_on_only = False):
        '''
        list of the masks which have a given pixel `on`.  

        the masks are given in hexadecimal representations
        '''
        out = []
        for d in self.hexs.keys():
            mask = hex2mask(d, rank = self.rank)
            if mask[m,n] == 1:
                # pixel is on
                if half_on_only:
                    if sum(mask) == self.rank:
                        out.append(d)
                else:
                    out.append(d)
        return out
    
    
        
    def cal_of(self, hex_dec):
        '''
        Calibration for a given mask, or pixel
        '''
        
        ##TODO: for no-cal or static cal this could be only calculated
        # once to improve performance
        if self.cal is None:
            freq = self.frequency
            n = len(freq)
            coefs = {'directivity':zeros(n),
                    'source match': zeros(n),
                    'reflection tracking':ones(n)}
            cal = OnePort.from_coefs(frequency = freq, coefs = coefs)
            return cal
            
        if not self.cal_each_mask:
            return self.cal
        else:
            # we want a calibration for each mask, so create the calbration
            # for this mask,or pixel
            cal = deepcopy(self.cal)
            ideals = cal.ideals

            if isinstance(hex_dec, tuple):
                # decode the measurements 
                measured = []
                for ideal in ideals:
                    m = self.raw_ntwk_of(hex_dec,ideal.name)
                    measured.append(m)
                
            else:
                measured = rf.ran(self.hexs[hex_dec]).values()
            
            cal.measured, cal.ideals = rf.align_measured_ideals(measured,ideals)
            cal.name = str(hex_dec)
            return cal

    def error_ntwk_of(self, hex_dec):
        '''
        error ntwk for a given mask, or pixel
        '''
        if isinstance(hex_dec, tuple):
            ntwks = [self.error_ntwk_of(k) for k in self.pixel2hexs(*dec)]
            return rf.average(ntwks)
        
        ntwk = self.cal_of(hex_dec).error_ntwk
        ntwk.name = hex_dec
        return ntwk
    
    def raw_ntwk_of(self, hex_dec, name):
        '''
        raw ntwk for a given mask, or pixel
        '''
        if isinstance(hex_dec, tuple):
            ntwks = [self.raw_ntwk_of(k, name) for k in self.pixel2hexs(*hex_dec)]
            return rf.average(ntwks)
        ntwk = rf.ran(str(self.hexs[hex_dec]), contains = name).values()[0]
        
        return ntwk
        
    def cor_ntwk_of(self, hex_dec, name, loc = 'corrected'):
        '''
        corrected ntwk for a given mask, or pixel
        '''
        if isinstance(hex_dec, tuple):
            if loc  == 'corrected':
                # decode in corrected-space
                ntwks = [self.cor_ntwk_of(k,name) for k in self.pixel2hexs(*hex_dec)]
                return rf.average(ntwks)
            elif loc == 'measured':
                # decode in measured space
                m = self.raw_ntwk_of(hex_dec,name)
                return self.cal_of(hex_dec).apply_cal(m)
        
        # correct a measurement for a single mask
        return self.cal_of(hex_dec).apply_cal(self.raw_ntwk_of(hex_dec,name))
    
    
    
    def cor_cube(self, name, attr = 's_db'):
        '''
        a corrected datacube
        
        constructs a `corrected`  3D data cube with dimensions 
        (FxMXN), where F is frequency axis, M and N are pixels 
        starting from upper left. 
        
        Parameters
        --------------
        name : str
            name of network
        attr: 's', 's_db', 's_deg', any skrf.Network property
            the attribute to put in the cube
        
        '''
        rank = self.rank
        z = array([getattr(self.cor_ntwk_of((m,n),name),attr) \
            for m in range(rank) for n in range(rank)])
        z = z.T.reshape(-1,rank,rank)
        return z
    
    def interact_cor_cube(self, name, attr='s_db', clims=None):
        '''
        an interactive image projection of the cor_cube
        '''
        z = self.cor_cube(name=name, attr=attr)
        if clims == None:
            if attr =='s_db':
                clims = (-20,10)
            elif attr=='s_deg':
                clims = (-180,180)
        freq = self.frequency    
        def func(n):
            plt.matshow(z[n])
            plt.title('%i%s'%(freq.f_scaled[n],freq.unit)) 
            plt.grid(0)
            plt.colorbar()
            if clims is not None:
                plt.clim(clims)
        return interactive (func, n = (0,len(freq)))


