package com.careerchat.backend.diagnosis.ai.client;

public class AiAnalysisClientException extends RuntimeException {

    public AiAnalysisClientException(String message) {
        super(message);
    }

    public AiAnalysisClientException(String message, Throwable cause) {
        super(message, cause);
    }
}
