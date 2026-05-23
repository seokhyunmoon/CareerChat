package com.careerchat.backend.diagnosis.service;

import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.JDResult;
import com.careerchat.backend.diagnosis.dto.DiagnosisCreateRequest;
import com.careerchat.backend.diagnosis.dto.DiagnosisCreateResponse;
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

    public DiagnosisService(
            UserRepository userRepository,
            ProfileRepository profileRepository,
            DiagnosisRepository diagnosisRepository,
            JDResultRepository jdResultRepository
    ) {
        this.userRepository = userRepository;
        this.profileRepository = profileRepository;
        this.diagnosisRepository = diagnosisRepository;
        this.jdResultRepository = jdResultRepository;
    }

    @Transactional
    public DiagnosisCreateResponse createDiagnosis(Long userId, DiagnosisCreateRequest request) {
        User user = getCurrentUser(userId);
        Profile profile = profileRepository.findByUser(user)
                .orElseThrow(() -> new BusinessException(ErrorCode.PROFILE_NOT_FOUND));

        validateJobsCount(request.jobs());

        Diagnosis diagnosis = diagnosisRepository.save(new Diagnosis(profile));
        List<JDResult> jdResults = saveJdResults(diagnosis, request.jobs());

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

    private User getCurrentUser(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.UNAUTHORIZED, "Authentication is required."));
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
