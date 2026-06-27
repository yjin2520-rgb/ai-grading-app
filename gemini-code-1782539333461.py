import streamlit as st
import re

st.set_page_config(page_title="국어 서논술형 자동 채점 시스템", layout="wide")

st.title("📝 2회고사 대비 국어 서논술형 자동 채점 시스템")
st.caption("설명 방법 및 매체 복합양식성 실전 적용 문항 채점 엔진 (ver 1.0)")

# 세션 상태 초기화
if "score" not in st.session_state:
    st.session_state.score = {}

# ----------------------------------------------------------------                      
# 헬퍼 함수: 텍스트 정규화 및 단순 매칭
# ----------------------------------------------------------------
def normalize(text):
    return re.sub(r'\s+', ' ', text.strip())

def check_keywords(text, keywords):
    return any(kw in text for kw in keywords)

# ================================================================
# 세트 1 채점 로직 (사회적 촉진과 억제)
# ================================================================
def grade_set1(s1_1_1, s1_1_2, s1_1_3, s1_2_1, s1_2_2, s1_3_vis, s1_3_vis_eff, s1_3_aud, s1_3_aud_eff):
    results = {}
    total = 0.0
    
    # [서논술형 1]
    # (1) 쉬운 과제
    ans1 = normalize(s1_1_1)
    if check_keywords(ans1, ["쉬운", "친숙", "노력이 필요 없는", "취미", "일상적인"]):
        results["1-1-(1)"] = (1.0, "정답")
    else:
        results["1-1-(1)"] = (0.0, "오답 ('쉬운/친숙한 과제' 의미 누락)")
        
    # (2) 혼자 집중
    ans2 = normalize(s1_1_2)
    if "함께" in ans2 or "모임" in ans2: # 오개념 필터
        results["1-1-(2)"] = (0.0, "오답 (오개념: 어려운 과제에 '함께/모임' 서술)")
    elif check_keywords(ans2, ["혼자", "나홀로", "타인 없이"]) and check_keywords(ans2, ["집중", "연습"]):
        results["1-1-(2)"] = (1.5, "정답")
    else:
        results["1-1-(2)"] = (0.0, "오답 ('혼자 집중' 의미 누락)")
        
    # (3) 사회적 억제
    ans3 = normalize(s1_1_3).replace(" ", "")
    if "사회적억제" in ans3:
        results["1-1-(3)"] = (1.0, "정답")
    else:
        results["1-1-(3)"] = (0.0, "오답 (정확한 학술 용어 미기재)")

    # [서논술형 2]
    # (1) 문장 - 예시 선호
    m1 = normalize(s1_2_1)
    type1_match = re.search(r'\(([^)]+)\)$', m1)
    if not type1_match:
        results["1-2-(1)"] = (0.0, "오답 (문장 끝 괄호 설명 방법 명시 누락)")
    else:
        method1 = type1_match.group(1).replace(" ", "")
        if "예시" in method1:
            if check_keywords(m1, ["독서실", "스터디카페"]): # 지문 외 단어 차단
                results["1-2-(1)"] = (0.0, "오답 (지문에 없는 외부 배경지식 사용)")
            elif check_keywords(m1, ["커피숍", "도서관", "모임"]) and check_keywords(m1, ["쉬운", "친숙"]):
                results["1-2-(1)"] = (1.5, "정답 (예시의 특징 및 결론 방향 만족)")
            else:
                results["1-2-(1)"] = (0.5, "부분점수 (예시 형식은 맞으나 필수 구체적 장소/상황 누락)")
        else:
            results["1-2-(1)"] = (0.0, f"오답 (제시한 {method1}의 특성이 문장에 구현되지 않음)")

    # (2) 문장 - 대조 선호
    m2 = normalize(s1_2_2)
    type2_match = re.search(r'\(([^)]+)\)$', m2)
    if not type2_match:
        results["1-2-(2)"] = (0.0, "오답 (문장 끝 괄호 설명 방법 명시 누락)")
    else:
        method2 = type2_match.group(1).replace(" ", "")
        if "대조" in method2:
            if not check_keywords(m2, ["반면", "달리", "반대로", "대조적으로"]): # 대조 특성 검사
                results["1-2-(2)"] = (0.5, "부분점수 (대조 내용이나 역접 접속어/문구 누락으로 논리 흐름 미흡)")
            elif check_keywords(m2, ["어려운", "도전"]) and check_keywords(m2, ["혼자", "차분"]):
                results["1-2-(2)"] = (1.5, "정답 (대조의 특성 및 결론 방향 만족)")
            else:
                results["1-2-(2)"] = (0.0, "오답 (대조군 내용 정보 오류)")
        else:
            results["1-2-(2)"] = (0.0, f"오답 (제시한 {method2}의 특성이 문장에 구현되지 않음)")

    # [서논술형 3] 복합양식성 연출 계획 및 효과
    # 시각 요소 Ⓐ
    v_ans = normalize(s1_3_vis)
    if check_keywords(v_ans, ["넓은", "풀샷", "친구들과"]): # 오개념 필터
        results["1-3-시각"] = (0.0, "오답 ([장면1]의 시각 특성을 혼용함)")
    elif check_keywords(v_ans, ["방", "독서실", "개인", "가까이", "클로즈업", "혼자"]):
        results["1-3-시각"] = (1.0, "정답")
    else:
        results["1-3-시각"] = (0.0, "오답 (어려운 과제 환경과 대비되는 시각 연출 미흡)")
        
    # 시각 효과
    v_eff = normalize(s1_3_vis_eff)
    if check_keywords(v_eff, ["혼자", "차분하게", "집중", "방해 없이"]) and "어려운 과제" in v_eff:
        results["1-3-시각효과"] = (1.5, "정답 (지문 근거 및 결론 방향 통과)")
    else:
        results["1-3-시각효과"] = (0.0, "오답 (지문 속 환경적 특성 근거 누락)")

    # 청각 요소 Ⓑ
    a_ans = normalize(s1_3_aud)
    if check_keywords(a_ans, ["경쾌", "리듬", "발소리", "책장"]): # 오개념 필터
        results["1-3-청각"] = (0.0, "오답 ([장면1]의 청각 특성을 혼용함)")
    elif check_keywords(a_ans, ["고요", "적막", "소리 없는", "음소거", "없애고", "낮은"]):
        results["1-3-청각"] = (1.0, "정답")
    else:
        results["1-3-청각"] = (0.0, "오답 (고요한 상태에 대한 청각 연출 미흡)")
        
    # 청각 효과
    a_eff = normalize(s1_3_aud_eff)
    if check_keywords(a_eff, ["집중", "차분", "몰입"]):
        results["1-3-청각효과"] = (1.5, "정답 (지문 근거 만족)")
    else:
        results["1-3-청각효과"] = (0.0, "오답 (차분하게 집중하는 시간 연계 효과 미흡)")

    for k, v in results.items():
        total += v[0]
    return total, results

