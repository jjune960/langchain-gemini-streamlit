import streamlit as st
import json
import os

def load_faq_data(file_path):
    """외부 JSON 파일에서 FAQ 데이터를 읽어옵니다."""
    # 파일 존재 여부 확인
    if not os.path.exists(file_path):
        st.error(f"'{file_path}' 파일을 찾을 수 없습니다. 경로를 확인해 주세요.")
        return None
        
    # JSON 파일 읽기 (한글 깨짐 방지를 위해 encoding="utf-8" 필수)
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            st.error("JSON 파일의 형식이 올바르지 않습니다. 콤마나 괄호의 짝을 확인해 주세요.")
            return None

def main():
    st.set_page_config(page_title="지원사업 FAQ", page_icon="📝", layout="centered")
    
    st.title("📌 전통시장 지원사업 FAQ")
    st.info("자주 묻는 질문 10가지를 정리했습니다. 질문을 클릭하여 답변을 확인해 보세요.")
    st.markdown("---")
    
    # 외부 JSON 파일 연동
    json_file_path = "./faq/faq.json"
    faqs = load_faq_data(json_file_path)

    # 데이터가 정상적으로 로드되었을 때만 화면에 출력
    if faqs:
        for faq in faqs:
            with st.expander(f"**Q{faq['id']}. {faq['question']}**"):
                st.write(faq['answer'])

if __name__ == "__main__":
    main()