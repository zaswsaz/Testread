### Control Points API

`POST https://testread-zaswsaz.vercel.app/controlpoints.py`

    'Accept: text/plain'
    'Content-Type: text/csv'

### Input

Post body should be input data in CSV format. First threelines are parameters also in CSV format. 

- sValue
- eValue
- Seasonality, The time period to compare against.

```
sValue,.99
eValue,40
Seasonality,7
```    
    
These may be ommited in which case default values will be used.

[Params are followed by data as shown in example input.](https://github.com/zaswsaz/Testread/blob/main/Input.csv)

### Output

Output is JSON style string

    {
        "Change Point": {                       #full list of values for respective dates, populated by zeroes if no change point detected to aid with graphing
             "Date": value
        },
        "Change Points Only": {                 #only dates of change points with respective values
            "Change Point": {
                "Date": value
            }
        },
        "Ev": {                                 #expected value for respective dates
            "Date": value
        },
        "LCL": {                                #lower control limit value for respective dates
            "Date": value
        },
        "Moving Average": {                     #moving average value for respective dates
            "Date": value
        },
        "UCL": {                                #upper control limit value for respective dates
            "Date": value
        },
        "Value": {                              #user input value for respective dates
            "Date": value
        }
    }
