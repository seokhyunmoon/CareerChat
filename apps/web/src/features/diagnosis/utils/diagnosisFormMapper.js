export function buildDiagnosisCreateRequest(jobCards) {
  return {
    jobs: jobCards.map((job) => ({
      companyName: job.companyName.trim(),
      position: job.position.trim() || null,
      content: job.content.trim(),
    })),
  };
}
