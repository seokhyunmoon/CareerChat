package com.careerchat.backend.global.exception;

import static org.assertj.core.api.Assertions.assertThat;

import jakarta.validation.Valid;
import java.lang.reflect.Method;
import org.junit.jupiter.api.Test;
import org.springframework.core.MethodParameter;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.BeanPropertyBindingResult;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;

class GlobalExceptionHandlerTest {

	private final GlobalExceptionHandler handler = new GlobalExceptionHandler();

	@Test
	void handlesBusinessException() {
		BusinessException exception = new BusinessException(
			ErrorCode.DUPLICATE_RESOURCE,
			"Email already exists."
		);

		ResponseEntity<ErrorResponse> response = handler.handleBusinessException(exception);

		assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CONFLICT);
		assertThat(response.getBody()).isNotNull();
		assertThat(response.getBody().success()).isFalse();
		assertThat(response.getBody().code()).isEqualTo("DUPLICATE_RESOURCE");
		assertThat(response.getBody().message()).isEqualTo("Email already exists.");
	}

	@Test
	void handlesMethodArgumentNotValidException() throws NoSuchMethodException {
		Method method = ValidationFixture.class.getDeclaredMethod("validate", ValidationRequest.class);
		MethodParameter parameter = new MethodParameter(method, 0);
		ValidationRequest target = new ValidationRequest("");
		BeanPropertyBindingResult bindingResult = new BeanPropertyBindingResult(target, "request");
		bindingResult.addError(new FieldError("request", "email", "must be a valid email"));
		MethodArgumentNotValidException exception = new MethodArgumentNotValidException(parameter, bindingResult);

		ResponseEntity<ErrorResponse> response = handler.handleMethodArgumentNotValidException(exception);

		assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
		assertThat(response.getBody()).isNotNull();
		assertThat(response.getBody().success()).isFalse();
		assertThat(response.getBody().code()).isEqualTo("INVALID_INPUT");
		assertThat(response.getBody().errors()).containsEntry("email", "must be a valid email");
	}

	private record ValidationRequest(String email) {
	}

	private static class ValidationFixture {

		@SuppressWarnings("unused")
		void validate(@Valid ValidationRequest request) {
		}
	}
}
