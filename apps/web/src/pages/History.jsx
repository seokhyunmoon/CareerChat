import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function History() {
  const navigate = useNavigate();

  const historyData = [
    {
      day: '22',
      month: 'MAY \'25',
      companies: '토스 · 카카오 · 네이버 클라우드',
      jobs: 'Frontend Engineer · 백엔드 · DevOps',
      score: '87점'
    },
    {
      day: '10',
      month: 'MAY \'25',
      companies: '라인 · 쿠팡',
      jobs: 'Frontend Developer · 풀스택',
      score: '74점'
    },
    {
      day: '28',
      month: 'APR \'25',
      companies: '당근마켓 · 뱅크샐러드 · 야놀자',
      jobs: 'React 개발자 · Frontend · 앱 개발',
      score: '69점'
    }
  ];

  return (
    <div id="page-history" className="page active">
      <div className="history-layout">
        <div className="history-header">
          <div className="history-title">진단 기록</div>
          <div className="history-sub">과거에 진행한 비교 진단 결과를 다시 확인하세요.</div>
        </div>
        <div className="history-list">
          {historyData.map((item, idx) => (
            <div key={idx} className="history-item" onClick={() => navigate('/result')}>
              <div className="history-date">
                <div className="h-day">{item.day}</div>
                <div>{item.month}</div>
              </div>
              <div className="history-divider"></div>
              <div className="history-info">
                <div className="history-companies">{item.companies}</div>
                <div className="history-jobs">{item.jobs}</div>
              </div>
              <div className="history-meta">
                <div className="history-score">{item.score}</div>
                <div className="history-score-label">최고 적합도</div>
              </div>
              <div className="history-arrow">›</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
