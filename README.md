# picknames
取中文名字

# Usage

## 先執行選字程式

```sh
$ ./pickwords.py
```

這個程式會產生兩個檔案

* words-selected.pkl: 選上的字，pickle 格式 （pickwords.py 下次執行時會載入這個檔案）
* words-selected.txt: 選上的字，純文字格式 （picknames.py 的輸入）

## 再執行選名字程式

```sh
$ ./picknames.py
```

這個程式需要 pickwords.py 產生的 words-selected.txt

這個程式會產生兩個檔案
* names-selected.txt: 選上的名字 （picknames.py 下次執行時會載入）
* names-refused.txt: 不要的名字 （picknames.py 下次執行時會載入）
