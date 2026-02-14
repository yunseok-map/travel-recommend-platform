#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gemini API - 좌표 검증 강화 버전
모델: gemini-2.5-flash-lite
"""

import requests
import json
from typing import Dict, List

class GeminiTravelEngine:
    """Gemini REST API + 좌표 검증"""
    
    # 지역별 실제 좌표 범위
    REGION_COORDS = {
        "강원": {"lat": (37.1, 38.6), "lng": (127.7, 129.4), "center": (37.8, 128.5)},
        "경기": {"lat": (36.9, 38.3), "lng": (126.4, 127.9), "center": (37.5, 127.2)},
        "충청": {"lat": (36.0, 37.5), "lng": (126.3, 128.5), "center": (36.6, 127.4)},
        "전라": {"lat": (34.4, 36.0), "lng": (126.1, 127.8), "center": (35.2, 126.9)},
        "경상": {"lat": (34.6, 36.9), "lng": (128.0, 129.5), "center": (35.8, 128.7)},
        "부산": {"lat": (35.0, 35.4), "lng": (128.9, 129.3), "center": (35.2, 129.1)},
        "제주": {"lat": (33.1, 33.6), "lng": (126.1, 126.9), "center": (33.4, 126.5)},
        "전체": {"lat": (33.0, 38.6), "lng": (126.0, 130.0), "center": (36.5, 127.5)}
    }
    
    # 도시별 실제 중심 좌표
    CITY_COORDS = {
        # 강원
        "강릉": (37.7519, 128.8761),
        "속초": (38.2070, 128.5918),
        "양양": (38.0754, 128.6190),
        "평창": (37.3709, 128.3906),
        "정선": (37.3807, 128.6608),
        "동해": (37.5247, 129.1144),
        
        # 경기
        "가평": (37.8314, 127.5095),
        "양평": (37.4914, 127.4949),
        "수원": (37.2636, 127.0286),
        "파주": (37.7599, 126.7800),
        "포천": (38.0314, 127.2003),
        "이천": (37.2722, 127.4350),
        
        # 충청
        "단양": (36.9846, 128.3659),
        "충주": (36.9910, 127.9260),
        "천안": (36.8151, 127.1139),
        "공주": (36.4465, 127.1189),
        "보령": (36.3334, 126.6129),
        "태안": (36.7456, 126.2981),
        
        # 전라
        "전주": (35.8242, 127.1480),
        "순천": (34.9506, 127.4872),
        "여수": (34.7604, 127.6622),
        "담양": (35.3209, 126.9882),
        "보성": (34.7714, 127.0800),
        "군산": (35.9676, 126.7369),
        
        # 경상
        "경주": (35.8562, 129.2247),
        "안동": (36.5684, 128.7294),
        "포항": (36.0190, 129.3435),
        "울산": (35.5384, 129.3114),
        "통영": (34.8544, 128.4331),
        "거제": (34.8806, 128.6214),
        
        # 부산
        "부산": (35.1796, 129.0756),
        "해운대": (35.1585, 129.1603),
        "광안리": (35.1532, 129.1187),
        "송도": (35.0757, 129.0177),
        "기장": (35.2445, 129.2219),
        
        # 제주
        "제주": (33.4996, 126.5312),
        "제주시": (33.4996, 126.5312),
        "서귀포": (33.2541, 126.5601),
        "애월": (33.4672, 126.3319),
        "성산": (33.4547, 126.8806),
        "한림": (33.4114, 126.2691)
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.5-flash-lite"
        
        print(f"✅ Gemini API 초기화 완료 (model: {self.model})")
    
    def generate_destinations(self, keywords: Dict, selected_region: str = "전체", count: int = 5) -> List[Dict]:
        """여행지 생성 + 좌표 검증"""
        
        actual_count = min(max(count, 3), 5)
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                print(f"\n🤖 Gemini 호출 (시도 {attempt + 1}/{max_retries})")
                print(f"   모델: {self.model}")
                print(f"   지역: {selected_region}, 개수: {actual_count}")
                
                prompt = self._build_prompt(selected_region, actual_count, keywords)
                
                # v1 API 호출
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
                    print(f"❌ API 오류 {response.status_code}:")
                    print(f"   {json.dumps(error_detail, indent=2, ensure_ascii=False)[:500]}")
                    
                    if attempt < max_retries - 1:
                        continue
                    raise Exception(f"API 오류: {response.status_code}")
                
                result = response.json()
                
                # 응답 구조 확인
                if 'candidates' not in result or len(result['candidates']) == 0:
                    print(f"❌ 응답 형식 오류")
                    if attempt < max_retries - 1:
                        continue
                    raise Exception("응답 형식 오류")
                
                # 텍스트 추출
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"📨 응답 받음: {len(text)}자")
                
                # JSON 파싱
                destinations = self._parse_json(text)
                
                if destinations and len(destinations) >= 2:
                    # ✅ 좌표 검증 및 보정
                    destinations = self._validate_and_fix_coords(destinations, selected_region)
                    
                    for i, dest in enumerate(destinations):
                        dest['id'] = i + 1
                    
                    print(f"✅ 성공! {len(destinations)}개 생성")
                    for i, d in enumerate(destinations[:3], 1):
                        city = d.get('city', '?')
                        lat = d.get('centerLat', 0)
                        lng = d.get('centerLng', 0)
                        print(f"   {i}. {city} ({lat:.4f}, {lng:.4f})")
                    
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
        
        # 모든 시도 실패
        print("❌ 모든 시도 실패")
        raise Exception("여행지 생성 실패. API 키와 모델명을 확인해주세요.")
    
    def _validate_and_fix_coords(self, destinations: List[Dict], region: str) -> List[Dict]:
        """좌표 검증 및 보정"""
        
        print("\n🔍 좌표 검증 시작...")
        
        region_data = self.REGION_COORDS.get(region, self.REGION_COORDS["전체"])
        lat_range = region_data["lat"]
        lng_range = region_data["lng"]
        
        for dest in destinations:
            city = dest.get('city', '')
            
            # 1. 도시 중심 좌표 설정
            if city in self.CITY_COORDS:
                real_lat, real_lng = self.CITY_COORDS[city]
                dest['centerLat'] = real_lat
                dest['centerLng'] = real_lng
                print(f"   ✓ {city}: 실제 좌표 적용 ({real_lat:.4f}, {real_lng:.4f})")
            else:
                # 도시가 DB에 없으면 지역 중심 좌표 사용
                dest['centerLat'] = region_data["center"][0]
                dest['centerLng'] = region_data["center"][1]
                print(f"   ⚠ {city}: 지역 중심 좌표 사용")
            
            # 2. 스팟 좌표 검증
            if 'spots' in dest:
                for i, spot in enumerate(dest['spots']):
                    spot_lat = spot.get('lat', 0)
                    spot_lng = spot.get('lng', 0)
                    
                    # 좌표가 범위 밖이거나 예시 좌표(37.5, 127.0)인 경우
                    is_invalid = (
                        spot_lat < lat_range[0] or spot_lat > lat_range[1] or
                        spot_lng < lng_range[0] or spot_lng > lng_range[1] or
                        (abs(spot_lat - 37.5) < 0.01 and abs(spot_lng - 127.0) < 0.01) or
                        spot_lat == 0 or spot_lng == 0
                    )
                    
                    if is_invalid:
                        # 도시 중심 주변으로 분산 배치
                        import random
                        offset_lat = random.uniform(-0.05, 0.05)
                        offset_lng = random.uniform(-0.05, 0.05)
                        spot['lat'] = dest['centerLat'] + offset_lat
                        spot['lng'] = dest['centerLng'] + offset_lng
                        print(f"      ⚠ {spot.get('name', '?')}: 좌표 보정 ({spot['lat']:.4f}, {spot['lng']:.4f})")
        
        print("✅ 좌표 검증 완료\n")
        return destinations
    
    def _parse_json(self, text: str) -> List[Dict]:
        """JSON 파싱"""
        
        # 방법 1: 직접 파싱
        try:
            result = json.loads(text)
            if isinstance(result, list) and len(result) > 0:
                print(f"   ✅ JSON 파싱 성공 (직접)")
                return result
        except:
            pass
        
        # 방법 2: 마크다운 제거
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
        
        # 방법 3: [ ] 추출
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
        print(f"   응답 앞부분: {text[:500]}")
        return None
    
    def _build_prompt(self, region: str, count: int, keywords: Dict) -> str:
        """프롬프트 생성 - 좌표 강화"""
        
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
        
        # 지역별 실제 좌표 예시
        coord_examples = self._get_coord_examples(region)
        
        return f"""당신은 한국 여행 전문가입니다. 아래 조건에 맞는 여행지를 JSON 배열로만 출력하세요.

