from pathlib import Path
import os
import pandas as pd
import argparse

def parse_arguments():
    # 현재 스크립트의 위치를 기준으로 상위 디렉토리 경로 설정
    base_dir = Path(__file__).parent.parent
    default_data_dir = base_dir / 'data'
    
    parser = argparse.ArgumentParser(description='이미지 키워드 평가 HTML 생성기')
    parser.add_argument('--base_dir', type=str, 
                        default=str(base_dir),
                        help='프로젝트 기본 디렉토리 경로')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # 기본 디렉토리 경로 설정
    base_dir = Path(args.base_dir)
    data_dir = base_dir / "data"
    img_dir = data_dir / "all_imgs"
    output_dir = base_dir / "output"

    # output 디렉토리가 없는 경우 생성
    output_dir.mkdir(parents=True, exist_ok=True)

    # keyword.txt 파일 경로
    keyword_file = data_dir / "keyword.txt"
    if not keyword_file.exists():
        raise FileNotFoundError(f"keyword.txt 파일을 찾을 수 없습니다: {keyword_file}")

    # 이미지 파일과 키워드를 저장할 리스트
    image_files = []
    blip2_captions = []
    keywords = []
    similarities = []  # O, X 평가 저장 리스트

    # keyword.txt 파일 읽기
    with open(keyword_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(' : ')
            if len(parts) == 2:
                image_files.append(parts[0])
                caption_keyword_sim = parts[1].split(' / ')
                if len(caption_keyword_sim) == 3:
                    blip2_captions.append(caption_keyword_sim[0])
                    keywords.append(caption_keyword_sim[1])
                    similarities.append(caption_keyword_sim[2])

    # 통계 계산
    total_images = len(image_files)
    similar_count = similarities.count('O')
    not_similar_count = similarities.count('X')
    similar_percent = (similar_count / total_images) * 100

    # HTML 파일 생성
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            table {{
                border-collapse: collapse;
                width: 100%;
            }}
            th, td {{
                border: 1px solid black;
                padding: 8px;
                text-align: center;
            }}
            img {{
                max-width: 300px;
                max-height: 300px;
            }}
            .stats {{
                margin: 20px 0;
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="stats">
            <h2>통계</h2>
            <p>총 이미지 개수: {total_images}개</p>
            <p>유사한 경우(O): {similar_count}개 ({similar_percent:.1f}%)</p>
            <p>유사하지 않은 경우(X): {not_similar_count}개 ({100-similar_percent:.1f}%)</p>
        </div>
        <table>
            <tr>
                <th>이미지</th>
                <th>BLIP-2 캡셔닝</th>
                <th>키워드</th>
                <th>정성평가</th>
            </tr>
    """

    # 각 이미지, BLIP-2 캡셔닝, 키워드, 유사도에 대한 행 추가
    for img_file, caption, keyword, similarity in zip(image_files, blip2_captions, keywords, similarities):
        img_path = img_dir / img_file
        if img_path.exists():
            html_content += f"""
            <tr>
                <td><img src="{img_path}" alt="{img_file}"></td>
                <td>{caption}</td>
                <td>{keyword}</td>
                <td>{similarity}</td>
            </tr>
            """

    html_content += """
        </table>
    </body>
    </html>
    """

    # HTML 파일로 저장 (출력 경로 수정)
    output_file = output_dir / "image_keywords.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # 콘솔에 통계 출력
    print(f"총 이미지 개수: {total_images}개")
    print(f"유사한 경우(O): {similar_count}개 ({similar_percent:.1f}%)")
    print(f"유사하지 않은 경우(X): {not_similar_count}개 ({100-similar_percent:.1f}%)")

if __name__ == "__main__":
    main()