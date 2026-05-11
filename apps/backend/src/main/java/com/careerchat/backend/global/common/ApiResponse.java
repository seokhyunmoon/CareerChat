package com.careerchat.backend.global.common;

public record ApiResponse<T>(
	boolean success,
	T data,
	String message
) {

	private static final String DEFAULT_SUCCESS_MESSAGE = "Request succeeded.";

	public static <T> ApiResponse<T> success(T data) {
		return success(data, DEFAULT_SUCCESS_MESSAGE);
	}

	public static <T> ApiResponse<T> success(T data, String message) {
		return new ApiResponse<>(true, data, message);
	}

	public static ApiResponse<Void> empty() {
		return new ApiResponse<>(true, null, DEFAULT_SUCCESS_MESSAGE);
	}
}
