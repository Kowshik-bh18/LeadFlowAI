"""
Management command: seed_sample_data
Loads the sample reference documents and questionnaire into the database
for a given user (or creates a demo user).

Usage:
    python manage.py seed_sample_data
    python manage.py seed_sample_data --email admin@demo.com
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with sample reference documents and questionnaire'

    def add_arguments(self, parser):
        parser.add_argument('--email', default='demo@leadflow.ai', help='User email')
        parser.add_argument('--password', default='demo1234!', help='User password')

    def handle(self, *args, **options):
        from apps.references.models import ReferenceDocument
        from apps.questionnaires.models import Questionnaire, Question
        from apps.rag_engine.pipeline import index_document

        email = options['email']
        password = options['password']

        # Create or get user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': 'Demo',
                'last_name': 'User',
                'organization': 'LeadFlow AI',
            }
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {email} / {password}'))
        else:
            self.stdout.write(f'Using existing user: {email}')

        # Sample documents
        base = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'sample_data')
        base = os.path.abspath(base)

        docs = [
            ('LeadFlow AI Security Policy', 'security_policy.txt', 'Security Policy'),
            ('Infrastructure Overview', 'infrastructure_overview.txt', 'Infrastructure Overview'),
            ('Data Retention Policy', 'data_retention_policy.txt', 'Data Retention Policy'),
            ('Incident Response Policy', 'incident_response_policy.txt', 'Incident Response Policy'),
            ('Access Control Policy', 'access_control_policy.txt', 'Access Control Policy'),
        ]

        for title, filename, doc_type in docs:
            filepath = os.path.join(base, filename)
            if not os.path.exists(filepath):
                self.stdout.write(self.style.WARNING(f'File not found: {filepath}'))
                continue

            with open(filepath, 'r') as f:
                text = f.read()

            doc, created = ReferenceDocument.objects.get_or_create(
                user=user,
                title=title,
                defaults={'doc_type': doc_type, 'raw_text': text}
            )
            if not created:
                doc.raw_text = text
                doc.save()

            self.stdout.write(f'Indexing: {title}…')
            success = index_document(doc)
            status = 'OK' if success else 'FAILED (check OPENAI_API_KEY)'
            self.stdout.write(f'  → {status}')

        # Sample questionnaire
        questions = [
            "Does LeadFlow AI support multi-factor authentication (MFA) for all user accounts?",
            "What encryption standards are used for data at rest and in transit?",
            "How does LeadFlow AI handle data isolation between different customer tenants?",
            "What is the company's incident response time SLA for critical security breaches?",
            "Where is customer data stored, and what data residency options are available?",
            "Does LeadFlow AI conduct regular third-party penetration testing? How often?",
            "How are user access permissions managed and reviewed?",
            "What is the data retention policy for customer CRM data after contract termination?",
            "Does LeadFlow AI maintain SOC 2 Type II or ISO 27001 certification?",
            "How are backup and disaster recovery procedures implemented?",
            "What logging and audit trail capabilities are available for compliance purposes?",
            "How does LeadFlow AI handle personally identifiable information (PII) under GDPR?",
        ]

        q, created = Questionnaire.objects.get_or_create(
            user=user,
            title='Sample Security Assessment – LeadFlow AI',
            defaults={'description': 'Enterprise security vendor questionnaire (sample)'}
        )
        if created:
            for i, text in enumerate(questions):
                Question.objects.create(questionnaire=q, order=i + 1, text=text)
            self.stdout.write(self.style.SUCCESS(f'Created sample questionnaire with {len(questions)} questions'))
        else:
            self.stdout.write('Sample questionnaire already exists')

        self.stdout.write(self.style.SUCCESS('\nDone! Log in at /auth/login/'))
        self.stdout.write(f'  Email:    {email}')
        self.stdout.write(f'  Password: {password}')
