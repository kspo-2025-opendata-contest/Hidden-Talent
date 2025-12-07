/**
 * 숨인재 API 클라이언트
 * 백엔드 API와 통신하는 모든 함수를 정의합니다.
 */

// 환경에 따라 API URL 자동 선택
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000/api'
    : 'https://hidden-talent-api.onrender.com/api';

// 토큰 저장/조회
function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(token) {
    localStorage.setItem('access_token', token);
}

function removeToken() {
    localStorage.removeItem('access_token');
}

function getUserData() {
    const data = localStorage.getItem('user_data');
    return data ? JSON.parse(data) : null;
}

function setUserData(user) {
    localStorage.setItem('user_data', JSON.stringify(user));
}

function removeUserData() {
    localStorage.removeItem('user_data');
}

// 공통 fetch 래퍼
async function apiRequest(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: '요청 실패' }));
        throw new Error(error.detail || '요청 실패');
    }

    return response.json();
}

// ============ Auth API ============

async function apiSignup(data) {
    const response = await apiRequest('/auth/signup', {
        method: 'POST',
        body: JSON.stringify(data),
    });

    if (response.access_token) {
        setToken(response.access_token);
        setUserData(response.user);
    }

    return response;
}

async function apiLogin(email, password) {
    const response = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
    });

    if (response.access_token) {
        setToken(response.access_token);
        setUserData(response.user);
    }

    return response;
}

async function apiGetMe() {
    return apiRequest('/auth/me');
}

function apiLogout() {
    removeToken();
    removeUserData();
}

async function apiCheckEmail(email) {
    return apiRequest('/auth/check-email', {
        method: 'POST',
        body: JSON.stringify({ email }),
    });
}

// 비밀번호 요건 검증 (클라이언트)
function validatePassword(password) {
    const errors = [];

    if (password.length < 8) {
        errors.push('8자 이상');
    }
    if (!/[A-Z]/.test(password)) {
        errors.push('영문 대문자');
    }
    if (!/[a-z]/.test(password)) {
        errors.push('영문 소문자');
    }
    if (!/\d/.test(password)) {
        errors.push('숫자');
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        errors.push('특수문자');
    }

    return {
        valid: errors.length === 0,
        errors: errors,
        message: errors.length === 0
            ? '사용 가능한 비밀번호입니다.'
            : `다음이 필요합니다: ${errors.join(', ')}`
    };
}

// ============ Talent API ============

async function apiTalentDiagnosis(data) {
    return apiRequest('/talent/score', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

async function apiGetTalentHistory() {
    return apiRequest('/talent/tests');
}

async function apiGetTalentDetail(testId) {
    return apiRequest(`/talent/tests/${testId}`);
}

// ============ Programs API ============

async function apiGetPrograms(params = {}) {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/programs?${query}`);
}

async function apiGetProgramDetail(programId) {
    return apiRequest(`/programs/${programId}`);
}

async function apiGetProgramRegions() {
    return apiRequest('/programs/regions/list');
}

// ============ Facilities API ============

async function apiGetFacilities(params = {}) {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/facilities?${query}`);
}

async function apiGetFacilitySummary() {
    return apiRequest('/facilities/summary');
}

async function apiGetFacilityRegions() {
    return apiRequest('/facilities/regions');
}

// ============ Dashboard API ============

async function apiGetDashboardSummary() {
    return apiRequest('/dashboard/summary');
}

async function apiGetDashboardRegions() {
    return apiRequest('/dashboard/regions');
}

async function apiGetCoachStats() {
    return apiRequest('/dashboard/coaches');
}

// ============ MyPage API ============

async function apiGetMyOverview() {
    return apiRequest('/me/overview');
}

async function apiUpdateProfile(data) {
    const response = await apiRequest('/me/profile', {
        method: 'PUT',
        body: JSON.stringify(data),
    });

    // 로컬 사용자 데이터 업데이트
    const userData = getUserData();
    if (userData) {
        setUserData({ ...userData, ...response });
    }

    return response;
}

async function apiGetMyBookmarks(params = {}) {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/me/bookmarks?${query}`);
}

async function apiAddBookmark(targetType, targetId) {
    return apiRequest('/me/bookmarks', {
        method: 'POST',
        body: JSON.stringify({ target_type: targetType, target_id: targetId }),
    });
}

async function apiDeleteBookmark(bookmarkId) {
    return apiRequest(`/me/bookmarks/${bookmarkId}`, {
        method: 'DELETE',
    });
}

async function apiGetMyNotifications(params = {}) {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/me/notifications?${query}`);
}

