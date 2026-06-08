package com.careerchat.backend.diagnosis.ai.client;

import com.careerchat.backend.diagnosis.ai.dto.AiAnalysisJobCreateResponse;
import com.careerchat.backend.diagnosis.ai.dto.AiAnalysisJobRequest;
import com.careerchat.backend.diagnosis.ai.dto.AiResultChatResponse;
import com.careerchat.backend.diagnosis.ai.dto.AiResultChatResponseRequest;

public interface AiAnalysisClient {

    AiAnalysisJobCreateResponse createAnalysisJob(AiAnalysisJobRequest request);

    AiResultChatResponse createResultChatResponse(AiResultChatResponseRequest request);
}
