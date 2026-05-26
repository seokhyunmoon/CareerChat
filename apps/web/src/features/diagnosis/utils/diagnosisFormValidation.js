const MAX_JOBS = 3;
const MAX_TITLE_LENGTH = 255;

export function validateDiagnosisJobs(jobCards) {
  if (jobCards.length < 1) {
    return '공고를 최소 1개 이상 입력해주세요.';
  }

  if (jobCards.length > MAX_JOBS) {
    return '공고는 최대 3개까지 입력할 수 있습니다.';
  }

  const invalidIndex = jobCards.findIndex((job) => (
    job.companyName.trim() === '' || job.content.trim() === ''
  ));
  if (invalidIndex >= 0) {
    return `공고 ${invalidIndex + 1}의 회사명과 공고 내용을 입력해주세요.`;
  }

  const tooLongCompanyIndex = jobCards.findIndex((job) => job.companyName.trim().length > MAX_TITLE_LENGTH);
  if (tooLongCompanyIndex >= 0) {
    return `공고 ${tooLongCompanyIndex + 1}의 회사명은 255자 이하로 입력해주세요.`;
  }

  const tooLongPositionIndex = jobCards.findIndex((job) => job.position.trim().length > MAX_TITLE_LENGTH);
  if (tooLongPositionIndex >= 0) {
    return `공고 ${tooLongPositionIndex + 1}의 직무명은 255자 이하로 입력해주세요.`;
  }

  return '';
}

export function getDiagnosisCreateErrorMessage(error) {
  if (error.code === 'PROFILE_NOT_FOUND') {
    return '내 정보를 먼저 저장한 뒤 진단을 시작할 수 있습니다.';
  }

  if (error.status === 401 || error.code === 'UNAUTHORIZED') {
    return '로그인 상태를 확인한 뒤 다시 시도해주세요.';
  }

  if (error.code === 'INVALID_INPUT') {
    return '공고 입력값을 다시 확인해주세요.';
  }

  return error.message ?? '진단 요청을 처리하지 못했습니다.';
}
