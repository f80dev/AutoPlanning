from datetime import datetime
import pandas as pd


def datetostr(dt:datetime) -> str:
    return dt.strftime("%m-%d %H:%M")

def plagetostr(plage:tuple) -> str:
    return datetostr(plage[0])+" -> "+datetostr(plage[1])

def strtodate(dt:str) -> datetime :
    if type(dt)==datetime: return dt
    if type(dt) == pd.Timestamp: return dt.to_pydatetime()
    dt = dt.replace("  ", " ").replace(" ", "/2026 ")
    if not " " in dt: dt=dt+" 00:00"
    return datetime.strptime(dt, "%d/%m/%Y %H:%M")



