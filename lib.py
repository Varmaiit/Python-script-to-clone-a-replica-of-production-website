import json, jinja2, shlex
from subprocess import call, check_output, Popen, PIPE
from shovel import task



with open('config.json') as data_file:  
    CONFIG = json.load(data_file)


@task
def create_test_db_from_backupfile(dbName, tldName = "cvarma.com", sqlDumpFilePath = CONFIG['sqlDumpFilePath'],  hostName = CONFIG['hostName'] , mysqlUserName = CONFIG['mysqlUserName'], mysqlPassword = CONFIG['mysqlPassword'] ):
    
    '''This command will create dev db from backup sql file.
    
    It takes 6 arguments, Only one is mandatory:
    -- dbName = test
    -- tldName = cvarma.com
    -- sqlDumpFilePath  = /home/ubuntu/livebackup.sql  
    - userName = root
    - password = password
    - hostName = localhost

    

    
    Examples:
        shovel lib.create_test_db_from_backupfile test 
        shovel lib.create_test_db_from_backupfile --dbName=test --tldName=cvarma.com --sqlDumpFilePath= /home/ubuntu/livebackup.sql

        Both of those examples above are identical
        Each of those examples should create a devdb from sql file
    
    
    '''
    
    ##
    #  def mysql_create_db   $> mysql -u root -pxxxxxxx -h localhost -e "CREATE DATABASE test;"
    mysqlDatabase = "mysql -u {userName} -p{password} -h {hostName} -e \"CREATE DATABASE IF NOT EXISTS {dbName};\"".format(userName = userName, password = password, dbName = dbName, hostName = hostName)
    print(check_output("{mysqlDatabase}".format(mysqlDatabase = mysqlDatabase), shell=True))

    # def mysql_import_db $> mysql -u username -pxxxxxxxx test <  
    mysqlImportdb = "mysql -u {userName} -p{password} {dbName} < {sqlDumpFilePath.sql}".format(userName = userName, password = password, dbName = dbName, sqlDumpFilePath = sqlDumpFilePath)
    print(check_output("{mysqlImportdb}".format(mysqlImportdb = mysqlImportdb), shell=True))

    # def mysql_grant_file_on_*_to_user $> mysql -u root -pxxxxxxxxxxxxx -h localhost -e "GRANT FILE ON *.* TO 'root'@'localhost';"
    mysqlGrantFile = "mysql -u {userName} -p{password} -h {hostName} -e \"GRANT FILE  ON *.* TO '{mysqlUserName}'@'{hostName}';\"".format(userName = userName, password = password, hostName = hostName, mysqlUserName = mysqlUserName, mysqlPassword = mysqlPassword, dbName = dbName)
    print(check_output("{mysqlGrantFile}".format(mysqlGrantFile = mysqlGrantFile), shell=True))

    # def mysql_grant_privileges_on_db_to_user $> mysql -u root -pxxxxxxx -h localhost -e "GRANT ALL PRIVILEGES ON test.* TO 'root'@'localhost';"
    mysqlGrant = "mysql -u {userName} -p{password} -h {hostName} -e \"GRANT ALL PRIVILEGES ON {dbName}.* TO '{mysqlUserName}'@'{hostName}';\"".format(userName = userName, password = password, hostName = hostName, mysqlUserName = mysqlUserName, mysqlPassword = mysqlPassword, dbName = dbName)
    print(check_output("{mysqlGrant}".format(mysqlGrant = mysqlGrant), shell=True))

    # def mysql_flush_privileges $> mysql -u root -pxxxxxxxxxxxxx -h localhost -e "FLUSH PRIVILEGES;"
    mysqlPrivileges = "mysql -u {userName} -p{password} -h {hostName} -e \"FLUSH PRIVILEGES;\"".format(userName = userName, password = password, hostName = hostName)
    print(check_output("{mysqlPrivileges}".format(mysqlPrivileges = mysqlPrivileges), shell=True))


