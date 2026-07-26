# African Graduate Launch mobile app

This single-page Flutter app collects the model's 11 education, employability,
and first-job pathway inputs. It calls `POST /predict` and displays a historical
first-monthly-income benchmark in 2018 NGN, its survey band, or a useful error.

```bash
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

Replace the URL with the deployed Render API for the submission build.
