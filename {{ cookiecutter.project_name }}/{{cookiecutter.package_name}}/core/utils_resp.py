from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

@dataclass(init=True, repr=True, eq=True, order=True, unsafe_hash=False, frozen=False)
class RespJSON:
    code:int
    data:Any
    error:str
    msg:str

def gen_resp(data=None, code=200, msg='ok', error='') -> RespJSON:
    return RespJSON(
        code=code,
        data=data,
        error=error,
        msg=msg
    )