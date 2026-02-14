// 전역 상태 관리
const state = {
    currentStep: 0,
    maxStep: 4,
    selectedRegion: '전체',
    keywords: {
        여행_스타일: null,
        동행: null,
        테마: [],
        페이스: null,
        교통: null,
        분위기: []
    },
    recommendations: []
};

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    updateProgress();
});

// 이벤트 리스너 초기화
function initializeEventListeners() {
    // 지역 선택 버튼
    document.querySelectorAll('[data-step="0"] .region-card').forEach(btn => {
        btn.addEventListener('click', () => selectRegion(btn));
    });

    // 단일 선택 옵션 버튼
    document.querySelectorAll('.option-card:not(.multi-select)').forEach(btn => {
        const category = btn.dataset.category;
        if (category && category !== 'region') {
            btn.addEventListener('click', () => selectSingleOption(btn));
        }
    });

    // 다중 선택 옵션 버튼  
    document.querySelectorAll('.option-card.multi-select').forEach(btn => {
        btn.addEventListener('click', () => selectMultiOption(btn));
    });
}

// 여행 시작하기
function startSelection() {
    document.getElementById('hero-section').classList.add('hidden');
    document.getElementById('selection-section').classList.remove('hidden');
}

// 지역 선택
function selectRegion(button) {
    // 기존 선택 해제
    document.querySelectorAll('[data-step="0"] .region-card').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // 새로운 선택
    button.classList.add('selected');
    state.selectedRegion = button.dataset.value;
    
    console.log('선택된 지역:', state.selectedRegion);
}

// 단일 선택 옵션
function selectSingleOption(button) {
    const category = button.dataset.category;
    const value = button.dataset.value;
    const step = button.closest('.step-content');
    
    // 같은 카테고리의 다른 버튼 선택 해제
    step.querySelectorAll(`[data-category="${category}"]:not(.multi-select)`).forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // 새로운 선택
    button.classList.add('selected');
    state.keywords[category] = value;
    
    console.log('선택됨:', category, value);
}

// 다중 선택 옵션
function selectMultiOption(button) {
    const category = button.dataset.category;
    const value = button.dataset.value;
    const maxCount = category === '테마' ? 3 : 2;
    
    // 현재 선택된 개수 확인
    const currentSelected = state.keywords[category].length;
    
    if (button.classList.contains('selected')) {
        // 선택 해제
        button.classList.remove('selected');
        const index = state.keywords[category].indexOf(value);
        if (index > -1) {
            state.keywords[category].splice(index, 1);
        }
    } else {
        // 선택
        if (currentSelected < maxCount) {
            button.classList.add('selected');
            state.keywords[category].push(value);
        } else {
            alert(`최대 ${maxCount}개까지 선택 가능합니다.`);
        }
    }
    
    // 테마 카운터 업데이트
    if (category === '테마') {
        document.getElementById('theme-count').textContent = state.keywords.테마.length;
    }
    
    console.log('다중 선택:', category, state.keywords[category]);
}

// 다음 스텝
function nextStep() {
    // 현재 스텝 유효성 검사
    if (!validateCurrentStep()) {
        return;
    }
    
    if (state.currentStep < state.maxStep) {
        state.currentStep++;
        updateStepDisplay();
        updateProgress();
        updateButtons();
        scrollToTop();
    }
}

// 이전 스텝
function prevStep() {
    if (state.currentStep > 0) {
        state.currentStep--;
        updateStepDisplay();
        updateProgress();
        updateButtons();
        scrollToTop();
    }
}

// 현재 스텝 유효성 검사
function validateCurrentStep() {
    const step = state.currentStep;
    
    // Step 0: 지역 (선택 안 해도 됨 - 전체로 자동 설정)
    if (step === 0) {
        if (!state.selectedRegion) {
            state.selectedRegion = '전체';
        }
        return true;
    }
    
    // Step 1: 여행 스타일
    if (step === 1) {
        if (!state.keywords.여행_스타일) {
            alert('여행 스타일을 선택해주세요.');
            return false;
        }
    }
    
    // Step 2: 동행
    if (step === 2) {
        if (!state.keywords.동행) {
            alert('동행을 선택해주세요.');
            return false;
        }
    }
    
    // Step 3: 테마
    if (step === 3) {
        if (state.keywords.테마.length === 0) {
            alert('테마를 최소 1개 선택해주세요.');
            return false;
        }
    }
    
    // Step 4: 세부 옵션
    if (step === 4) {
        if (!state.keywords.페이스 || !state.keywords.교통) {
            alert('여행 페이스와 교통수단을 선택해주세요.');
            return false;
        }
    }
    
    return true;
}

