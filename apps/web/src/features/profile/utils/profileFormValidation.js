import { buildProjectDescription } from '@/features/profile/utils/profileFormMapper';

export function getCurrentDateLimit() {
  const today = new Date();

  return {
    year: today.getFullYear(),
    month: today.getMonth() + 1,
  };
}

export function validateYearMonth(year, month, dateLimit, options = {}) {
  if (!year || !month) {
    return true;
  }

  if (options.allowFuture) {
    return true;
  }

  const selectedYear = Number(year);
  const selectedMonth = Number(month);

  if (selectedYear < dateLimit.year) {
    return true;
  }

  return selectedYear === dateLimit.year && selectedMonth <= dateLimit.month;
}

export function validateProfileForm(educationList, careerList, projectList) {
  if (educationList.length === 0) {
    return '학력은 1개 이상 입력해주세요.';
  }

  if (careerList.length === 0 && projectList.length === 0) {
    return '경력 또는 프로젝트 중 1개 이상 입력해주세요.';
  }

  if (projectList.some((item) => !item.projectName?.trim() || !buildProjectDescription(item).trim())) {
    return '프로젝트명과 프로젝트 설명을 입력해주세요.';
  }

  return '';
}
