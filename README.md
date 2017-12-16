## Python script to clone a replica of production website and host it as a sub domain.
Make a replica and host a production website for testing using shovel (which turns python functions into tasks)


## Prerequisites for this python script to work
1. Unix based web server which also includes nginx
1. Python 2.7 Installed
1. Install shovel [Instructions to install Shovel](https://github.com/seomoz/shovel#installing-shovel)
1. Add the DNS for your testing website on you


## This repo contains 3 shovel tasks
1. create_test_db_from_backupfile -- Creates a new test database from backup sql file
1. clone_new_dev_instance  -- Clone the project repository on the web server.
1. teardown_dev  -- Delete the testing website and its related conf files in case you don't need it 


[Instructions to install Shovel](https://github.com/seomoz/shovel#installing-shovel)

 
