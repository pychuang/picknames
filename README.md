# picknames
取中文名字

# Installation

## Windows

從 https://www.python.org/downloads/ 下載並安裝 python 3.x

打開 command prompt，執行

```
py -m pip install Pmw
```

# Usage

## 先執行選字程式

```
pickwords.py
```

這個程式會產生一個檔案

* words-selected.pkl: 選上的字，pickle 格式

## 再執行選名字程式

有兩個選名字的方法

* 選擇所有的排列組合

```
picknames.py
```

* 先選拼音組合，再選擇選漢字組合

```
picknames2.py
```

這兩個程式都使用 pickwords.py 產生的 words-selected.pkl 作為輸入

這兩個程式會產生的檔案

* names-selected.txt: 選上的名字
* names-refused.txt: 不要的名字
