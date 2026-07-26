import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'prediction_page.dart';

void main() {
  runApp(const GraduateLaunchApp());
}

class GraduateLaunchApp extends StatelessWidget {
  const GraduateLaunchApp({super.key});

  static const canvas = Color(0xFFF3EFE4);
  static const forest = Color(0xFF173D34);
  static const clay = Color(0xFFC86545);
  static const ink = Color(0xFF18211E);

  @override
  Widget build(BuildContext context) {
    final bodyTheme = GoogleFonts.dmSansTextTheme();
    final displayTheme = GoogleFonts.frauncesTextTheme();

    return MaterialApp(
      title: 'African Youth Career Pathways',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: canvas,
        colorScheme: ColorScheme.fromSeed(
          seedColor: forest,
          brightness: Brightness.light,
          primary: forest,
          secondary: clay,
          surface: const Color(0xFFFFFCF4),
        ),
        textTheme: bodyTheme.copyWith(
          displayLarge: displayTheme.displayLarge?.copyWith(
            color: const Color(0xFFFFF8E9),
            fontWeight: FontWeight.w700,
            height: 0.95,
          ),
          headlineMedium: displayTheme.headlineMedium?.copyWith(
            color: ink,
            fontWeight: FontWeight.w700,
          ),
          titleLarge: displayTheme.titleLarge?.copyWith(
            color: ink,
            fontWeight: FontWeight.w700,
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white.withValues(alpha: 0.82),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 15,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: Color(0xFFD8D1C2)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: Color(0xFFD8D1C2)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: forest, width: 2),
          ),
        ),
      ),
      home: const PredictionPage(),
    );
  }
}
