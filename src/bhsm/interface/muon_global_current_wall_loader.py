"""Stream actual original current/transpose directions into native wall images.

All six external canonical columns and their complete FE2/C6/n1 tests are
addressable. A selected column is an action source restriction, not a pole
or spin-state selection. The held initial trace and free-final reaction
remain those of the original saved field problem.
"""
from __future__ import annotations
from collections import OrderedDict
from hashlib import sha256
from pathlib import Path
import json
import numpy as np
from .muon_chronological_current_source_images import (
    current_direction_wall_point, native_images_of_current_direction)
from .muon_chronological_spectral_blocks import homogeneous_scalar_degree_reduction


def even_current_source_components(right_source,literal_left):
    """Exact n0+n2 source reduction AFTER its complete real Gaunt image.

    The three n2 spectator sources are distinct. They must be summed as
    current applications, rather than multiplied by a trace multiplicity.
    The left coordinate transport is the analytic inverse map, with no
    conjugation of its coefficients.
    """
    R=np.asarray(right_source,complex);L=np.asarray(literal_left,complex)
    if (R.ndim!=2 or R.shape[0]!=60 or L.shape!=(R.shape[1],60)
            or not np.isfinite(R).all()or not np.isfinite(L).all()):
        raise ValueError('complete real n0+n2 source and literal left required')
    ids0=(np.arange(6)*10)
    ids2=(np.arange(6)[:,None]*10+np.arange(1,10)[None,:]).ravel()
    U=homogeneous_scalar_degree_reduction(2)['real_to_complex_coefficient_map']
    change=np.kron(np.eye(6),U);Rc=change@R[ids2];Lc=L[:,ids2]@change.conj().T
    out=[dict(degree=0,spectator=0,right_source=R[ids0],literal_left=L[:,ids0])]
    for k in range(3):
        ids=(np.arange(6)[:,None]*9+np.arange(3)[None,:]*3+k).ravel()
        out.append(dict(degree=2,spectator=k,right_source=Rc[ids],literal_left=Lc[:,ids]))
    return out


