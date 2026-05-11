package com.careerchat.backend.global.exception;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.util.Map;

@JsonInclude(JsonInclude.Include.NON_EMPTY)
public record ErrorResponse(
	boolean success,
	String code,
	String message,
	Map<String, String> errors
) {

	public static ErrorResponse from(ErrorCode errorCode) {
		return from(errorCode, errorCode.getMessage());
	}

	public static ErrorResponse from(ErrorCode errorCode, String message) {
		return new ErrorResponse(false, errorCode.getCode(), message, null);
	}

	public static ErrorResponse validation(Map<String, String> errors) {
		return new ErrorResponse(
			false,
			ErrorCode.INVALID_INPUT.getCode(),
			ErrorCode.INVALID_INPUT.getMessage(),
			Map.copyOf(errors)
		);
	}
}
