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
  final _ageController = TextEditingController(text: '24');
  final _hoursController = TextEditingController(text: '40');

  String _education = 'Upper secondary education';
  String _career = 'ICT';
  String _sector = 'Services';
  String _employer = 'Private business or VUP';
  String _contract = 'Written contract';
  String _residence = 'Urban';
  String _province = 'Kigali city';
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

  static const careerFields = [
    'ICT',
    'Science and engineering',
    'Education, health and social services',
    'Business, management and office work',
    'Sales and services',
    'Skilled trades and operators',
    'Agriculture',
    'Elementary and other work',
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
                        _section('Education and direction', [
                          _numberField(_ageController, 'Age', 16, 30),
                          _dropdown(
                            'Education level',
                            _education,
                            educationLevels,
                            (value) => setState(() => _education = value),
                          ),
                          _dropdown(
                            'Career field',
                            _career,
                            careerFields,
                            (value) => setState(() => _career = value),
                          ),
                        ]),
                        const SizedBox(height: 18),
                        _section('Work pathway', [
                          _dropdown(
                            'Main sector',
                            _sector,
                            const ['Agriculture', 'Industry', 'Services'],
                            (value) => setState(() => _sector = value),
                          ),
                          _dropdown(
                            'Employer type',
                            _employer,
                            employerTypes,
                            (value) => setState(() => _employer = value),
                          ),
                          _dropdown(
                            'Contract type',
                            _contract,
                            const ['Oral agreement', 'Written contract'],
                            (value) => setState(() => _contract = value),
                          ),
                          _numberField(
                            _hoursController,
                            'Usual weekly hours',
                            1,
                            118,
                          ),
                          _dropdown(
                            'Residence',
                            _residence,
                            const ['Rural', 'Urban'],
                            (value) => setState(() => _residence = value),
                          ),
                          _dropdown(
                            'Province',
                            _province,
                            provinces,
                            (value) => setState(() => _province = value),
                          ),
                        ]),
                        const SizedBox(height: 24),
                        SizedBox(
                          width: double.infinity,
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
                        if (_error != null) _messageCard(_error!, true),
                        if (_result == null && _error == null)
                          _messageCard(
                            'Your estimated monthly income will appear here.',
                            false,
                          ),
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
                    'AFRICAN YOUTH CAREER PATHWAYS',
                    style: TextStyle(
                      color: Color(0xFFE6B557),
                      fontWeight: FontWeight.w800,
                      letterSpacing: 1.1,
                    ),
                  ),
                  const SizedBox(height: 18),
                  Text(
                    'Explore a path.\nBuild the skills.\nEnter the industry.',
                    style: Theme.of(
                      context,
                    ).textTheme.displayLarge?.copyWith(fontSize: 42),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Compare education and work pathways using a Rwanda '
                    'Labour Force Survey income benchmark.',
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

  Widget _section(String title, List<Widget> children) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFFFFCF4),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFFE3DCCF)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleLarge),
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
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: GraduateLaunchApp.forest,
        borderRadius: BorderRadius.circular(22),
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
              fontSize: 40,
            ),
          ),
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
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: error ? const Color(0xFFFFE8DF) : Colors.transparent,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Text(message),
    );
  }
}
