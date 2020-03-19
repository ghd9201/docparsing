from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from konlpy.tag import Kkma
from konlpy.utils import pprint

import os
import re


def convert_pdf_to_txt(f):
    # pdf리소스 매니저 객체 생성
    rsrcmgr = PDFResourceManager()
    # 문자열 데이터를 파일처럼 처리하는 stringio -> pdf 파일 내용이 여기 담김
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(f, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)
    # text에 결과가 담김
    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

def txt_write(f, d):
    file = open(f,'w',-1,'utf-8')           # -1 은 버퍼 / utf-8 추가 or 파일 인코딩 ANSI 변경으로 인코딩 문제 해결 가능
    file.write(d)
    file.close()

def word_list_write(f, l):
    file = open(f,'w',-1,'utf-8')           # -1 은 버퍼 / utf-8 추가 or 파일 인코딩 ANSI 변경으로 인코딩 문제 해결 가능
    cnt = 0
    for word in l:
        if len(word) > 20 or len(word) <= 1:            # 단어 길이가 20 이상 이거나 1 --> 무의미하다고 가정
            continue
        file.write(word+"\n")
        cnt += 1
    print(f + ' 총 단어 수 : %d개\n' % cnt)
    file.close()

#파일 이름 기반으로 메모장 이름 생성
def make_txt_name(f):
    o = re.sub('.pdf',"_pdf 읽기.txt", f)
    k = re.sub('.pdf',"_형태소 분석.txt",f)
    return o, k


#특수 문자 제거
def data_cleansing_character(d):                      # 정규표현식을 활용 but, 목차 제거 등은 다른 방법이 필요한 듯
    parse = re.sub('[-=+,#/\?:^$.@*\"※~⚫&%ㆍ!』\"\'\\‘|\(\)\[\]\<\>`\'…》]'," ",d)          #parse = re.sub('[^\w\s]',"",d)   이것도 되나?
    return parse

def data_cleansing(f):
    t1 = 'temp1.txt'        # pdf 읽은 내용 저장할 텍스트 파일 이름
    t2 = 'temp2.txt'        # 형태소 분석
    t1, t2 = make_txt_name(f)

    # pdf 파일 읽어와 텍스트 파일 저장
    v = convert_pdf_to_txt(f)
    txt_write(t1, v)

    # 특수 문자 제거
    c = data_cleansing_character(v)
    data_konlpy_write(t2, data_konlpy(c))

#형태소 분석기
def data_konlpy(d):
    kkma = Kkma()
    konlpy_array = kkma.morphs(d)
    #pprint(konlpy_array)
    return konlpy_array

#형태소 분석 결과 파일 저장
def data_konlpy_write(f, l):
    file = open(f,'w',-1,'utf-8')           # -1 은 버퍼 / utf-8 추가 or 파일 인코딩 ANSI 변경으로 인코딩 문제 해결 가능
    cnt = 0
    for word in l:
        if len(word) <= 1:            # 단어 길이가 1 이면 --> 무의미하다고 가정
            continue
        file.write(word+"\n")
        cnt += 1
    print(f + ' 형태소 총 개수 : %d개\n' % cnt)
    file.close()

# 테스트 파일이 위치한 절대 경로 구하기
def get_file_dir_path():
    path = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.join(path, 'file')
    return dir_path

# 테스트 파일 목록 읽어오기
def get_file_list(p):
    file_list = os.listdir(p)
    file_list_pdf = [ file for file in file_list if file.endswith('.pdf') ]
    return file_list_pdf

if __name__ == '__main__':
    
    cur_path = get_file_dir_path()
    file_list = get_file_list(cur_path)

    for file in file_list:
        file_path = os.path.join(cur_path,file)
        data_cleansing(file_path)