class GlobalCurrentWallLoader:
    """Hash-bound, bounded-memory loader of the actual 176-row saddles."""

    def __init__(self, current_folder, action_folder, *, cache_chunks=8):
        self.current_folder=Path(current_folder);self.action_folder=Path(action_folder)
        if type(cache_chunks)is not int or cache_chunks<1:
            raise ValueError('positive bounded chunk cache required')
        self.cache_chunks=cache_chunks;self._cache=OrderedDict();self.input_hashes={}
        self.current=self._receipt(self.current_folder)
        self.action=self._receipt(self.action_folder)
        if (self.current.get('full_right_source_columns')!=288
                or self.current.get('complete_external_C6_columns')!=6
                or self.current.get('exact_spectators')!=2
                or self.current.get('original_initial_face_held')!=0):
            raise ValueError('complete original 288-column/two-spectator current problem required')
        self.free_nodes=int(self.current['original_free_temporal_nodes'])
        a=self._archive(self.action_folder,self.action,
                        'original_n1_angular_and_source_incidence.npz')
        self.U=np.asarray(a['real_to_complex'],complex)
        self.spectator_indices=np.asarray(a['spectator_field_indices'])
        wall=np.asarray(a['original_wall_map_real'],complex)
        if wall.shape!=(96,336)or self.spectator_indices.shape!=(2,168):
            raise ValueError('complete original wall/H and spectator incidence required')
        self.wall_map=wall.reshape(24,4,84,4)[:,0,:,0].copy()
        if not np.array_equal(wall,np.kron(self.wall_map,np.eye(4))):
            raise ValueError('actual common angular-constant wall map required')

    def _receipt(self,folder):
        path=folder/'result.json';raw=path.read_bytes()
        self.input_hashes[str(path.resolve())]=sha256(raw).hexdigest()
        return json.loads(raw)

    def _archive(self,folder,receipt,name,keys=None):
        path=folder/name;raw=path.read_bytes()
        expected=receipt['archives'][name]['sha256']
        if sha256(raw).hexdigest()!=expected:
            raise ValueError('actual current/source archive hash changed: '+str(path))
        self.input_hashes[str(path.resolve())]=expected
        with np.load(path,allow_pickle=False)as a:
            return {k:a[k].copy()for k in(a.files if keys is None else keys)}

    @staticmethod
    def _columns(columns):
        ids=np.asarray(columns)
        if (ids.ndim!=1 or not len(ids)or not np.issubdtype(ids.dtype,np.integer)
                or np.any(ids<0)or np.any(ids>=288)or len(np.unique(ids))!=len(ids)):
            raise ValueError('distinct exact current columns in externalC6/FE2/internalC6/realn1 order required')
        return ids.astype(int,copy=False)

    def nodal_directions(self,node,columns,*,spectator,analytic_adjoint=False):
        """Return selected actual u or p without replacing moments by fields."""
        columns=self._columns(columns)
        if (type(node)is not int or not 0<=node<=self.free_nodes
                or type(spectator)is not int or spectator not in(0,1)):
            raise ValueError('exact original trace node and spectator required')
        if node==0:return np.zeros((176,len(columns)),complex)
        out=np.empty((176,len(columns)),complex)
        start=8*((node-1)//8)+1
        for spin in np.unique(columns//48):
            key=(spectator,int(spin),start)
            if key not in self._cache:
                name=f'spectator_{spectator}_external_{spin}_nodes_{start}.npz'
                data=self._archive(self.current_folder,self.current,name,(
                    'original_node_start','original_node_stop_exclusive','source_column_indices',
                    'original_current_response','original_transpose_current_adjoint'))
                if (int(data['original_node_start'])!=start
                        or not np.array_equal(data['source_column_indices'],int(spin)*48+np.arange(48))
                        or int(data['original_node_stop_exclusive'])<=node):
                    raise ValueError('actual source chunk incidence changed')
                self._cache[key]=data
                while len(self._cache)>self.cache_chunks:self._cache.popitem(last=False)
            data=self._cache[key];self._cache.move_to_end(key)
            chosen=np.flatnonzero(columns//48==spin)
            field='original_transpose_current_adjoint'if analytic_adjoint else'original_current_response'
            out[:,chosen]=data[field][node-start][:,columns[chosen]%48]
        return out

    def point(self,rows,columns,*,lapse,right_clock):
        """Restore both spectators, all 24 wall/H values and future rates."""
        columns=self._columns(columns);r=np.asarray(rows,complex)
        if (r.shape!=(2,3)or not np.isfinite(r).all()or np.any(r[:,0].imag)
                or np.any(r[:,0].real!=np.floor(r[:,0].real))
                or int(r[1,0].real)!=int(r[0,0].real)+1):
            raise ValueError('actual adjacent integer trace rows required')
        result={}
        for label,adj in(('u',False),('p',True)):
            values=[];rates=[];frames=[]
            for s in range(2):
                nodal=np.array([self.nodal_directions(int(j.real),columns,
                    spectator=s,analytic_adjoint=adj)for j in r[:,0]])
                a=current_direction_wall_point(nodal,r,self.wall_map,self.U,self.spectator_indices[s],
                    lapse=lapse,right_clock=right_clock,analytic_adjoint=adj)
                values.append(a['wall_coefficients']);rates.append(a['wall_coordinate_rate'])
                frames.append(a['original_frame_direction'])
            result[label+'_wall_coefficients']=sum(values)
            result[label+'_wall_coordinate_rate']=sum(rates)
            result[label+'_frame_reactions_by_spectator']=np.array(frames)
        result.update(source_column_indices=columns,source_direction_conjugated=False,
            complete_canonical_columns_available=288,physical_external_state_assigned=False,
            original_initial_trace_held=0,original_free_final_trace=self.free_nodes)
        return result

    def node_images(self,q,columns,*,family,even_field_odd_gaunt):
        """Produce actual Xi_u and literal Xi_p, including induced Higgs."""
        a=self.point(q['rows'],columns,lapse=q['N'],right_clock=q['right_clock'])
        for label in('u','p'):
            a[label+'_native_images']=native_images_of_current_direction(a[label+'_wall_coefficients'],
                radius=q['R'],lapse=q['N'],reflected_radius=q['Rsharp'],reflected_lapse=q['Nsharp'],
                family=family,even_field_odd_gaunt=even_field_odd_gaunt)
        return a

    def verify_consumed_hashes(self):
        if any(sha256(Path(p).read_bytes()).hexdigest()!=h for p,h in self.input_hashes.items()):
            raise RuntimeError('consumed original current/source changed')
        return dict(self.input_hashes)
