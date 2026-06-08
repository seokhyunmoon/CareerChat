import React, { useState } from 'react';
import { useNavigate, useOutletContext } from 'react-router-dom';
import { createDiagnosis } from '@/features/diagnosis/api/diagnosisApi';
import AnalysisLoadingOverlay from '@/features/diagnosis/AnalysisLoadingOverlay';
import { buildDiagnosisCreateRequest } from '@/features/diagnosis/utils/diagnosisFormMapper';
import {
  getDiagnosisCreateErrorMessage,
  validateDiagnosisJobs,
} from '@/features/diagnosis/utils/diagnosisFormValidation';

function createJobCard(id) {
  return {
    id,
    companyName: '',
    position: '',
    content: '',
  };
}

export default function Analyze() {
  const navigate = useNavigate();
  const { user } = useOutletContext();
  const [jobCards, setJobCards] = useState([createJobCard(1)]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formMessage, setFormMessage] = useState('');
  const [needsProfile, setNeedsProfile] = useState(false);

  const addJobCard = () => {
    if (jobCards.length >= 3) return;

    const nextId = Math.max(...jobCards.map((job) => job.id), 0) + 1;
    setJobCards([...jobCards, createJobCard(nextId)]);
    setFormMessage('');
  };

  const removeJobCard = (id) => {
    if (jobCards.length <= 1) return;

    setJobCards(jobCards.filter((job) => job.id !== id));
    setFormMessage('');
  };

  const updateJobCard = (id, field, value) => {
    setJobCards((currentJobs) => currentJobs.map((job) => (
      job.id === id ? { ...job, [field]: value } : job
    )));
    setFormMessage('');
    setNeedsProfile(false);
  };

  const runAnalysis = async () => {
    const validationMessage = validateDiagnosisJobs(jobCards);
    if (validationMessage) {
      setFormMessage(validationMessage);
      return;
    }

    const shouldRunAnalysis = window.confirm(
      '입력한 공고와 저장된 내 정보를 기준으로 진단을 시작할까요?\n진단에는 약 30초 ~ 1분 정도 소요됩니다.',
    );

    if (!shouldRunAnalysis) {
      return;
    }

    setIsSubmitting(true);
    setFormMessage('');
    setNeedsProfile(false);

    try {
      const response = await createDiagnosis(buildDiagnosisCreateRequest(jobCards));
      navigate(`/result/${response.diagnosisId}`);
    } catch (error) {
      setNeedsProfile(error.code === 'PROFILE_NOT_FOUND');
      setFormMessage(getDiagnosisCreateErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  const displayName = user?.name ?? '사용자';
  const avatarText = displayName.trim().slice(0, 1) || 'C';

  return (
    <>
      <div id="page-diagnose" className="page active">
        <div className="diag-layout">
          <div>
            <div className="jobs-header page-header">
              <div>
                <div className="tag page-step">STEP 2 / 4</div>
                <div className="jobs-title page-title">채용공고 입력</div>
                <div className="jobs-sub page-subtitle">비교하고 싶은 공고를 최대 3개까지 입력하세요.</div>
              </div>
              <div className="jobs-count" id="jobs-count">
                {jobCards.length} / 3
              </div>
            </div>
            <div className="job-cards" id="job-cards">
              {jobCards.map((job, index) => (
                <div className="job-card" key={job.id}>
                  <div className="job-card-header">
                    <span className="job-card-num">공고 {String(index + 1).padStart(2, '0')}</span>
                    <button
                      className="job-card-remove"
                      onClick={() => removeJobCard(job.id)}
                      disabled={jobCards.length <= 1 || isSubmitting}
                      aria-label={`공고 ${index + 1} 삭제`}
                    >
                      ×
                    </button>
                  </div>
                  <div className="job-card-grid">
                    <div className="field">
                      <label>회사명</label>
                      <input
                        placeholder="예: 토스"
                        value={job.companyName}
                        onChange={(event) => updateJobCard(job.id, 'companyName', event.target.value)}
                        disabled={isSubmitting}
                      />
                    </div>
                    <div className="field">
                      <label>직무명</label>
                      <input
                        placeholder="예: Backend Engineer"
                        value={job.position}
                        onChange={(event) => updateJobCard(job.id, 'position', event.target.value)}
                        disabled={isSubmitting}
                      />
                    </div>
                  </div>
                  <div className="field">
                    <label>채용공고 내용</label>
                    <textarea
                      rows="6"
                      placeholder="채용공고 전문을 그대로 붙여넣으세요.&#10;&#10;주요업무, 자격요건, 우대사항이 포함될수록 더 정확하게 비교할 수 있습니다."
                      value={job.content}
                      onChange={(event) => updateJobCard(job.id, 'content', event.target.value)}
                      disabled={isSubmitting}
                    ></textarea>
                  </div>
                </div>
              ))}
            </div>
            <button
              className={`add-job-btn ${jobCards.length >= 3 ? 'disabled' : ''}`}
              id="add-job-btn"
              onClick={addJobCard}
              disabled={jobCards.length >= 3 || isSubmitting}
            >
              <span style={{ fontSize: '20px' }}>＋</span>
              공고 추가 (최대 3개)
            </button>
            {formMessage && (
              <div className="diagnosis-message error">
                <span>{formMessage}</span>
                {needsProfile && (
                  <button className="btn btn-ghost" onClick={() => navigate('/myinfo')}>
                    내 정보 입력
                  </button>
                )}
              </div>
            )}
            <div className="run-btn-wrap">
              <div className="run-btn-info">
                <strong>준비되셨나요?</strong>
                내 정보와 입력한 공고를 AI가 분석합니다. 약 30초 ~ 1분 소요됩니다.
              </div>
              <button
                className="btn btn-primary"
                style={{ whiteSpace: 'nowrap' }}
                onClick={runAnalysis}
                disabled={isSubmitting}
              >
                {isSubmitting ? '요청 중...' : '진단 시작 →'}
              </button>
            </div>
          </div>

          <div className="diag-sidebar">
            <div className="diag-profile-card">
              <div className="diag-card-title">분석 기준 프로필</div>
              <div className="diag-profile-header">
                <div className="diag-profile-av">{avatarText}</div>
                <div>
                  <div className="diag-profile-name">{displayName}</div>
                  <div className="diag-profile-badge">저장된 내 정보로 공고와 비교합니다.</div>
                </div>
              </div>
              <div className="diag-profile-label">포함 정보</div>
              <div className="profile-chips">
                <span className="chip green">학력</span>
                <span className="chip green">경력</span>
                <span className="chip green">프로젝트</span>
                <span className="chip">어학/자격/수상</span>
              </div>
              <div className="diag-profile-action">
                <span>최근 저장된 정보를 기준으로 분석합니다.</span>
                <button className="btn btn-ghost diag-profile-edit" onClick={() => navigate('/myinfo')}>
                  내 정보 수정
                </button>
              </div>
            </div>
            <div className="diag-tip">
              <strong>TIP</strong>
              공고의 주요 업무, 자격 요건, 우대 사항을 함께 입력하면 내 정보와 더 정확히 비교할 수 있습니다.
            </div>
          </div>
        </div>
      </div>
      <AnalysisLoadingOverlay show={isSubmitting} message="진단 요청 중..." />
    </>
  );
}
