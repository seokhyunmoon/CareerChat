package com.careerchat.backend.ai.client;

public class AiAnalysisClientException extends RuntimeException {

    public AiAnalysisClientException(String message) {
        super(message);
    }

    public AiAnalysisClientException(String message, Throwable cause) {
        super(message, cause);
    }
}
