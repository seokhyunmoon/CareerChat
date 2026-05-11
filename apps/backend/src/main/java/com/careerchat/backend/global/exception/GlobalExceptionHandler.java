package com.careerchat.backend.global.exception;

import jakarta.validation.ConstraintViolationException;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.context.support.DefaultMessageSourceResolvable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {

	@ExceptionHandler(BusinessException.class)
	public ResponseEntity<ErrorResponse> handleBusinessException(BusinessException exception) {
		ErrorCode errorCode = exception.getErrorCode();

		return ResponseEntity
			.status(errorCode.getStatus())
			.body(ErrorResponse.from(errorCode, exception.getMessage()));
	}

	@ExceptionHandler(MethodArgumentNotValidException.class)
	public ResponseEntity<ErrorResponse> handleMethodArgumentNotValidException(
		MethodArgumentNotValidException exception
	) {
		Map<String, String> errors = new LinkedHashMap<>();
		exception.getBindingResult()
			.getFieldErrors()
			.forEach(error -> errors.putIfAbsent(error.getField(), resolveMessage(error)));

		return ResponseEntity
			.status(ErrorCode.INVALID_INPUT.getStatus())
			.body(ErrorResponse.validation(errors));
	}

	@ExceptionHandler(ConstraintViolationException.class)
	public ResponseEntity<ErrorResponse> handleConstraintViolationException(
		ConstraintViolationException exception
	) {
		Map<String, String> errors = new LinkedHashMap<>();
		exception.getConstraintViolations()
			.forEach(violation -> errors.putIfAbsent(
				violation.getPropertyPath().toString(),
				violation.getMessage()
			));

		return ResponseEntity
			.status(ErrorCode.INVALID_INPUT.getStatus())
			.body(ErrorResponse.validation(errors));
	}

	@ExceptionHandler(Exception.class)
	public ResponseEntity<ErrorResponse> handleException(Exception exception) {
		return ResponseEntity
			.status(ErrorCode.INTERNAL_SERVER_ERROR.getStatus())
			.body(ErrorResponse.from(ErrorCode.INTERNAL_SERVER_ERROR));
	}

	private static String resolveMessage(DefaultMessageSourceResolvable error) {
		if (error.getDefaultMessage() == null || error.getDefaultMessage().isBlank()) {
			return ErrorCode.INVALID_INPUT.getMessage();
		}

		return error.getDefaultMessage();
	}
}
