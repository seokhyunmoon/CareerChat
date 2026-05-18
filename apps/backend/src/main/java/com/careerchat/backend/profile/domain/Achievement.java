package com.careerchat.backend.profile.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.ForeignKey;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import java.time.LocalDate;
import java.util.Objects;

@Entity
@Table(name = "achievements")
public class Achievement {

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	@Column(name = "award_id")
	private Long id;

	@ManyToOne(fetch = FetchType.LAZY, optional = false)
	@JoinColumn(
		name = "profile_id",
		nullable = false,
		foreignKey = @ForeignKey(name = "fk_achievements_profile")
	)
	private Profile profile;

	@Column(name = "title", nullable = false, length = 255)
	private String title;

	@Column(name = "issuer", length = 255)
	private String issuer;

	@Column(name = "score_or_grade", length = 100)
	private String scoreOrGrade;

	@Column(name = "acquired_date")
	private LocalDate acquiredDate;

	protected Achievement() {
	}

	public Achievement(
		Profile profile,
		String title,
		String issuer,
		String scoreOrGrade,
		LocalDate acquiredDate
	) {
		this.profile = Objects.requireNonNull(profile);
		this.title = Objects.requireNonNull(title);
		this.issuer = issuer;
		this.scoreOrGrade = scoreOrGrade;
		this.acquiredDate = acquiredDate;
	}

	public Long getId() {
		return id;
	}

	public Profile getProfile() {
		return profile;
	}

	public String getTitle() {
		return title;
	}

	public String getIssuer() {
		return issuer;
	}

	public String getScoreOrGrade() {
		return scoreOrGrade;
	}

	public LocalDate getAcquiredDate() {
		return acquiredDate;
	}
}
