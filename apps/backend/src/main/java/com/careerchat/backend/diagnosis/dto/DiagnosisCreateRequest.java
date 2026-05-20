package com.careerchat.backend.diagnosis.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.util.List;

public record DiagnosisCreateRequest(

    @NotNull
    @Size(min = 1, max = 3)
    List<@Valid JobRequest> jobs
) {

    public record JobRequest(
            @NotBlank
            @Size(max = 255)
            String companyName,

            @Size(max = 255)
            String position,

            @NotBlank
            String content
    ) {
    }
}