# ================================================================
# 세트 2 채점 로직 (정전기)
# ================================================================
def grade_set2(s2_1_1, s2_1_2, s2_1_3, s2_2_1, s2_2_2, s2_3_vis, s2_3_vis_eff, s2_3_aud, s2_3_aud_eff):
    results = {}
    total = 0.0
    
    # [서논술형 1]
    if check_keywords(normalize(s2_1_1), ["고여 있는 물", "고인 물"]):
        results["2-1-(1)"] = (1.0, "정답")
    else:
        results["2-1-(1)"] = (0.0, "오답 (비유어 '고여 있는 물' 오기)")
        
    if "이동함" in normalize(s2_1_2): # 오개념
        results["2-1-(2)"] = (0.0, "오답 (오개념: 실생활 전기의 특성을 기술함)")
    elif check_keywords(normalize(s2_1_2), ["이동하지 않고", "머물러", "정지"]):
        results["2-1-(2)"] = (1.5, "정답")
    else:
        results["2-1-(2)"] = (0.0, "오답 (전하의 정지 상태 설명 부족)")
        
    if check_keywords(normalize(s2_1_3), ["위험하지 않음", "위험하지 않다", "안전", "피해가 없음"]):
        results["2-1-(3)"] = (1.0, "정답")
    else:
        results["2-1-(3)"] = (0.0, "오답 (위험성 결론 방향 오류)")

    # [서논술형 2]
    # (1) 정의 문장
    m1 = normalize(s2_2_1)
    t1 = re.search(r'\(([^)]+)\)$', m1)
    if not t1:
        results["2-2-(1)"] = (0.0, "오답 (괄호 설명 방법 누락)")
    else:
        method = t1.group(1).replace(" ", "")
        if "정의" in method:
            if check_keywords(m1, ["란 ", "이란 ", "말한다"]): # 정의의 문장 특성 문형 확인
                if check_keywords(m1, ["전하가 정지", "머물러 있는"]):
                    results["2-2-(1)"] = (1.5, "정답 (정의 문형 및 특성 일치)")
                else:
                    results["2-2-(1)"] = (0.5, "부분점수 (정의 형식을 취했으나 핵심 개념어 누락)")
            else:
                results["2-2-(1)"] = (0.5, "부분점수 (의미는 통하나 용어의 개념을 밝히는 정의 문형 아님)")
        else:
             results["2-2-(1)"] = (0.0, f"오답 ({method} 특성 미구현)")

    # (2) 대조 문장
    m2 = normalize(s2_2_2)
    t2 = re.search(r'\(([^)]+)\)$', m2)
    if not t2:
        results["2-2-(2)"] = (0.0, "오답 (괄호 설명 방법 누락)")
    else:
        method = t2.group(1).replace(" ", "")
        if "대조" in method or "비유" in method:
            if check_keywords(m2, ["흐르는 물", "고여 있는 물"]) and check_keywords(m2, ["위험하지"]):
                results["2-2-(2)"] = (1.5, "정답 (실생활 전기와의 대조 결론 명확)")
            else:
                results["2-2-(2)"] = (0.0, "오답 (대조 핵심인 전하의 이동 유무 및 위험성 결과 누락)")
        else:
            results["2-2-(2)"] = (0.0, f"오답 ({method} 특성 미구현)")

    # [서논술형 3] 효과 서술 시 지문 근거 필터링
    v_ans = normalize(s2_3_vis)
    if "쏟아지는" in v_ans or "폭포" in v_ans:
        results["2-3-시각"] = (0.0, "오답 ([장면1]의 역동적 흐름 혼용)")
    elif check_keywords(v_ans, ["멈춰", "고여 있는", "움직이지 않는"]):
        results["2-3-시각"] = (1.0, "정답")
    else:
        results["2-3-시각"] = (0.0, "오답 (고여 있는 물의 정적 시각화 부족)")
        
    v_eff = normalize(s2_3_vis_eff)
    if check_keywords(v_eff, ["이동하지 않고", "머물러"]) and check_keywords(v_eff, ["위험하지"]):
        results["2-3-시각효과"] = (1.5, "정답 (지문 내용 근거 완벽 포함)")
    else:
        results["2-3-시각효과"] = (0.0, "오답 (지문 근거인 '이동 안 함, 위험하지 않음' 누락)")

    a_ans = normalize(s2_3_aud)
    if "웅장" in a_ans or "거센" in a_ans:
        results["2-3-청각"] = (0.0, "오답 ([장면1]의 큰 소리 속성 혼용)")
    elif check_keywords(a_ans, ["고요", "적막", "소리가 없는", "소거"]):
        results["2-3-청각"] = (1.0, "정답")
    else:
        results["2-3-청각"] = (0.0, "오답 (조용한 청각 연출 미흡)")
        
    a_eff = normalize(s2_3_aud_eff)
    if check_keywords(a_eff, ["조용하다", "한자 정", "흐르지 않는"]):
        results["2-3-청각효과"] = (1.5, "정답")
    else:
        results["2-3-청각효과"] = (0.0, "오답 (조용하다(靜) 혹은 흐르지 않는 성질 결부 누락)")

    for k, v in results.items():
        total += v[0]
    return total, results

