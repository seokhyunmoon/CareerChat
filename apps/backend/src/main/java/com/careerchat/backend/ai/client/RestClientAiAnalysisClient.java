package com.careerchat.backend.ai.client;

import com.careerchat.backend.ai.config.AiBackendProperties;
import com.careerchat.backend.ai.dto.AiAnalysisJobCreateResponse;
import com.careerchat.backend.ai.dto.AiAnalysisJobRequest;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

@Component
public class RestClientAiAnalysisClient implements AiAnalysisClient {

    private static final String ANALYSIS_JOBS_PATH = "/analysis/jobs";

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
}
