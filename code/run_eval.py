import subprocess
import sys
from pathlib import Path
import argparse

def run_evaluation(base_dir):
    """
    정성평가와 BERTScore 평가를 순차적으로 실행하는 함수
    """
    print("=== Auto Diary 프로젝트 평가 시작 ===\n")

    # 실행할 스크립트들의 경로
    current_dir = Path(__file__).parent
    quan_eval_script = current_dir / "quan_eval_html_generator.py"
    bert_eval_script = current_dir / "bert_score_eval.py"

    try:
        # 1. 정성평가 HTML 생성 실행
        print("1. 정성평가 HTML 생성 중...")
        subprocess.run([sys.executable, str(quan_eval_script), "--base_dir", str(base_dir)], check=True)
        print("정성평가 HTML 생성 완료\n")

        # 2. BERTScore 평가 실행
        print("2. BERTScore 평가 시작...")
        subprocess.run([sys.executable, str(bert_eval_script), "--data_dir", str(base_dir / "data")], check=True)
        print("BERTScore 평가 완료\n")

        print("=== 모든 평가가 성공적으로 완료되었습니다 ===")
        print(f"결과는 {base_dir}/output 디렉토리에서 확인하실 수 있습니다.")

    except subprocess.CalledProcessError as e:
        print(f"평가 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1)

def main():
    # 현재 스크립트의 위치를 기준으로 상위 디렉토리 경로 설정
    default_base_dir = Path(__file__).parent.parent

    parser = argparse.ArgumentParser(description='Auto Diary 프로젝트 평가 실행')
    parser.add_argument('--base_dir', type=str, 
                       default=str(default_base_dir),
                       help='프로젝트 기본 디렉토리 경로')
    
    args = parser.parse_args()
    run_evaluation(Path(args.base_dir))

if __name__ == "__main__":
    main()