# ================================================================
# 세트 3 채점 로직 (인공지능 예술)
# ================================================================
def grade_set3(s3_1_1, s3_1_2, s3_1_3, s3_2_1, s3_2_2, s3_3_vis, s3_3_vis_eff, s3_3_aud, s3_3_aud_eff):
    results = {}
    total = 0.0
    
    # [서논술형 1]
    if check_keywords(normalize(s3_1_1), ["로봇", "피겨"]):
        results["3-1-(1)"] = (1.0, "정답")
    else:
        results["3-1-(1)"] = (0.0, "오답 (올림픽 비유 파트 '로봇 피겨 스케이팅' 누락)")
        
    if "경험" in normalize(s3_1_2) or "관점" in normalize(s3_1_2): # 오개념
        results["3-1-(2)"] = (0.0, "오답 (오개념: 인간 고유의 속성을 AI 근거에 기재함)")
    elif check_keywords(normalize(s3_1_2), ["감정이 없고", "철학이 없고", "이야기가 없"]):
        if "예술로 보기 어렵다" in normalize(s3_1_2) or "예술이 아니다" in normalize(s3_1_2):
            results["3-1-(2)"] = (1.5, "정답 (근거 및 결론 완벽)")
        else:
            results["3-1-(2)"] = (0.5, "부분점수 (근거는 맞으나 예술 가능 여부 결론 미흡)")
    else:
        results["3-1-(2)"] = (0.0, "오답 (AI 예술 판단의 핵심 근거 누락)")
        
    if check_keywords(normalize(s3_1_3), ["미술계에 큰 변화", "범주를 확장", "상징적 가치"]):
        results["3-1-(3)"] = (1.0, "정답")
    else:
        results["3-1-(3)"] = (0.0, "오답 (지문에 제시된 상징적 가치 의미 누락)")

    # [서논술형 2]
    m1 = normalize(s3_2_1)
    t1 = re.search(r'\(([^)]+)\)$', m1)
    if not t1:
        results["3-2-(1)"] = (0.0, "오답 (괄호 설명 방법 명시 누락)")
    else:
        method = t1.group(1).replace(" ", "")
        if "예시" in method:
            if "벨라미" in m1:
                results["3-2-(1)"] = (1.5, "정답 (지문 속 명확한 예시 제시 완료)")
            else:
                results["3-2-(1)"] = (0.5, "부분점수 (예시 형식이나 구체적 작품명 누락)")
        else:
            results["3-2-(1)"] = (0.0, f"오답 ({method}의 특성 미구현)")

    m2 = normalize(s3_2_2)
    t2 = re.search(r'\(([^)]+)\)$', m2)
    if not t2:
        results["3-2-(2)"] = (0.0, "오답 (괄호 설명 방법 명시 누락)")
    else:
        method = t2.group(1).replace(" ", "")
        if "대조" in method:
            if check_keywords(m2, ["인간", "달리", "반면"]) and check_keywords(m2, ["감정", "철학"]):
                results["3-2-(2)"] = (1.5, "정답 (대조 차이 및 결론 통과)")
            else:
                results["3-2-(2)"] = (0.0, "오답 (인간과의 대조 핵심 가치 서술 오류)")
        else:
            results["3-2-(2)"] = (0.0, f"오답 ({method}의 특성 미구현)")

    # [서논술형 3] 총 6점 (각 요소 1.5점 배분)
    v_ans = normalize(s3_3_vis)
    if "실수 없는" in v_ans or "로봇" in v_ans:
        results["3-3-시각(1.5)"] = (0.0, "오답 ([장면1]의 로봇 특징 혼용)")
    elif check_keywords(v_ans, ["인간", "선수", "땀", "열정", "관객"]):
        results["3-3-시각(1.5)"] = (1.5, "정답")
    else:
        results["3-3-시각(1.5)"] = (0.0, "오답 (인간 선수의 열정 시각화 계획 누락)")
        
    v_eff = normalize(s3_3_vis_eff)
    if check_keywords(v_eff, ["노력", "열정", "경험", "관점"]):
        results["3-3-시각효과(1.5)"] = (1.5, "정답 (지문 근거 충족)")
    else:
        results["3-3-시각효과(1.5)"] = (0.0, "오답 (효과 부분 지문 속 인간 예술 특성 근거 누락)")

    a_ans = normalize(s3_3_aud)
    if "메트로놈" in a_ans or "기계음" in a_ans:
        results["3-3-청각(1.5)"] = (0.0, "오답 ([장면1]의 기계음 속성 혼용)")
    elif check_keywords(a_ans, ["따뜻한", "웅장한", "음악", "박수", "호흡"]):
        results["3-3-청각(1.5)"] = (1.5, "정답")
    else:
        results["3-3-청각(1.5)"] = (0.0, "오답 (감동을 유발하는 따뜻한 청각 연출 미흡)")
        
    a_eff = normalize(s3_3_aud_eff)
    if check_keywords(a_eff, ["울림", "감동"]):
        results["3-3-청각효과(1.5)"] = (1.5, "정답 (결론 방향 일치)")
    else:
        results["3-3-청각효과(1.5)"] = (0.0, "오답 (마음의 울림, 감동 선사 가치 누락)")

    for k, v in results.items():
        total += v[0]
    return total, results


