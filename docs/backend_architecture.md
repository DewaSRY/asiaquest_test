# backend architecture 

My backend architecture is quite simple with minimal layer, it's contain "dto", "route", "service". in my opinion python already handle a lot of complexity for developer so it's not really need to do loot of boiler palets. 

then this is the brief explanation about the code structure 

```bash 
/app                           # App is the module/container for the source code 
    /dtos                      # dtos is a object contain what data received from the out side then what data wil return to the out side 
    /errors                    # errors is directory container of custom error                  
    /models                    # models is directory contain of database entity ('orm entity')
    /routes                    # routes is directory place to define end point, it's documentation and passing data to process 
    /services                  # services is directory to handle the business logic 
    /utils                     # utils is place to create reusable function 
    config.py                  # config is file use to load config variable from environment variable 
    database.py                # database is file use to define the database  connection 
    main.py                    # main is file of assemble the logic to a system 
```
