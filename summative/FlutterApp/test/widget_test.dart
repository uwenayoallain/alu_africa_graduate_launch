import 'package:africa_tech_benchmark/main.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('renders the complete prediction page', (tester) async {
    await tester.pumpWidget(const GraduateLaunchApp());

    expect(
      find.text('Learn skills.\nBuild experience.\nLaunch a career.'),
      findsOneWidget,
    );
    expect(find.text('01  Learning foundation'), findsOneWidget);
    expect(find.text('02  First opportunity'), findsOneWidget);
    expect(find.text('03  Job-ready experience'), findsOneWidget);
    expect(find.text('Predict'), findsOneWidget);
  });
}
