import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function MyInfo() {
  const navigate = useNavigate();
  const [jobType, setJobType] = useState('new'); // 'new' or 'exp'
  const [activeSection, setActiveSection] = useState('sec-type');

  // State for lists
  const [educationList, setEducationList] = useState([
    { 
      id: 1, 
      title: '연세대학교', 
      sub: '학사 · 응용정보공학과 · 2019.09 ~ 졸업 예정',
      school: '연세대학교',
      major: '응용정보공학과',
      degree: '학사',
      startYear: '2019',
      startMonth: '9'
    }
  ]);
  const [careerList, setCareerList] = useState([
    { 
      id: 1, 
      title: 'A*STAR Institute of High Performance Computing (IHPC)', 
      sub: 'Research Intern · 2025.09 – 2025.12',
      company: 'A*STAR Institute of High Performance Computing (IHPC)',
      position: 'Research Intern',
      startYear: '2025',
      startMonth: '9',
      endYear: '2025',
      endMonth: '12'
    }
  ]);
  const [projectList, setProjectList] = useState([
    { 
      id: 1, 
      title: 'CareerChat', 
      sub: 'Spring Boot, FastAPI, LangGraph, Next.js, PostgreSQL, Docker',
      projectName: 'CareerChat',
      techStack: 'Spring Boot, FastAPI, LangGraph, Next.js, PostgreSQL, Docker'
    }
  ]);
  const [optionalList, setOptionalList] = useState([
    { 
      id: 1, 
      title: 'OPIc IH', 
      sub: '어학 · 2025.03',
      category: '어학',
      content: 'OPIc IH',
      year: '2025',
      month: '3'
    }
  ]);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalType, setModalType] = useState(''); // 'edu', 'career', 'project', 'optional'
  const [currentEntry, setCurrentEntry] = useState(null);
  const [formData, setFormData] = useState({});

  const selectType = (type) => {
    setJobType(type);
  };

  const scrollToSection = (id) => {
    setActiveSection(id);
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const saveProfile = () => {
    alert('내 정보가 저장되었습니다.');
  };

  const openModal = (type, entry = null) => {
    setModalType(type);
    setCurrentEntry(entry);
    setFormData(entry ? { ...entry } : {});
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setCurrentEntry(null);
    setFormData({});
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const years = Array.from({ length: 2026 - 1900 + 1 }, (_, i) => 2026 - i);
  const months = Array.from({ length: 12 }, (_, i) => i + 1);

  const validateDate = (year, month) => {
    if (!year || !month) return true;
    const y = Number(year);
    const m = Number(month);
    if (y === 2026 && m > 5) return false;
    return true;
  };

  const saveEntry = (e) => {
    e.preventDefault();
    
    // Validation
    if (modalType === 'edu' || modalType === 'career') {
      if (!validateDate(formData.startYear, formData.startMonth) || !validateDate(formData.endYear, formData.endMonth)) {
        alert('날짜가 올바르지 않습니다 (2026년 5월까지만 선택 가능).');
        return;
      }
    } else if (modalType === 'optional') {
      if (!validateDate(formData.year, formData.month)) {
        alert('날짜가 올바르지 않습니다 (2026년 5월까지만 선택 가능).');
        return;
      }
    }

    const entryData = {
      ...formData,
      id: currentEntry ? currentEntry.id : Date.now(),
      title: modalType === 'edu' ? formData.school : 
             modalType === 'career' ? formData.company : 
             modalType === 'project' ? formData.projectName : 
             formData.content,
      sub: generateSubText(modalType, formData)
    };

    if (modalType === 'edu') {
      if (currentEntry) setEducationList(prev => prev.map(item => item.id === currentEntry.id ? entryData : item));
      else setEducationList(prev => [...prev, entryData]);
    } else if (modalType === 'career') {
      if (currentEntry) setCareerList(prev => prev.map(item => item.id === currentEntry.id ? entryData : item));
      else setCareerList(prev => [...prev, entryData]);
    } else if (modalType === 'project') {
      if (currentEntry) setProjectList(prev => prev.map(item => item.id === currentEntry.id ? entryData : item));
      else setProjectList(prev => [...prev, entryData]);
    } else if (modalType === 'optional') {
      if (currentEntry) setOptionalList(prev => prev.map(item => item.id === currentEntry.id ? entryData : item));
      else setOptionalList(prev => [...prev, entryData]);
    }
    closeModal();
  };

  const generateSubText = (type, data) => {
    if (type === 'edu') {
      const start = data.startYear ? `${data.startYear}.${String(data.startMonth).padStart(2, '0')}` : '';
      const end = data.endYear ? `${data.endYear}.${String(data.endMonth).padStart(2, '0')}` : '졸업 예정';
      return `${data.degree || '학사'} · ${data.major || ''} · ${start} ~ ${end}`;
    }
    if (type === 'career') {
      const start = data.startYear ? `${data.startYear}.${String(data.startMonth).padStart(2, '0')}` : '';
      const end = data.endYear ? `${data.endYear}.${String(data.endMonth).padStart(2, '0')}` : '재직 중';
      return `${data.position || ''} · ${start} – ${end}`;
    }
    if (type === 'project') return `${data.techStack || ''}`;
    if (type === 'optional') {
      const date = data.year ? `${data.year}.${String(data.month).padStart(2, '0')}` : '';
      return `${data.category || ''} · ${date}`;
    }
    return '';
  };

  const deleteEntry = (type, id) => {
    if (type === 'edu') setEducationList(prev => prev.filter(item => item.id !== id));
    else if (type === 'career') setCareerList(prev => prev.filter(item => item.id !== id));
    else if (type === 'project') setProjectList(prev => prev.filter(item => item.id !== id));
    else if (type === 'optional') setOptionalList(prev => prev.filter(item => item.id !== id));
  };

  return (
    <div id="page-profile" className="page active">
      <div className="profile-layout">
        {/* Sidebar */}
        <div className="profile-sidebar">
          <div className="profile-user-card">
            <div className="profile-avatar">문</div>
            <div className="profile-username">문석현</div>
            <div className="profile-email">moon@example.com</div>
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

        {/* Main */}
        <div className="profile-main">
          <div className="profile-section-header">
            <div className="profile-section-title">내 정보 관리</div>
            <div className="profile-required">* 필수 항목</div>
          </div>

          {/* Type */}
          <div className="section-block" id="sec-type">
            <div className="section-block-header">
              <div className="section-block-title">
                지원 상태 <span className="badge-required">필수</span>
              </div>
            </div>
            <div className="type-toggle">
              <button
                className={`type-btn ${jobType === 'new' ? 'selected' : ''}`}
                onClick={() => selectType('new')}
              >
                <span className="type-icon">🌱</span>
                신입
              </button>
              <button
                className={`type-btn ${jobType === 'exp' ? 'selected' : ''}`}
                onClick={() => selectType('exp')}
              >
                <span className="type-icon">💼</span>
                경력
              </button>
            </div>
          </div>

          {/* Education */}
          <div className="section-block" id="sec-edu">
            <div className="section-block-header">
              <div className="section-block-title">
                학력 <span className="badge-required">필수</span>
              </div>
              <button className="add-btn" onClick={() => openModal('edu')}>+ 추가</button>
            </div>
            <div id="edu-list">
              {educationList.map(item => (
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

          {/* Career */}
          <div className="section-block" id="sec-career">
            <div className="section-block-header">
              <div className="section-block-title">
                경력 <span style={{ fontSize: '11px', color: 'var(--muted)', fontWeight: 400 }}>(경력 또는 프로젝트 중 1개 이상 필수)</span>
              </div>
              <button className="add-btn" onClick={() => openModal('career')}>+ 추가</button>
            </div>
            <div id="career-list">
              {careerList.map(item => (
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

          {/* Project */}
          <div className="section-block" id="sec-project">
            <div className="section-block-header">
              <div className="section-block-title">
                프로젝트 <span className="badge-required">1개 이상</span>
              </div>
              <button className="add-btn" onClick={() => openModal('project')}>+ 추가</button>
            </div>
            <div id="project-list">
              {projectList.map(item => (
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

          {/* Optional */}
          <div className="section-block" id="sec-optional">
            <div className="section-block-header">
              <div className="section-block-title">
                어학 / 자격증 / 수상 <span style={{ fontSize: '11px', color: 'var(--muted)', fontWeight: 400 }}>선택</span>
              </div>
              <button className="add-btn" onClick={() => openModal('optional')}>+ 추가</button>
            </div>
            <div id="optional-list">
              {optionalList.map(item => (
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

      {/* Modal */}
      {isModalOpen && (
        <div className="modal-overlay show" onClick={(e) => e.target.className === 'modal-overlay show' && closeModal()}>
          <div className="modal">
            <form onSubmit={saveEntry}>
              {modalType === 'edu' && (
                <>
                  <div className="modal-title">학력 {currentEntry ? '수정' : '추가'}</div>
                  <div className="modal-sub">학교 정보를 입력하세요.</div>
                  <div className="form-grid" style={{ gap: '14px' }}>
                    <div className="field span-2">
                      <label>학교명 *</label>
                      <input name="school" placeholder="한국대학교" value={formData.school || ''} onChange={handleInputChange} required />
                    </div>
                    <div className="field">
                      <label>전공 *</label>
                      <input name="major" placeholder="컴퓨터공학과" value={formData.major || ''} onChange={handleInputChange} required />
                    </div>
                    <div className="field">
                      <label>학위</label>
                      <select name="degree" value={formData.degree || '학사'} onChange={handleInputChange}>
                        <option value="학사">학사</option><option value="석사">석사</option><option value="박사">박사</option><option value="전문학사">전문학사</option>
                      </select>
                    </div>
                    <div className="field">
                      <label>입학 연도</label>
                      <select name="startYear" value={formData.startYear || ''} onChange={handleInputChange}>
                        <option value="">선택</option>
                        {years.map(y => <option key={y} value={y}>{y}년</option>)}
                      </select>
                    </div>
                    <div className="field">
                      <label>입학 월</label>
                      <select name="startMonth" value={formData.startMonth || ''} onChange={handleInputChange}>
                        <option value="">선택</option>
                        {months.map(m => <option key={m} value={m}>{m}월</option>)}
                      </select>
                    </div>
                    <div className="field">
                      <label>졸업 연도</label>
                      <select name="endYear" value={formData.endYear || ''} onChange={handleInputChange}>
                        <option value="">선택</option>
                        {years.map(y => <option key={y} value={y}>{y}년</option>)}
                      </select>
                    </div>
                    <div className="field">
                      <label>졸업 월</label>
                      <select name="endMonth" value={formData.endMonth || ''} onChange={handleInputChange}>
                        <option value="">선택</option>
                        {months.map(m => <option key={m} value={m}>{m}월</option>)}
                      </select>
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
                      <label>직무/직책</label>
                      <input name="position" placeholder="프론트엔드 개발자" value={formData.position || ''} onChange={handleInputChange} />
                    </div>
                    <div className="field">
                      <label>입사 연도</label>
                      <select name="startYear" value={formData.startYear || ''} onChange={handleInputChange}>
                        <option value="">선택</option>
                        {years.map(y => <option key={y} value={y}>{y}년</option>)}
                      </select>
                    </div>
                    <div className="field">
                      <label>입사 월</label>
                      <select name="startMonth" value={formData.startMonth || ''} onChange={handleInputChange}>
                        <option value="">선택</option>
                        {months.map(m => <option key={m} value={m}>{m}월</option>)}
                      </select>
                    </div>
                    <div className="field">
                      <label>퇴사 연도</label>
                      <select name="endYear" value={formData.endYear || ''} onChange={handleInputChange}>
                        <option value="">선택</option>
                        {years.map(y => <option key={y} value={y}>{y}년</option>)}
                      </select>
                    </div>
                    <div className="field">
                      <label>퇴사 월</label>
                      <select name="endMonth" value={formData.endMonth || ''} onChange={handleInputChange}>
                        <option value="">선택</option>
                        {months.map(m => <option key={m} value={m}>{m}월</option>)}
                      </select>
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
                      <label>사용 기술</label>
                      <input name="techStack" placeholder="React, TypeScript, Node.js, ..." value={formData.techStack || ''} onChange={handleInputChange} />
                    </div>
                  </div>
                </>
              )}
              {modalType === 'optional' && (
                <>
                  <div className="modal-title">어학/자격/수상 {currentEntry ? '수정' : '추가'}</div>
                  <div className="modal-sub">선택 항목을 입력하세요.</div>
                  <div className="form-grid" style={{ gap: '14px' }}>
                    <div className="field span-2">
                      <label>종류</label>
                      <select name="category" value={formData.category || '어학'} onChange={handleInputChange}>
                        <option value="어학">어학</option><option value="자격증">자격증</option><option value="수상">수상</option>
                      </select>
                    </div>
                    <div className="field span-2">
                      <label>내용 *</label>
                      <input name="content" placeholder="TOEIC 900점 / 정보처리기사 / ..." value={formData.content || ''} onChange={handleInputChange} required />
                    </div>
                    <div className="field">
                      <label>취득 연도</label>
                      <select name="year" value={formData.year || ''} onChange={handleInputChange}>
                        <option value="">선택</option>
                        {years.map(y => <option key={y} value={y}>{y}년</option>)}
                      </select>
                    </div>
                    <div className="field">
                      <label>취득 월</label>
                      <select name="month" value={formData.month || ''} onChange={handleInputChange}>
                        <option value="">선택</option>
                        {months.map(m => <option key={m} value={m}>{m}월</option>)}
                      </select>
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
        <span className="save-notice">변경사항은 자동 저장되지 않습니다</span>
        <button className="btn btn-outline btn-ghost" onClick={() => navigate('/analyze')}>
          진단하기로 이동
        </button>
        <button className="btn btn-primary" onClick={saveProfile}>
          저장하기
        </button>
      </div>
    </div>
  );
}
