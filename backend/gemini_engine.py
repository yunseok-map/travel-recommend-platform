#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gemini API - 지도 없는 버전 (좌표 불필요)
식당 추천 강화
"""

import requests
import json
from typing import Dict, List

class GeminiTravelEngine:
    """Gemini REST API - 식당 상세 추천"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.5-flash-lite"
        
        print(f"✅ Gemini API 초기화 완료 (model: {self.model})")
    
    def generate_destinations(self, keywords: Dict, selected_region: str = "전체", count: int = 5) -> List[Dict]:
        """여행지 생성 - 식당 정보 강화"""
        
        actual_count = min(max(count, 3), 5)
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                print(f"\n🤖 Gemini 호출 (시도 {attempt + 1}/{max_retries})")
                print(f"   모델: {self.model}")
                print(f"   지역: {selected_region}, 개수: {actual_count}")
                
                prompt = self._build_prompt(selected_region, actual_count, keywords)
                
                url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.9,
                        "maxOutputTokens": 16384,
                        "topP": 0.95,
                        "topK": 64
                    }
                }
                
                headers = {
                    "Content-Type": "application/json"
                }
                
                print(f"   📡 요청중...")
                
                response = requests.post(url, json=payload, headers=headers, timeout=60)
                
                if response.status_code != 200:
                    error_detail = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                    print(f"❌ API 오류 {response.status_code}")
                    
                    if attempt < max_retries - 1:
                        continue
                    raise Exception(f"API 오류: {response.status_code}")
                
                result = response.json()
                
                if 'candidates' not in result or len(result['candidates']) == 0:
                    print(f"❌ 응답 형식 오류")
                    if attempt < max_retries - 1:
                        continue
                    raise Exception("응답 형식 오류")
                
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"📨 응답 받음: {len(text)}자")
                
                destinations = self._parse_json(text)
                
                if destinations and len(destinations) >= 2:
                    for i, dest in enumerate(destinations):
                        dest['id'] = i + 1
                    
                    print(f"✅ 성공! {len(destinations)}개 생성")
                    for i, d in enumerate(destinations[:3], 1):
                        city = d.get('city', '?')
                        print(f"   {i}. {city}")
                    
                    return destinations
                else:
                    print(f"⚠️  결과 부족 ({len(destinations) if destinations else 0}개), 재시도...")
                    
            except requests.exceptions.Timeout:
                print(f"❌ 시도 {attempt + 1} 타임아웃")
                if attempt < max_retries - 1:
                    continue
            except Exception as e:
                print(f"❌ 시도 {attempt + 1} 실패: {e}")
                if attempt < max_retries - 1:
                    continue
        
        print("❌ 모든 시도 실패")
        raise Exception("여행지 생성 실패. API 키와 모델명을 확인해주세요.")
    
    def _parse_json(self, text: str) -> List[Dict]:
        """JSON 파싱"""
        
        # 직접 파싱
        try:
            result = json.loads(text)
            if isinstance(result, list) and len(result) > 0:
                print(f"   ✅ JSON 파싱 성공 (직접)")
                return result
        except:
            pass
        
        # 마크다운 제거
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split('\n')
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned = '\n'.join(lines)
            
            result = json.loads(cleaned.strip())
            if isinstance(result, list) and len(result) > 0:
                print(f"   ✅ JSON 파싱 성공 (정리 후)")
                return result
        except:
            pass
        
        # [ ] 추출
        try:
            start = text.find('[')
            end = text.rfind(']')
            if start != -1 and end != -1 and end > start:
                json_str = text[start:end+1]
                result = json.loads(json_str)
                if isinstance(result, list) and len(result) > 0:
                    print(f"   ✅ JSON 파싱 성공 (배열 추출)")
                    return result
        except:
            pass
        
        print("   ❌ JSON 파싱 실패")
        return None
    
    def _build_prompt(self, region: str, count: int, keywords: Dict) -> str:
        """프롬프트 생성 - 식당 정보 강화, 좌표 제거"""
        
        kw = self._format_keywords(keywords)
        cities = self._get_cities(region)
        
        # 페이스에 따른 스팟 개수
        pace = keywords.get("페이스", "적당")
        
        if pace == "여유":
            min_spots, max_spots = 2, 3
        elif pace == "빡빡":
            min_spots, max_spots = 6, 8
        else:
            min_spots, max_spots = 4, 5
        
        return f"""당신은 한국 여행 전문가입니다. 아래 조건에 맞는 여행지를 JSON 배열로만 출력하세요.

**조건:**
- 지역: {region} (도시: {cities})
- 개수: {count}개
- 사용자 선호: {kw}
- 페이스: {pace} → 각 여행지당 {min_spots}-{max_spots}개 스팟

**중요 규칙:**
1. 순수 JSON 배열만 출력 (설명, 주석, 마크다운 금지)
2. 각 여행지는 서로 다른 도시여야 함
3. {region} 지역 내의 실제 도시만 추천
4. 반드시 {count}개 생성
5. **좌표 불필요** (lat, lng 필드 제거)

**🍽️ 식당 추천 강화 규칙:**
- 스팟 중 최소 2개는 **실제 식당명**으로 추천
- 식당 정보에 다음 포함:
  * 대표 메뉴 (예: "간장게장 정식")
  * 가격대 (예: "1인 2만원대")
  * 영업시간 (예: "11:00-21:00")
  * 예약 필요 여부
  * 웨이팅 정보
- 식당은 실제 존재하는 유명 맛집으로만 추천
- 지역 특산 음식 중심으로 추천

**출력 형식:**
[
{{
  "city": "전주",
  "region": "{region}",
  "description": "한옥마을과 비빔밥의 도시",
  "scores": {{
    "여행_스타일": {{"계획형": 70, "즉흥형": 85, "중간형": 80}},
    "동행": {{"솔로": 80, "친구": 90, "커플": 85, "가족": 95, "단체": 85}},
    "테마": {{"맛집": 95, "카페": 80, "로컬": 90, "감성": 85, "액티비티": 65, "휴양": 60, "문화예술": 85, "쇼핑": 70, "자연": 70}},
    "페이스": {{"여유": 85, "적당": 90, "빡빡": 70}},
    "교통": {{"대중교통": 80, "자차": 90, "도보": 85}},
    "분위기": {{"핫플": 90, "한적": 60, "이색": 75, "전통": 95, "트렌디": 80}}
  }},
  "quickInfo": {{
    "location": "전북 전주시",
    "duration": "1박 2일",
    "parking": "보통 (한옥마을 주변 유료주차)",
    "budget": "15-20만원/인"
  }},
  "spots": [
    {{
      "name": "한국집",
      "category": "맛집",
      "parking": true,
      "description": "전주 비빔밥 원조 맛집",
      "menu": "비빔밥 정식 (15,000원)",
      "price": "1인 1.5만원",
      "hours": "11:00-21:00 (브레이크타임 15:00-17:00)",
      "reservation": "예약 가능",
      "waiting": "점심시간 30분 웨이팅",
      "tip": "오픈런 추천, 콩나물국밥도 유명"
    }},
    {{
      "name": "삼백집",
      "category": "맛집",
      "parking": false,
      "description": "100년 전통 콩나물국밥",
      "menu": "콩나물국밥 (7,000원)",
      "price": "1인 7천원",
      "hours": "06:00-20:00",
      "reservation": "불가",
      "waiting": "평일 10분, 주말 20분",
      "tip": "아침 일찍 방문 추천"
    }},
    {{
      "name": "전주한옥마을",
      "category": "문화예술",
      "parking": false,
      "description": "한옥 700여 채가 모여있는 전통마을",
      "tip": "야간 조명이 아름다움, 도보 이동 권장"
    }},
    {{
      "name": "경기전",
      "category": "문화예술",
      "parking": true,
      "description": "조선 태조 이성계의 어진을 모신 곳",
      "tip": "입장료 3,000원"
    }}
  ],
  "restaurants": [
    {{
      "name": "한국집",
      "specialty": "비빔밥",
      "mustTry": "전주비빔밥 정식",
      "priceRange": "15,000-20,000원",
      "address": "전북 전주시 완산구 태조로 119",
      "reservationTip": "예약 필수, 웨이팅 30분"
    }},
    {{
      "name": "삼백집",
      "specialty": "콩나물국밥",
      "mustTry": "콩나물국밥 + 수육",
      "priceRange": "7,000-15,000원",
      "address": "전북 전주시 완산구 풍남동3가",
      "reservationTip": "예약 불가, 오픈 직후 방문 권장"
    }}
  ],
  "tips": [
    "한옥마을은 도보로 이동하는 것이 편리",
    "비빔밥 맛집은 대부분 점심시간 웨이팅 있음",
    "전동성당-경기전-한옥마을 코스 추천",
    "저녁에는 야시장 즐기기"
  ],
  "avgRating": 4.8,
  "coverImage": "https://loremflickr.com/800/600/jeonju,korea"
}}
]

**반드시:**
- lat, lng 필드 제거 (좌표 불필요)
- {min_spots}-{max_spots}개 스팟
- 최소 2개 이상 실제 식당 추천
- 식당마다 메뉴, 가격, 시간, 예약 정보 포함
- restaurants 배열에 상세 식당 정보 추가

순수 JSON 배열만 출력!"""
    
    def _format_keywords(self, kw: Dict) -> str:
        """키워드 문자열"""
        parts = []
        if kw.get("여행_스타일"): parts.append(kw["여행_스타일"])
        if kw.get("동행"): parts.append(kw["동행"])
        if kw.get("테마"): parts.extend(kw["테마"])
        if kw.get("페이스"): parts.append(kw["페이스"])
        if kw.get("교통"): parts.append(kw["교통"])
        if kw.get("분위기"): parts.extend(kw["분위기"])
        return ", ".join(parts) if parts else "자유여행"
    
    def _get_cities(self, region: str) -> str:
        """지역별 도시"""
        data = {
            "강원": "강릉, 속초, 양양, 평창, 정선, 동해",
            "경기": "가평, 양평, 수원, 파주, 포천, 이천",
            "충청": "단양, 충주, 천안, 공주, 보령, 태안",
            "전라": "전주, 순천, 여수, 담양, 보성, 군산",
            "경상": "경주, 안동, 포항, 울산, 통영, 거제",
            "부산": "해운대, 광안리, 송도, 기장, 남포동",
            "제주": "제주시, 서귀포, 애월, 성산, 한림"
        }
        return data.get(region, "전국 주요 도시")