# ================================================================
# Streamlit 화면 인터페이스 레이아웃 구성
# ================================================================
tabs = st.tabs(["[세트 1] 사회적 촉진/억제", "[세트 2] 정전기 비유", "[세트 3] AI 예술 공방"])

# ----------------------------------------------------------------
# TAB 1 인터페이스
# ----------------------------------------------------------------
with tabs[0]:
    st.header("실전 적용-1 학생 답안 입력란")
    st.markdown("---")
    st.subheader("[서·논술형 1] 표 채우기 요약")
    col1, col2, col3 = st.columns(3)
    s1_1_1 = col1.text_input("빈칸 (1) 입력", placeholder="예: 비교적 쉬운 과제", key="s111")
    s1_1_2 = col2.text_input("빈칸 (2) 입력", placeholder="예: 차분하게 혼자 집중하는 시간", key="s112")
    s1_1_3 = col3.text_input("빈칸 (3) 입력", placeholder="예: 사회적 억제", key="s113")
    
    st.subheader("[서·논술형 2] 이어지는 설명문 완성")
    st.caption("주어진 문장: 과제의 특성과 난이도에 따라 우리의 학습 효율을 높이는 방법은 다르게 적용되어야 한다.")
    s1_2_1 = st.text_input("(1) 첫 번째 이어질 문장 (설명 방법 포함)", placeholder="예: 쉬운 과제는 커피숍에서 하는 것이 좋다. (예시)", key="s121")
    s1_2_2 = st.text_input("(2) 두 번째 이어질 문장 (설명 방법 포함)", placeholder="예: 반면 어려운 과제는 혼자 집중해야 한다. (대조)", key="s122")
    
    st.subheader("[서·논술형 3] 스토리보드 영상 기획안")
    colA, colB = st.columns(2)
    s1_3_vis = colA.text_area("[장면2] 시각 요소 Ⓐ", placeholder="개인 독서실 책상에서 한 학생이 공부에 몰입함.", key="s13v")
    s1_3_vis_eff = colA.text_area("시각 요소 Ⓐ의 연출 효과", placeholder="혼자 차분히 집중해야 하는 환경을 강조한다.", key="s13ve")
    s1_3_aud = colB.text_area("[장면2] 청각 요소 Ⓑ", placeholder="배경음악을 소거하여 조용한 상태를 만듦.", key="s13a")
    s1_3_aud_eff = colB.text_area("청각 요소 Ⓑ의 연출 효과", placeholder="차분하게 집중할 수 있는 청각적 환경을 체감시킨다.", key="s13ae")
    
    if st.button("세트 1 답안 채점하기", type="primary"):
        total, res = grade_set1(s1_1_1, s1_1_2, s1_1_3, s1_2_1, s1_2_2, s1_3_vis, s1_3_vis_eff, s1_3_aud, s1_3_aud_eff)
        st.success(f"채점 완료! 총점: {total} / 10.0점")
        st.json(res)

