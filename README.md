# 姿勢偵測系統

作者：翁嘉沅、孫逸平

---

此程式為 Tsukuba Science Edge 2024 及 113年青少年科學人才培育計畫所需。

這是一個可以偵測受測者姿勢相關數據，並依據數據繪製折線圖的程式。主要是拿來偵測受測者的不良姿勢，包含：駝背、頭前伸、高低肩、圓肩。

## 系統要求
* python3
* python module
  * tkinter
  * cv2
  * PIL
  * time
  * mediapipe
  * math
  * argarse
  * matplotlib

## 程式執行指南

### 執行程式

在終端機輸入以下指令，即可執行程式

```
  python3 videoCapture_with_tk_test.py
```

### 提供其他可調參數

可以透過添加以下參數，設定更多詳細數據

1. `--help`：查看參數調整說明
2. `--textSize`：調整圖片中標示數字的文字大小，預設為：2
3. `--textBold`：調整圖片中標示數字的文字粗細，預設為：5
4. `--cameraWidth`：調整畫面寬度（攝影機寬度），預設為：1280（單位：px）
5. `--cameraHeight`：調整畫面高度（攝影機高度），預設為：720（單位：px）
6. `--detectType`：調整偵測模式，預設為：2（駝背：0，頭前伸：1，高低肩：2，圓肩：3）
7. `--detectSide`：調整偵測方向，預設為：L（左：L，右：R）
8. `--correctDistance`：設定正確姿勢時的距離，預設為：200（單位：px），限駝背及圓肩使用
