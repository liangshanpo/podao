# 朴刀 podao
一把朴刀开局。
朴刀是一个 Python 项目搭建脚手架，组合使用 pyenv、venv 和 pip 等工具搭建虚拟环境、分组依赖包。

Podao is an python project environment setup tool, it combines pyenv, venv, pip to ease the work to build an isolated environment for python project.




![朴刀](https://github.com/imlzg/image/blob/6c2dcdd72ddbfb4174733e8dae6f3043e472788f/podao.jpg)


朴刀是一种刀身窄长、刀柄较短的刀，装上“杆棒”后变为枪，名为朴刀枪，以“搠、刺”为主。

朴刀在《水浒传》里广为人知，印象里朴刀都很长，这是错的；正确的定义是：朴刀短柄，柄中空，是单手持握的短兵器，特点在于刀柄中空，旋入一根哨棒就可以当做长兵器使用，故尔武松等人都习惯手持哨棒，腰配朴刀，如此两件兵器可以在需要时合二为一，就像 pyenv 和 venv 一样。

如：“卢俊义取出朴刀，装在杆棒上，三个了丫儿扣牢了，赶著车子奔梁山泊路上来”。




### 优势 advantage
-使用 pyenv、venv 和 pip 搭建项目，零学习成本；
-使用文件夹名作为 shell session 提示符，无随机字符、好看、有意义；
-使用 pyproject.toml 和 requirements.txt 文件描述项目，不造轮子、零侵入；




### 局限 weakness
podao 只解决虚拟环境的搭建和依赖包的分组的问题，更具体的项目配置需要手动更改 pyproject.toml 文件。



### pyenv
pyenv 用于管理项目环境的 python 版本，要使用 podao 需事先安装 pyenv，参考[官网](https://github.com/pyenv/pyenv)。

#### pyenv installation
pyenv 的安装配置稍显复杂，安装过程可分 3 步：
1. 安装 pyenv 依赖，包括 `git`，[wiki](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)
2. 安装 pyenv，[wiki](https://github.com/pyenv/pyenv-installer)
3. 配置 pyenv 环境，[wiki](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv)

有人将安装过程封装成了[安装脚本](https://github.com/zaemiel/ubuntu-pyenv-installer)，目前只有 Ubuntu 版。




### 安装 install
```shell
pip install podao
```


一般将 podao 安装在系统环境，也可以安装在虚拟环境：

#### 安装在系统环境
1. 切换到项目路径
2. 执行 `podao init .`

#### 安装在虚拟环境
1. 激活安装有 podao 的虚拟环境
2. 切换到项目路径
3. 执行 `podao init .`
4. 退出安装有 podao 的虚拟环境 `deactivate`
5. 激活项目虚拟环境 `source bin/activate`




### 示例 examples

#### 创建项目环境
```shell
pd init . 3.10.4
pd init ~/workspace/project_name 
```

#### 安装软件包
```shell
pd install pytest -d
pd install 'ReportLab>=1.2' -g pdf
```

#### 卸载软件包
```shell
pd uninstall requests
```

#### 创建快照
```shell
pd freeze
pd freeze -a
pd freeze -d
pd freeze -g pdf

```



### 使用 usage
#### pd init dir [python] [-ide]
`pd init` 命令使用 dir 目录和 python 版本创建虚拟环境，包括 src、test、pyproject.toml、LICENSE、README.md和.gitignore。使用目录名作为项目名、当前系统用户作为author、MIT 为默认 LICENSE、当前年份和系统用户作为 LICENSE 时间和用户。
- `dir` - 项目目录，必填项，使用 `.` 表示当前目录
- `python` - python 版本号，如果不指定 python，则使用当前系统安装的最高版本的python
- `-ide` - 如果指定 IDE 会生成 IDE 的配置文件，目前仅支持 vscode



#### pd install packages
`pd install` 命令使用当前虚拟环境的 `pip install -U` 命令安装 packages 所指定的包，并将包添加到 pyproject 的相应依赖组中。
- `-d` - 将软件包添加到 `optional-dependencies` 表的 `dev` 组
- `-g` - 将软件包添加到 `optional-dependencies` 表的指定的组
- 不使用选项，将软件包默认安装到 dependencies 表



#### pd uninstall packages
`pd uninstall` 命令使用 `pip uninstall` 命令卸载 packages 所指定的包



#### pd freeze
`pd freeze` 命令结合 `pip freeze` 和 `pyproject.toml` 生成当前系统所需的软件包的版本快照到 `requirements.txt` 文件，然后使用 `pip install -r requirements.txt` 命令安装即可。
- `-d` - 创建 dev 依赖和主依赖的版本快照
- `-a` - 创建所有依赖的版本快照
- 不适用选项，将创建主依赖的版本快照



#### source bin/activate
激活虚拟环境，会在 shell 提示符左侧显示当前虚拟环境的名字，即虚拟环境文件夹的名字。



#### pip install -r requirements.txt
将通过 requirements.txt 文件定义的虚拟环境快照按照到当前环境。




### License
[MIT](LICENSE) © Li zhigang