**조건:**
- 지역: {region} (도시: {cities})
- 개수: {count}개
- 사용자 선호: {kw}
- 페이스: {pace} → 각 여행지당 {min_spots}-{max_spots}개 스팟

**🚨 좌표 입력 필수 규칙 🚨**
1. **실제 장소의 정확한 좌표만 사용**
2. **예시 좌표 절대 금지**: 37.5, 127.0 같은 둥근 숫자 사용 금지
3. **소수점 4자리 이상** (예: 37.7519, 128.8761)
4. **{region} 지역 좌표 범위**: {self._get_coord_range(region)}
5. **실제 좌표 예시**: {coord_examples}

**출력 형식 (실제 좌표 예시):**
[
{{
  "city": "강릉",
  "region": "{region}",
  "description": "여유로운 카페 투어와 바다",
  "scores": {{
    "여행_스타일": {{"계획형": 65, "즉흥형": 85, "중간형": 80}},
    "동행": {{"솔로": 90, "친구": 85, "커플": 95, "가족": 80, "단체": 65}},
    "테마": {{"맛집": 80, "카페": 95, "로컬": 75, "감성": 90, "액티비티": 70, "휴양": 95, "문화예술": 60, "쇼핑": 50, "자연": 85}},
    "페이스": {{"여유": 95, "적당": 80, "빡빡": 50}},
    "교통": {{"대중교통": 65, "자차": 90, "도보": 70}},
    "분위기": {{"핫플": 85, "한적": 80, "이색": 70, "전통": 60, "트렌디": 75}}
  }},
  "quickInfo": {{
    "location": "강원 강릉시",
    "duration": "1박 2일",
    "parking": "편리함",
    "budget": "15-20만원/인"
  }},
  "spots": [
    {{"name": "안목해변 커피거리", "category": "카페", "parking": true, "tip": "바다뷰 추천", "lat": 37.7714, "lng": 128.9469, "description": "동해를 보며 커피 한잔"}},
    {{"name": "테라로사 커피공장", "category": "카페", "parking": true, "tip": "원두 구매 가능", "lat": 37.6852, "lng": 128.8531, "description": "로스터리 카페"}},
    {{"name": "경포대", "category": "자연", "parking": true, "tip": "일출 명소", "lat": 37.7955, "lng": 128.9085, "description": "강릉 대표 해변"}}
  ],
  "tips": ["카페 투어 최적", "자차 이동 편리"],
  "avgRating": 4.8,
  "centerLat": 37.7519,
  "centerLng": 128.8761,
  "coverImage": "https://loremflickr.com/800/600/gangneung,korea"
}}
]