# ----------------------------------------------------------------
# TAB 2 인터페이스
# ----------------------------------------------------------------
with tabs[1]:
    st.header("실전 적용-2 학생 답안 입력란")
    st.markdown("---")
    st.subheader("[서·논술형 1] 표 채우기 요약")
    col1, col2, col3 = st.columns(3)
    s2_1_1 = col1.text_input("빈칸 (1) 입력", placeholder="예: 높은 곳에 고여 있는 물", key="s211")
    s2_1_2 = col2.text_input("빈칸 (2) 입력", placeholder="예: 전하가 이동하지 않고 머물러 있음", key="s212")
    s2_1_3 = col3.text_input("빈칸 (3) 입력", placeholder="예: 위험하지 않음", key="s213")
    
    st.subheader("[서·논술형 2] 이어지는 설명문 완성")
    st.caption("주어진 문장: 겨울철에 흔히 겪는 정전기는 우리가 평소 집에서 사용하는 전기와는 다른 뚜렷한 특징이 있다.")
    s2_2_1 = st.text_input("(1) 첫 번째 이어질 문장 (설명 방법 포함)", placeholder="예: 정전기란 흐르지 않고 머물러 있는 전기를 뜻한다. (정의)", key="s221")
    s2_2_2 = st.text_input("(2) 두 번째 이어질 문장 (설명 방법 포함)", placeholder="예: 실생활 전기는 흐르지만 정전기는 고여 있는 물 같아서 위험하지 않다. (대조)", key="s222")
    
    st.subheader("[서·논술형 3] 스토리보드 영상 기획안")
    colA, colB = st.columns(2)
    s2_3_vis = colA.text_area("[장면2] 시각 요소 Ⓐ", key="s23v")
    s2_3_vis_eff = colA.text_area("시각 요소 Ⓐ의 연출 효과", key="s23ve")
    s2_3_aud = colB.text_area("[장면2] 청각 요소 Ⓑ", key="s23a")
    s2_3_aud_eff = colB.text_area("청각 요소 Ⓑ의 연출 효과", key="s23ae")
    
    if st.button("세트 2 답안 채점하기", type="primary"):
        total, res = grade_set2(s2_1_1, s2_1_2, s2_1_3, s2_2_1, s2_2_2, s2_3_vis, s2_3_vis_eff, s2_3_aud, s2_3_aud_eff)
        st.success(f"채점 완료! 총점: {total} / 10.0점")
        st.json(res)

