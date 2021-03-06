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
from ipywidgets import  interact

import os 
from numpy.linalg import inv
from numpy.random import randint
from xarray import DataArray
from scipy.linalg import hadamard

#import cai



# conversion between masks representations
def dec2bin(dec, rank):
    '''
    convert decimal to binary with given width
    '''
    binary = binary_repr(int(dec), width=(2**rank)**2)
    return binary

def hex2bin(hex_dec, rank):
    '''
    convert hexadecimal to binary with given width
    '''
    dec = int(hex_dec, base = 0)
    binary = binary_repr(int(dec), width = (2**rank)**2)
    return binary
    
def dec2mask(dec,rank,**kw):
    '''
    translates a decimal representaion into a binary mask (numpy array) 
    '''
    binary = dec2bin(dec=dec,rank=rank)
    return array([int(k) for k in binary ]).reshape((2**rank,2**rank),**kw)

def hex2mask(hex_dec,rank,**kw):
    '''
    translates a decimal representation into a binary mask (numpy array)
    '''
    binary = hex2bin(hex_dec = hex_dec, rank = rank)
    return array([int(k) for k in binary ]).reshape((2**rank,2**rank),**kw)
    
def bin2dec(binary):
    '''
    convert binary to decimal
    '''
    return int('0b'+''.join(binary),base=0)

def bin2hex(binary):
    '''
    convert binary to hexadecimal
    '''
    return hex(int('0b'+''.join(binary),base = 0))
    
def mask2dec(mask):
    '''
    translates a mask to its decimal representation
    '''
    flat = mask.flatten().astype('str')
    return bin2dec(flat)

def mask2hex(mask):
    '''
    translates a mask to its hexadecimal representation
    '''
    flat = mask.flatten().astype('str')
    return hex(bin2dec(flat))

## masks 
class MaskSet(object):
    def __init__(self, rank, invert=False):
        self.rank =rank
        self.invert=False
    
    @property
    def res(self):
        return 2**self.rank
    
    @property
    def vector_dim(self):
        return self.res**2
        
    @property
    def masks(self):
        raise NotImplementedError
    
    @property
    def hexs(self):
        return [mask2hex(k) for k in masks]
        
class Hadamard(MaskSet):
    '''
    '''
    @property
    def masks(self):
        rank = self.rank
        if self.invert:
            matrixList = cai.list2bn(rank, cai.inverse_ML(cai.createH(rank,'111-',[])))
        else:
            matrixList = cai.list2bn(rank, cai.createH(rank,'111-',[]))
        return array([[int(k) for k in matrix] for matrix in matrixList]).reshape(((2**rank)**2,(2**rank)**2))

class Raster(MaskSet):
    '''
    raster masks 
    '''
    @property
    def masks(self):
        rank = self.rank
        
        length = (2**rank)**2
        if self.invert:
            pixel = 0
            arr = array([[1 for x in range(0,length)] for y in range(0,length)])
        else:
            pixel = 1
            arr = array([[0 for x in range(0,length)] for y in range(0,length)])
        count = 0
        for mask in arr:
            mask[count] = pixel
            count += 1
        
        arr = [ mask.reshape(self.res, self.res) for mask in arr]
        return arr

class Walsh(MaskSet):
    '''
    '''
    @property
    def masks(self):
        rank = self.rank
        res = 2**rank
        
        H = hadamard(res**2)
        H[H==-1]=0
        if self.invert:
            H = -H+1
        return [H[:,k].reshape(res,res) for k in range(res**2)]

class Random(MaskSet):
    '''
    '''
    @property
    def masks(self):
        rank = self.rank
        res = self.res
        dim = self.vector_dim
        return [randint(0,2,(dim)).reshape(res,res) for k in range(res**2)]


