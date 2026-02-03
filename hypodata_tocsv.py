import csv
import os
from glob import glob
from datetime import datetime

#=================================
#メイン（設定領域）
"""
■file_setting
1=import_dataで指定した1ファイルをoutput_csvへ出力
2=import_dataで指定したフォルダ内全ファイルを個別の同名.csvへ出力
3=import_dataで指定したフォルダ内全ファイルをoutput_csv1ファイルにまとめて出力
※2or3について、このpyファイルが置いてある同じフォルダ内のファイルを指定する場合「"."」としてください
※2or3を実行する場合、このpyファイルと「震源データ」のファイルのみで実行しなければ、失敗します

■output_format
1=震源データの内容をそのまま付記（但し、小数点処理あり）
2=震源データをある程度解釈できる文字・数値データとして出力
3=震源データを2に加え、年月日日時をdatetime型、緯度経度を10進数として出力
"""
file_setting = 1
output_format = 3

import_data = "h2023"
output_csv = "h2023_hypodata.csv"

#=================================
#以下、プログラム開始（変更必要なし）

#=================================
agency_map = {
    "J": "JMA",
    "U": "USGS",
    "I": "Other"
}

mag_type_map = {
    "J": "JMA_old observe Tuboi displacement",
    "D": "JMA_Tuboi displacement",
    "d": "JMA_Tuboi displacement_2points",
    "V": "JMA_Tuboi velocity",
    "v": "JMA_Tuboi velocity_2or3points",
    "B": "USGS etc_body wave",
    "S": "USGS etc_surface wave",
}

travel_time_map = {
    "1": "ichikawa and mochiduki (1971) or 83A",
    "2": "LL [Sanriku oki etc]",
    "3": "Ichikawa and mochiduki (1971) and LL or 83A and LL [Hokkaido toho oki etc]",
    "4": "Ichikawa and mochiduki (1971) and LL or 83A and LL [Kuril Islands etc]",
    "5": "JMA2001",
    "6": "JMA2001_and_LL [Kuril Islands etc]",
    "7": "MA2001A or JMA2020A or JMA2020B or JMA2020C",
}

hypo_eval_map = {
    "1": "Depth_free",
    "2": "Optimal solution found using depth-step condition",
    "3": "Depth fixed etc, based on human judgment",
    "4": "Used Depth Phase",
    "5": "Used S-P",
    "7": "Reference",
    "8": "Undecided or not adopted",
    "9": "Fixed hypocenter",
    "M": "Used Matched Filter method",
}

eq_cause_map = {
    "1": "Natural Earthquakes",
    "2": "Dependent on other agencies",
    "3": "Artificial Earthquakes",
    "4": "Volcanic related",
    "5": "Low_frequency Events",
}

max_intensity_map = {
    "1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7",
    "A": "5-", "B": "5+", "C": "6-", "D": "6+",
    "L": "Local earthquake",
    "S": "Minor local earthquake",
    "M": "Moderately noticeable earthquake",
    "R": "Noticeable earthquake",
    "F": "Felt earthquake",
    "X": "Felt in the vicinity",
}

disaster_scale_map = {
    "1": "Minor_cracks",
    "2": "Minor_damage",
    "3": "Fatalities_or_destroyed_houses",
    "4": "20+fatalities_or_1000+destroyed",
    "5": "200+fatalities_or_10000+destroyed",
    "6": "2000+fatalities_or_100000+destroyed",
    "7": "20000+fatalities_or_1M+destroyed",
    "X": "Unknown_damage",
    "Y": "Damage_not_isolatable",
}

hypo_flag_map = {
    "K": "JMA Hypocenter",
    "S": "Reference Hypocenter",
    "k": "Simplified JMA Hypocenter",
    "s": "Simplified reference Hypocenter",
    "A": "Automatic JMA Hypocenter",
    "a": "Automatic reference Hypocenter",
    "N": "Hypocenter Fixed/Hypocenter Uncertain/Not Calculated",
    "F": "Distant",
}

