# 赛马娘(国服)育成事件助手

## 功能
+ [协助卡事件/育成事件]选项效果提示

## 效果如图
![本地图片](image/效果展示.png)

## 使用方法
+ 把整个output文件夹下载下来，双击main.exe就可以用了
+ 工具一开始会让你输入育成的角色名，输入名称的部分即可，工具会列出所有可能的候选名单。
  + 比如育成的是“超级溪流”，输入“溪流”即可。

## 注意
+ 使用前需要修改output/config.json中的“模拟器窗口名”字段，改为需要监听的模拟器窗口名
  + alt+tab 选择程序窗口的时候，左上角就是各自窗口的名字
+ 为了达到最好的效果，请把模拟器分辨率设置成竖屏720*1280分辨率
+ 工具开启后会自动调整模拟器窗口的大小，确保事件识别的正确率。开启后，就不要再手动拉伸窗口的大小了，会导致识别错误。
+ 不要最小化模拟器窗口，会导致识别出错。（不要最小化就行，被遮挡或者模拟器窗口不在最上层是没有影响的）
+ 工具打开的时候会有点慢，等待一会儿即可。
+ 开头会显示一些警告信息，无视即可。

## 识别问题
+ 如果出现识别不准确问题，大概率是识别区域位置偏移了，解决方法如下：
  + 打开config.json文件，把“校准模式”字段改成1，保存文件
  + 再次打开main.exe，就会进入校准模式，依次根据提示点击育成事件文字的显示区域，即可完成校准。
  + 然后再次打开main.exe，识别应该就没问题了。