# Construction Subscriber
Tracking the construction progress of 大華昇耕

## Features
- 訂閱 Line notify 即可收到大華昇耕官方網站工程進度更新資訊

## Architecture
<p align="center">
  <img src="img/delpha_crawling.jpg" alt="delpha_carwling"/>
</p>

1. Cloud Scheduler 每日排程定期觸發 Cloud Functions
2. Cloud Functions 抓取大華昇耕工程進度官方網站 html 檔，並儲存於 Cloud Storage
3. Cloud Functions 比對當天與前一天的 html 檔內容
4. 透過 Line notify 通知訂閱戶是否有工程進度更新


## Demo
<dl>
  <dt>1. 大華昇耕官方網站更新工程進度</dt>
  <dd align="center">
      <img src="img/line_notify_with_updates.jpeg" width="350" alt="line_notify_with_updates"/>
  </dd>
  <dt>2. 大華昇耕官方網站無更新工程進度<dt>
  <dd align="center">
      <img src="img/line_notify_no_progress.jpeg" width="350" alt="line_notify_no_progress"/>
  </dd>
</dl>