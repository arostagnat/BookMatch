from bookmatch.params import *

def flatten_txt(data,id="item_id",colname="txt"):
    """
    permet de concat les "txt" de datafram par "item_im"
    et renvoit un df avec autant de lignes que de item_id
    """
    return data.groupby(id, as_index=False).agg({colname: " ".join})