@task
def clone_new_dev_instance(devName, tldName = CONFIG['tldName'], userName = CONFIG['userName'], hostName = CONFIG['hostName'] , mysqlUserName = CONFIG['mysqlUserName'], 
                                mysqlPassword = CONFIG['mysqlPassword'],  WebAppGitRemotePath =  "https://github.com/example/example.git"):
    '''This command will clone a new dev into /var/www/

    It takes 7 arguments, 1 argument is mandatory and the rest has been taken from default parameter in config.json file:
    -- devName = "test1"  
    -- tldName = "cvarma.com"    
    -- userName = "ubuntu"
    - hostName = "localhost"
    - mysqlUsername = "root"
    - mysqlPassword = "password"
    - WebAppGitRemotePath =  "https://github.com/example/example.git"


    
    Examples:
        shovel lib.clone_new_dev_instance test1 ubuntu
        shovel lib.clone_new_dev_instance --devName=test1 -- userName=ubuntu

        Each of those examples should create a new dev in 
        /var/www/test1/public_html

    '''

    ## dbName has to be same as devName, But it's not mandatory
    dbName = devName

    ## devNginxRootpath is the root folder where your repo gets cloned.
    devRootPath = "/var/www/{devName}".format(devName = devName)
    devNginxRootPath = devRootPath + "/public_html"

    ##
    # Creating directory for new dev in /var/www/{devName}/
    print(check_output("mkdir -p {devRootPath}".format(devRootPath = devRootPath), shell=True))

    ##
    # Cloning the website's git repository into root folder
    print(check_output("git clone {WebAppGitRemotePath} {devNginxRootPath}".format(WebAppGitRemotePath = WebAppGitRemotePath, devNginxRootPath = devNginxRootPath), shell=True))

    # Using server side templating using jinja 2
    # Rendering  robots.txt, conf.d files for nginx according to the website hostname 
    # One may also include other files in template which need to be specifically render according to the website hostname
    templatePath = "/home/{userName}/.shovel/templates/".format(userName = userName)
    templateLoader = jinja2.FileSystemLoader( searchpath = templatePath )
    templateEnv = jinja2.Environment( loader=templateLoader )

    ##
    #Render dev robots.txt
    devRobotsTxtTemplate = templateEnv.get_template("dev.robots.txt")
    devRobotsTxtTemplateVars = {}
    devRobotsTxtOutputPath = devNginxRootPath + "/robots.txt"
    devRobotsTxtOutputText = devRobotsTxtTemplate.render(devRobotsTxtTemplateVars)
    with open(devRobotsTxtOutputPath, "wb") as fh:
        fh.write(devRobotsTxtOutputText)
    print("printed out robots.txt to {devRobotsTxtOutputPath}".format(devRobotsTxtOutputPath = devRobotsTxtOutputPath))   

    ##
    # Render dev conf.d
    confFile = "cg2-{devName}.conf".format(devName = devName, tldName = tldName)
    devConfTemplate = templateEnv.get_template("cg2-dev-http.conf")
    devConfTemplateVars = {"devName" : devName,
                           "tldName" : tldName}
    devConfOutputPath = "/etc/nginx/conf.d/" + confFile
    devConfOutputText = devConfTemplate.render(devConfTemplateVars)
    with open(devConfOutputPath, "wb") as fh:
         fh.write(devConfOutputText)
    print("printed out cg2-dev.conf to {devConfOutputPath}".format(devConfOutputPath = devConfOutputPath))


    ## One may also change the permissions depending on the requirements, also one may also change the type of permission
    
    # change Perm PermChngFolder
    # devPermChngFolderFolder = devNginxRootPath + "/name_of_the_folder_whoose_permissions_need_to_be_changed"
    # chmodPermChngFolder = "sudo chmod -R 777 {devPermChngFolderFolder}".format(devPermChngFolderFolder = devPermChngFolderFolder)
    # changePermPermChngFolder = "sudo chown -R www-data:www-data {devPermChngFolderFolder}".format(devPermChngFolderFolder = devPermChngFolderFolder)
    # print(check_output("{chmodPermChngFolder}".format(chmodPermChngFolder = chmodPermChngFolder), shell = True))
    # print(check_output("{changePermPermChngFolder}".format(changePermPermChngFolder = changePermPermChngFolder), shell = True))    


    ##
    # Resart the nginx 
    restartNginx = "sudo systemctl restart nginx"
    print(check_output("{restartNginx}".format(restartNginx = restartNginx), shell=True))



@task
def teardown_dev(devName, tldName = CONFIG['tldName'], hostName = CONFIG['hostName'] , mysqlUserName = CONFIG['mysqlUserName'], mysqlPassword = CONFIG['mysqlPassword']):
    
    '''This command will delete complete testing website, helpful incase you have too many testing websites

    It takes 5 arguments, 2 (devName, tldName) arguments are mandatory:
    -- devName = "test1" 
    -- tldName = "cvarma.com"    
    - hostName = "localhost"
    - mysqlUsername = "root"
    - mysqlPassword = "password"



    
    Examples:
        shovel lib.teardown_dev test 
        shovel lib.teardown_dev --devName=test --devName=cvarma.com

        Each of those examples should create a new dev in 
        /var/www/test/public_html

    '''
    dbName = devName

    devRootPath = "/var/www/{devName}".format(devName = devName)

    ##
    # Delete folder in nginx root folder
    print(check_output("sudo rm -rf {devRootPath}".format(devRootPath = devRootPath), shell=True))
    print("deleted {devName} folder www folder".format(devName = devName))

    ##
    # Delete specific conf.d file
    confFile = "cg2-{devName}.conf".format(devName = devName)
    devConfOutputPath = "/etc/nginx/conf.d/" + confFile
    print(check_output("sudo rm -rf {devConfOutputPath}".format(devConfOutputPath = devConfOutputPath), shell=True))
    print("delted {devName} specific conf file from conf.d folder ".format(devName = devName))


    ##
    #  def mysql drop database   $> mysql -u root -pxxxxxxxxx -h localhost -e "DROP DATABASE IF EXISTS dbName;"
    mysqlDatabase = "mysql -u {mysqlUser} -p{password} -h {hostName} -e \"DROP DATABASE IF EXISTS {dbName};\"".format(mysqlUser = mysqlUser, password = password, dbName = dbName, hostName = hostName)
    print(check_output("{mysqlDatabase}".format(mysqlDatabase = mysqlDatabase), shell=True))


    ##
    # Resart the nginx 
    restartNginx = "sudo systemctl restart nginx"
    print(check_output("{restartNginx}".format(restartNginx = restartNginx), shell=True))