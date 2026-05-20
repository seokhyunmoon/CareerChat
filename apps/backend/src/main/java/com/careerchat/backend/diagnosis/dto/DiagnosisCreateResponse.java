package com.careerchat.backend.diagnosis.dto;

import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.DiagnosisStatus;
import com.careerchat.backend.diagnosis.domain.JDResult;
import java.util.List;

public record DiagnosisCreateResponse(
        Long diagnosisId,
        DiagnosisStatus status,
        List<JobResponse> jobs
) {

    public static DiagnosisCreateResponse of(Diagnosis diagnosis, List<JDResult> jdResults) {
        return new DiagnosisCreateResponse(
                diagnosis.getId(),
                diagnosis.getStatus(),
                jdResults.stream()
                        .map(JobResponse::from)
                        .toList()
        );
    }

    public record JobResponse(
            Long jdId,
            Integer displayOrder,
            String companyName,
            String position
    ) {

        public static JobResponse from(JDResult jdResult) {
            return new JobResponse(
                    jdResult.getId(),
                    jdResult.getDisplayOrder(),
                    jdResult.getCompanyName(),
                    jdResult.getPosition()
            );
        }
    }
}