**반드시:**
- lat, lng는 소수점 4자리 이상
- 실제 장소 좌표만 사용
- 37.5, 127.0 같은 예시 좌표 금지
- {min_spots}-{max_spots}개 스팟

순수 JSON 배열만 출력!"""
    
    def _get_coord_examples(self, region: str) -> str:
        """지역별 실제 좌표 예시"""
        examples = {
            "강원": "강릉(37.7519, 128.8761), 속초(38.2070, 128.5918)",
            "경기": "가평(37.8314, 127.5095), 수원(37.2636, 127.0286)",
            "충청": "단양(36.9846, 128.3659), 공주(36.4465, 127.1189)",
            "전라": "전주(35.8242, 127.1480), 여수(34.7604, 127.6622)",
            "경상": "경주(35.8562, 129.2247), 통영(34.8544, 128.4331)",
            "부산": "해운대(35.1585, 129.1603), 광안리(35.1532, 129.1187)",
            "제주": "제주시(33.4996, 126.5312), 서귀포(33.2541, 126.5601)"
        }
        return examples.get(region, "서울(37.5665, 126.9780), 부산(35.1796, 129.0756)")
    
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
    
    def _get_coord_range(self, region: str) -> str:
        """지역별 좌표 범위"""
        ranges = {
            "강원": "위도 37.1-38.6, 경도 127.7-129.4",
            "경기": "위도 36.9-38.3, 경도 126.4-127.9",
            "충청": "위도 36.0-37.5, 경도 126.3-128.5",
            "전라": "위도 34.4-36.0, 경도 126.1-127.8",
            "경상": "위도 34.6-36.9, 경도 128.0-129.5",
            "부산": "위도 35.0-35.4, 경도 128.9-129.3",
            "제주": "위도 33.1-33.6, 경도 126.1-126.9"
        }
        return ranges.get(region, "대한민국 전역")