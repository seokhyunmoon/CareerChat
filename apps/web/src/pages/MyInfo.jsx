import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useOutletContext } from 'react-router-dom';
import { getProfile, saveProfile as saveProfileApi } from '@/features/profile/api/profileApi';
import {
  buildProfileRequest,
  createEmptyProfileFormState,
  generateSubText,
  getDefaultFormData,
  getEntryTitle,
  mapProfileResponseToFormState,
} from '@/features/profile/utils/profileFormMapper';
import {
  getCurrentDateLimit,
  validateProfileForm,
  validateYearMonth,
} from '@/features/profile/utils/profileFormValidation';

function createProfileSnapshot(state) {
  return JSON.stringify(buildProfileRequest(state));
}

export default function MyInfo() {
  const navigate = useNavigate();
  const { user } = useOutletContext();
  const [jobType, setJobType] = useState('new');
  const [activeSection, setActiveSection] = useState('sec-type');
  const [educationList, setEducationList] = useState([]);
  const [careerList, setCareerList] = useState([]);
  const [projectList, setProjectList] = useState([]);
  const [optionalList, setOptionalList] = useState([]);
  const [isProfileLoading, setIsProfileLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [profileError, setProfileError] = useState('');
  const [saveMessage, setSaveMessage] = useState('');
  const [savedProfileSnapshot, setSavedProfileSnapshot] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalType, setModalType] = useState('');
  const [currentEntry, setCurrentEntry] = useState(null);
  const [formData, setFormData] = useState({});
  const dateLimit = getCurrentDateLimit();
  const monthInputMax = `${dateLimit.year}-${String(dateLimit.month).padStart(2, '0')}`;

  useEffect(() => {
    let ignore = false;

    const loadProfile = async () => {
      setIsProfileLoading(true);
      setProfileError('');
      setSaveMessage('');

      try {
        const profile = await getProfile();
        if (!ignore) {
          const nextProfileState = mapProfileResponseToFormState(profile);
          setJobType(nextProfileState.jobType);
          setEducationList(nextProfileState.educationList);
          setCareerList(nextProfileState.careerList);
          setProjectList(nextProfileState.projectList);
          setOptionalList(nextProfileState.optionalList);
          setSavedProfileSnapshot(createProfileSnapshot(nextProfileState));
        }
      } catch (error) {
        if (ignore) {
          return;
        }

        if (error.code === 'PROFILE_NOT_FOUND') {
          const emptyProfileState = createEmptyProfileFormState();
          setJobType(emptyProfileState.jobType);
          setEducationList(emptyProfileState.educationList);
          setCareerList(emptyProfileState.careerList);
          setProjectList(emptyProfileState.projectList);
          setOptionalList(emptyProfileState.optionalList);
          setSavedProfileSnapshot(createProfileSnapshot(emptyProfileState));
          return;
        }

        setProfileError(error.message ?? '프로필을 불러오지 못했습니다.');
      } finally {
        if (!ignore) {
          setIsProfileLoading(false);
        }
      }
    };

    loadProfile();

    return () => {
      ignore = true;
    };
  }, []);

  const selectType = (type) => {
    setJobType(type);
    setSaveMessage('');
  };

  const scrollToSection = (id) => {
    setActiveSection(id);
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const saveProfile = async () => {
    setProfileError('');
    setSaveMessage('');

    if (!hasUnsavedChanges) {
      return;
    }

    const validationMessage = validateProfileForm(educationList, careerList, projectList);
    if (validationMessage) {
      setProfileError(validationMessage);
      return;
    }

    setIsSaving(true);

    try {
      const request = buildProfileRequest({
        jobType,
        educationList,
        careerList,
        projectList,
        optionalList,
      });
      const profile = await saveProfileApi(request);
      const nextProfileState = mapProfileResponseToFormState(profile);
      setJobType(nextProfileState.jobType);
      setEducationList(nextProfileState.educationList);
      setCareerList(nextProfileState.careerList);
      setProjectList(nextProfileState.projectList);
      setOptionalList(nextProfileState.optionalList);
      setSavedProfileSnapshot(createProfileSnapshot(nextProfileState));
      setSaveMessage('내 정보가 저장되었습니다.');
    } catch (error) {
      setProfileError(error.message ?? '내 정보를 저장하지 못했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  const openModal = (type, entry = null) => {
    setModalType(type);
    setCurrentEntry(entry);
    setFormData(entry ? { ...entry } : getDefaultFormData(type));
    setIsModalOpen(true);
    setSaveMessage('');
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setCurrentEntry(null);
    setFormData({});
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const getYearMonthValue = (year, month) => {
    if (!year || !month) {
      return '';
    }

    return `${year}-${String(month).padStart(2, '0')}`;
  };

  const handleYearMonthChange = (yearField, monthField) => (e) => {
    const [year = '', month = ''] = e.target.value.split('-');
    setFormData((prev) => ({
      ...prev,
      [yearField]: year,
      [monthField]: month ? String(Number(month)) : '',
    }));
  };

  const validateDate = (year, month, options = {}) => {
    return validateYearMonth(year, month, dateLimit, options);
  };

  const getNextEntryId = (type) => {
    const listByType = {
      edu: educationList,
      career: careerList,
      project: projectList,
      optional: optionalList,
    };
    const list = listByType[type] || [];

    return Math.max(...list.map((item) => item.id), 0) + 1;
  };

  const saveEntry = (e) => {
    e.preventDefault();

    if (modalType === 'edu' || modalType === 'career') {
      const allowFutureEndDate = modalType === 'edu' && formData.gradStatus === 'EXPECTED';

      if (!validateDate(formData.startYear, formData.startMonth) || !validateDate(formData.endYear, formData.endMonth, { allowFuture: allowFutureEndDate })) {
        alert(`날짜가 올바르지 않습니다 (${dateLimit.year}년 ${dateLimit.month}월까지만 선택 가능).`);
        return;
      }
    } else if (modalType === 'optional') {
      if (!validateDate(formData.year, formData.month)) {
        alert(`날짜가 올바르지 않습니다 (${dateLimit.year}년 ${dateLimit.month}월까지만 선택 가능).`);
        return;
      }
    }

    const entryData = {
      ...formData,
      id: currentEntry ? currentEntry.id : getNextEntryId(modalType),
      title: getEntryTitle(modalType, formData),
      sub: generateSubText(modalType, formData),
    };

    if (modalType === 'edu') {
      if (currentEntry) {
        setEducationList((prev) => prev.map((item) => item.id === currentEntry.id ? entryData : item));
      } else {
        setEducationList((prev) => [...prev, entryData]);
      }
    } else if (modalType === 'career') {
      if (currentEntry) {
        setCareerList((prev) => prev.map((item) => item.id === currentEntry.id ? entryData : item));
      } else {
        setCareerList((prev) => [...prev, entryData]);
      }
    } else if (modalType === 'project') {
      if (currentEntry) {
        setProjectList((prev) => prev.map((item) => item.id === currentEntry.id ? entryData : item));
      } else {
        setProjectList((prev) => [...prev, entryData]);
      }
    } else if (modalType === 'optional') {
      if (currentEntry) {
        setOptionalList((prev) => prev.map((item) => item.id === currentEntry.id ? entryData : item));
      } else {
        setOptionalList((prev) => [...prev, entryData]);
      }
    }

    setProfileError('');
    closeModal();
  };

  const deleteEntry = (type, id) => {
    setSaveMessage('');

    if (type === 'edu') {
      setEducationList((prev) => prev.filter((item) => item.id !== id));
    } else if (type === 'career') {
      setCareerList((prev) => prev.filter((item) => item.id !== id));
    } else if (type === 'project') {
      setProjectList((prev) => prev.filter((item) => item.id !== id));
    } else if (type === 'optional') {
      setOptionalList((prev) => prev.filter((item) => item.id !== id));
    }
  };

  const displayName = user?.name ?? '사용자';
  const displayEmail = user?.email ?? '';
  const avatarText = displayName.trim().charAt(0) || '?';
  const statusMessage = profileError || saveMessage || (isProfileLoading ? '프로필을 불러오는 중입니다.' : '변경사항은 자동 저장되지 않습니다');
  const currentProfileSnapshot = useMemo(() => createProfileSnapshot({
    jobType,
    educationList,
    careerList,
    projectList,
    optionalList,
  }), [jobType, educationList, careerList, projectList, optionalList]);
  const hasUnsavedChanges = !isProfileLoading && savedProfileSnapshot !== '' && currentProfileSnapshot !== savedProfileSnapshot;
  const saveButtonTitle = hasUnsavedChanges ? '변경사항을 저장합니다' : '변경 사항이 없습니다';

  return (
    <div id="page-profile" className="page active">
      <div className="profile-layout">
        <div className="profile-sidebar">
          <div className="profile-user-card">
            <div className="profile-avatar">{avatarText}</div>
            <div className="profile-username">{displayName}</div>
            <div className="profile-email">{displayEmail}</div>
          </div>
          <div className="sidebar-nav">
            <div className={`sidebar-item ${activeSection === 'sec-type' ? 'active' : ''}`} onClick={() => scrollToSection('sec-type')}>
              <span className="dot"></span>신입/경력 선택
            </div>
            <div className={`sidebar-item ${activeSection === 'sec-edu' ? 'active' : ''}`} onClick={() => scrollToSection('sec-edu')}>
              <span className="dot"></span>학력
            </div>
            <div className={`sidebar-item ${activeSection === 'sec-career' ? 'active' : ''}`} onClick={() => scrollToSection('sec-career')}>
              <span className="dot"></span>경력
            </div>
            <div className={`sidebar-item ${activeSection === 'sec-project' ? 'active' : ''}`} onClick={() => scrollToSection('sec-project')}>
              <span className="dot"></span>프로젝트
            </div>
            <div className={`sidebar-item ${activeSection === 'sec-optional' ? 'active' : ''}`} onClick={() => scrollToSection('sec-optional')}>
              <span className="dot"></span>어학/자격/수상
            </div>
          </div>
        </div>

        <div className="profile-main">
          {(profileError || saveMessage || isProfileLoading) && (
            <div className={`profile-message ${profileError ? 'error' : saveMessage ? 'success' : ''}`}>
              {statusMessage}
            </div>
          )}

          <div className="profile-header page-header">
            <div className="tag page-step">STEP 1 / 4</div>
            <div className="profile-title page-title">내 정보</div>
            <div className="profile-sub page-subtitle">경험을 기반으로 나의 직무 역량을 관리합니다.</div>
          </div>

          <div className="section-block" id="sec-type">
            <div className="section-block-header">
              <div className="section-block-title">
                지원 상태 <span className="badge-required">필수</span>
              </div>
            </div>
            <div className="type-toggle">
              <button
                className={`type-btn ${jobType === 'new' ? 'selected' : ''}`}
                disabled={isProfileLoading}
                onClick={() => selectType('new')}
              >
                <span className="type-icon">🌱</span>
                신입
              </button>
              <button
                className={`type-btn ${jobType === 'exp' ? 'selected' : ''}`}
                disabled={isProfileLoading}
                onClick={() => selectType('exp')}
              >
                <span className="type-icon">💼</span>
                경력
              </button>
            </div>
          </div>

          <div className="section-block" id="sec-edu">
            <div className="section-block-header">
              <div className="section-block-title">
                학력 <span className="badge-required">필수</span>
              </div>
              <button className="add-btn" disabled={isProfileLoading} onClick={() => openModal('edu')}>+ 추가</button>
            </div>
            <div id="edu-list">
              {educationList.length === 0 && <div className="entry-empty">등록된 학력이 없습니다.</div>}
              {educationList.map((item) => (
                <div className="entry-card" key={item.id}>
                  <div className="entry-info">
                    <div className="entry-title">{item.title}</div>
                    <div className="entry-sub">{item.sub}</div>
                  </div>
                  <div className="entry-actions">
                    <button className="icon-btn" onClick={() => openModal('edu', item)}>✏️</button>
                    <button className="icon-btn del" onClick={() => deleteEntry('edu', item.id)}>🗑</button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="section-block" id="sec-career">
            <div className="section-block-header">
              <div className="section-block-title">
                경력 <span style={{ fontSize: '11px', color: 'var(--muted)', fontWeight: 400 }}>(경력 또는 프로젝트 중 1개 이상 필수)</span>
              </div>
              <button className="add-btn" disabled={isProfileLoading} onClick={() => openModal('career')}>+ 추가</button>
            </div>
            <div id="career-list">
              {careerList.length === 0 && <div className="entry-empty">등록된 경력이 없습니다.</div>}
              {careerList.map((item) => (
                <div className="entry-card" key={item.id}>
                  <div className="entry-info">
                    <div className="entry-title">{item.title}</div>
                    <div className="entry-sub">{item.sub}</div>
                  </div>
                  <div className="entry-actions">
                    <button className="icon-btn" onClick={() => openModal('career', item)}>✏️</button>
                    <button className="icon-btn del" onClick={() => deleteEntry('career', item.id)}>🗑</button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="section-block" id="sec-project">
            <div className="section-block-header">
              <div className="section-block-title">
                프로젝트 <span className="badge-required">1개 이상</span>
              </div>
              <button className="add-btn" disabled={isProfileLoading} onClick={() => openModal('project')}>+ 추가</button>
            </div>
            <div id="project-list">
              {projectList.length === 0 && <div className="entry-empty">등록된 프로젝트가 없습니다.</div>}
              {projectList.map((item) => (
                <div className="entry-card" key={item.id}>
                  <div className="entry-info">
                    <div className="entry-title">{item.title}</div>
                    <div className="entry-sub">{item.sub}</div>
                  </div>
                  <div className="entry-actions">
                    <button className="icon-btn" onClick={() => openModal('project', item)}>✏️</button>
                    <button className="icon-btn del" onClick={() => deleteEntry('project', item.id)}>🗑</button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="section-block" id="sec-optional">
            <div className="section-block-header">
              <div className="section-block-title">
                어학 / 자격증 / 수상 <span style={{ fontSize: '11px', color: 'var(--muted)', fontWeight: 400 }}>선택</span>
              </div>
              <button className="add-btn" disabled={isProfileLoading} onClick={() => openModal('optional')}>+ 추가</button>
            </div>
            <div id="optional-list">
              {optionalList.length === 0 && <div className="entry-empty">등록된 선택 이력이 없습니다.</div>}
              {optionalList.map((item) => (
                <div className="entry-card" key={item.id}>
                  <div className="entry-info">
                    <div className="entry-title">{item.title}</div>
                    <div className="entry-sub">{item.sub}</div>
                  </div>
                  <div className="entry-actions">
                    <button className="icon-btn" onClick={() => openModal('optional', item)}>✏️</button>
                    <button className="icon-btn del" onClick={() => deleteEntry('optional', item.id)}>🗑</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {isModalOpen && (
        <div className="modal-overlay show" onClick={(e) => e.target === e.currentTarget && closeModal()}>
          <div className={`modal ${modalType === 'career' || modalType === 'project' ? 'modal-wide' : ''}`}>
            <form onSubmit={saveEntry}>
              {modalType === 'edu' && (
                <>
                  <div className="modal-title">학력 {currentEntry ? '수정' : '추가'}</div>
                  <div className="modal-sub">학교 정보를 입력하세요.</div>
                  <div className="form-grid" style={{ gap: '14px' }}>
                    <div className="field span-2">
                      <label>학교명 *</label>
                      <input name="school" placeholder="연세대학교" value={formData.school || ''} onChange={handleInputChange} required />
                    </div>
                    <div className="field span-2">
                      <label>전공 *</label>
                      <input name="major" placeholder="응용정보공학전공" value={formData.major || ''} onChange={handleInputChange} required />
                    </div>
                    <div className="field">
                      <label>학위</label>
                      <select name="degree" value={formData.degree || '학사'} onChange={handleInputChange}>
                        <option value="학사">학사</option>
                        <option value="석사">석사</option>
                        <option value="박사">박사</option>
                        <option value="전문학사">전문학사</option>
                      </select>
                    </div>
                    <div className="field">
                      <label>학적 상태 *</label>
                      <select name="gradStatus" value={formData.gradStatus || 'EXPECTED'} onChange={handleInputChange} required>
                        <option value="ENROLLED">재학 중</option>
                        <option value="EXPECTED">졸업 예정</option>
                        <option value="GRADUATED">졸업</option>
                        <option value="LEAVE">휴학</option>
                      </select>
                    </div>
                    <div className="field">
                      <label>입학 년월</label>
                      <input type="month" value={getYearMonthValue(formData.startYear, formData.startMonth)} max={monthInputMax} onChange={handleYearMonthChange('startYear', 'startMonth')} />
                    </div>
                    <div className="field">
                      <label>졸업 년월</label>
                      <input type="month" value={getYearMonthValue(formData.endYear, formData.endMonth)} max={formData.gradStatus === 'EXPECTED' ? undefined : monthInputMax} onChange={handleYearMonthChange('endYear', 'endMonth')} />
                    </div>
                  </div>
                </>
              )}
              {modalType === 'career' && (
                <>
                  <div className="modal-title">경력 {currentEntry ? '수정' : '추가'}</div>
                  <div className="modal-sub">회사 정보를 입력하세요.</div>
                  <div className="form-grid" style={{ gap: '14px' }}>
                    <div className="field span-2">
                      <label>회사명 *</label>
                      <input name="company" placeholder="(주)예시회사" value={formData.company || ''} onChange={handleInputChange} required />
                    </div>
                    <div className="field">
                      <label>고용 형태 *</label>
                      <select name="employmentType" value={formData.employmentType || 'FULL_TIME'} onChange={handleInputChange} required>
                        <option value="FULL_TIME">정규직</option>
                        <option value="CONTRACT">계약직</option>
                        <option value="INTERN">인턴</option>
                        <option value="OTHER">기타</option>
                      </select>
                    </div>
                    <div className="field">
                      <label>직무/직책</label>
                      <input name="position" placeholder="프론트엔드 개발자" value={formData.position || ''} onChange={handleInputChange} />
                    </div>
                    <div className="field">
                      <label>입사 년월</label>
                      <input type="month" value={getYearMonthValue(formData.startYear, formData.startMonth)} max={monthInputMax} onChange={handleYearMonthChange('startYear', 'startMonth')} />
                    </div>
                    <div className="field">
                      <label>퇴사 년월</label>
                      <input type="month" value={getYearMonthValue(formData.endYear, formData.endMonth)} max={monthInputMax} onChange={handleYearMonthChange('endYear', 'endMonth')} />
                    </div>
                    <div className="field span-2">
                      <label>주요 업무</label>
                      <textarea className="textarea-long" name="description" rows="8" placeholder="담당 업무와 성과를 입력하세요." value={formData.description || ''} onChange={handleInputChange} />
                    </div>
                  </div>
                </>
              )}
              {modalType === 'project' && (
                <>
                  <div className="modal-title">프로젝트 {currentEntry ? '수정' : '추가'}</div>
                  <div className="modal-sub">프로젝트 경험을 입력하세요.</div>
                  <div className="form-grid" style={{ gap: '14px' }}>
                    <div className="field span-2">
                      <label>프로젝트명 *</label>
                      <input name="projectName" placeholder="AI 기반 서비스" value={formData.projectName || ''} onChange={handleInputChange} required />
                    </div>
                    <div className="field span-2">
                      <label>프로젝트 설명 *</label>
                      <textarea className="textarea-long" name="description" rows="10" placeholder="프로젝트 목표, 역할, 구현 내용을 입력하세요." value={formData.description || ''} onChange={handleInputChange} required />
                    </div>
                    <div className="field span-2">
                      <label>사용 기술</label>
                      <input name="techStack" placeholder="React, Spring Boot, PostgreSQL, ..." value={formData.techStack || ''} onChange={handleInputChange} />
                    </div>
                  </div>
                </>
              )}
              {modalType === 'optional' && (
                <>
                  <div className="modal-title">어학 / 자격 / 수상 {currentEntry ? '수정' : '추가'}</div>
                  <div className="modal-sub">선택 항목을 입력하세요.</div>
                  <div className="form-grid" style={{ gap: '14px' }}>
                    <div className="field span-2">
                      <label>종류</label>
                      <select name="category" value={formData.category || '어학'} onChange={handleInputChange}>
                        <option value="어학">어학</option>
                        <option value="자격증">자격증</option>
                        <option value="수상">수상</option>
                        <option value="기타">기타</option>
                      </select>
                    </div>
                    <div className="field span-2">
                      <label>내용 *</label>
                      <input name="content" placeholder="TOEIC 900점 / 정보처리기사 / ..." value={formData.content || ''} onChange={handleInputChange} required />
                    </div>
                    <div className="field">
                      <label>발급기관/주관</label>
                      <input name="issuer" placeholder="한국산업인력공단" value={formData.issuer || ''} onChange={handleInputChange} />
                    </div>
                    <div className="field">
                      <label>점수/등급</label>
                      <input name="scoreOrGrade" placeholder="IH / 900점 / 대상" value={formData.scoreOrGrade || ''} onChange={handleInputChange} />
                    </div>
                    <div className="field">
                      <label>취득 년월</label>
                      <input type="month" value={getYearMonthValue(formData.year, formData.month)} max={monthInputMax} onChange={handleYearMonthChange('year', 'month')} />
                    </div>
                  </div>
                </>
              )}
              <div className="modal-actions">
                <button type="button" className="btn btn-ghost" onClick={closeModal}>취소</button>
                <button type="submit" className="btn btn-primary">{currentEntry ? '수정하기' : '추가하기'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="save-bar">
        <span className={`save-notice ${profileError ? 'error' : saveMessage ? 'success' : ''}`}>
          {statusMessage}
        </span>
        <button className="btn btn-outline btn-ghost" onClick={() => navigate('/analyze')}>
          진단하기로 이동
        </button>
        <button
          className={`btn save-submit ${hasUnsavedChanges ? 'btn-primary' : 'btn-muted'}`}
          disabled={isProfileLoading || isSaving}
          data-tooltip={hasUnsavedChanges ? undefined : '변경 사항이 없습니다'}
          title={saveButtonTitle}
          onClick={saveProfile}
        >
          {isSaving ? '저장 중...' : '저장하기'}
        </button>
      </div>
    </div>
  );
}
