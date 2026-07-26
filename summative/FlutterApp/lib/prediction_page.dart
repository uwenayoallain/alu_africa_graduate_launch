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
  final _ageController = TextEditingController(text: '23');
  final _hoursController = TextEditingController(text: '36');

  String _education = 'Primary education';
  String _career = 'Agriculture';
  String _sector = 'Agriculture';
  String _employer = 'Private business or VUP';
  String _contract = 'Oral agreement';
  String _residence = 'Rural';
  String _province = 'Eastern Province';
  bool _loading = false;
  PredictionResult? _result;
  String? _error;

  static const educationLevels = [
    'No formal education',
    'Pre-primary',
    'Primary education',
    'Lower secondary education',
    'Upper secondary education',
    'Tertiary education',
  ];

  static const employerTypes = [
    'Private business or VUP',
    'Public institution',
    'Public-private enterprise',
    'Household',
    'Cooperative',
    'NGO or international organisation',
    'Other',
  ];

  static const provinces = [
    'Kigali city',
    'Eastern Province',
    'Northern Province',
    'Southern Province',
    'Western Province',
  ];

  static const educationCareers = {
    'No formal education': ['Agriculture', 'Elementary and other work'],
    'Pre-primary': ['Agriculture', 'Elementary and other work'],
    'Primary education': [
      'Sales and services',
      'Skilled trades and operators',
      'Education, health and social services',
      'Agriculture',
      'Elementary and other work',
    ],
    'Lower secondary education': [
      'Sales and services',
      'Skilled trades and operators',
      'Education, health and social services',
      'Agriculture',
      'Elementary and other work',
    ],
    'Upper secondary education': [
      'ICT',
      'Science and engineering',
      'Education, health and social services',
      'Business, management and office work',
      'Sales and services',
      'Skilled trades and operators',
      'Agriculture',
      'Elementary and other work',
    ],
    'Tertiary education': [
      'ICT',
      'Science and engineering',
      'Education, health and social services',
      'Business, management and office work',
      'Sales and services',
      'Skilled trades and operators',
      'Elementary and other work',
    ],
  };

  static const careerSectors = {
    'ICT': ['Services'],
    'Science and engineering': ['Industry', 'Services'],
    'Education, health and social services': ['Services'],
    'Business, management and office work': ['Industry', 'Services'],
    'Sales and services': ['Industry', 'Services'],
    'Skilled trades and operators': ['Industry', 'Services'],
    'Agriculture': ['Agriculture', 'Industry', 'Services'],
    'Elementary and other work': ['Agriculture', 'Industry', 'Services'],
  };

  static const employerContracts = {
    'Private business or VUP': ['Oral agreement', 'Written contract'],
    'Public institution': ['Oral agreement', 'Written contract'],
    'Public-private enterprise': ['Written contract'],
    'Household': ['Oral agreement', 'Written contract'],
    'Cooperative': ['Oral agreement'],
    'NGO or international organisation': ['Oral agreement', 'Written contract'],
    'Other': ['Oral agreement'],
  };

  List<String> get _careerOptions => educationCareers[_education]!;
  List<String> get _sectorOptions => careerSectors[_career]!;
  List<String> get _contractOptions => employerContracts[_employer]!;

  String get _careerSupport {
    if (_education == 'Pre-primary') {
      return 'This education level has limited survey coverage, so use the estimate carefully.';
    }
    if (const [
      'ICT',
      'Science and engineering',
      'Business, management and office work',
    ].contains(_career)) {
      return 'This career has limited survey coverage, so use the estimate carefully.';
    }
    return 'This career has broader coverage in the survey.';
  }

  void _changeEducation(String value) {
    setState(() {
      _education = value;
      final careers = educationCareers[value]!;
      if (!careers.contains(_career)) _career = careers.first;
      final sectors = careerSectors[_career]!;
      if (!sectors.contains(_sector)) _sector = sectors.first;
    });
  }

  void _changeCareer(String value) {
    setState(() {
      _career = value;
      final sectors = careerSectors[value]!;
      if (!sectors.contains(_sector)) _sector = sectors.first;
    });
  }

  void _changeEmployer(String value) {
    setState(() {
      _employer = value;
      final contracts = employerContracts[value]!;
      if (!contracts.contains(_contract)) _contract = contracts.first;
    });
  }

  @override
  void dispose() {
    _ageController.dispose();
    _hoursController.dispose();
    super.dispose();
  }

  String? _numberError(
    String? value,
    String label,
    double minimum,
    double maximum,
  ) {
    if (value == null || value.trim().isEmpty) return '$label is required';
    final number = double.tryParse(value);
    if (number == null) return 'Enter a number';
    if (number < minimum || number > maximum) {
      return 'Use a value from ${minimum.round()} to ${maximum.round()}';
    }
    return null;
  }

  Future<void> _predict() async {
    FocusScope.of(context).unfocus();
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _loading = true;
      _error = null;
      _result = null;
    });

    final payload = {
      'age': int.parse(_ageController.text),
      'education_level': _education,
      'career_field': _career,
      'main_sector': _sector,
      'employer_type': _employer,
      'contract_type': _contract,
      'weekly_hours': double.parse(_hoursController.text),
      'residence': _residence,
      'province': _province,
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
        physics: const BouncingScrollPhysics(),
        slivers: [
          SliverToBoxAdapter(child: _hero()),
          SliverPadding(
            padding: const EdgeInsets.fromLTRB(16, 18, 16, 40),
            sliver: SliverToBoxAdapter(
              child: Form(
                key: _formKey,
                child: Column(
                  children: [
                    _section(
                      '01',
                      'Education & direction',
                      'Start with your current learning and career path.',
                      [
                        _numberField(_ageController, 'Age', 16, 30),
                        _dropdown(
                          'Education level',
                          _education,
                          educationLevels,
                          _changeEducation,
                        ),
                        _dropdown(
                          'Career field',
                          _career,
                          _careerOptions,
                          _changeCareer,
                          helperText: _careerSupport,
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    _section(
                      '02',
                      'Work pathway',
                      'Describe the work setting you want to compare.',
                      [
                        _dropdown(
                          'Main sector',
                          _sector,
                          _sectorOptions,
                          (value) => setState(() => _sector = value),
                          helperText: 'Choices match the selected career.',
                        ),
                        _dropdown(
                          'Employer type',
                          _employer,
                          employerTypes,
                          _changeEmployer,
                        ),
                        _dropdown(
                          'Contract type',
                          _contract,
                          _contractOptions,
                          (value) => setState(() => _contract = value),
                          helperText: 'Choices match the selected employer.',
                        ),
                        _numberField(
                          _hoursController,
                          'Usual weekly hours',
                          1,
                          118,
                        ),
                        _dropdown(
                          'Province',
                          _province,
                          provinces,
                          (value) => setState(() => _province = value),
                        ),
                        _dropdown(
                          'Area type',
                          _residence,
                          const ['Rural', 'Urban'],
                          (value) => setState(() => _residence = value),
                          helperText:
                              'Rural and urban are both represented in $_province.',
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    SizedBox(
                      width: double.infinity,
                      height: 58,
                      child: FilledButton.icon(
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
                            : const Icon(Icons.arrow_outward_rounded),
                        label: Text(
                          _loading ? 'Calculating…' : 'Predict income',
                        ),
                        style: FilledButton.styleFrom(
                          backgroundColor: GraduateLaunchApp.clay,
                          foregroundColor: Colors.white,
                          textStyle: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(17),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    if (_result != null) _resultCard(_result!),
                    if (_error != null) _messageCard(_error!, true),
                    if (_result == null && _error == null)
                      _messageCard(
                        'Complete the fields to compare this pathway.',
                        false,
                      ),
                  ],
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
      decoration: const BoxDecoration(color: GraduateLaunchApp.forest),
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          Positioned(
            right: -68,
            top: 14,
            child: Container(
              width: 180,
              height: 180,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: GraduateLaunchApp.gold.withValues(alpha: 0.14),
                  width: 30,
                ),
              ),
            ),
          ),
          SafeArea(
            bottom: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 28, 20, 30),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 11,
                      vertical: 7,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.08),
                      borderRadius: BorderRadius.circular(999),
                      border: Border.all(
                        color: Colors.white.withValues(alpha: 0.14),
                      ),
                    ),
                    child: const Text(
                      'RWANDA LFS  •  2024',
                      style: TextStyle(
                        color: GraduateLaunchApp.gold,
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.2,
                      ),
                    ),
                  ),
                  const SizedBox(height: 22),
                  Text(
                    'See where your\npath could lead.',
                    style: Theme.of(
                      context,
                    ).textTheme.displayLarge?.copyWith(fontSize: 38),
                  ),
                  const SizedBox(height: 14),
                  const Text(
                    'Compare education and work choices using a youth '
                    'income benchmark from Rwanda.',
                    style: TextStyle(
                      color: Color(0xFFDCE9E3),
                      height: 1.45,
                      fontSize: 15,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _section(
    String number,
    String title,
    String description,
    List<Widget> children,
  ) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 8),
      decoration: BoxDecoration(
        color: const Color(0xFFFFFCF4),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE0D8C9)),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0D123D35),
            blurRadius: 24,
            offset: Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 34,
                height: 34,
                alignment: Alignment.center,
                decoration: const BoxDecoration(
                  color: Color(0xFFE7EFEA),
                  shape: BoxShape.circle,
                ),
                child: Text(
                  number,
                  style: const TextStyle(
                    color: GraduateLaunchApp.forest,
                    fontSize: 12,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ),
              const SizedBox(width: 11),
              Expanded(
                child: Text(
                  title,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            description,
            style: const TextStyle(
              color: Color(0xFF68716D),
              fontSize: 13,
              height: 1.4,
            ),
          ),
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
    ValueChanged<String> onChanged, {
    String? helperText,
  }) {
    return DropdownButtonFormField<String>(
      key: ValueKey('$label-$value-${items.join('|')}'),
      initialValue: value,
      isExpanded: true,
      menuMaxHeight: 360,
      borderRadius: BorderRadius.circular(18),
      icon: const Icon(Icons.keyboard_arrow_down_rounded),
      decoration: InputDecoration(
        labelText: label,
        helperText: helperText,
        helperMaxLines: 2,
      ),
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

  Widget _numberField(
    TextEditingController controller,
    String label,
    double minimum,
    double maximum,
  ) {
    return TextFormField(
      controller: controller,
      keyboardType: TextInputType.number,
      decoration: InputDecoration(labelText: label),
      validator: (value) => _numberError(value, label, minimum, maximum),
    );
  }

  Widget _resultCard(PredictionResult result) {
    final money = NumberFormat.currency(
      locale: 'en',
      symbol: 'RWF ',
      decimalDigits: 0,
    );
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF123D35), Color(0xFF1C5549)],
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: const [
          BoxShadow(
            color: Color(0x26123D35),
            blurRadius: 28,
            offset: Offset(0, 12),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'ESTIMATED MONTHLY INCOME',
            style: TextStyle(
              color: Color(0xFFE6B557),
              fontWeight: FontWeight.w800,
              letterSpacing: 1.1,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            money.format(result.incomeRwf),
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              color: Colors.white,
              fontSize: 36,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            result.incomeBand,
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

  Widget _messageCard(String message, bool error) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: error ? const Color(0xFFFFE8DF) : const Color(0xFFE7EFEA),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: error ? const Color(0xFFF4B9A4) : const Color(0xFFC8DAD1),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            error ? Icons.error_outline_rounded : Icons.info_outline_rounded,
            color: error ? GraduateLaunchApp.clay : GraduateLaunchApp.forest,
            size: 21,
          ),
          const SizedBox(width: 10),
          Expanded(child: Text(message, style: const TextStyle(height: 1.4))),
        ],
      ),
    );
  }
}