// 스텝 디스플레이 업데이트
function updateStepDisplay() {
    document.querySelectorAll('.step-content').forEach((content, index) => {
        if (index === state.currentStep) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
}

// 진행률 업데이트
function updateProgress() {
    document.querySelectorAll('.progress-step').forEach((step, index) => {
        if (index <= state.currentStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

// 버튼 상태 업데이트
function updateButtons() {
    const prevBtn = document.querySelector('.btn-prev');
    const nextBtn = document.querySelector('.btn-next');
    const submitBtn = document.querySelector('.btn-submit');
    
    // 이전 버튼
    prevBtn.disabled = state.currentStep === 0;
    
    // 다음/제출 버튼
    if (state.currentStep === state.maxStep) {
        nextBtn.classList.add('hidden');
        submitBtn.classList.remove('hidden');
    } else {
        nextBtn.classList.remove('hidden');
        submitBtn.classList.add('hidden');
    }
}

// 키워드 제출
async function submitKeywords() {
    // 최종 유효성 검사
    if (!validateCurrentStep()) {
        return;
    }
    
    // 로딩 표시
    document.getElementById('loading').classList.remove('hidden');
    
    try {
        // API 호출 - 키워드와 지역 정보 함께 전송
        const response = await fetch('/api/recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                keywords: state.keywords,
                region: state.selectedRegion
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            state.recommendations = result.data;
            displayResults();
        } else {
            alert('추천 결과를 가져오는데 실패했습니다: ' + result.error);
        }
    } catch (error) {
        console.error('API 호출 오류:', error);
        alert('서버와 통신 중 오류가 발생했습니다.');
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
}

// 결과 표시
function displayResults() {
    // 화면 전환
    document.getElementById('selection-section').classList.add('hidden');
    document.getElementById('results-section').classList.remove('hidden');
    
    // 선택된 키워드 표시
    displaySelectedKeywords();
    
    // 결과 리스트 표시
    displayRecommendationList();
    
    scrollToTop();
}

// 선택된 키워드 표시
function displaySelectedKeywords() {
    const container = document.getElementById('selected-keywords');
    const keywords = [];
    
    // 지역
    if (state.selectedRegion && state.selectedRegion !== '전체') {
        keywords.push(state.selectedRegion);
    }
    
    // 나머지 키워드
    Object.entries(state.keywords).forEach(([key, value]) => {
        if (Array.isArray(value)) {
            keywords.push(...value);
        } else if (value) {
            keywords.push(value);
        }
    });
    
    container.innerHTML = keywords.map(keyword => 
        `<span class="keyword-tag">${keyword}</span>`
    ).join('');
}

// 추천 리스트 표시
function displayRecommendationList() {
    const container = document.getElementById('results-list');
    
    if (state.recommendations.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-gray);">조건에 맞는 여행지가 없습니다. 다른 키워드로 다시 시도해보세요.</p>';
        return;
    }
    
    container.innerHTML = state.recommendations.map(dest => `
        <div class="result-card" onclick="showDetail(${dest.id})">
            <img src="${dest.coverImage}" alt="${dest.city}" class="result-image" onerror="this.src='https://via.placeholder.com/400x300?text=${dest.city}'">
            <div class="result-content">
                <div class="result-header">
                    <div>
                        <div class="result-city">${dest.city}</div>
                        <div class="result-region">${dest.region}</div>
                    </div>
                    <div class="match-score">${dest.matchScore}%</div>
                </div>
                <div class="result-description">${dest.description}</div>
                <div class="result-tags">
                    ${getTopTags(dest).map(tag => `<span class="tag">${tag}</span>`).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

// 상위 태그 가져오기
function getTopTags(destination) {
    const tags = [];
    
    // 점수가 높은 카테고리 추출
    Object.entries(destination.scores).forEach(([category, scores]) => {
        if (typeof scores === 'object') {
            const topScore = Object.entries(scores)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 2);
            tags.push(...topScore.map(([key, _]) => key));
        }
    });
    
    return tags.slice(0, 4);
}

// 상세 정보 표시 (지도 없는 버전)
async function showDetail(destId) {
    const destination = state.recommendations.find(d => d.id === destId);
    if (!destination) return;
    
    const modal = document.getElementById('detail-modal');
    const body = document.getElementById('modal-body');
    
    body.innerHTML = `
        <div style="position: relative;">
            <img src="${destination.coverImage}" style="width: 100%; height: 300px; object-fit: cover; border-radius: 16px 16px 0 0;" alt="${destination.city}">
            <div style="padding: 40px;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 24px;">
                    <div>
                        <h2 style="font-size: 36px; font-weight: 700; margin-bottom: 8px;">${destination.city}</h2>
                        <p style="font-size: 16px; color: var(--text-gray);">${destination.region}</p>
                    </div>
                    <div style="background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; padding: 12px 24px; border-radius: 24px; font-size: 18px; font-weight: 700;">
                        ${destination.matchScore}% 매칭
                    </div>
                </div>
                
                <div style="background: var(--bg-light); padding: 24px; border-radius: 12px; margin-bottom: 32px;">
                    <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 16px;">✨ 왜 추천하나요?</h3>
                    <p style="color: var(--text-gray); line-height: 1.8;">${destination.description}</p>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 32px;">
                    <div style="background: var(--bg-light); padding: 16px; border-radius: 12px;">
                        <div style="font-size: 14px; color: var(--text-gray); margin-bottom: 4px;">📍 위치</div>
                        <div style="font-weight: 600;">${destination.quickInfo.location}</div>
                    </div>
                    <div style="background: var(--bg-light); padding: 16px; border-radius: 12px;">
                        <div style="font-size: 14px; color: var(--text-gray); margin-bottom: 4px;">⏱️ 추천 기간</div>
                        <div style="font-weight: 600;">${destination.quickInfo.duration}</div>
                    </div>
                    <div style="background: var(--bg-light); padding: 16px; border-radius: 12px;">
                        <div style="font-size: 14px; color: var(--text-gray); margin-bottom: 4px;">🚗 주차</div>
                        <div style="font-weight: 600;">${destination.quickInfo.parking}</div>
                    </div>
                    <div style="background: var(--bg-light); padding: 16px; border-radius: 12px;">
                        <div style="font-size: 14px; color: var(--text-gray); margin-bottom: 4px;">💰 예상 경비</div>
                        <div style="font-weight: 600;">${destination.quickInfo.budget}</div>
                    </div>
                </div>
                
                <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 16px;">📍 추천 스팟</h3>
                
                <div style="display: grid; gap: 16px; margin-bottom: 32px;">${destination.spots.map((spot, index) => `
                        <div style="background: var(--bg-light); padding: 20px; border-radius: 12px; position: relative;">
                            <div style="position: absolute; top: 16px; left: 16px; width: 32px; height: 32px; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px;">
                                ${index + 1}
                            </div>
                            <div style="padding-left: 44px;">
                                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                    <div style="font-weight: 600; font-size: 16px;">${spot.name}</div>
                                    <span style="background: white; padding: 4px 12px; border-radius: 12px; font-size: 13px; color: var(--text-gray);">${spot.category}</span>
                                </div>
                                <div style="color: var(--text-gray); font-size: 14px; margin-bottom: 8px;">${spot.description || ''}</div>
                                ${spot.parking ? '<div style="font-size: 13px; color: var(--success); margin-bottom: 4px;">🚗 주차 가능</div>' : ''}
                                ${spot.tip ? `<div style="font-size: 13px; color: var(--text-gray);">💡 ${spot.tip}</div>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 16px;">💡 여행 팁</h3>
                <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(139, 92, 246, 0.05)); padding: 20px; border-radius: 12px; border-left: 4px solid var(--primary);">
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        ${destination.tips.map(tip => `
                            <li style="margin-bottom: 12px; padding-left: 24px; position: relative;">
                                <span style="position: absolute; left: 0;">✓</span>
                                ${tip}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        </div>
    `;
    
    modal.classList.remove('hidden');
}

// 모달 닫기
function closeModal() {
    document.getElementById('detail-modal').classList.add('hidden');
}

// 다시 선택하기
function goBack() {
    document.getElementById('results-section').classList.add('hidden');
    document.getElementById('selection-section').classList.remove('hidden');
    
    updateStepDisplay();
    updateProgress();
    updateButtons();
    
    scrollToTop();
}

// 처음으로 돌아가기
function resetAll() {
    state.currentStep = 0;
    state.selectedRegion = '전체';
    state.keywords = {
        여행_스타일: null,
        동행: null,
        테마: [],
        페이스: null,
        교통: null,
        분위기: []
    };
    state.recommendations = [];
    
    document.querySelectorAll('.option-card.selected').forEach(card => {
        card.classList.remove('selected');
    });
    
    const themeCounter = document.getElementById('theme-count');
    if (themeCounter) {
        themeCounter.textContent = '0';
    }
    
    document.getElementById('results-section').classList.add('hidden');
    document.getElementById('selection-section').classList.add('hidden');
    document.getElementById('hero-section').classList.remove('hidden');
    
    updateStepDisplay();
    updateProgress();
    updateButtons();
    
    scrollToTop();
}

// 스크롤 최상단
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}