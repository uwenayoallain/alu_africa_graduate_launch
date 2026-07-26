import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import 'main.dart';
import 'prediction_service.dart';

class PredictionPage extends StatefulWidget {
  const PredictionPage({super.key});

  @override
  State<PredictionPage> createState() => _PredictionPageState();
}

class _PredictionPageState extends State<PredictionPage> {
  final _formKey = GlobalKey<FormState>();
  final _service = PredictionService();
  final _graduationController = TextEditingController(text: '2017');
  final _skillCountController = TextEditingController(text: '5');

  String _education = "Bachelor's degree";
  String _course = 'Technology and computing';
  String _jobLevel = 'Entry level';
  String _sector = 'Technology and telecommunications';
  String _qualification = 'Gave an advantage';
  String _nysc = 'No';
  int _preparationScore = 3;
  bool _problemSolving = true;
  bool _communication = true;
  bool _loading = false;
  PredictionResult? _result;
  String? _error;

  static const educationLevels = [
    'Ordinary National Diploma (OND)',
    'Higher National Diploma (HND)',
    "Bachelor's degree",
    "Master's degree",
    'MBA degree',
    'PhD/Doctorate degree',
  ];
  static const courseGroups = [
    'Technology and computing',
    'Engineering and built environment',
    'Business and economics',
    'Health and life sciences',
    'Social sciences',
    'Arts, communication and humanities',
    'Law',
    'Education',
    'Other',
  ];
  static const jobLevels = [
    'Entry level',
    'Clerical and administrative',
    'Experienced/professional',
    'Managerial',
    'Executive',
  ];
  static const sectors = [
    'Technology and telecommunications',
    'Finance and consulting',
    'Engineering, construction and energy',
    'Education',
    'Health',
    'Media, marketing and creative',
    'Public and nonprofit',
    'Trade and services',
    'Other',
  ];
  static const qualificationRequirements = [
    'Formal requirement',
    'Gave an advantage',
    'Not required',
    'Unknown',
  ];
  @override
  void dispose() {
    _graduationController.dispose();
    _skillCountController.dispose();
    super.dispose();
  }

  String? _validateInteger(
    String? value, {
    required int minimum,
    required int maximum,
    required String label,
  }) {
    if (value == null || value.trim().isEmpty) return '$label is required';
    final number = int.tryParse(value);
    if (number == null) return 'Enter a whole number';
    if (number < minimum || number > maximum) {
      return 'Use a value from $minimum to $maximum';
    }
    return null;
  }

  Future<void> _predict() async {
    FocusScope.of(context).unfocus();
    if (!_formKey.currentState!.validate()) return;
    final skillCount = int.parse(_skillCountController.text);
    final selectedSkills = (_problemSolving ? 1 : 0) + (_communication ? 1 : 0);
    if (skillCount < selectedSkills) {
      setState(() {
        _error = 'Skill count cannot be lower than the selected skill groups.';
        _result = null;
      });
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
      _result = null;
    });

    final payload = {
      'graduation_year': int.parse(_graduationController.text),
      'education_level': _education,
      'course_group': _course,
      'first_job_level': _jobLevel,
      'first_job_sector': _sector,
      'qualification_requirement': _qualification,
      'first_job_via_nysc': _nysc,
      'course_preparation_score': _preparationScore,
      'employability_skill_count': skillCount,
      'problem_solving_skill': _problemSolving,
      'communication_skill': _communication,
    };

