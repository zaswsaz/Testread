### Control Points API

`POST /thing/`

    'Accept: text/plain'
    'Content-Type: text/csv'

### Input

Post body should be input data in CSV format. First threelines are parameters.

- sValue
- eValue
- Seasonality

[Followed by data as shown in example input.](https://github.com/zaswsaz/Testread/blob/main/Input.csv)

    {"id":1,"name":"Foo","status":"new"}
