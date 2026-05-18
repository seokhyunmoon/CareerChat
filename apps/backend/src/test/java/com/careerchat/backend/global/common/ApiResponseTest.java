package com.careerchat.backend.global.common;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class ApiResponseTest {

	@Test
	void successWrapsData() {
		ApiResponse<String> response = ApiResponse.success("ok", "Done.");

		assertThat(response.success()).isTrue();
		assertThat(response.data()).isEqualTo("ok");
		assertThat(response.message()).isEqualTo("Done.");
	}

	@Test
	void emptyReturnsSuccessWithoutData() {
		ApiResponse<Void> response = ApiResponse.empty();

		assertThat(response.success()).isTrue();
		assertThat(response.data()).isNull();
		assertThat(response.message()).isEqualTo("Request succeeded.");
	}
}
