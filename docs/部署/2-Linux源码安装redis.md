### 安装编译工具

```shell
sudo apt install build-essential
```

### 下载安装包并编译安装

```shell
wget https://download.redis.io/redis-stable.tar.gz

tar -xzvf redis-stable.tar.gz

cd redis-stable

#编译，这里开启10个线程，加快速度
make -j10
 
# 创建安装目录
mkdir /usr/local/redis

#自定义安装位置
make PREFIX=/usr/local/redis install 

#软链接到环境变量
ln -s /usr/local/redis/bin/* /usr/local/bin/
```

### 复制redis配置文件

```shell
mkdir /usr/local/redis/{conf,log} 
cp /usr/local/redis-stable/{redis.conf,sentinel.conf,redis-full.conf} /usr/local/redis/conf

cp -r /usr/local/redis-stable/utils /usr/local/redis/
```

### 配置守护进程

```shell
vim /etc/systemd/system/redis-server.service

[Unit]
Description=redis-server
After=network.target

[Service]
User=root
Group=root
#如果这里配置配置成守护进程，则配置文件中需要将守护进程的给关闭，否则会冲突
ExecStart=/usr/local/redis/bin/redis-server /usr/local/redis/conf/redis.conf

[Install]
WantedBy=multi-user.target
```

