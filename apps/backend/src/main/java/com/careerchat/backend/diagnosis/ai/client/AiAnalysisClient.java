package com.careerchat.backend.diagnosis.ai.client;

import com.careerchat.backend.diagnosis.ai.dto.AiAnalysisJobCreateResponse;
import com.careerchat.backend.diagnosis.ai.dto.AiAnalysisJobRequest;

public interface AiAnalysisClient {

    AiAnalysisJobCreateResponse createAnalysisJob(AiAnalysisJobRequest request);
}
