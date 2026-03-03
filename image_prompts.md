# 訪問看護ステーション経営シミュレーション 画像生成プロンプト集

## 推奨設定
- **解像度**: 1920x1080 (背景) / 512x768 (キャラクター)
- **スタイル**: Photorealistic, Japanese setting
- **ネガティブプロンプト**: cartoon, anime, illustration, low quality, blurry

---

## 1. 背景画像

### bg_station_office.png - 訪問看護ステーション オフィス
```
Japanese home nursing station office interior, modern medical office,
several desks with computers, medical charts on walls, bright and clean atmosphere,
white walls, fluorescent lighting, filing cabinets, medical supplies shelf,
whiteboard with schedule, photorealistic, professional workplace,
warm and welcoming atmosphere, Japan
```

### bg_station_meeting.png - カンファレンスルーム
```
Japanese medical office meeting room, conference table with chairs,
whiteboard with patient care plans, medical professionals discussion,
projector screen, clean modern interior, bright lighting,
photorealistic, Japan healthcare setting
```

### bg_patient_living.png - 患者宅リビング
```
Japanese elderly person's living room, traditional Japanese house interior,
low table (kotatsu), tatami mats, sliding doors (fusuma),
TV set, family photos on shelf, comfortable living space,
slightly cluttered but clean, warm lighting, photorealistic, Japan
```

### bg_patient_bedroom.png - 患者宅寝室
```
Japanese elderly patient bedroom, hospital bed at home,
medical equipment nearby, oxygen concentrator, bedside table with medicines,
natural light from window, comfortable home care setting,
photorealistic, Japan home healthcare
```

---

## 2. マップ画像

### map_area.png - 担当エリアマップ
```
Aerial view of Japanese suburban residential area, bird's eye view,
traditional Japanese neighborhood, houses with tile roofs,
narrow streets, small parks, convenience stores, clinic buildings,
clear sunny day, photorealistic satellite view style, Japan
```

---

## 3. スタッフキャラクター

### 共通設定
- 背景: 透明または単色（後で切り抜き）
- 構図: バストアップ（胸から上）
- 服装: 医療従事者の制服

### staff_manager.png - 管理者（所長）
```
Portrait of Japanese woman in her 50s, nursing station manager,
wearing white medical coat, professional appearance,
warm smile, confident expression, short hair, glasses optional,
looking at camera, solid light background, photorealistic,
Japanese healthcare professional
```

**表情バリエーション**: smile, serious, thinking, explaining

### staff_nurse_01.png - 看護師A（女性・30代）
```
Portrait of Japanese female nurse in her 30s,
wearing light blue or pink nurse scrubs, stethoscope around neck,
friendly smile, professional appearance, ponytail hairstyle,
looking at camera, solid light background, photorealistic
```

### staff_nurse_02.png - 看護師B（女性・20代）
```
Portrait of young Japanese female nurse in her 20s,
wearing nurse uniform, cheerful expression,
short bob haircut, energetic appearance,
looking at camera, solid light background, photorealistic
```

### staff_nurse_03.png - 看護師C（男性・30代）
```
Portrait of Japanese male nurse in his 30s,
wearing medical scrubs, professional appearance,
short hair, kind smile, calm expression,
looking at camera, solid light background, photorealistic
```

### staff_pt.png - 理学療法士
```
Portrait of Japanese physical therapist, 30s,
wearing polo shirt with clinic logo, athletic build,
friendly professional appearance, short hair,
looking at camera, solid light background, photorealistic
```

### staff_ot.png - 作業療法士
```
Portrait of Japanese occupational therapist, female, 30s,
wearing casual medical attire, warm and approachable expression,
medium length hair, glasses, caring appearance,
looking at camera, solid light background, photorealistic
```

### staff_st.png - 言語聴覚士
```
Portrait of Japanese speech therapist, female, 40s,
wearing professional medical attire, intelligent expression,
neat appearance, gentle smile,
looking at camera, solid light background, photorealistic
```

### staff_clerk.png - 事務員
```
Portrait of Japanese office clerk, female, 20s-30s,
wearing business casual attire, professional appearance,
friendly smile, neat hairstyle,
looking at camera, solid light background, photorealistic
```

---

## 4. 患者キャラクター

### patient_male_01.png - 高齢男性患者A
```
Portrait of elderly Japanese man, 70s-80s,
wearing comfortable home clothes (cardigan or sweater),
sitting position, kind grandfatherly appearance,
slightly thin, gentle expression,
solid light background, photorealistic
```

**表情バリエーション**: smile, tired, worried, relieved, sleeping

### patient_male_02.png - 高齢男性患者B
```
Portrait of elderly Japanese man, 80s,
wearing traditional Japanese clothes or pajamas,
calm expression, wise appearance, white hair,
solid light background, photorealistic
```

### patient_female_01.png - 高齢女性患者A
```
Portrait of elderly Japanese woman, 70s-80s,
wearing comfortable home clothes,
warm grandmotherly appearance, gentle smile,
short permed gray hair,
solid light background, photorealistic
```

### patient_female_02.png - 高齢女性患者B
```
Portrait of elderly Japanese woman, 80s,
wearing cardigan, sitting comfortably,
kind expression, slightly frail appearance,
solid light background, photorealistic
```

---

## 5. UI・アイコン画像

### icon_station.png - ステーションアイコン
```
Simple icon of Japanese nursing station building,
modern medical facility exterior, clean design,
white and light blue colors, minimal style
```

### icon_home.png - 患者宅アイコン
```
Simple icon of Japanese house,
traditional tile roof, wooden structure,
warm colors, minimal style
```

---

## 画像生成時の注意点

1. **一貫性**: 同じキャラクターの表情違いは、同じシード値やベース画像から生成
2. **背景除去**: キャラクター画像は後で背景を透過処理する想定
3. **解像度**: ゲームでの使用サイズより大きめに生成してからリサイズ
4. **著作権**: AI生成画像の商用利用規約を確認

## フォルダ構成

```
/images/
  /backgrounds/
    bg_station_office.png
    bg_station_meeting.png
    bg_patient_living.png
    bg_patient_bedroom.png
  /maps/
    map_area.png
  /staff/
    /manager/
      manager_smile.png
      manager_serious.png
      manager_thinking.png
    /nurse_01/
      nurse_01_smile.png
      nurse_01_worried.png
      ...
    /nurse_02/
    /nurse_03/
    /pt/
    /ot/
    /st/
    /clerk/
  /patients/
    /male_01/
      male_01_smile.png
      male_01_tired.png
      ...
    /male_02/
    /female_01/
    /female_02/
```
