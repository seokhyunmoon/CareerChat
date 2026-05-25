package com.careerchat.backend.diagnosis.ai.config;

import java.net.URI;
import java.time.Duration;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "careerchat.ai")
public class AiBackendProperties {

    private URI backendBaseUrl = URI.create("http://localhost:8000");
    private URI callbackBaseUrl = URI.create("http://localhost:8080");
    private Duration requestTimeout = Duration.ofSeconds(10);

    public URI getBackendBaseUrl() {
        return backendBaseUrl;
    }

    public void setBackendBaseUrl(URI backendBaseUrl) {
        this.backendBaseUrl = backendBaseUrl;
    }

    public URI getCallbackBaseUrl() {
        return callbackBaseUrl;
    }

    public void setCallbackBaseUrl(URI callbackBaseUrl) {
        this.callbackBaseUrl = callbackBaseUrl;
    }

    public Duration getRequestTimeout() {
        return requestTimeout;
    }

    public void setRequestTimeout(Duration requestTimeout) {
        this.requestTimeout = requestTimeout;
    }
}
