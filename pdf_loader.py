# pip install pypdf langchain-core langchain-community langchain-text-splitters

import pypdf
from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_text_from_pdf(file_path):
    """
    pypdf를 사용하여 PDF 파일에서 텍스트를 추출합니다.
    """
    text_list = []
    
    try:
        with open(file_path, "rb") as file:
            reader = pypdf.PdfReader(file)
            
            # 모든 페이지를 순회하며 텍스트 추출
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                
                if text and text.strip():
                    text_list.append(text.strip())
                    
    except Exception as e:
        raise ValueError(f"{file_path} 파일을 읽는 중 오류가 발생했습니다: {e}")
            
    # 각 페이지의 텍스트를 줄바꿈으로 연결하여 반환
    return "\n\n".join(text_list)

class PdfLoader(BaseLoader):
    """LangChain의 BaseLoader를 상속받은 커스텀 PDF 로더"""
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self):
        text = extract_text_from_pdf(self.file_path)
        metadata = {"source": self.file_path}
        # LangChain Document 객체 리스트로 반환
        return [Document(page_content=text, metadata=metadata)]

# ----------------- 실행 테스트 -----------------
if __name__ == "__main__":
    # 테스트할 PDF 파일 경로를 지정하세요.
    file_name = "./srcdata/sample_document.pdf" 
    
    try:
        print(f"[{file_name}] PDF 텍스트 추출 및 분석 중...")
        loader = PdfLoader(file_name)
        documents = loader.load()
        
        # 텍스트 스플리터 설정
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)
        
        print(f"성공! 총 {len(docs)}개의 조각으로 분할되었습니다.\n")
        print("--- 정제된 텍스트 추출 미리보기 ---")
        if docs:
            print(docs[0].page_content)
        else:
            print("추출된 텍스트가 없습니다. (이미지로만 구성된 PDF일 수 있습니다.)")
        
    except FileNotFoundError:
        print("지정된 경로에서 PDF 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")