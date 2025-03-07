# Auto Diary Project (mini24) (1/24/2025/Analysis)
> 사진과 키워드를 입력하면 AI가 개인화 된 일기를 자동 작성하는 프로젝트

</br>

## Usage
- [ ] 세션
- [ ] 컨퍼런스
- [X] 미니프로젝트
- [ ] 스터디

<br/>

## Period
### 2025.2~2025.2

<br/>

## Team
| 역할 | 이름 | GitHub |
|:---:|:---:|:---:|
| 팀장 | 정주현 | [peter520416](https://github.com/peter520416) |
| 팀원 | 김가영 | [GaYoung0601](https://github.com/GaYoung0601/) |
| 팀원 | 박소연 | [yeoniip](https://github.com/yeoniip/) |
| 팀원 | 배현진 | [BaeHyeonJinee](https://github.com/BaeHyeonJinee/) |


<br/>

## Project Summary
### BLIP-2 + GPT 모델을 활용한 일기 작성 프로젝트
1. 사용자의 사진을 업로드하면 BLIP-2 모델이 캡션을 생성
2. 사용자가 일기에 필요한 추가 정보를 입력
3. GPT 모델이 캡션과 추가 정보를 바탕으로 일기를 작성

<br/>

## ETCs
- .env 파일에 OPENAI_API_KEY 입력

### 🛠 Installation & Usage
```bash
# 저장소 복제
git clone https://github.com/BOAZ-bigdata/24_MiniProject_AutoDiaryProject.git

# 프로젝트 폴더로 이동
cd 24_MiniProject_AutoDiaryProject/code

# 필요한 패키지 설치
pip install -r requirements.txt

# 실행
python main.py
```

### main.py로 실행되지 않는 파일 설명
- `gpt_img_kw.py`: 이미지와 키워드 정보를 GPT 모델에 입력하여 일기 생성
- `gpt_kw.py`: 키워드 정보만을 GPT 모델에 입력하여 일기 생성
- `gpt_cap.py`: BLIP-2가 생성한 캡션만을 GPT 모델에 입력하여 일기 생성

### Evaluation
#### 1. 데이터 준비
- `data/all_imgs/` 폴더에 테스트할 이미지 파일들을 위치시킵니다.
- 현재는 예시 데이터만 포함되어 있으므로 실제 평가를 위해서는 사용자의 이미지를 추가해야 합니다.

#### 2. 키워드 파일 작성
- `data/keyword.txt` 파일은 수기로 작성하셔야 합니다. 다음 형식을 따라 작성해 주시면 감사하겠습니다:
```
[이미지명] : [생성된 캡션] / [키워드] / [평가(O/X)]
```

예시 데이터:
```
01_눈 오는 날.jpg : a snowy scene with a bench and a building / 눈 / O
```
- 수기로 데이터를 입력해 주셔야 하는 점 양해 부탁드립니다.

#### 3. 평가 실행
```bash
python run_eval.py
```
- 실행 시 정성평가 결과(HTML)와 BERTScore 평가 결과(CSV)가 output 폴더에 생성됩니다.

#### 4. 평가 기준
- O: 이미지와 캡션, 키워드가 적절히 매칭됨
- X: 부적절한 매칭

### 출력 결과 예시
- [프랑스 여행 일기 예시](output/(BLIP+GPT)_주현_프랑스.pdf)

> 💡 **참고**: 위 예시는 실제 사용자의 사진과 키워드를 바탕으로 생성된 일기입니다.