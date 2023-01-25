# AssignmentFamPay
There are 2 components to this project. 1st the fetchvideo.py which basically fetches the latest video based on a query. 2nd is responsible for facilitating
the customer api requests. Hence there are two docker files one for setting up each container. There will be an instance of MySql db needed. Also run the create_databse.sql to create database in the mysql instance.

Preparing the ./script/config.json
You need to enter the details of database such as the host ip, port etc. Also you need to enter the API keys for the youtube apis. If you have two keys then 
you have to create 2 enteries ex. "API_TOKN_1":"asdasda","API_TOKN_2":"ASdasdfr".
