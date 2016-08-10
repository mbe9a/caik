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
import numpy as np
from numpy.linalg import inv
from numpy.random import randint
from xarray import DataArray
from scipy.linalg import hadamard

from cPickle import load

import encoder
import structure


# conversion between masks representations
def dec2bin(dec, rank):
    '''
    convert decimal to binary with given width
    '''
    binary = binary_repr(int(dec), width = (2**rank)**2)
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
    binary_adj = ''
    for character in binary:
        binary_adj += str(character)
    rank = int(log2(sqrt(len(binary_adj))))
    return "{0:#0{1}x}".format(int('0b'+''.join(binary_adj), base = 0), (2**rank)**2/4 + 2)
    
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
    return bin2hex(flat)

## masks 
class MaskSet(object):
    def __init__(self, rank, invert = False):
        self.rank =int(rank)
        self.invert=False
        
    @property
    def res(self):
        return int( 2**self.rank)
    
    @property
    def vector_dim(self):
        return self.res**2
        
    @property
    def masks(self):
        raise NotImplementedError
    
    @property
    def primary_masks(self):
        self.invert = False
        return self.masks

    #TO DO: fix this
    @property
    def inverse_masks(self):
        self.invert = True
        return self.masks

    @property
    def hexs(self):
        return [mask2hex(k) for k in self.masks]
    
    @property
    def frame(self):
        return np.array([k.flatten() for k in self.masks])
    
    @property
    def inv_frame(self):
        return inv(self.frame)

class Hadamard(MaskSet):
    '''
    a little redundant with encoder, need to edit code structure/hierarchy
    '''
    @property
    def hadamard_encoder(self):
        return encoder.Hadamard(self.rank)

    @property
    def masks(self):
        if self.invert:
            m= self.hadamard_encoder.inverse_masks
        else:
            m= self.hadamard_encoder.primary_masks
            
        res = self.res
        return [m[k].reshape(res,res) for k in range(res**2)]
    

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
            arr = array([[1 for x in range(0, length)] for y in range(0, length)])
        else:
            pixel = 1
            arr = array([[0 for x in range(0, length)] for y in range(0, length)])
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
        # we have to cache this or its random everytime!
        try:
            return self._masks
        except(AttributeError):
            pass
            
        rank = self.rank
        res = self.res
        dim = self.vector_dim
        masks =  [randint(0,2,(dim)).reshape(res,res) for k in range(res**2)]
        self._masks = masks
        return masks

class FromHexs(MaskSet):
    '''
    Mask Set created from list of hexs
    '''
    def __init__(self, hexs):
        self._hexs = hexs
    
    @property
    def res(self):
        return int(sqrt(len(self.hexs)))
    @property
    def rank(self):
        return int(log2(self.res))
        
    @property
    def hexs(self):
        return self._hexs
        
    @property
    def masks(self):
        return [hex2mask(k, rank=self.rank) for k in self.hexs]
        

