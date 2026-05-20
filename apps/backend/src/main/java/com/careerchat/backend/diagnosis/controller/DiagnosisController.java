package com.careerchat.backend.diagnosis.controller;

import com.careerchat.backend.diagnosis.dto.DiagnosisCreateRequest;
import com.careerchat.backend.diagnosis.dto.DiagnosisCreateResponse;
import com.careerchat.backend.diagnosis.service.DiagnosisService;
import com.careerchat.backend.global.common.ApiResponse;
import com.careerchat.backend.global.security.AuthenticatedUser;
import jakarta.validation.Valid;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class DiagnosisController {

    private final DiagnosisService diagnosisService;

    public DiagnosisController(DiagnosisService diagnosisService) {
        this.diagnosisService = diagnosisService;
    }

    @PostMapping("/diagnoses")
    public ApiResponse<DiagnosisCreateResponse> createDiagnosis(
            @AuthenticationPrincipal AuthenticatedUser authenticatedUser,
            @Valid @RequestBody DiagnosisCreateRequest request
    ) {
        DiagnosisCreateResponse response = diagnosisService.createDiagnosis(authenticatedUser.userId(), request);

        return ApiResponse.success(response);
    }
}