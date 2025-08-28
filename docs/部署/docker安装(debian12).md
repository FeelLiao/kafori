
[debian 12 基于清华源安装docker - 老猿新码 - 博客园](https://www.cnblogs.com/netcore3/p/18281305)


清华源docker地址:

```bash
https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/debian/
```

安装docker之前需要添加 GPG 公钥，主要是用来验证安装文件是否被篡改，先安装工具：curl和gnupg2，两个工具。

```bash
apt install curl gnupg2
```

下面是清华源GPG地址，下载和添加。

```bash
curl -fsSL https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/debian/gpg |apt-key add -
```

配置清华源

```bash
vim /etc/apt/sources.list
```

在尾部添加清华源，bookworm代表debian12。stable代表发布分支，主要有三个：`stable`（稳定版）、`testing`（测试版）和 `unstable`（不稳定版）。

```shell
deb https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/debian bookworm stable
```

更新库，然后安装

```bash
sudo apt update  && sudo apt install docker-ce
```

