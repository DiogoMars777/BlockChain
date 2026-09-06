import 'user_model.dart';

class LoginRequest {
  final String tenantSlug;
  final String email;
  final String password;

  LoginRequest({
    required this.tenantSlug,
    required this.email,
    required this.password,
  });

  Map<String, dynamic> toJson() {
    return {
      'tenant_slug': tenantSlug.trim().toLowerCase(),
      'email': email.trim().toLowerCase(),
      'password': password,
    };
  }
}

class TokenResponse {
  final String accessToken;
  final String tokenType;
  final UserModel user;

  TokenResponse({
    required this.accessToken,
    required this.tokenType,
    required this.user,
  });

  factory TokenResponse.fromJson(Map<String, dynamic> json) {
    return TokenResponse(
      accessToken: json['access_token'] ?? '',
      tokenType: json['token_type'] ?? 'bearer',
      user: UserModel.fromJson(json['user'] ?? {}),
    );
  }
}

class ForgotPasswordRequest {
  final String tenantSlug;
  final String email;

  ForgotPasswordRequest({
    required this.tenantSlug,
    required this.email,
  });

  Map<String, dynamic> toJson() {
    return {
      'tenant_slug': tenantSlug.trim().toLowerCase(),
      'email': email.trim().toLowerCase(),
    };
  }
}

class ResetPasswordRequest {
  final String token;
  final String newPassword;
  final String confirmPassword;

  ResetPasswordRequest({
    required this.token,
    required this.newPassword,
    required this.confirmPassword,
  });

  Map<String, dynamic> toJson() {
    return {
      'token': token,
      'new_password': newPassword,
      'confirm_password': confirmPassword,
    };
  }
}

class MessageResponse {
  final String message;

  MessageResponse({required this.message});

  factory MessageResponse.fromJson(Map<String, dynamic> json) {
    return MessageResponse(
      message: json['message'] ?? json['detail'] ?? '',
    );
  }
}
