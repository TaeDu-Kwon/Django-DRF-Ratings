## DRF Rating API

### **소개**


이 프로젝트는 Django REST Framework 기반으로 제작 된 프로젝트로
방송콘텐츠 종합반응 지표(2023) 데이터를 통하여 방송 데이터 관리, 월간 시청률 계산, 필터링 및 통계 조회 기능이 포함되어 있습니다.
---

### **목차**
1. [앱 개요](#앱-개요)
2. [모델 설명](#모델-설명)
3. [기능 설명](#기능-설명)

---

### **앱 개요**
- **`broadcast`**: 방송 프로그램 및 관련 데이터를 관리하는 앱.
- **`broadcast_ratings`**: 방송 시청률 데이터를 관리 및 분석하는 앱.

---

### **모델 설명**

#### **1. `broadcast` 앱**

|모델 이름| 필드 이름| 데이터 타입| 설명|
|:---:|:---:|:---:|:---:|
| `Channel`      | `channel_name` | `CharField`         | 방송 채널 이름 (예: KBS, MBC)|
| `BroadcastDay` | `day`          | `CharField`         | 방송 요일 (예: 월요일, 화요일)|
| `Broadcast`    | `program`      | `CharField`         | 방송 프로그램 이름 (예: 놀라운 토요일)|
|                | `channel`      | `ForeignKey`        | 방송 채널과의 관계|
|                | `broadcast_day`| `ManyToManyField`   | 방송 요일과의 관계|

#### **2. `broadcast_ratings` 앱**

|모델 이름| 필드 이름| 데이터 타입| 설명|
|:---:|:---:|:---:|:---:|
| `AudienceSampleSize` | `audience_type` | `CharField`         | 시청자 타입 (예: 10대, 20대, 가구)|
|                      | `sample_size`   | `IntegerField`      | 시청자 타입 총 인원 수 (예: 남성 : 24624000명 / 시청률 계산할 때 사용할 목적)|
| `BroadcastRatings`   | `broadcast`     | `ForeignKey`        | 방송 프로그램과의 관계|
|                      | `month`         | `CharField`         | 방송 월 (예: 2023-01)|
|                      | `ratings_type`  | `CharField`         | 시청자 타입 (예: 10대, 20대, 가구)|
|                      | `ratings`       | `FloatField`        | 시청률|

---

### **기능 설명**
#### **1. 방송 데이터 관리**
- 방송 프로그램, 채널, 방송 요일 데이터를 입력/ 수정/ 삭제할 수 있습니다.
- `POST/broadcast`를 통해 방송 데이터를 등록합니다.
- 기능 예시 test.py (line 95 : 155)
#### **2. 방송 월간 시청률 계산**
- 프로그램과 시청자 수를 입력받아 월간 시청률을 계산합니다.
- `POST/broadcast-ratings/`를 통해 시청률 데이터를 추가할 수 있습니다.
- 기능 예시 test.py (line 157 : 182)
#### **3. 시청률 필터링 및 최대 최소 조회**
- 특정 조건(프로그램,월,채널 등)에 따라 시청률 데이터를 필터링 합니다.
- `GET/broadcast-ratings/stats/`를 통해 필터링 된 데이터를 조회 합니다.
- `?`URL 쿼리 문자열을 통해 필터링의 정보를 넘겨줍니다.
- 기능 예시 test.py (line 185 : 260)
#### **4. 프로그램 평균 시청률 조회**
- 특정 프로그램의 평균 시청률을 계산합니다.
- `GET/broadcast-ratings/average/<프로그램 이름>` 호출하여 확인합니다.
- 기능 예시 test.py (line 262 : 268)
#### **5. 시청자 타입별 최고 시청률 조회**
- 특정 시청자 타입에 대한 최고 시청률을 조회합니다.
- `GET//broadcast-ratings/ranking/filter/value`를 통해 조회합니다.
- filter는 프로그램, 년-월, 시청자 타입, 채널, 요일
- filter값에 맞는 값
- 기능 예시 test.py (line 270 : 286)
  
---
### **테스트 코드**
#### **기본 베이스 데이터 생성** 
필요한 데이터를 Json파일에 저장하여 사용하였습니다.
다른 테스트 캐이스와 동일하게 테스트 함수에서 데이터를 생성할 경우 최대 5 ~ 6초가 소모되어 다른 태스트 캐이스 실행하는데 있어
필요 없는 시간이 많이 들어간다 생각하여 `setUpTestData` 함수를 사용하여 태스트 클래스 실행 시 한번만 실행 하여 다른 함수들에서 해당 데이터를 사용할 수 있습니다.

















