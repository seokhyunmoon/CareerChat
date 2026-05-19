package com.careerchat.backend.diagnosis.repository;

import com.careerchat.backend.diagnosis.domain.ChatMessage;
import com.careerchat.backend.diagnosis.domain.Diagnosis;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ChatMessageRepository extends JpaRepository<ChatMessage, Long> {

    List<ChatMessage> findAllByDiagnosisOrderByCreatedAtAscIdAsc(Diagnosis diagnosis);
}
