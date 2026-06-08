package com.careerchat.backend.diagnosis.service;

import com.careerchat.backend.diagnosis.ai.service.AiAnalysisJobStarter;
import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.JDResult;
import com.careerchat.backend.diagnosis.dto.AiDiagnosisCompleteRequest;
import com.careerchat.backend.diagnosis.dto.AiDiagnosisFailRequest;
import com.careerchat.backend.diagnosis.dto.DiagnosisCreateRequest;
import com.careerchat.backend.diagnosis.dto.DiagnosisCreateResponse;
import com.careerchat.backend.diagnosis.dto.DiagnosisHistoryResponse;
import com.careerchat.backend.diagnosis.dto.DiagnosisResultResponse;
import com.careerchat.backend.diagnosis.repository.DiagnosisRepository;
import com.careerchat.backend.diagnosis.repository.JDResultRepository;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.profile.domain.Profile;
import com.careerchat.backend.profile.repository.ProfileRepository;
import com.careerchat.backend.user.domain.User;
import com.careerchat.backend.user.repository.UserRepository;
import java.util.List;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class DiagnosisService {

    private final UserRepository userRepository;
    private final ProfileRepository profileRepository;
    private final DiagnosisRepository diagnosisRepository;
    private final JDResultRepository jdResultRepository;
    private final AiAnalysisJobStarter aiAnalysisJobStarter;

    public DiagnosisService(
            UserRepository userRepository,
            ProfileRepository profileRepository,
            DiagnosisRepository diagnosisRepository,
            JDResultRepository jdResultRepository,
            AiAnalysisJobStarter aiAnalysisJobStarter
    ) {
        this.userRepository = userRepository;
        this.profileRepository = profileRepository;
        this.diagnosisRepository = diagnosisRepository;
        this.jdResultRepository = jdResultRepository;
        this.aiAnalysisJobStarter = aiAnalysisJobStarter;
    }

    @Transactional
    public DiagnosisCreateResponse createDiagnosis(Long userId, DiagnosisCreateRequest request) {
        User user = getCurrentUser(userId);
        Profile profile = profileRepository.findByUser(user)
                .orElseThrow(() -> new BusinessException(ErrorCode.PROFILE_NOT_FOUND));

        validateJobsCount(request.jobs());

        Diagnosis diagnosis = diagnosisRepository.save(new Diagnosis(profile));
        List<JDResult> jdResults = saveJdResults(diagnosis, request.jobs());
        aiAnalysisJobStarter.start(diagnosis, jdResults);

        return DiagnosisCreateResponse.of(diagnosis, jdResults);
    }

    @Transactional(readOnly = true)
    public DiagnosisResultResponse getDiagnosis(Long userId, Long diagnosisId) {
        User user = getCurrentUser(userId);
        Diagnosis diagnosis = diagnosisRepository.findById(diagnosisId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "Diagnosis not found."));

        validateDiagnosisOwner(user, diagnosis);

        List<JDResult> jdResults = jdResultRepository.findAllByDiagnosisOrderByDisplayOrderAsc(diagnosis);

        return DiagnosisResultResponse.of(diagnosis, jdResults);
    }

    @Transactional(readOnly = true)
    public DiagnosisHistoryResponse getDiagnoses(Long userId) {
        User user = getCurrentUser(userId);
        Profile profile = profileRepository.findByUser(user)
                .orElse(null);

        if (profile == null) {
            return new DiagnosisHistoryResponse(List.of());
        }

        List<DiagnosisHistoryResponse.DiagnosisSummaryResponse> diagnoses = diagnosisRepository
                .findAllByProfileOrderByCreatedAtDescIdDesc(profile)
                .stream()
                .map(diagnosis -> DiagnosisHistoryResponse.DiagnosisSummaryResponse.of(
                        diagnosis,
                        jdResultRepository.findAllByDiagnosisOrderByDisplayOrderAsc(diagnosis)
                ))
                .toList();

        return new DiagnosisHistoryResponse(diagnoses);
    }

    @Transactional
    public void completeDiagnosisFromAi(Long diagnosisId, AiDiagnosisCompleteRequest request) {
        Diagnosis diagnosis = getDiagnosisForCallback(diagnosisId);
        validateAiTaskId(diagnosis, request.taskId());
        List<JdResultUpdate> jdResultUpdates = request.jobs().stream()
                .map(jobResult -> new JdResultUpdate(resolveJdResult(diagnosis, jobResult.jdId()), jobResult))
                .toList();

        diagnosis.updateAiMetadata(
                request.modelName(),
                request.promptVersion(),
                request.analysisMetadata()
        );
        diagnosis.complete(
                request.reportSummary(),
                request.reportContent(),
                request.completedAt()
        );
        jdResultUpdates.forEach(JdResultUpdate::apply);
    }

    @Transactional
    public void failDiagnosisFromAi(Long diagnosisId, AiDiagnosisFailRequest request) {
        Diagnosis diagnosis = getDiagnosisForCallback(diagnosisId);
        validateAiTaskId(diagnosis, request.taskId());

        diagnosis.fail(
                request.errorCode(),
                request.errorMessage(),
                request.failedStep(),
                request.errorDetails(),
                request.failedAt()
        );
    }

    private User getCurrentUser(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.UNAUTHORIZED, "Authentication is required."));
    }

    private Diagnosis getDiagnosisForCallback(Long diagnosisId) {
        return diagnosisRepository.findById(diagnosisId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "Diagnosis not found."));
    }

    private void validateAiTaskId(Diagnosis diagnosis, String taskId) {
        if (!Objects.equals(diagnosis.getAiTaskId(), taskId)) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "Invalid AI task id.");
        }
    }

    private JDResult resolveJdResult(Diagnosis diagnosis, Long jdId) {
        return jdResultRepository.findByIdAndDiagnosis(jdId, diagnosis)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "JD result not found."));
    }

    private record JdResultUpdate(
            JDResult jdResult,
            AiDiagnosisCompleteRequest.JobResultRequest jobResult
    ) {

        private void apply() {
            jdResult.updateAnalysisResult(
                    jobResult.rankOrder(),
                    jobResult.fitScore(),
                    jobResult.strengthsSummary(),
                    jobResult.gapsSummary(),
                    jobResult.highlightPoints(),
                    jobResult.strengths(),
                    jobResult.relatedExperiences(),
                    jobResult.gaps(),
                    jobResult.resumeHighlights(),
                    jobResult.strategyAdvice(),
                    jobResult.matchDetails()
            );
        }
    }

    private void validateDiagnosisOwner(User user, Diagnosis diagnosis) {
        Long ownerId = diagnosis.getProfile().getUser().getId();
        if (!Objects.equals(user.getId(), ownerId)) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "Cannot access this diagnosis.");
        }
    }

    private void validateJobsCount(List<DiagnosisCreateRequest.JobRequest> jobs) {
        if (jobs.isEmpty() || jobs.size() > 3) {
            throw new BusinessException(
                    ErrorCode.INVALID_INPUT,
                    "Diagnosis requires 1 to 3 job postings."
            );
        }
    }

    private List<JDResult> saveJdResults(
            Diagnosis diagnosis,
            List<DiagnosisCreateRequest.JobRequest> jobs
    ) {
        List<JDResult> jdResults = jobs.stream()
                .map(job -> new JDResult(
                        diagnosis,
                        job.companyName(),
                        job.position(),
                        job.content(),
                        jobs.indexOf(job) + 1
                ))
                .toList();

        return jdResultRepository.saveAll(jdResults);
    }
}
