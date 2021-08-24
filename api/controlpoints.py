from http.server import BaseHTTPRequestHandler
import csv
import json
import pandas as pd
import io
import cgi


class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        
        
        length = int(self.headers.get('content-length'))
        data = self.rfile.read(length).decode('utf-8')    
        param_number = check_Data(data)
        if isinstance(param_number, str):
            self.send_response(404)
            output = "incorrect data formating in <" + param_number + "> line, must be CSV format: 2 values for parameters and 3 values for data"
            Length = len(output)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length",  Length)
            self.wfile.write(output.encode("utf-8"))
            
        else:   
            output = json.dumps(do_math(data,param_number), indent=4, sort_keys=True, default=str)
            Length = len(output)
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.send_header('Content-length', Length)
            self.end_headers()
            self.wfile.write(output.encode('utf-8'))
            
        

def create_Offset(s):    # creates list of 0s equivalent to seasonality parameter for offsetting data
      i = 0
      s_offset = []
      while i < s:
          s_offset.append(0)
          i=i+1
      return s_offset 

def check_Data(data):   # checks recieved data for correct formating and returns either error string line or int amount of parameters
    stri= io.StringIO(data)
    num_params = int(0)
    while True:
        n1 = stri.readline()
        if len(n1.split(',')) < 2 or len(n1.split(',')) > 3:
            return n1
        if len(n1.split(',')) == 2:
            num_params = num_params + 1
        else:
            break    
    return num_params

def do_math(data,param_number): #does data calculation returns dictionary of output
    
    
    input_dic = {'Data' : [] , 'Parameters' : []}
    fieldnames = ("Param", "Value")
    reader = csv.DictReader( data.splitlines(), fieldnames)
    
    i = 0
    while i < param_number:
        input_dic['Parameters'].append(next(reader))
        i = i + 1
    fieldnames = ('Date','Hour','Value')
    
    reader = csv.DictReader( data.splitlines(), fieldnames)
    
    for i, row in enumerate(reader):
        if i >= param_number:
             input_dic['Data'].append(row)
        
    params =  input_dic.pop('Parameters')
    
    df2 = pd.DataFrame()
    df = pd.json_normalize(input_dic, record_path=['Data'])
    df['Value'] = pd.to_numeric(df['Value'], downcast="float")
    df['Date'] = pd.to_datetime(df['Date'], errors='ignore')
    df = df.drop('Hour', axis=1)
    df = df.resample('d', on='Date').mean()
    
    
    if param_number == 0:
        statistical_band = .995 / 100
        eV_threshold_percent = 40 / 100
        seasonality = 7
    if param_number == 1:
        statistical_band = float(params[0]["Value"]) / 100
        eV_threshold_percent = 40 / 100
        seasonality = 7
    if param_number == 2:
        statistical_band = float(params[0]["Value"]) / 100
        eV_threshold_percent = int(params[1]["Value"]) / 100
        seasonality = 7
    if param_number == 3:
        statistical_band = float(params[0]["Value"]) / 100
        eV_threshold_percent = int(params[1]["Value"]) / 100
        seasonality = int(params[2]["Value"])
        if seasonality > len(df.index)/ 2:
            seasonality = round(len(df.index)/2)
    
    
    eV_threshold = eV_threshold_percent * df['Value'].mean()
    
    Moving_average = list(create_Offset(seasonality))
    m1 = 1
    m2 = seasonality

    for q in df['Value'][seasonality:]:
        Moving_average.append(df['Value'][m1:m2].quantile(q=0.5))
        m1 += 1
        m2 += 1
    
    df["Moving Average"] = Moving_average
    
    UCL = list(create_Offset(seasonality))
    LCL = list(create_Offset(seasonality))
    p2 = 0
    p3 = seasonality

    for i in df['Value'][seasonality:]:
        UCL.append(df['Value'][p2:p3].quantile(q=0.5 + (statistical_band / 2)))
        LCL.append(df['Value'][p2:p3].quantile(q=0.5 - (statistical_band / 2)))
        p2 += 1
        p3 += 1
    
    df["UCL"] = UCL
    df["LCL"] = LCL
    
    EV = list(create_Offset(seasonality))
    j = 0
    o1 = 0
    o2 = seasonality
    
    for j in df['Value'][seasonality:]:
        if (UCL[o1] - df['Value'][o2]) > 0:
            EV1 = 0
        else:
            EV1 = df['Value'][o2] - UCL[o1]
        if (df['Value'][o2] - LCL[o1]) > 0:
            EV2 = 0
        else:
            EV2 = df['Value'][o2] - LCL[o1]
    
        if EV1 != 0:
            EV.append(EV1)
        else:
            EV.append(EV2)
        o1 += 1
        o2 += 1
    
    df["EV"] = EV
    
    EV_normalized = []
    
    for i in EV:
        if abs(i) < eV_threshold:
            EV_normalized.append(0)
        else:
            EV_normalized.append(i)
    
    Change_points = [0]
    z = 1
    
    for b in EV_normalized[1:]:
        if EV_normalized[z] * EV_normalized[z-1] <= 0 and EV_normalized[z] != EV_normalized[z-1] and EV_normalized[z-1] == 0:
            Change_points.append(Moving_average[z])
        else:
            Change_points.append(0)
        z += 1
        
    df["Change Point"] = Change_points
    total_change_points = 0
    
    for i in Change_points:
        if i != 0:
            total_change_points += 1
           
    simDate = []
    simChange_point = []
    simDates = df.index.tolist()
    simValues = df['Change Point'].tolist()
    
    i = 0
    for l in simValues:
        if simValues[i] > 0:
            simDate.append(simDates[i])
            simChange_point.append(simValues[i])
        i = i + 1
             
    df2["Date"] = simDate
    df2["Change Point"] = simChange_point
    df2["Date"]= df2["Date"].dt.strftime('%Y-%m-%d')
    df2.set_index('Date',inplace=True)
    df.index = df.index.strftime(('%Y-%m-%d'))
    D_t = df.to_dict()
    Chp = df2.to_dict()
    output = D_t
    output["Change Points Only"]= Chp
    
    return output


