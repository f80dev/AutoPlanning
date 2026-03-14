from datetime import datetime
import pandas as pd


def datetostr(dt:datetime) -> str:
    return dt.strftime("%m-%d %H:%M")

def plagetostr(plage:tuple) -> str:
    return datetostr(plage[0])+" -> "+datetostr(plage[1])

def strtodate(dt:str) -> datetime | None :
    if type(dt)==datetime: return dt
    if type(dt) == pd.Timestamp: return dt.to_pydatetime()
    if type(dt)==float:
        return None

    dt = dt.replace("  ", " ")
    if not " " in dt: dt=dt+" 00:00"
    try:
        return datetime.strptime(dt, "%d/%m/%Y %H:%M")
    except:
        return None


def get_idx_day_of_string(day:str):
    try:
        return ["lundi", "mardi", "mercredi", "jeudi", "vendredi","samedi","dimanche"].index(day)
    except:
        return ["lu", "ma", "me", "je", "ve","sa","di"].index(day)



