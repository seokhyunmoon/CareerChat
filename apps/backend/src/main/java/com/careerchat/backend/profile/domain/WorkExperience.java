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
@Table(name = "work_experience")
public class WorkExperience {

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	@Column(name = "career_id")
	private Long id;

	@ManyToOne(fetch = FetchType.LAZY, optional = false)
	@JoinColumn(
		name = "profile_id",
		nullable = false,
		foreignKey = @ForeignKey(name = "fk_work_experience_profile")
	)
	private Profile profile;

	@Column(name = "company_name", nullable = false, length = 255)
	private String companyName;

	@Column(name = "employment_type", nullable = false, length = 50)
	private String employmentType;

	@Column(name = "position", length = 255)
	private String position;

	@Column(name = "start_date")
	private LocalDate startDate;

	@Column(name = "end_date")
	private LocalDate endDate;

	@Column(name = "description", columnDefinition = "TEXT")
	private String description;

	protected WorkExperience() {
	}

	public WorkExperience(
		Profile profile,
		String companyName,
		String employmentType,
		String position,
		LocalDate startDate,
		LocalDate endDate,
		String description
	) {
		this.profile = Objects.requireNonNull(profile);
		this.companyName = Objects.requireNonNull(companyName);
		this.employmentType = Objects.requireNonNull(employmentType);
		this.position = position;
		this.startDate = startDate;
		this.endDate = endDate;
		this.description = description;
	}

	public Long getId() {
		return id;
	}

	public Profile getProfile() {
		return profile;
	}

	public String getCompanyName() {
		return companyName;
	}

	public String getEmploymentType() {
		return employmentType;
	}

	public String getPosition() {
		return position;
	}

	public LocalDate getStartDate() {
		return startDate;
	}

	public LocalDate getEndDate() {
		return endDate;
	}

	public String getDescription() {
		return description;
	}
}
