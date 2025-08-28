

### 1.去官网下载安装包

  

下载链接：

  

<https://dev.mysql.com/downloads/>

  

![[Pasted image 20250820160851.png]]

  

### 2. 查看系统是否已经安装mysql

  

```bash

sudo dpkg --get-selections | grep mysql

```

  

如果有信息，将mysql卸载



```bash

sudo apt-get --purge remove mysql-serversudo 
apt-get --purge remove mysql-clientsudo 
apt-get --purge remove mysql-common
apt-get autoremove 
apt-get autoclean 
rm /etc/mysql/ -R 
rm /var/lib/mysql/ -R

```

  

### 3.安装MySQL依赖包libao

  

```bash
sudo apt install libnuma1  #mysql启动依赖库
sudo apt install libtinfo5 #mysql客户端连接依赖库
```



### 4. 创建MySQL安装目录和数据存放目录

  

```

mkdir /usr/local/mysql

mkdir /usr/local/mysql/mysqldb

```

  

### 5. 创建MySQL组：创建MySQL用户，并设置密码。

  

```bash

sudo useradd mysql

sudo passwd mysql

```

  

### 6. 将mysql目录的权限授给mysql用户和mysql组。

  

```bash

chown -R mysql:mysql /usr/local/mysql

```

  
  

### 7.上传解压安装包

  

```bash

cd /usr/local/mysql

  

tar -xvf mysql-8.0.24-linux-glibc2.12-x86_64.tar.xz

  
#将mysql-8.0.27-el7-x86_64目录下的所有文件移动到/usr/local/mysql目录下
mv mysql-8.0.24-linux-glibc2.12-x86_64/* ./ 
  
 #解压完后可以将mysql-8.0.24-linux-glibc2.12-x86_64目录和压缩包删除
rm -rf mysql-8.0.24-linux-glibc2.12-x86_64.tar.xz mysql-8.0.24-linux-glibc2.12-x86_64

```

  

### 9.给mysql目录授权

  

```

chmod -R 777 /usr/local/mysql

chmod -R 777 /usr/local/mysql/mysqldb/

```

  

### 10.在系统根目录的/etc创建MySQL的安装初始化配置文件my.cnf

  

**创建my.cnf文件**

  

```bash

vim /etc/my.cnf

```

  

**内容如下：**

  

```bash

[mysqld]

# 设置3306端口

port=3306

# 设置mysql的安装目录

basedir=/usr/local/mysql

# 设置mysql数据库的数据的存放目录

datadir=/usr/local/mysql/mysqldb

# 允许最大连接数

max_connections=10000

# 允许连接失败的次数。这是为了防止有人从该主机试图攻击数据库系统

max_connect_errors=10

# 服务端使用的字符集默认为UTF8

character-set-server=utf8

# 创建新表时将使用的默认存储引擎

default-storage-engine=INNODB

# 默认使用“mysql_native_password”插件认证

default_authentication_plugin=mysql_native_password

[mysql]

# 设置mysql客户端默认字符集

default-character-set=utf8

[client]

# 设置mysql客户端连接服务端时默认使用的端口

port=3306

default-character-set=utf8

```

  

### 11.安装MySQL8.0.22

  

**1、进入MySQL安装目录的bin目录下**

  

```bash

 cd /usr/local/mysql/bin

```

  

**2、执行命令，并记住随机密码**

  

```bash

 ./mysqld --initialize --console

```



  

### 12.启动MySQL服务

  

```bash

1、cd /usr/local/mysql/support-files #进入support-files

2、./mysql.server start #启动mysql服务

```

  

**PS: 此处容易出现的问题：**

  

**1、启动MySQL服务时报 my_print_defaults：未找到命令错误。**

  

![img](https://img2020.cnblogs.com/blog/2254101/202012/2254101-20201218125837464-1071358648.png)

  

**解决方法：**检查并修改 /etc/my.cnf 中的 MySQL的安装目录！

  

![img](https://img2020.cnblogs.com/blog/2254101/202012/2254101-20201218125837464-1071358648.png)

  

```

检查my.cnf文件中的mysql安装目录的地址是否与创建的一致，如果不一致改成MySQL的安装目录。

```

  

**2.报without updating PID file错误**

  

![img](https://img2020.cnblogs.com/blog/2254101/202012/2254101-20201218125859858-2096286127.png)

  

**解决办法：**

  

```shell

该问题出现的原因是解压mysql的tar包文件，权限不够。只需要重新授权即可：

chmod -R 777 /usr/local/mysql

chmod -R 777 /usr/local/mysql/mysqldb

```

  

### 13.将MySQL加入系统进程中

  

```shell

1、cp mysql.server /etc/init.d/mysqld

  

然后重启MySQL服务：

2、service mysqld restart

```

  

### 14.创建一个软连接到 /usr/bin。--一定要执行成功，否则启动不了！

  

```shell

ln -s /usr/local/mysql/bin/mysql /usr/bin

```

  

![img](https://img2020.cnblogs.com/blog/2254101/202012/2254101-20201218125926121-1875525707.png)

  

PS：

  

```

由于/usr/bin已经添加到环境变量PATH中了，只需要将mysql的软连接添加到/usr/bin即可全局访问

```

  

### 15.修改登录密码

  

```shell

mysql> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '新密码';

```

  

![img](https://img2020.cnblogs.com/blog/2254101/202012/2254101-20201218125948772-1145767685.png)

  

### 16.设置允许远程登录

  

```

1、mysql> use mysql;

2、mysql> update user set user.Host='%' where user.User='root';

  

3、mysql> flush privileges;

```

  

![img](https://img2020.cnblogs.com/blog/2254101/202012/2254101-20201218130007356-2050794506.png)

  

**退出MySQL：**

  

```

mysql> quit;

```

  

**重启MySQL服务：**

  

```

service mysqld restart

```

  

**检查3306端口是否开放**

  

```bash

ss -tunlp | grep 3306

```


**至此MySQL安装完成！**