## decoder class
class Decoder(object):
    def __init__(self, dir_, cal=None,  averaging=True,caching=True):
        '''
        Simple Image Decoder 
        
        Examples
        ----------
        dir_= '../CAI/Bar Image/hadamard_2/Primary'
        d = Decoder(dir_=dir_,averaging =True)
        
        
        d.da # full data available as `xarray.DataArray`
        d.image_at(634) # image at a given frequency
        d.image_interact() # images at all frequencies
        
        '''
        self.dir_=dir_
        self.cal = cal
        self.averaging =averaging
        self._da = None
        self.caching=caching
    
    
    @property
    def hexs(self):
        return os.listdir(self.dir_)
    
    @property
    def res(self):
        return int(sqrt(len(self.hexs)))
    @property
    def rank(self):
        return int(log2(self.res))
    
    @property
    def da(self):
        '''
        a xarray.DataArray object representing the entire data-set
        '''
        # return cached value if it exists
        if self._da is not None and caching:
            return self._da
            
        hexs= self.hexs
        res = self.res
        rank = self.rank
        
        M=[] # will hold weighted masks
         
        for k in hexs:
            n = rf.ran(self.dir_+'/'+k)
            
            if self.cal is not None:
                n = self.cal.apply_cal_to_list(n)
            
            if self.averaging:
                n = rf.average(n.values())
            else:
                n = n[sorted(n.keys())[-1]]
            
            s = n.s[:,0,0].reshape(-1,1,1) # pull out single complex number
            
            m = hex2mask(k,rank=rank) 
            #copy mask allong frequency dimension
            m = expand_dims(m,0).repeat(s.shape[0],0) 
            m = m*s
            M.append(m)

        M= array(M)
        n.frequency.unit='ghz'
        da = DataArray(M, coords=[('mask_hex',hexs),
                                  ('f_ghz',n.frequency.f_scaled),
                                  ('row',range(res)),
                                  ('col',range(res))])
        
        if caching: 
            self._da = da 
        return da
    
    @property
    def ntwk(self, *args, **kw):
        '''
        Network representation of this spectral image
        
        the ports are the pixels. nuff said
        '''
        s = self.da.mean(dim='mask_hex').data
        return rf.Network(s=s,z0=1,frequency=self.frequency,*args, **kw)

    @property
    def frequency(self):
        return rf.ran(self.dir_+'/'+self.hexs[0]).values()[0].frequency
    
    
    def image_at(self, f,  attr='s_db'):
        '''
        Image at `f` for a given scalar `attr` of a skrf.Network
        
        Examples
        ---------
        d.image_at(634,'s_db')
        '''
        n = self.ntwk[str(f)]
        x = n.__getattribute__(attr)[0,...]
        matshow(x)
        colorbar()
        grid(0)
    
    def image_interact(self,  attr='s_db'):
        '''
        interactive repr of the sprectral image projection onto `attr`
        '''
        freq= self.frequency
        f=(freq.start_scaled, freq.stop_scaled,freq.step_scaled)
        def func(f):
            x = self.ntwk[str(f)].__getattribute__(attr)[0,...]
            matshow(x)
            colorbar()
            grid(0)
        return interact(func,f=f )
        
        
    
# this is dum. but might be good for pixel cross-talk estimattion
def decode_with_rotation(dir_, f='634ghz', cal=None,  averaging=True):
    '''
    decode a hadamard-encoded dataset at a given frequency
    
    
    Examples
    ----------
    f = '634ghz'
    dir_= '../CAI/Bar Image/hadamard_2/Primary'

    a = decode(dir_=dir_, f = f,averaging =True)
    matshow(rf.complex_2_db(a))
    cb = colorbar()
    #clim(-26,-25)
    grid(0)

    '''
    hexs = os.listdir(dir_)
    
    #determine resolution and rank 
    res = int(sqrt(len(hexs)))
    rank = int(log2(res))

    # calculate inverse hadamard-delta transform`T`
    # this can be pre-computed 
    bins = [hex2bin(k,rank=rank) for k in hexs]
    T = array([array(list(k), dtype=int) for k in bins])
    T_inv = inv(T)

    # create measurement frame `M` in hadamard space. 
    M = []

    for k in hexs:
        b = array(list(hex2bin(k,rank=rank)),dtype=int)
        n = rf.ran(dir_+'/'+k)
        
        if cal is not None:
            n = cal.apply_cal_to_list(n)
        if averaging:
            n = rf.average(n.values())
        else:
            n = n[sorted(n.keys())[-1]]
        
        
            
        s = n[f].s[0,0,0] # pull out single complex number
        m = s*b
        M.append(m)

    M= array(M)

    # transform the frame `M` in hadamard space to 
    # frame `A` in delta space
    A = T_inv.dot(M)

    # pixels lay along the diagonal. 
    A_diag = array([A[k,k] for k in range(res**2)])

    #reshape the diagonal matrix into the image
    a = A_diag.reshape(res,res)
    return a,A