## decoder class
class Decoder(object):
    def __init__(self, dataset, calset, caching = True):
        '''
        Image Decoder 
        
        Examples
        ----------
        dec = Decoder(dataset ='../Imaging/hi_c.p',
                      calset = '../Imaging/new_cals.p')

        dec.image_interact(name=0, clims=(-4,4))
        
        
        d.da # full data available as `xarray.DataArray`
        d.image_at(634) # image at a given frequency
        d.image_interact() # images at all frequencies
        
        '''
        
        masktype='primary'
        
        ## allow dataset/calset to be a filename or open file
        if isinstance(dataset, str):
            with open(dataset, 'rb') as p:
                self.dataset = load(p)
        else:
            self.dataset=dataset
        
        if isinstance(calset, str):
            with open(calset, 'rb') as p:
                self.calset = load(p)
        else:
            self.calset=calset
        
        # single  out masktype for now
        self.dataset =self.dataset[masktype]
        self.calset =self.calset[masktype]
        
        self._da = None
        self.caching = caching
        
        
        
        
    
    @property
    def hexs(self):
        return self.dataset.keys()
        
    @property
    def maskset(self):
        return FromHexs(self.hexs)
    
    @property
    def res(self):
        return self.maskset.res
    @property
    def rank(self):
        return self.maskset.rank
    
    @property
    def frequency(self):
        return self.calset.values()[0].frequency
    
    def checkcal(self, k =0):
        self.calset.values()[k].plot_caled_ntwks()
        
    
        
    def caled(self,name=None):
        '''
        [calibrated or averaged]  measurements  of a given dut
        
        Returns 
        --------
        out : dict skrf.Networks
        '''
        
        if name is None:
            name = 'measurement' # default name 
        frequency = self.frequency 
        nf = len(frequency)
        
        caled = {}
        
        if isinstance(name, str):
            for k in self.dataset:
                ntwks = [l for l in self.dataset[k] if name in l.name]
                caled[k] = self.calset[k].apply_cal_to_list(ntwks)
                caled[k] = rf.average(caled[k])
        if isinstance(name, int):
            for k in self.dataset:
                caled[k] = self.calset[k].caled_ntwks[name]
                
        return caled
            
            
    
    def da(self, name=None):
        '''
        a xarray.DataArray object representing the entire data-set
        '''
        # return cached value if it exists
        if self._da is not None and self.caching:
            return self._da
           
        frequency = self.frequency 
        nf = len(frequency)  
           
        ms = self.maskset
        caled = self.caled(name=name)
        
        s={}
        for h,m in zip(ms.hexs, ms.masks):
            s[h] = caled[h].s*sum(m) # scale s-parameters by number of on pixels
            
        inv_frame = ms.inv_frame.T
        out = []
        for f_idx in range(nf):
            # measurment vector
            m = array([s[h][f_idx,0,0].squeeze() for h in ms.hexs] )
            out.append(m.dot(inv_frame))


        out=array(out)
        out = out.reshape((nf, ms.res,ms.res))


        frequency.unit='ghz'
        
        dat= DataArray(out, coords = [ ('f_ghz', frequency.f_scaled),
                                  ('row', range(ms.res)),
                                  ('col', range(ms.res))])
        
        if self.caching: 
            self._da = dat
        return dat
    
    
    def ntwk(self, name=None, *args, **kw):
        '''
        Network representation of this spectral image
        
        the ports are the pixels. nuff said
        '''
        da = self.da(name=name)
        return rf.Network(s=da.data,z0=1,frequency=self.frequency,
                          *args, **kw)

   
    
    def image_at(self, f, name=None,  attr = 's_db', dead = False,clims=None):
        '''
        Image at `f` for a given scalar `attr` of a skrf.Network
        
        Examples
        ---------
        d.image_at(634,'s_db')
        '''
        n = self.ntwk(name=name)[str(f)]
        x = n.__getattribute__(attr)[0,...]
        temp = 0
        if dead:
            for k in range(0, self.res):
                for j in range(0, self.res):
                    if x[j][k] < temp:
                        temp = x[j][k]
            x[0][0] = temp
        matshow(x)
        colorbar()
        grid(0)
        if clims is not None:
            clim(clims)
    
    def image_interact(self, name=None, attr = 's_db',clims=None):
        '''
        interactive repr of the sprectral image projection onto `attr`
        '''
        freq = self.frequency
        f = (freq.start_scaled, freq.stop_scaled,freq.step_scaled)
        def func(f):
            x = self.ntwk(name=name)[str(f)].__getattribute__(attr)[0,...]
            matshow(x)
            colorbar()
            grid(0)
            if clims is not None:
                clim(clims)
            
        return interact(func, f = f )
        
        
    
# this is dum. but might be good for pixel cross-talk estimattion
def decode_with_rotation(dir_, f = '634ghz', cal = None,  averaging = True):
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
    bins = [hex2bin(k,rank = rank) for k in hexs]
    T = array([array(list(k), dtype = int) for k in bins])
    T_inv = inv(T)

    # create measurement frame `M` in hadamard space. 
    M = []

    for k in hexs:
        b = array(list(hex2bin(k,rank = rank)), dtype = int)
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

    M = array(M)

    # transform the frame `M` in hadamard space to 
    # frame `A` in delta space
    A = T_inv.dot(M)

    # pixels lay along the diagonal. 
    A_diag = array([A[k,k] for k in range(res**2)])

    #reshape the diagonal matrix into the image
    a = A_diag.reshape(res,res)
    return a,A
