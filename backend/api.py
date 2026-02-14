#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import traceback

# 경로
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

app = Flask(__name__)

# CORS 완전 허용
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"],
     supports_credentials=True)

# 환경변수에서 API 키 읽기
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get('GOOGLE_API_KEY')

if not API_KEY:
    print("❌ 오류: GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.")
    print("   .env 파일에 GOOGLE_API_KEY=your-key 를 추가하세요.")
    sys.exit(1)

print("\n" + "="*60)
print("🚀 서버 시작")
print("="*60)
print(f"🔑 API 키: {API_KEY[:20]}...")

# Gemini 로드
engine = None
try:
    from gemini_engine import GeminiTravelEngine
    engine = GeminiTravelEngine(api_key=API_KEY)
except Exception as e:
    print(f"❌ Gemini 로드 실패: {e}")
    traceback.print_exc()

# 프론트엔드
frontend = os.path.join(os.path.dirname(current_dir), 'frontend')
print(f"📁 프론트: {frontend}")
print("="*60 + "\n")


@app.after_request
def after_request(response):
    """모든 응답에 CORS 헤더 추가"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response


@app.route('/')
def index():
    """메인"""
    try:
        return send_from_directory(frontend, 'index.html')
    except:
        return """
        <h1>✅ 서버 실행 중</h1>
        <ul>
            <li><a href="/api/health">Health Check</a></li>
        </ul>
        """, 200


@app.route('/<path:filename>')
def files(filename):
    """정적 파일"""
    try:
        return send_from_directory(frontend, filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route('/api/health')
def health():
    """상태"""
    return jsonify({
        "status": "healthy",
        "engine": "Gemini 2.5 Flash Lite + 좌표 검증" if engine else "None"
    })


@app.route('/api/recommendations', methods=['POST', 'OPTIONS'])
def recommend():
    """추천 API"""
    
    # OPTIONS
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # 엔진 체크
        if not engine:
            return jsonify({
                "success": False,
                "error": "Gemini 엔진 없음"
            }), 500
        
        # 데이터
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "데이터 없음"
            }), 400
        
        keywords = data.get('keywords', {})
        region = data.get('region', '전체')
        
        print(f"\n📥 요청: {region}")
        print(f"   키워드: {keywords}")
        
        # Gemini 호출 (좌표 검증 포함)
        count = 5 if region == '전체' else 8
        destinations = engine.generate_destinations(
            keywords=keywords,
            selected_region=region,
            count=count
        )
        
        # 매칭률 계산
        for dest in destinations:
            score = 55
            
            # 스타일
            if keywords.get("여행_스타일"):
                s = dest.get("scores", {}).get("여행_스타일", {}).get(keywords["여행_스타일"], 0)
                score += s * 0.2
            
            # 동행
            if keywords.get("동행"):
                s = dest.get("scores", {}).get("동행", {}).get(keywords["동행"], 0)
                score += s * 0.15
            
            # 테마
            if keywords.get("테마"):
                scores = []
                for t in keywords["테마"]:
                    s = dest.get("scores", {}).get("테마", {}).get(t, 0)
                    scores.append(s)
                if scores:
                    score += (sum(scores) / len(scores)) * 0.4
            
            # 페이스
            if keywords.get("페이스"):
                s = dest.get("scores", {}).get("페이스", {}).get(keywords["페이스"], 0)
                score += s * 0.1
            
            # 교통
            if keywords.get("교통"):
                s = dest.get("scores", {}).get("교통", {}).get(keywords["교통"], 0)
                score += s * 0.1
            
            # 분위기
            if keywords.get("분위기"):
                scores = []
                for v in keywords["분위기"]:
                    s = dest.get("scores", {}).get("분위기", {}).get(v, 0)
                    scores.append(s)
                if scores:
                    score += (sum(scores) / len(scores)) * 0.05
            
            dest['matchScore'] = min(98, max(72, int(score)))
        
        # 정렬
        destinations.sort(key=lambda x: x.get('matchScore', 0), reverse=True)
        
        print(f"✅ {len(destinations)}개 반환")
        for i, d in enumerate(destinations[:3], 1):
            print(f"   {i}. {d.get('city', '?')} - {d.get('matchScore', 0)}%")
        print()
        
        return jsonify({
            "success": True,
            "data": destinations[:8],
            "count": len(destinations[:8]),
            "mode": "AI + 좌표검증"
        })
    
    except Exception as e:
        print(f"❌ 오류: {e}")
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(500)
def error(e):
    return jsonify({"error": "Server Error"}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("✨ 준비 완료")
    print("="*60)
    print("🌐 http://localhost:5000")
    print("📡 http://localhost:5000/api/recommendations")
    print("💊 http://localhost:5000/api/health")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )