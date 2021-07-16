# LxBot Peek Client

仅供参考

## 配置环境
必选：
1. Python 3.7+ (?)
2. 安装第三方库：
   - PyQt5：`pip install PyQt5`
   - flask：`pip install flask`
   - pillow：`pip install pillow`
   - pywin32：`pip install pywin32`
3. 将 [frpc](https://github.com/fatedier/frp) 的可执行文件移至目录内

可选：
1. ui 文件需要使用 Qt Designer 设计
2. 编译到 exe 需要安装 pyinstaller：`pip install pyinstaller`

## 开始
运行 main.py

## 常用操作

### .ui 至 .py
```
pyuic5 xyz.ui -o xyz.py
```

### 编译到 exe
```
pyinstaller -F -w -n "LxBot Peek Client" -i .\src\icon.ico main.py
```