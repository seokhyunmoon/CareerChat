package com.careerchat.backend.auth.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record SignupRequest(

        @NotBlank(message = "Name is required.")
        @Size(max = 100, message = "Name must be 100 characters or less.")
        String name,

        @NotBlank(message = "Email is required.")
        @Email(message = "Email must be valid.")
        @Size(max = 100, message = "Email must be 100 characters or less.")
        String email,

        @NotBlank(message = "Password is required.")
        @Size(min = 8, max = 72, message = "Password must be between 8 and 72 characters.")
        String password,

        @Size(max = 20, message = "Telephone must be 20 characters or less.")
        String telephone
) {
}
