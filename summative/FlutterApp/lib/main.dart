import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'prediction_page.dart';

void main() {
  runApp(const GraduateLaunchApp());
}

class GraduateLaunchApp extends StatelessWidget {
  const GraduateLaunchApp({super.key});

  static const canvas = Color(0xFFF4F0E6);
  static const forest = Color(0xFF123D35);
  static const clay = Color(0xFFD76542);
  static const gold = Color(0xFFF2C66D);
  static const ink = Color(0xFF16231F);

  @override
  Widget build(BuildContext context) {
    final bodyTheme = GoogleFonts.dmSansTextTheme();
    final displayTheme = GoogleFonts.frauncesTextTheme();

    return MaterialApp(
      title: 'African Youth Career Pathways',
      debugShowCheckedModeBanner: false,
      builder: (context, child) {
        return ColoredBox(
          color: forest,
          child: Align(
            alignment: Alignment.topCenter,
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 480),
              child: child,
            ),
          ),
        );
      },
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
            height: 1.02,
            letterSpacing: -0.8,
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
          fillColor: const Color(0xFFFFFEFA),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 17,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: Color(0xFFD8D1C2)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: Color(0xFFD8D1C2)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: forest, width: 2),
          ),
          errorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: clay),
          ),
        ),
      ),
      home: const PredictionPage(),
    );
  }
}
