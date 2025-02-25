import os
from bert_score.scorer import BERTScorer
import pandas as pd

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

def main():
    # 디렉토리 경로 설정
    directory = r"C:\Users\peter\OneDrive\바탕 화면\BOAZ\미프\모든사진"
    keyword_file = os.path.join(directory, "keyword.txt")
    
    # 데이터 로드
    image_files, blip2_captions, keywords, manual_scores = load_captions_and_keywords(keyword_file)
    
    print("BERTScore 계산 중...")
    # BERTScore 계산
    precision_scores, recall_scores, f1_scores = calculate_bert_scores(blip2_captions, keywords)
    
    # 결과를 DataFrame으로 정리
    results_df = pd.DataFrame({
        '이미지 파일': image_files,
        'BLIP-2 캡션': blip2_captions,
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
    output_file = os.path.join(directory, "bert_score_results.csv")
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n결과가 {output_file}에 저장되었습니다.")

if __name__ == "__main__":
    main() 