#=================================
def to_float_fixed_decimal(s, decpos):
    if s is None:
        return None
    if all(ch == ' ' for ch in s):
        return None
    if len(s) < decpos:
        return None
    int_part = s[:-decpos]
    frac_part = s[-decpos:]

    #以下で数字の部分のみ抽出し、出力
    int_part_digits = "".join(ch for ch in int_part if ch.isdigit())
    frac_part_digits = "".join(ch for ch in frac_part if ch.isdigit())

    if int_part_digits == "" and frac_part_digits == "":
        return None
    
    if int_part_digits == "":
        int_part_digits= "0"
    
    if frac_part_digits == "":
        frac_part_digits = "0"

    return float(int_part_digits + "." + frac_part_digits)

#=================================
def to_lonlat_clean(s):
    if s is None:
        return None
    s = s.strip()
    if s == "":
        return None
    s = s.replace(" ", "")
    try:
        return float(s)
    except:
        return None
    

#=================================
def build_datetime(year, month, day, hour, minute, second):
    try:
        if second is None:
            sec_int = 0
            usec = 0
        else:
            sec = float(second)
            sec_int = int(sec)
            usec = int((sec - sec_int) * 1_000_000)
        
        dt = datetime(
            int(year), int(month), int(day), int(hour), int(minute),
            sec_int, usec
        )
        return dt
    except:
        return None
    
#=================================
def parse_magnitude(code):
    code = code.strip()
    if code == "":
        return None
    if code.startswith('-') and len(code) == 2:
        return round(-0.1 * int(code[1]), 1)
    if code[0] == "A":
        return round(-1.0 - 0.1 * int(code[1]), 1)
    if code[0] == "B":
        return round(-2.0 - 0.1 * int(code[1]), 1)
    if code == "C0":
        return -3.0
    try:
        return round(to_float_fixed_decimal(code, 1), 1)
    except:
        return(None)

