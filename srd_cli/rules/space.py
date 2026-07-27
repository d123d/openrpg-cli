"""Authoritative range-band space plus optional square-grid adapter."""
from __future__ import annotations
from dataclasses import dataclass, replace
from enum import IntEnum, Enum
from .turns import RangeSpec, TargetSpec

MAX_ACTORS=256; MAX_COORD=10000; MAX_PATH=256

class RangeBand(IntEnum):
    SAME=0; NEAR=1; FAR=2; REMOTE=3
class TargetKind(str,Enum):
    SINGLE="single"; MULTIPLE="multiple"; SELF="self"; ALLY="ally"; ENEMY="enemy"
    POINT="point"; LINE="line"; CONE="cone"; CUBE="cube"; SPHERE="sphere"; CYLINDER="cylinder"
class AreaShape(str,Enum):
    LINE="line"; CONE="cone"; CUBE="cube"; SPHERE="sphere"; CYLINDER="cylinder"

@dataclass(frozen=True,slots=True)
class RelativePosition:
    actor_a:str; actor_b:str; band:RangeBand
    def __post_init__(self):
        if not self.actor_a or not self.actor_b or self.actor_a==self.actor_b: raise ValueError("invalid relative position")

@dataclass(frozen=True,slots=True)
class SpatialState:
    actor_ids:tuple[str,...]; positions:tuple[RelativePosition,...]
    def __post_init__(self):
        if not self.actor_ids or len(self.actor_ids)>MAX_ACTORS or len(set(self.actor_ids))!=len(self.actor_ids): raise ValueError("invalid actors")
        found={}
        for p in self.positions:
            if p.actor_a not in self.actor_ids or p.actor_b not in self.actor_ids: raise ValueError("unknown actor")
            key=tuple(sorted((p.actor_a,p.actor_b)))
            if key in found and found[key]!=p.band: raise ValueError("asymmetric position")
            found[key]=p.band
    def band(self,a:str,b:str)->RangeBand:
        if a==b:return RangeBand.SAME
        for p in self.positions:
            if {p.actor_a,p.actor_b}=={a,b}:return p.band
        raise ValueError("missing relative position")

@dataclass(frozen=True,slots=True)
class AreaSpec:
    shape:AreaShape; origin_actor_id:str; maximum_band:RangeBand
    dimensions:tuple[int,...]=()
    def __post_init__(self):
        if len(self.dimensions)>3 or any(type(x)is not int or not 0<x<=10000 for x in self.dimensions):raise ValueError("invalid area")

@dataclass(frozen=True,slots=True)
class TargetResolution:
    accepted:tuple[str,...]; rejected:tuple[tuple[str,str],...]
@dataclass(frozen=True,slots=True)
class MovementTransition:
    accepted:bool; reason:str|None; actor_id:str; from_band:RangeBand; to_band:RangeBand; cost:int

def move(state:SpatialState,actor_id:str,reference_id:str,destination:RangeBand,available:int)->tuple[SpatialState,MovementTransition]:
    old=state.band(actor_id,reference_id); cost=abs(int(destination)-int(old))*30
    if cost>available:return state,MovementTransition(False,"insufficient_movement",actor_id,old,destination,cost)
    ps=[p for p in state.positions if {p.actor_a,p.actor_b}!={actor_id,reference_id}]
    ps.append(RelativePosition(actor_id,reference_id,destination))
    return replace(state,positions=tuple(sorted(ps,key=lambda p:(p.actor_a,p.actor_b)))),MovementTransition(True,None,actor_id,old,destination,cost)

def resolve_targets(state:SpatialState,source_id:str,candidates:tuple[str,...],target:TargetSpec,range_spec:RangeSpec,teams:dict[str,str]|None=None)->TargetResolution:
    if len(candidates)>MAX_ACTORS:return TargetResolution((),(("*","too_many_targets"),))
    accepted=[]; rejected=[]
    maximum=RangeBand(min(3,range_spec.maximum))
    for actor in sorted(set(candidates)):
        reason=None
        if actor not in state.actor_ids:reason="unknown_target"
        elif state.band(source_id,actor)>maximum:reason="out_of_range"
        elif "self" in target.kinds and actor!=source_id:reason="target_not_self"
        elif "ally" in target.kinds and teams and teams.get(actor)!=teams.get(source_id):reason="target_not_ally"
        elif "enemy" in target.kinds and teams and teams.get(actor)==teams.get(source_id):reason="target_not_enemy"
        (rejected if reason else accepted).append((actor,reason) if reason else actor)
    if len(accepted)<target.minimum or len(accepted)>target.maximum:
        return TargetResolution((),tuple(rejected)+tuple((x,"invalid_target_count") for x in accepted))
    return TargetResolution(tuple(accepted),tuple(rejected))

def resolve_area(state:SpatialState,area:AreaSpec)->TargetResolution:
    return resolve_targets(state,area.origin_actor_id,tuple(x for x in state.actor_ids if x!=area.origin_actor_id),TargetSpec(("multiple",),0,MAX_ACTORS),RangeSpec(0,int(area.maximum_band)))

@dataclass(frozen=True,slots=True)
class GridPosition:
    x:int;y:int
    def __post_init__(self):
        if type(self.x)is not int or type(self.y)is not int or abs(self.x)>MAX_COORD or abs(self.y)>MAX_COORD:raise ValueError("invalid coordinates")
@dataclass(frozen=True,slots=True)
class GridState:
    positions:tuple[tuple[str,GridPosition],...]; blocked:frozenset[GridPosition]=frozenset()
    def __post_init__(self):
        ids=[x[0] for x in self.positions]; coords=[x[1] for x in self.positions]
        if len(ids)>MAX_ACTORS or len(ids)!=len(set(ids)) or len(coords)!=len(set(coords)):raise ValueError("invalid grid occupancy")

def grid_to_spatial(grid:GridState)->SpatialState:
    pairs=[]; positions=dict(grid.positions); ids=tuple(sorted(positions))
    for i,a in enumerate(ids):
        for b in ids[i+1:]:
            # Chebyshev metric: diagonal square costs same as orthogonal square.
            d=max(abs(positions[a].x-positions[b].x),abs(positions[a].y-positions[b].y))*5
            band=RangeBand.SAME if d==0 else RangeBand.NEAR if d<=30 else RangeBand.FAR if d<=120 else RangeBand.REMOTE
            pairs.append(RelativePosition(a,b,band))
    return SpatialState(ids,tuple(pairs))