# ----------------------------------------------------------------
# TAB 3 인터페이스
# ----------------------------------------------------------------
with tabs[2]:
    st.header("실전 적용-3 학생 답안 입력란")
    st.markdown("---")
    st.subheader("[서·논술형 1] 표 채우기 요약")
    col1, col2, col3 = st.columns(3)
    s3_1_1 = col1.text_input("빈칸 (1) 입력", placeholder="예: 로봇의 피겨 스케이팅 연기", key="s311")
    s3_1_2 = col2.text_input("빈칸 (2) 입력", placeholder="예: 감정이 없어 예술로 보기 어렵다", key="s312")
    s3_1_3 = col3.text_input("빈칸 (3) 입력", placeholder="예: 미술계 변화 및 예술 범주 확장", key="s313")
    
    st.subheader("[서·논술형 2] 이어지는 설명문 완성")
    st.caption("주어진 문장: 인공 지능이 그린 그림이 늘어나는 요즘, 우리는 이 작품들을 어떤 눈으로 바라봐야 할지 올바르게 생각해야 한다.")
    s3_2_1 = st.text_input("(1) 첫 번째 이어질 문장 (설명 방법 포함)", placeholder="예: 대표적인 AI 작품으로는 벨라미 백작 그림이 있다. (예시)", key="s321")
    s3_2_2 = st.text_input("(2) 두 번째 이어질 문장 (설명 방법 포함)", placeholder="예: 작가의 감정이 담긴 인간 예술과 달리 AI 예술은 감정이 없다. (대조)", key="s322")
    
    st.subheader("[서·논술형 3] 스토리보드 영상 기획안 [배점 6점]")
    colA, colB = st.columns(2)
    s3_3_vis = colA.text_area("[장면2] 시각 요소 Ⓐ", key="s33v")
    s3_3_vis_eff = colA.text_area("시각 요소 Ⓐ의 연출 효과", key="s33ve")
    s3_3_aud = colB.text_area("[장면2] 청각 요소 Ⓑ", key="s33a")
    s3_3_aud_eff = colB.text_area("청각 요소 Ⓑ의 연출 효과", key="s33ae")
    
    if st.button("세트 3 답안 채점하기", type="primary"):
        total, res = grade_set3(s3_1_1, s3_1_2, s3_1_3, s3_2_1, s3_2_2, s3_3_vis, s3_3_vis_eff, s3_3_aud, s3_3_aud_eff)
        st.success(f"채점 완료! 총점: {total} / 10.0점 (서논술형3 배점 6점 분할 적용됨)")
        st.json(res)
