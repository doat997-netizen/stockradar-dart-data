#!/usr/bin/env python3
"""Read-only contract check for Stock Radar's published DART cache."""
import datetime as dt
import json
import re
import sys
from pathlib import Path

def day(s):
    if not isinstance(s,str) or re.fullmatch(r"\d{8}",s) is None:
        return False
    try:
        dt.datetime.strptime(s,"%Y%m%d")
        return True
    except ValueError:
        return False

def validate(data):
    errors=[]
    if not isinstance(data,dict):
        return ["root must be an object"],{}
    if data.get("schema")!="sr-dart-cache-v1":
        errors.append("incorrect schema")
    stamp=data.get("updated_at")
    try:
        timestamp=dt.datetime.fromisoformat(stamp)
        if timestamp.utcoffset() is None: raise ValueError("offset missing")
    except (TypeError,ValueError,OverflowError):
        errors.append("updated_at must be offset-aware ISO 8601")
    days=data.get("covered_days")
    if not isinstance(days,list) or len(days)>95 or any(not day(d) for d in days):
        errors.append("invalid covered_days")
        days=[]
    elif len(days)!=len(set(days)):
        errors.append("duplicate covered_days")
    items=data.get("items")
    if not isinstance(items,list) or len(items)>60000:
        errors.append("items must be an array with at most 60000 rows")
        items=[]
    if type(data.get("count")) is not int or data.get("count")!=len(items):
        errors.append("count mismatch")
    seen=set()
    for i,x in enumerate(items):
        if not isinstance(x,dict):
            errors.append(f"item {i}: not an object")
            continue
        no=x.get("rcept_no")
        if not isinstance(no,str) or re.fullmatch(r"\d{14}",no) is None:
            errors.append(f"item {i}: invalid receipt")
        elif no in seen:
            errors.append(f"item {i}: duplicate receipt")
        else:
            seen.add(no)
        if not day(x.get("rcept_dt")):
            errors.append(f"item {i}: invalid filing date")
        elif x["rcept_dt"] not in set(days):
            errors.append(f"item {i}: receipt date outside covered_days")
        corp=x.get("corp_code")
        if not isinstance(corp,str) or re.fullmatch(r"\d{8}",corp) is None or corp=="00000000":
            errors.append(f"item {i}: invalid corporate code")
        for field,limit in (("corp_name",150),("report_nm",350)):
            value=x.get(field)
            if not isinstance(value,str) or not value.strip() or len(value)>limit:
                errors.append(f"item {i}: invalid {field}")
        for field,limit in (("rm",100),("stock_code",12)):
            value=x.get(field,"")
            if value is not None and (not isinstance(value,str) or len(value)>limit):
                errors.append(f"item {i}: invalid {field}")
        if len(errors)>20:
            errors.append("errors truncated")
            break
    return errors,{"count":data.get("count"),"items":len(items),"receipt_unique":len(seen),"covered_days":len(days),"updated_at":stamp}

if __name__=="__main__":
    source=Path(sys.argv[1] if len(sys.argv)>1 else "data/dart_cache.json")
    try:
        data=json.loads(source.read_text(encoding="utf-8"))
        errors,meta=validate(data)
    except (OSError,ValueError) as error:
        errors,meta=[str(error)],{}
    print(json.dumps({"result":"FAIL" if errors else "PASS","source":str(source),"details":meta,"errors":errors},ensure_ascii=False,indent=2))
    sys.exit(1 if errors else 0)
