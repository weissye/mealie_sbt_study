"""Keep generated fixture logins locally, protected by the Windows user account."""
import ctypes,json,os
from pathlib import Path


def save_fixture_credentials(receipt,review_name,case,sample):
    if os.name!='nt':return None
    from ctypes import wintypes
    class Blob(ctypes.Structure):
        _fields_=[('cbData',wintypes.DWORD),('pbData',ctypes.POINTER(ctypes.c_ubyte))]
    data={}
    observations=receipt['identity_program']['observations']
    for actor in ('A','B'):
        key=actor.lower();identity=observations['self_'+key]['body']
        data[actor]={k:identity[k] for k in ('id','email','groupId','householdId')}
        data[actor]['password']=os.environ['SBT_IDP_'+actor+'_PASSWORD']
    raw=json.dumps(data).encode('utf-8');buffer=ctypes.create_string_buffer(raw);source=Blob(len(raw),ctypes.cast(buffer,ctypes.POINTER(ctypes.c_ubyte)));destination=Blob()
    crypt=ctypes.WinDLL('crypt32',use_last_error=True);kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    crypt.CryptProtectData.argtypes=[ctypes.POINTER(Blob),wintypes.LPCWSTR,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(Blob)];crypt.CryptProtectData.restype=wintypes.BOOL
    kernel.LocalFree.argtypes=[ctypes.c_void_p];kernel.LocalFree.restype=ctypes.c_void_p
    if not crypt.CryptProtectData(ctypes.byref(source),'Mealie identity fixtures',None,None,None,1,ctypes.byref(destination)):raise OSError(ctypes.get_last_error(),'Could not protect fixture credentials.')
    path=Path(os.environ['LOCALAPPDATA'])/'MealieSbtStudy'/'IdentityCredentials'/review_name/(case+'-'+str(sample)+'.dpapi');path.parent.mkdir(parents=True,exist_ok=True)
    try:path.write_bytes(ctypes.string_at(destination.pbData,destination.cbData))
    finally:kernel.LocalFree(ctypes.cast(destination.pbData,ctypes.c_void_p))
    return str(path)
