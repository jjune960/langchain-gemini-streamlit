# pip install langchain-core langchain-community langchain-text-splitters

import zipfile
import xml.etree.ElementTree as ET
from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_text_from_hwpx(file_path):
    """
    HWPX 파일 내부의 압축을 해제하고 XML을 파싱하여 본문 텍스트를 추출합니다.
    """
    text_list = []
    
    try:
        # HWPX는 사실상 ZIP 파일이므로 zipfile로 엽니다.
        with zipfile.ZipFile(file_path, 'r') as zf:
            # 본문 내용이 담긴 XML 파일 목록 찾기 (보통 Contents/section0.xml, section1.xml 등)
            section_files = [f for f in zf.namelist() if f.startswith('Contents/section') and f.endswith('.xml')]
            
            # 페이지/섹션 순서를 맞추기 위해 정렬
            section_files.sort()
            
            for sec_file in section_files:
                xml_content = zf.read(sec_file)
                root = ET.fromstring(xml_content)
                
                # HWPX의 단락 네임스페이스 정의
                namespaces = {'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}
                
                # <hp:t> 태그가 실제 텍스트를 포함하고 있습니다.
                for t_tag in root.findall('.//hp:t', namespaces):
                    if t_tag.text and t_tag.text.strip():
                        text_list.append(t_tag.text.strip())
                        
    except zipfile.BadZipFile:
        raise ValueError(f"[{file_path}] 파일은 유효한 HWPX(ZIP 압축) 형식이 아닙니다.")
    except Exception as e:
        raise ValueError(f"HWPX 텍스트 추출 중 오류가 발생했습니다: {e}")
        
    # 추출된 텍스트 조각들을 줄바꿈으로 연결하여 반환
    return "\n".join(text_list)

class HwpxLoader(BaseLoader):
    """LangChain의 BaseLoader를 상속받은 커스텀 HWPX 로더"""
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self):
        text = extract_text_from_hwpx(self.file_path)
        metadata = {"source": self.file_path}
        # LangChain Document 객체 리스트로 반환
        return [Document(page_content=text, metadata=metadata)]

# ----------------- 실행 테스트 -----------------
if __name__ == "__main__":
    # 테스트할 HWPX 파일 경로를 지정하세요.
    file_name = "./srcdata/sample_document.hwpx" 
    
    try:
        print(f"[{file_name}] HWPX XML 구조 파싱 중...")
        loader = HwpxLoader(file_name)
        documents = loader.load()
        
        # 텍스트 스플리터 설정
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)
        
        print(f"성공! 총 {len(docs)}개의 조각으로 분할되었습니다.\n")
        print("--- 정제된 텍스트 추출 미리보기 ---")
        if docs:
            print(docs[0].page_content)
        else:
            print("추출된 텍스트가 없습니다.")
            
    except FileNotFoundError:
        print("지정된 경로에서 HWPX 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")