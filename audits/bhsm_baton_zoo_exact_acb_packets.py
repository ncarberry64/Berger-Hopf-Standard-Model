"""Exact dyadic midpoint/radius NPZ serialization, without expression eval."""
import numpy as np


def encode(value,prefix):
    from flint import acb,acb_mat
    if isinstance(value,acb_mat):
        array=np.asarray([[value[i,j]for j in range(value.ncols())]for i in range(value.nrows())],dtype=object).reshape(value.nrows(),value.ncols())
    else:array=np.asarray(value,dtype=object)
    result={prefix+'_exact_shape':np.asarray(array.shape,int)}
    for part in('real','imag'):
        midman=np.empty(array.shape,object);radman=np.empty(array.shape,object)
        midexp=np.empty(array.shape,np.int64);radexp=np.empty(array.shape,np.int64)
        for index in np.ndindex(array.shape):
            z=array[index]if isinstance(array[index],acb)else acb(array[index])
            if not z.is_finite():raise ArithmeticError('nonfinite exact action operand cannot be serialized as an admitted packet')
            component=getattr(z,part);mm,me=component.mid().man_exp();rm,re=component.rad().man_exp()
            midman[index],midexp[index]=str(mm),int(me);radman[index],radexp[index]=str(rm),int(re)
        result[prefix+'_'+part+'_mid_mantissa']=midman.astype(str);result[prefix+'_'+part+'_mid_exponent']=midexp
        result[prefix+'_'+part+'_rad_mantissa']=radman.astype(str);result[prefix+'_'+part+'_rad_exponent']=radexp
    return result


def decode_array(packet,prefix):
    from flint import acb,arb,ctx
    shape=tuple(map(int,packet[prefix+'_exact_shape']));out=np.empty(shape,object)
    for index in np.ndindex(shape):
        components=[]
        for part in('real','imag'):
            k=prefix+'_'+part
            mid=(int(packet[k+'_mid_mantissa'][index]),int(packet[k+'_mid_exponent'][index]))
            rad=(int(packet[k+'_rad_mantissa'][index]),int(packet[k+'_rad_exponent'][index]))
            # arb(mid, radius) can round a 30-bit MAG radius upward by
            # one unit even when it is already exactly representable.
            # The midpoint is exact at sufficient working precision.
            # If needed, a half-unit smaller constructor argument rounds
            # to the recorded MAG radius; verify both components exactly.
            with ctx.workprec(max(ctx.prec,abs(mid[0]).bit_length()+4)):
                value=arb(mid,rad)
                if value.mid().man_exp()!=mid or value.rad().man_exp()!=rad:
                    if rad[0]<=0:raise ArithmeticError('zero-radius exact dyadic reconstruction failed')
                    value=arb(mid,(2*rad[0]-1,rad[1]-1))
                if value.mid().man_exp()!=mid or value.rad().man_exp()!=rad:
                    raise ArithmeticError('exact recorded midpoint/radius reconstruction failed')
            components.append(value)
        out[index]=acb(*components)
    return out


def decode_matrix(packet,prefix):
    from flint import acb_mat
    array=decode_array(packet,prefix)
    if array.ndim!=2:raise ValueError('explicit 2D matrix schema required')
    if not array.shape[0]or not array.shape[1]:return acb_mat(*array.shape)
    return acb_mat(array.tolist())


def mutually_contains(value,packet,prefix):
    from flint import acb_mat
    restored=decode_array(packet,prefix)
    if isinstance(value,acb_mat):
        original=np.asarray([[value[i,j]for j in range(value.ncols())]for i in range(value.nrows())],object).reshape(value.nrows(),value.ncols())
    else:original=np.asarray(value,object)
    return original.shape==restored.shape and all(original[i].contains(restored[i])and restored[i].contains(original[i])for i in np.ndindex(original.shape))
