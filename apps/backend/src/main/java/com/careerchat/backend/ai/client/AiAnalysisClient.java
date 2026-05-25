package com.careerchat.backend.ai.client;

import com.careerchat.backend.ai.dto.AiAnalysisJobCreateResponse;
import com.careerchat.backend.ai.dto.AiAnalysisJobRequest;

public interface AiAnalysisClient {

    AiAnalysisJobCreateResponse createAnalysisJob(AiAnalysisJobRequest request);
}
