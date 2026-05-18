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
import java.util.Objects;

@Entity
@Table(name = "projects")
public class Project {

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	@Column(name = "project_id")
	private Long id;

	@ManyToOne(fetch = FetchType.LAZY, optional = false)
	@JoinColumn(
		name = "profile_id",
		nullable = false,
		foreignKey = @ForeignKey(name = "fk_projects_profile")
	)
	private Profile profile;

	@Column(name = "project_name", nullable = false, length = 255)
	private String projectName;

	@Column(name = "description", nullable = false, columnDefinition = "TEXT")
	private String description;

	protected Project() {
	}

	public Project(Profile profile, String projectName, String description) {
		this.profile = Objects.requireNonNull(profile);
		this.projectName = Objects.requireNonNull(projectName);
		this.description = Objects.requireNonNull(description);
	}

	public Long getId() {
		return id;
	}

	public Profile getProfile() {
		return profile;
	}

	public String getProjectName() {
		return projectName;
	}

	public String getDescription() {
		return description;
	}
}
