import 'dart:convert';

import 'package:http/http.dart' as http;

class PredictionResult {
  const PredictionResult({
    required this.incomeNgn,
    required this.incomeBand,
    required this.programUse,
  });

  final double incomeNgn;
  final String incomeBand;
  final String programUse;

  factory PredictionResult.fromJson(Map<String, dynamic> json) {
    return PredictionResult(
      incomeNgn: (json['predicted_first_monthly_income_ngn_2018'] as num)
          .toDouble(),
      incomeBand: json['income_band'] as String,
      programUse: json['program_use'] as String,
    );
  }
}

class PredictionException implements Exception {
  const PredictionException(this.message);
  final String message;

  @override
  String toString() => message;
}

class PredictionService {
  PredictionService({http.Client? client, String? baseUrl})
    : _client = client ?? http.Client(),
      _baseUrl = (baseUrl ?? _configuredBaseUrl).replaceAll(RegExp(r'/$'), '');

  static const _configuredBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  final http.Client _client;
  final String _baseUrl;

  Future<PredictionResult> predict(Map<String, dynamic> payload) async {
    try {
      final response = await _client
          .post(
            Uri.parse('$_baseUrl/predict'),
            headers: const {'Content-Type': 'application/json; charset=UTF-8'},
            body: jsonEncode(payload),
          )
          .timeout(const Duration(seconds: 25));
      final decoded = jsonDecode(response.body);
      if (response.statusCode == 200 && decoded is Map<String, dynamic>) {
        return PredictionResult.fromJson(decoded);
      }
      throw PredictionException(_extractError(decoded, response.statusCode));
    } on PredictionException {
      rethrow;
    } on FormatException {
      throw const PredictionException(
        'The server returned an unreadable response.',
      );
    } catch (_) {
      throw const PredictionException(
        'Could not reach the prediction service. Check the API URL and connection.',
      );
    }
  }

  String _extractError(dynamic body, int statusCode) {
    if (body is Map<String, dynamic>) {
      final detail = body['detail'];
      if (detail is String) return detail;
      if (detail is List) {
        return detail
            .whereType<Map<String, dynamic>>()
            .map((item) => item['msg']?.toString())
            .whereType<String>()
            .join('\n');
      }
    }
    return 'Prediction failed (HTTP $statusCode).';
  }
}
