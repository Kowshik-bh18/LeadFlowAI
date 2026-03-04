import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('title', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='questionnaires/')),
                ('status', models.CharField(choices=[('uploaded','Uploaded'),('processing','Processing'),('ready','Ready'),('error','Error')], default='uploaded', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questionnaires', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('text', models.TextField()),
                ('category', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('questionnaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='questionnaires.questionnaire')),
            ],
            options={'ordering': ['order']},
        ),
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('status', models.CharField(choices=[('pending','Pending'),('running','Running'),('completed','Completed'),('failed','Failed')], default='pending', max_length=20)),
                ('run_number', models.PositiveIntegerField(default=1)),
                ('total_questions', models.PositiveIntegerField(default=0)),
                ('answered_count', models.PositiveIntegerField(default=0)),
                ('not_found_count', models.PositiveIntegerField(default=0)),
                ('error_message', models.TextField(blank=True)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('questionnaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='runs', to='questionnaires.questionnaire')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-started_at']},
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('answer_text', models.TextField()),
                ('is_edited', models.BooleanField(default=False)),
                ('confidence_score', models.FloatField(default=0.0)),
                ('citations', models.JSONField(default=list)),
                ('evidence_snippets', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='questionnaires.question')),
                ('run', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='questionnaires.run')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
