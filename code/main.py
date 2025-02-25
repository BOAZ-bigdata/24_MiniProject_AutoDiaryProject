import subprocess

def main():
    try:
        # Streamlit 앱 실행
        print("Streamlit 앱을 실행하는 중...")
        subprocess.run(["streamlit", "run", "blip_streamlit.py"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"오류 발생: {e}")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")

if __name__ == "__main__":
    main()