#=================================
def parse_fixed_width_record(line):
    agency = agency_map.get(line[0], None) if output_format >= 2 else line[0]

    year = line[1:5].strip() or None
    month = line[5:7].strip() or None
    day = line[7:9].strip() or None
    hour = line[9:11].strip() or None
    minute = line[11:13].strip() or None

    second = to_float_fixed_decimal(line[13:17], 2)
    second_err = to_float_fixed_decimal(line[17:21], 2)

    lat_deg = to_lonlat_clean(line[21:24])
    lat_min = to_float_fixed_decimal(line[24:28], 2)
    lat_min_err = to_float_fixed_decimal(line[28:32], 2)

    lon_deg = to_lonlat_clean(line[32:36])
    lon_min = to_float_fixed_decimal(line[36:40], 2)
    lon_min_err = to_float_fixed_decimal(line[40:44], 2)

    if output_format == 3:
        lat_decimal = None
        lon_decimal = None
        if lat_deg and lat_min is not None:
            lat_decimal = float(lat_deg) + lat_min / 60.0
        if lon_deg and lon_min is not None:
            lon_decimal = float(lon_deg) + lon_min / 60.0

    depth = to_float_fixed_decimal(line[44:49], 2)
    depth_err = to_float_fixed_decimal(line[49:52], 2)

    mag1 = parse_magnitude(line[52:54])
    mag2 = parse_magnitude(line[55:57])

    if output_format >= 2:
        mag1_type_raw = line[54]

        if mag1_type_raw == "W":
            mag1_type = "JMA moment" if line[0] == "J" else "JMA or others moment"
        else:
            mag1_type = mag_type_map.get(mag1_type_raw, None)

        mag2_type_raw = line[57]

        if mag2_type_raw == "W":
            mag2_type = "JMA moment" if line[0] == "J" else "JMA or others moment"
        else:
            mag2_type = mag_type_map.get(mag2_type_raw, None)

        travel = travel_time_map.get(line[58], None)
        hypo_eval = hypo_eval_map.get(line[59], None)
        eq_cause = eq_cause_map.get(line[60], None)
        max_intensity = max_intensity_map.get(line[61], None)
        disaster = disaster_scale_map.get(line[62], None)
        tsunami_raw = line[63]
        if year is not None and year.isdigit(): #isdigitで数値判別
            if int(year) <= 1988:
                tsunami = {
                    "1": "Tsunami detected by tide gauge, but no damage reported", 
                    "T": "Tunami"
                }.get(tsunami_raw, None)
            else:
                tsunami_scale_map = {
                    "1": "below 50cm",
                    "2": "around 1m",
                    "3": "around 2m",
                    "4": "around 4-6m",
                    "5": "around 10-20m",
                    "6": "above 30m",
                }
                tsunami = tsunami_scale_map.get(tsunami_raw, None)
        else:
            tsunami = None
        hypo_flag = hypo_flag_map.get(line[95], None)
    else:
        # mapping しない（素の値）
        mag1_type = line[54].strip() or None
        mag2_type = line[57].strip() or None
        travel = line[58].strip() or None
        hypo_eval = line[59].strip() or None
        eq_cause = line[60].strip() or None
        max_intensity = line[61].strip() or None
        disaster = line[62].strip() or None
        tsunami = line[63].strip() or None
        hypo_flag = line[95].strip() or None

    
    major_reg = line[64].strip() or None
    minor_reg = line[65:68].strip() or None

    region = line[68:92].strip() or None
    n_obs = line[92:95].strip() or None

    if output_format == 3:
        dt = build_datetime(year, month, day, hour, minute, second)
        if dt is not None:
            times = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        else:
            times = None

    rec = {
        "hypocenter reporting agency": agency,
        "year": year, "month": month, "day": day,
        "hour": hour, "minute": minute, "second": second, "second standard error": second_err,
        "latitude[degree]": lat_deg, "latitude[minute]": lat_min, "latitude[minute] standard error": lat_min_err,
        "longitude[degree]": lon_deg, "longitude[minute]": lon_min, "longitude[minute] standard error": lon_min_err,
        "depth[km]": depth, "depth[km] standard error": depth_err,
        "magnitude1": mag1, "magnitude1 type": mag1_type,
        "magnitude2": mag2, "magnitude2 type": mag2_type,
        "travel time tables": travel, "hypocenter evaluation": hypo_eval,
        "earthquake cause": eq_cause, "maximum seismic intensity": max_intensity,
        "disaster scale": disaster, "tsunami scale": tsunami,
        "major regional classification number": major_reg,
        "minor regional classification number": minor_reg,
        "epicenter region": region, "number of observation points": n_obs,
        "hypocenter determination Flag": hypo_flag
    }

    if output_format == 3:
        rec["daytime"] = times
        del rec["year"]; del rec["month"]; del rec["day"]
        del rec["hour"]; del rec["minute"]; del rec["second"]

        rec["latitude"] = lat_decimal
        rec["longitude"] = lon_decimal


        del rec["latitude[degree]"]
        del rec["latitude[minute]"]
        del rec["longitude[degree]"]
        del rec["longitude[minute]"]

    return rec

#=================================
def convert_file_to_csv(input_file, output_csv, append):
    mode = "a" if append else "w"
    with open(input_file, encoding="utf-8") as f, open(output_csv, mode, newline="", encoding="utf-8") as out:
        writer = None

        for line in f:
            line = line.rstrip("\n") #改行マークを削除
            if len(line) < 96:
                continue

            rec = parse_fixed_width_record(line)

            if writer is None:
                writer = csv.DictWriter(out, fieldnames=list(rec.keys())) #各行に辞書を書き込む
                if not append:
                    writer.writeheader() #ヘッダ行の書き込み

            writer.writerow(rec) #すべての行の書き込み
            
#=================================
if file_setting == 1:
    convert_file_to_csv(import_data, output_csv, append=False)
elif file_setting == 2:
    files = glob(os.path.join(import_data, "*"))
    for f in files:
        outcsv = os.path.splitext(os.path.basename(f))[0] + ".csv" #splitextで拡張子と拡張子以外に分ける
        convert_file_to_csv(f, outcsv, append=False)
elif file_setting == 3:
    files = glob(os.path.join(import_data, "*"))
    first = True
    for f in files:
        convert_file_to_csv(f, output_csv, append=not first)
        first = False