async function apiMarkNotificationRead(notificationId) {
    return apiRequest(`/me/notifications/${notificationId}/read`, {
        method: 'POST',
    });
}

async function apiMarkAllNotificationsRead() {
    return apiRequest('/me/notifications/read-all', {
        method: 'POST',
    });
}

// ============ Inquiry API ============

async function apiCreateInquiry(data) {
    // 문의 생성은 /api 프리픽스 없이 /api/inquiry로 직접 호출
    const baseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://hidden-talent-api.onrender.com';

    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${baseUrl}/api/inquiry`, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: '문의 등록 실패' }));
        throw new Error(error.detail || '문의 등록 실패');
    }

    return response.json();
}

async function apiGetInquiries(params = {}) {
    const baseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://hidden-talent-api.onrender.com';

    const query = new URLSearchParams(params).toString();
    const token = getToken();

    const response = await fetch(`${baseUrl}/api/inquiry?${query}`, {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: '문의 목록 조회 실패' }));
        throw new Error(error.detail || '문의 목록 조회 실패');
    }

    return response.json();
}

async function apiGetInquiryDetail(inquiryId) {
    const baseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://hidden-talent-api.onrender.com';

    const token = getToken();

    const response = await fetch(`${baseUrl}/api/inquiry/${inquiryId}`, {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: '문의 조회 실패' }));
        throw new Error(error.detail || '문의 조회 실패');
    }

    return response.json();
}

async function apiReplyInquiry(inquiryId, adminReply) {
    const baseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://hidden-talent-api.onrender.com';

    const token = getToken();

    const response = await fetch(`${baseUrl}/api/inquiry/${inquiryId}/reply`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ admin_reply: adminReply }),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: '답변 등록 실패' }));
        throw new Error(error.detail || '답변 등록 실패');
    }

    return response.json();
}

async function apiGetInquiryStats() {
    const baseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://hidden-talent-api.onrender.com';

    const token = getToken();

    const response = await fetch(`${baseUrl}/api/inquiry/stats/summary`, {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: '통계 조회 실패' }));
        throw new Error(error.detail || '통계 조회 실패');
    }

    return response.json();
}

async function apiCloseInquiry(inquiryId) {
    const baseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://hidden-talent-api.onrender.com';

    const token = getToken();

    const response = await fetch(`${baseUrl}/api/inquiry/${inquiryId}/close`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: '문의 종료 실패' }));
        throw new Error(error.detail || '문의 종료 실패');
    }

    return response.json();
}

// Export for global use
window.SoominjaeAPI = {
    // Auth
    signup: apiSignup,
    login: apiLogin,
    logout: apiLogout,
    getMe: apiGetMe,
    getToken,
    getUserData,
    checkEmail: apiCheckEmail,
    validatePassword: validatePassword,

    // Talent
    talentDiagnosis: apiTalentDiagnosis,
    getTalentHistory: apiGetTalentHistory,
    getTalentDetail: apiGetTalentDetail,

    // Programs
    getPrograms: apiGetPrograms,
    getProgramDetail: apiGetProgramDetail,
    getProgramRegions: apiGetProgramRegions,

    // Facilities
    getFacilities: apiGetFacilities,
    getFacilitySummary: apiGetFacilitySummary,
    getFacilityRegions: apiGetFacilityRegions,

    // Dashboard
    getDashboardSummary: apiGetDashboardSummary,
    getDashboardRegions: apiGetDashboardRegions,
    getCoachStats: apiGetCoachStats,

    // MyPage
    getMyOverview: apiGetMyOverview,
    updateProfile: apiUpdateProfile,
    getMyBookmarks: apiGetMyBookmarks,
    addBookmark: apiAddBookmark,
    deleteBookmark: apiDeleteBookmark,
    getMyNotifications: apiGetMyNotifications,
    markNotificationRead: apiMarkNotificationRead,
    markAllNotificationsRead: apiMarkAllNotificationsRead,

    // Inquiry (문의하기)
    createInquiry: apiCreateInquiry,
    getInquiries: apiGetInquiries,
    getInquiryDetail: apiGetInquiryDetail,
    replyInquiry: apiReplyInquiry,
    getInquiryStats: apiGetInquiryStats,
    closeInquiry: apiCloseInquiry,
};
