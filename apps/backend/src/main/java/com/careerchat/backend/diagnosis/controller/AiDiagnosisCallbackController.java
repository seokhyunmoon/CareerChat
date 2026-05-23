package com.careerchat.backend.diagnosis.controller;

import com.careerchat.backend.diagnosis.dto.AiDiagnosisCompleteRequest;
import com.careerchat.backend.diagnosis.dto.AiDiagnosisFailRequest;
import com.careerchat.backend.diagnosis.service.DiagnosisService;
import com.careerchat.backend.global.common.ApiResponse;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import jakarta.validation.Valid;
import java.util.Objects;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AiDiagnosisCallbackController {

    private static final String BEARER_PREFIX = "Bearer ";

    private final DiagnosisService diagnosisService;
    private final String callbackToken;

    public AiDiagnosisCallbackController(
            DiagnosisService diagnosisService,
            @Value("${careerchat.ai.callback-token}") String callbackToken
    ) {
        this.diagnosisService = diagnosisService;
        this.callbackToken = callbackToken;
    }

    @PostMapping("/internal/ai/diagnoses/{diagnosisId}/complete")
    public ApiResponse<Void> completeDiagnosis(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable Long diagnosisId,
            @Valid @RequestBody AiDiagnosisCompleteRequest request
    ) {
        validateCallbackToken(authorization);
        diagnosisService.completeDiagnosisFromAi(diagnosisId, request);

        return ApiResponse.empty();
    }

    @PostMapping("/internal/ai/diagnoses/{diagnosisId}/fail")
    public ApiResponse<Void> failDiagnosis(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable Long diagnosisId,
            @Valid @RequestBody AiDiagnosisFailRequest request
    ) {
        validateCallbackToken(authorization);
        diagnosisService.failDiagnosisFromAi(diagnosisId, request);

        return ApiResponse.empty();
    }

    private void validateCallbackToken(String authorization) {
        if (authorization == null || !authorization.startsWith(BEARER_PREFIX)) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED, "Invalid AI callback token.");
        }

        String token = authorization.substring(BEARER_PREFIX.length());
        if (!Objects.equals(callbackToken, token)) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED, "Invalid AI callback token.");
        }
    }
}
