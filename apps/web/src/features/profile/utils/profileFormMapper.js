export const GRAD_STATUS_LABELS = {
  ENROLLED: '재학 중',
  EXPECTED: '졸업 예정',
  GRADUATED: '졸업',
  LEAVE: '휴학',
};

export const EMPLOYMENT_TYPE_LABELS = {
  FULL_TIME: '정규직',
  CONTRACT: '계약직',
  INTERN: '인턴',
  OTHER: '기타',
};

export function createEmptyProfileFormState() {
  return {
    jobType: 'new',
    educationList: [],
    careerList: [],
    projectList: [],
    optionalList: [],
  };
}

export function mapProfileResponseToFormState(profile) {
  return {
    jobType: profile.experienceLevel === 'EXPERIENCED' ? 'exp' : 'new',
    educationList: (profile.education ?? []).map(mapEducationResponse),
    careerList: (profile.workExperiences ?? []).map(mapWorkExperienceResponse),
    projectList: (profile.projects ?? []).map(mapProjectResponse),
    optionalList: (profile.achievements ?? []).map(mapAchievementResponse),
  };
}

export function buildProfileRequest({ jobType, educationList, careerList, projectList, optionalList }) {
  return {
    experienceLevel: jobType === 'exp' ? 'EXPERIENCED' : 'NEW',
    education: educationList.map((item) => ({
      schoolName: item.school,
      gradStatus: item.gradStatus || inferGradStatus(item),
      degree: item.degree || null,
      major: item.major || null,
      startDate: toApiDate(item.startYear, item.startMonth),
      endDate: toApiDate(item.endYear, item.endMonth),
    })),
    workExperiences: careerList.map((item) => ({
      companyName: item.company,
      employmentType: item.employmentType || 'OTHER',
      position: item.position || null,
      startDate: toApiDate(item.startYear, item.startMonth),
      endDate: toApiDate(item.endYear, item.endMonth),
      description: item.description || null,
    })),
    projects: projectList.map((item) => ({
      projectName: item.projectName,
      description: buildProjectDescription(item),
    })),
    achievements: optionalList.map((item) => ({
      title: item.content,
      issuer: item.issuer || item.category || null,
      scoreOrGrade: item.scoreOrGrade || null,
      acquiredDate: toApiDate(item.year, item.month),
    })),
  };
}

export function getDefaultFormData(type) {
  if (type === 'edu') {
    return { degree: '학사', gradStatus: 'EXPECTED' };
  }

  if (type === 'career') {
    return { employmentType: 'FULL_TIME' };
  }

  if (type === 'optional') {
    return { category: '어학' };
  }

  return {};
}

export function getEntryTitle(type, data) {
  if (type === 'edu') {
    return data.school;
  }

  if (type === 'career') {
    return data.company;
  }

  if (type === 'project') {
    return data.projectName;
  }

  return data.content;
}

export function generateSubText(type, data) {
  if (type === 'edu') {
    const start = formatYearMonth(data.startYear, data.startMonth);
    const end = formatYearMonth(data.endYear, data.endMonth) || GRAD_STATUS_LABELS[data.gradStatus] || '졸업 예정';
    return [data.degree || '학사', data.major, `${start || '시작일 미입력'} ~ ${end}`].filter(Boolean).join(' · ');
  }

  if (type === 'career') {
    const start = formatYearMonth(data.startYear, data.startMonth);
    const end = formatYearMonth(data.endYear, data.endMonth) || '재직 중';
    return [EMPLOYMENT_TYPE_LABELS[data.employmentType], data.position, `${start || '시작일 미입력'} - ${end}`].filter(Boolean).join(' · ');
  }

  if (type === 'project') {
    return data.techStack || data.description || '';
  }

  if (type === 'optional') {
    const date = formatYearMonth(data.year, data.month);
    return [data.category, data.scoreOrGrade, date].filter(Boolean).join(' · ');
  }

  return '';
}

export function buildProjectDescription(item) {
  const description = item.description?.trim() ?? '';
  const techStack = item.techStack?.trim() ?? '';

  if (description && techStack) {
    return `${description}\n\n사용 기술: ${techStack}`;
  }

  return description || techStack;
}

function mapEducationResponse(item, index) {
  const dates = splitDateRange(item.startDate, item.endDate);
  const data = {
    id: item.educationId ?? index + 1,
    school: item.schoolName ?? '',
    major: item.major ?? '',
    degree: item.degree ?? '학사',
    gradStatus: item.gradStatus ?? 'EXPECTED',
    ...dates,
  };

  return {
    ...data,
    title: data.school,
    sub: generateSubText('edu', data),
  };
}

function mapWorkExperienceResponse(item, index) {
  const dates = splitDateRange(item.startDate, item.endDate);
  const data = {
    id: item.workExperienceId ?? index + 1,
    company: item.companyName ?? '',
    employmentType: item.employmentType ?? 'OTHER',
    position: item.position ?? '',
    description: item.description ?? '',
    ...dates,
  };

  return {
    ...data,
    title: data.company,
    sub: generateSubText('career', data),
  };
}

function mapProjectResponse(item, index) {
  const data = {
    id: item.projectId ?? index + 1,
    projectName: item.projectName ?? '',
    description: item.description ?? '',
    techStack: '',
  };

  return {
    ...data,
    title: data.projectName,
    sub: generateSubText('project', data),
  };
}

function mapAchievementResponse(item, index) {
  const date = splitYearMonth(item.acquiredDate);
  const data = {
    id: item.achievementId ?? index + 1,
    category: '기타',
    content: item.title ?? '',
    issuer: item.issuer ?? '',
    scoreOrGrade: item.scoreOrGrade ?? '',
    year: date.year,
    month: date.month,
  };

  return {
    ...data,
    title: data.content,
    sub: generateSubText('optional', data),
  };
}

function inferGradStatus(item) {
  if (item.endYear && item.endMonth) {
    return 'GRADUATED';
  }

  return 'EXPECTED';
}

function toApiDate(year, month) {
  if (!year || !month) {
    return null;
  }

  return `${year}-${String(month).padStart(2, '0')}-01`;
}

function splitDateRange(startDate, endDate) {
  const start = splitYearMonth(startDate);
  const end = splitYearMonth(endDate);

  return {
    startYear: start.year,
    startMonth: start.month,
    endYear: end.year,
    endMonth: end.month,
  };
}

function splitYearMonth(date) {
  if (!date) {
    return { year: '', month: '' };
  }

  const [year, month] = date.split('-');

  return {
    year: year ?? '',
    month: month ? String(Number(month)) : '',
  };
}

function formatYearMonth(year, month) {
  if (!year || !month) {
    return '';
  }

  return `${year}.${String(month).padStart(2, '0')}`;
}