    try {
      final result = await _service.predict(payload);
      if (mounted) setState(() => _result = result);
    } on PredictionException catch (error) {
      if (mounted) setState(() => _error = error.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverToBoxAdapter(child: _hero()),
          SliverPadding(
            padding: const EdgeInsets.fromLTRB(18, 24, 18, 48),
            sliver: SliverToBoxAdapter(
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 720),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      children: [
                        _section(
                          '01',
                          'Learning foundation',
                          'Describe the education pathway before the first role.',
                          [
                            _pair(
                              _integerField(
                                _graduationController,
                                'Graduation year',
                                2013,
                                2017,
                              ),
                              _dropdown(
                                'Education level',
                                _education,
                                educationLevels,
                                (value) => setState(() => _education = value),
                              ),
                            ),
                            _dropdown(
                              'Course family',
                              _course,
                              courseGroups,
                              (value) => setState(() => _course = value),
                            ),
                            _dropdown(
                              'How well the course prepared you',
                              _preparationScore.toString(),
                              const ['1', '2', '3', '4'],
                              (value) => setState(
                                () => _preparationScore = int.parse(value),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 18),
                        _section(
                          '02',
                          'First opportunity',
                          'Compare possible entry roles and sectors.',
                          [
                            _dropdown(
                              'First-job level',
                              _jobLevel,
                              jobLevels,
                              (value) => setState(() => _jobLevel = value),
                            ),
                            _dropdown(
                              'Target sector',
                              _sector,
                              sectors,
                              (value) => setState(() => _sector = value),
                            ),
                            _dropdown(
                              'Qualification requirement',
                              _qualification,
                              qualificationRequirements,
                              (value) => setState(() => _qualification = value),
                            ),
                            _dropdown(
                              'First role came through NYSC',
                              _nysc,
                              const ['Yes', 'No', 'Not completed'],
                              (value) => setState(() => _nysc = value),
                            ),
                          ],
                        ),
                        const SizedBox(height: 18),
                        _section(
                          '03',
                          'Job-ready experience',
                          'Describe the transferable skills from your studies.',
                          [
                            _integerField(
                              _skillCountController,
                              'Employability skills represented',
                              0,
                              6,
                            ),
                            _skillSwitch(
                              'Problem-solving skill',
                              'Ability to solve complex problems.',
                              _problemSolving,
                              (value) =>
                                  setState(() => _problemSolving = value),
                            ),
                            _skillSwitch(
                              'Communication skill',
                              'Written or spoken communication.',
                              _communication,
                              (value) => setState(() => _communication = value),
                            ),
                          ],
                        ),
                        const SizedBox(height: 24),
                        SizedBox(
                          width: double.infinity,
                          child: FilledButton.icon(
                            key: const Key('predictButton'),
                            onPressed: _loading ? null : _predict,
                            icon: _loading
                                ? const SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      color: Colors.white,
                                    ),
                                  )
                                : const Icon(Icons.trending_up_rounded),
                            label: const Text('Predict'),
                            style: FilledButton.styleFrom(
                              backgroundColor: GraduateLaunchApp.clay,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 18),
                            ),
                          ),
                        ),
                        const SizedBox(height: 18),
                        if (_result != null) _resultCard(_result!),
                        if (_error != null) _errorCard(_error!),
                        if (_result == null && _error == null) _emptyCard(),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _hero() {
    return Container(
      decoration: const BoxDecoration(
        color: GraduateLaunchApp.forest,
        borderRadius: BorderRadius.vertical(bottom: Radius.circular(34)),
      ),
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 30, 24, 36),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 720),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'AFRICAN GRADUATE PATHWAYS',
                    style: TextStyle(
                      color: Color(0xFFE6B557),
                      fontWeight: FontWeight.w800,
                      letterSpacing: 1.1,
                    ),
                  ),
                  const SizedBox(height: 18),
                  Text(
                    'Learn skills.\nBuild experience.\nLaunch a career.',
                    style: Theme.of(
                      context,
                    ).textTheme.displayLarge?.copyWith(fontSize: 44),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Explore how education, employability skills, '
                    'and first-job choices relate to early career outcomes.',
                    style: TextStyle(
                      color: Color(0xFFDCE9E3),
                      height: 1.5,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _section(
    String number,
    String title,
    String note,
    List<Widget> children,
  ) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFFFFCF4),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFFE3DCCF)),
        boxShadow: const [
          BoxShadow(
            color: Color(0x110D2D25),
            blurRadius: 22,
            offset: Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$number  $title',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 5),
          Text(note, style: const TextStyle(color: Color(0xFF6C756F))),
          const SizedBox(height: 18),
          ...children.expand((child) => [child, const SizedBox(height: 14)]),
        ],
      ),
    );
  }

  Widget _dropdown(
    String label,
    String value,
    List<String> items,
    ValueChanged<String> onChanged,
  ) {
    return DropdownButtonFormField<String>(
      initialValue: value,
      isExpanded: true,
      decoration: InputDecoration(labelText: label),
      items: items
          .map(
            (item) => DropdownMenuItem(
              value: item,
              child: Text(item, overflow: TextOverflow.ellipsis),
            ),
          )
          .toList(),
      onChanged: (newValue) {
        if (newValue != null) onChanged(newValue);
      },
    );
  }

  Widget _integerField(
    TextEditingController controller,
    String label,
    int minimum,
    int maximum,
  ) {
    return TextFormField(
      controller: controller,
      keyboardType: TextInputType.number,
      decoration: InputDecoration(labelText: label),
      validator: (value) => _validateInteger(
        value,
        minimum: minimum,
        maximum: maximum,
        label: label,
      ),
    );
  }

  Widget _skillSwitch(
    String title,
    String subtitle,
    bool value,
    ValueChanged<bool> onChanged,
  ) {
    return SwitchListTile.adaptive(
      contentPadding: EdgeInsets.zero,
      title: Text(title),
      subtitle: Text(subtitle),
      value: value,
      activeTrackColor: GraduateLaunchApp.forest.withValues(alpha: .55),
      onChanged: onChanged,
    );
  }

  Widget _pair(Widget first, Widget second) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < 540) {
          return Column(children: [first, const SizedBox(height: 14), second]);
        }
        return Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(child: first),
            const SizedBox(width: 14),
            Expanded(child: second),
          ],
        );
      },
    );
  }

  Widget _resultCard(PredictionResult result) {
    final number = NumberFormat.currency(
      locale: 'en_NG',
      symbol: '₦',
      decimalDigits: 0,
    );
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: GraduateLaunchApp.forest,
        borderRadius: BorderRadius.circular(22),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'HISTORICAL FIRST-JOB BENCHMARK',
            style: TextStyle(
              color: Color(0xFFE6B557),
              fontWeight: FontWeight.w800,
              letterSpacing: 1.1,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            number.format(result.incomeNgn),
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              color: Colors.white,
              fontSize: 42,
            ),
          ),
          Text(
            'per month in 2018 · ${result.incomeBand}',
            style: const TextStyle(color: Color(0xFFDCE9E3)),
          ),
          const Divider(height: 30, color: Color(0x557FA496)),
          Text(
            result.programUse,
            style: const TextStyle(color: Color(0xFFCAD9D3), height: 1.45),
          ),
        ],
      ),
    );
  }

  Widget _errorCard(String error) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFFFE8DF),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Text(error),
    );
  }

  Widget _emptyCard() {
    return const Padding(
      padding: EdgeInsets.all(12),
      child: Text('The first-job pathway benchmark will appear here.'),
    );
  }
}
