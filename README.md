# Robot-Runner

## Introduction
使用Python Click Library將Run Robot這個步驟包起來，能夠更彈性且方便的做想做的操作，
例如: 跑完測試之後想retry failure的case，不需另外下指令，
或者是跑完測試後，可以Call API到測試管理工具或Youtrack，
希望透過此工具達成所有流程自動化的目標。


## Configuration
將respository clone專案同一層目錄
```
$ cd <your-folder> 
$ git clone https://gitlab.com/harvey.you-ce/robot-runner.git
$ ls
.
  |-- <first_project>
  |-- <second_project>
  |-- robot-runner
```
在專案目錄裡放置config.json檔案
```
$ cd <first_project>
$ ls
.
  |-- .robot-runner
  |    `-- config.json
```
config.json
```
{
    "sub_project": [{
        "testing_type": "web",
        "name": "web",
        "path": "automation/integration/web",
        "tag": "web",
        "type": "robot"
    }]
}
```
請將path指到你的Test Case目錄，runner會藉由tag，來抓取path

一切都設定完成後，目錄結構大概會長這樣
```
.
  |-- <first_project>
  |   |-- .robot-runner
  |   |    `-- config.json
  |   |-- automation
  |   |   |-- integration
  |   |   |   |-- web
  |   |   |        `-- test_login.robot
  |   |   |   |-- api
  |   |   |        `-- api_login.robot
  |-- robot-runner
```

## Run robot-runner
跑指定測試檔案
```
python .\robot-runner\ run -P <project_name> -i <tag> -O -s=test_login
```
跑指定測試案例
```
python .\robot-runner\ run -P <project_name> -i <tag> -O -t="Login Should Success"
```
其他指令用法
```
-P 專案資料夾的名字
-r 當測試失敗時，需要重跑測試的次數，預設為2，總共會跑三次
-O 使用robot預設的指令，可以使用robot --help查看有哪些指令
-i 輸入你所設定config.json裡的特定tag，會透過tag抓取測試資料夾的位置
```
