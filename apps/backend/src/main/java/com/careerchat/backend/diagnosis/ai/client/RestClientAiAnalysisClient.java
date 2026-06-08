package com.careerchat.backend.diagnosis.ai.client;

import com.careerchat.backend.diagnosis.ai.config.AiBackendProperties;
import com.careerchat.backend.diagnosis.ai.dto.AiAnalysisJobCreateResponse;
import com.careerchat.backend.diagnosis.ai.dto.AiAnalysisJobRequest;
import com.careerchat.backend.diagnosis.ai.dto.AiResultChatResponse;
import com.careerchat.backend.diagnosis.ai.dto.AiResultChatResponseRequest;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

@Component
public class RestClientAiAnalysisClient implements AiAnalysisClient {

    private static final String ANALYSIS_JOBS_PATH = "/analysis/jobs";
    private static final String RESULT_CHAT_RESPONSES_PATH = "/chat/responses";

    private final RestClient restClient;

    public RestClientAiAnalysisClient(AiBackendProperties properties) {
        SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
        requestFactory.setConnectTimeout(properties.getRequestTimeout());
        requestFactory.setReadTimeout(properties.getRequestTimeout());

        this.restClient = RestClient.builder()
                .baseUrl(properties.getBackendBaseUrl().toString())
                .requestFactory(requestFactory)
                .build();
    }

    @Override
    public AiAnalysisJobCreateResponse createAnalysisJob(AiAnalysisJobRequest request) {
        try {
            AiAnalysisJobCreateResponse response = restClient.post()
                    .uri(ANALYSIS_JOBS_PATH)
                    .contentType(MediaType.APPLICATION_JSON)
                    .accept(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .body(AiAnalysisJobCreateResponse.class);

            if (response == null || response.taskId() == null || response.taskId().isBlank()) {
                throw new AiAnalysisClientException("AI Backend returned an empty analysis task id.");
            }

            return response;
        } catch (RestClientException exception) {
            throw new AiAnalysisClientException("Failed to request AI analysis job.", exception);
        }
    }

    @Override
    public AiResultChatResponse createResultChatResponse(AiResultChatResponseRequest request) {
        try {
            AiResultChatResponse response = restClient.post()
                    .uri(RESULT_CHAT_RESPONSES_PATH)
                    .contentType(MediaType.APPLICATION_JSON)
                    .accept(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .body(AiResultChatResponse.class);

            if (response == null || response.content() == null || response.content().isBlank()) {
                throw new AiAnalysisClientException("AI Backend returned an empty chat response.");
            }
            if (response.evidenceData() == null) {
                throw new AiAnalysisClientException("AI Backend returned empty chat evidence data.");
            }

            return response;
        } catch (RestClientException exception) {
            throw new AiAnalysisClientException("Failed to request AI chat response.", exception);
        }
    }
}
