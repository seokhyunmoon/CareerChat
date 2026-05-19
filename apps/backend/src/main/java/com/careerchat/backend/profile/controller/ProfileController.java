package com.careerchat.backend.profile.controller;

import com.careerchat.backend.global.common.ApiResponse;
import com.careerchat.backend.global.security.AuthenticatedUser;
import com.careerchat.backend.profile.dto.ProfileRequest;
import com.careerchat.backend.profile.dto.ProfileResponse;
import com.careerchat.backend.profile.service.ProfileService;
import jakarta.validation.Valid;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProfileController {

    private final ProfileService profileService;

    public ProfileController(ProfileService profileService) {
        this.profileService = profileService;
    }

    @GetMapping("/profile")
    public ApiResponse<ProfileResponse> getProfile(
            @AuthenticationPrincipal AuthenticatedUser authenticatedUser
    ) {
        ProfileResponse response = profileService.getProfile(authenticatedUser.userId());

        return ApiResponse.success(response);
    }

    @PutMapping("/profile")
    public ApiResponse<ProfileResponse> saveProfile(
            @AuthenticationPrincipal AuthenticatedUser authenticatedUser,
            @Valid @RequestBody ProfileRequest request
    ) {
        ProfileResponse response = profileService.saveProfile(authenticatedUser.userId(), request);

        return ApiResponse.success(response);
    }
}
