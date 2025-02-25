import os
from bert_score.scorer import BERTScorer
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import argparse
from pathlib import Path

# .env 파일 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def load_captions_and_keywords(file_path):
    """키워드 파일에서 캡션과 키워드를 로드하는 함수"""
    image_files = []
    blip2_captions = []
    keywords = []
    manual_scores = []  # O/X 평가 저장
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(' : ')
            if len(parts) == 2:
                image_files.append(parts[0])
                caption_keyword_sim = parts[1].split(' / ')
                if len(caption_keyword_sim) == 3:
                    blip2_captions.append(caption_keyword_sim[0])
                    keywords.append(caption_keyword_sim[1])
                    manual_scores.append(caption_keyword_sim[2])
    
    return image_files, blip2_captions, keywords, manual_scores

def calculate_bert_scores(captions, keywords):
    """BERTScore를 계산하는 함수"""
    # rescale_with_baseline을 False로 설정
    scorer = BERTScorer(
        lang="ko",
        model_type="klue/bert-base",
        num_layers=9,
        batch_size=32,
        nthreads=4,
        rescale_with_baseline=False  # 베이스라인 스케일링 비활성화
    )
    
    try:
        # BERTScore 계산
        P, R, F1 = scorer.score(captions, keywords)
        
        # 텐서를 리스트로 변환
        precision_scores = P.tolist()
        recall_scores = R.tolist()
        f1_scores = F1.tolist()
        
        return precision_scores, recall_scores, f1_scores
    
    except Exception as e:
        print(f"Error during BERTScore calculation: {e}")
        raise e 

def translate_with_gpt4(texts):
    """GPT-4를 사용하여 영어 텍스트를 한국어로 번역"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    translated_texts = []
    
    for text in texts:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # 또는 사용 가능한 모델로 변경
                messages=[
                    {"role": "system", "content": "영어를 한국어로 번역해주세요. 자연스러운 한국어로 번역하되, 간단명료하게 번역해주세요."},
                    {"role": "user", "content": text}
                ],
                temperature=0.3
            )
            translated_text = response.choices[0].message.content.strip()
            translated_texts.append(translated_text)
            print(f"번역 완료: {text} -> {translated_text}")
        except Exception as e:
            print(f"번역 중 오류 발생: {e}")
            translated_texts.append(text)
    
    return translated_texts

def main():
    """
    명령줄 인자로 디렉토리 경로를 받거나, 기본 경로를 사용합니다.
    """
    # 현재 스크립트의 위치를 기준으로 상위 디렉토리 경로 설정
    base_dir = Path(__file__).parent.parent
    default_data_dir = base_dir / 'data'
    default_output_dir = base_dir / 'output'

    # 출력 디렉토리가 없으면 생성
    default_output_dir.mkdir(parents=True, exist_ok=True)

    # 명령줄 인자 파서 설정
    parser = argparse.ArgumentParser(description='BLIP-2 캡션과 키워드의 BERTScore 평가')
    parser.add_argument('--data_dir', type=str, 
                       default=str(default_data_dir),
                       help='키워드 파일이 있는 데이터 디렉토리 경로')
    parser.add_argument('--output_dir', type=str, 
                       default=str(default_output_dir),
                       help='결과 파일을 저장할 출력 디렉토리 경로')
    parser.add_argument('--keyword_file', type=str, 
                       default='keyword.txt',
                       help='키워드 파일명')
    parser.add_argument('--output_file', type=str, 
                       default='bert_score_results.csv',
                       help='결과를 저장할 CSV 파일명')
    
    args = parser.parse_args()
    
    # Path 객체를 사용하여 경로 처리
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    keyword_file = data_dir / args.keyword_file
    output_file = output_dir / args.output_file
    
    # 파일 존재 여부 확인
    if not keyword_file.exists():
        raise FileNotFoundError(f"키워드 파일을 찾을 수 없습니다: {keyword_file}")
    
    # 데이터 로드
    image_files, blip2_captions, keywords, manual_scores = load_captions_and_keywords(str(keyword_file))
    
    # BLIP-2 캡션 번역
    print("캡션 번역 중...")
    translated_captions = translate_with_gpt4(blip2_captions)
    
    print("BERTScore 계산 중...")
    # 번역된 캡션으로 BERTScore 계산
    precision_scores, recall_scores, f1_scores = calculate_bert_scores(translated_captions, keywords)
    
    # 결과를 DataFrame으로 정리
    results_df = pd.DataFrame({
        '이미지 파일': image_files,
        'BLIP-2 캡션(원본)': blip2_captions,
        'BLIP-2 캡션(번역)': translated_captions,
        '키워드': keywords,
        '수동 평가': manual_scores,
        'BERTScore_Precision': precision_scores,
        'BERTScore_Recall': recall_scores,
        'BERTScore_F1': f1_scores
    })
    
    # 통계 계산
    avg_precision = sum(precision_scores) / len(precision_scores)
    avg_recall = sum(recall_scores) / len(recall_scores)
    avg_f1 = sum(f1_scores) / len(f1_scores)
    
    print("\n=== BERTScore 평가 결과 ===")
    print(f"평균 Precision: {avg_precision:.4f}")
    print(f"평균 Recall: {avg_recall:.4f}")
    print(f"평균 F1 Score: {avg_f1:.4f}")
    
    # 수동 평가(O/X)와의 비교
    o_scores = results_df[results_df['수동 평가'] == 'O']['BERTScore_F1'].mean()
    x_scores = results_df[results_df['수동 평가'] == 'X']['BERTScore_F1'].mean()
    
    print("\n=== 수동 평가와의 비교 ===")
    print(f"수동 평가 'O'인 경우의 평균 F1 Score: {o_scores:.4f}")
    print(f"수동 평가 'X'인 경우의 평균 F1 Score: {x_scores:.4f}")
    
    # 결과를 CSV 파일로 저장
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n결과가 {output_file}에 저장되었습니다.")

if __name__ == "__main__":
    main()