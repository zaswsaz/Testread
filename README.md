### Control Points API

`POST /thing/`

    'Accept: text/plain'
    'Content-Type: text/csv'

### Input

    Post body should be input data in CSV format. First threelines are parameters.

    - sValue
    - eValue
    - Seasonality

    [Followed by data as shown in example input.](

    {"id":1,"name":"Foo","status":"new"}
