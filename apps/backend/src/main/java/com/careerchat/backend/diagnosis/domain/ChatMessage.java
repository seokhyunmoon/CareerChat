package com.careerchat.backend.diagnosis.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.ForeignKey;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import java.time.LocalDateTime;
import java.util.Objects;
import org.hibernate.annotations.ColumnTransformer;

@Entity
@Table(name = "chat_messages")
public class ChatMessage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "message_id")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(
            name = "diagnosis_id",
            nullable = false,
            foreignKey = @ForeignKey(name = "fk_chat_messages_diagnosis")
    )
    private Diagnosis diagnosis;

    @Enumerated(EnumType.STRING)
    @Column(name = "role", nullable = false, length = 20)
    private ChatRole role;

    @Column(name = "content", nullable = false, columnDefinition = "TEXT")
    private String content;

    @Column(name = "evidence_data", columnDefinition = "jsonb")
    @ColumnTransformer(write = "?::jsonb")
    private String evidenceData;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    protected ChatMessage() {
    }

    public ChatMessage(Diagnosis diagnosis, ChatRole role, String content, String evidenceData) {
        this.diagnosis = Objects.requireNonNull(diagnosis);
        this.role = Objects.requireNonNull(role);
        this.content = Objects.requireNonNull(content);
        this.evidenceData = evidenceData;
    }

    @jakarta.persistence.PrePersist
    void prePersist() {
        createdAt = LocalDateTime.now();
    }

    public Long getId() {
        return id;
    }

    public Diagnosis getDiagnosis() {
        return diagnosis;
    }

    public ChatRole getRole() {
        return role;
    }

    public String getContent() {
        return content;
    }

    public String getEvidenceData() {
        return evidenceData;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}
