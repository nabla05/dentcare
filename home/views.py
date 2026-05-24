from django.shortcuts import render, redirect
from django.contrib import messages
from clinic.models import Employee, Patient, Appointment
import datetime


def home(request):
    doctors = Employee.objects.filter(
        user__role='doctor', status='active'
    ).select_related('user')[:4]

    features = [
        ('patch-check',     'Dentistes Experts',    "Nos professionnels certifiés apportent des années d'expérience à chaque acte."),
        ('shield-plus',     'Sécurisé & Hygiénique', 'Nous appliquons des protocoles de stérilisation stricts pour votre sécurité.'),
        ('calendar2-check', 'Réservation Facile',    'Réservez en ligne en quelques minutes — sans attente.'),
        ('award',           'Équipement Moderne',    'Technologie de pointe pour un traitement précis et confortable.'),
        ('heart-pulse',     'Soins Doux',            'Votre confort est notre priorité à chaque visite.'),
        ('chat-dots',       'Assistance 24h/7j',     'Notre équipe est toujours disponible pour répondre à vos questions.'),
    ]
    return render(request, 'home/index.html', {
        'doctors':  doctors,
        'features': features,
    })


def about(request):
    doctors = Employee.objects.filter(
        user__role='doctor', status='active'
    ).select_related('user')
    return render(request, 'home/about.html', {'doctors': doctors})


def services(request):
    services_list = [
        {'icon': 'tooth',         'name': 'Dentisterie Générale',    'color': '#0d6efd', 'description': 'Bilans, nettoyages, plombages et soins préventifs pour tous les âges.'},
        {'icon': 'align-center',  'name': 'Orthodontie',             'color': '#6f42c1', 'description': "Bagues et gouttières pour aligner les dents et corriger l'occlusion."},
        {'icon': 'stars',         'name': 'Blanchiment Dentaire',    'color': '#ffc107', 'description': 'Traitements de blanchiment professionnels pour un sourire plus éclatant.'},
        {'icon': 'bandaid',       'name': 'Implants Dentaires',      'color': '#198754', 'description': "Solutions permanentes de remplacement dentaire à l'aspect naturel."},
        {'icon': 'heart-pulse',   'name': 'Traitement des Gencives', 'color': '#dc3545', 'description': 'Diagnostic et traitement des maladies parodontales pour protéger votre santé bucco-dentaire.'},
        {'icon': 'camera',        'name': 'Radiographies Dentaires', 'color': '#0dcaf0', 'description': 'Radiographies numériques pour un diagnostic précis avec un minimum de rayonnement.'},
        {'icon': 'emoji-smile',   'name': 'Dentisterie Esthétique',  'color': '#fd7e14', 'description': 'Facettes, collage et relookings du sourire pour le sourire de vos rêves.'},
        {'icon': 'shield-check',  'name': 'Dévitalisation',          'color': '#20c997', 'description': 'Traitement canalaire indolore pour sauver les dents endommagées ou infectées.'},
        {'icon': 'person-hearts', 'name': 'Dentisterie Pédiatrique', 'color': '#e83e8c', 'description': 'Soins dentaires doux et ludiques spécialement conçus pour les enfants.'},
    ]
    return render(request, 'home/services.html', {'services': services_list})


def contact(request):
    if request.method == 'POST':
        messages.success(request, 'Merci ! Nous vous répondrons très bientôt.')
        return redirect('home:contact')

    contact_info = [
        ('geo-alt',   'Adresse',    '123 Rue Dentaire, Quartier Médical'),
        ('telephone', 'Téléphone',  '+212 234 567 890'),
        ('envelope',  'E-mail',     'info@dentcare.com'),
        ('clock',     'Horaires',   'Lun–Ven : 9h–18h, Sam : 9h–14h'),
    ]
    return render(request, 'home/contact.html', {'contact_info': contact_info})


def doctors(request):
    doctors_qs = Employee.objects.filter(
        user__role='doctor', status='active'
    ).select_related('user').order_by('emp_id')
    return render(request, 'home/doctors.html', {'doctors': doctors_qs})


def blog(request):
    articles = [
        {
            'title':   'Comment Garder vos Dents en Bonne Santé',
            'date':    '10 avril 2026',
            'excerpt': 'Des habitudes quotidiennes simples qui font une grande différence pour votre santé bucco-dentaire.',
            'img':     'https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=600',
        },
        {
            'title':   'Tout ce que vous devez savoir sur les Implants Dentaires',
            'date':    '28 mars 2026',
            'excerpt': 'Une solution permanente qui ressemble et se comporte comme de vraies dents.',
            'img':     'https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=600',
        },
        {
            'title':   'La Vérité sur le Blanchiment Dentaire',
            'date':    '15 mars 2026',
            'excerpt': 'Professionnel vs. pharmacie : quelle option vous convient ?',
            'img':     'https://images.unsplash.com/photo-1559591935-b4a60e2a9faa?w=600',
        },
    ]
    return render(request, 'home/blog.html', {'articles': articles})


def book(request):
    doctors = Employee.objects.filter(
        user__role='doctor', status='active'
    ).select_related('user')

    if request.method == 'POST':
        name      = request.POST.get('name', '').strip()
        email     = request.POST.get('email', '').strip()
        phone     = request.POST.get('phone', '').strip()
        appt_date = request.POST.get('date', '').strip()
        doctor_id = request.POST.get('doctor', '').strip()
        reason    = request.POST.get('reason', '').strip()

        if not all([name, email, phone, appt_date, doctor_id]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
        else:
            try:
                parts      = name.split(' ', 1)
                first_name = parts[0]
                last_name  = parts[1] if len(parts) > 1 else ''

                patient, _ = Patient.objects.get_or_create(
                    email=email,
                    defaults={
                        'first_name':    first_name,
                        'last_name':     last_name,
                        'phone':         phone,
                        'date_of_birth': datetime.date(2000, 1, 1),
                        'gender':        'other',
                    },
                )

                doctor = Employee.objects.get(pk=doctor_id)

                Appointment.objects.create(
                    patient    = patient,
                    doctor     = doctor,
                    date       = appt_date,
                    start_time = datetime.time(9, 0),
                    end_time   = datetime.time(9, 30),
                    reason     = reason,
                    status     = 'pending',
                )

                messages.success(
                    request,
                    f"Demande de rendez-vous reçue pour {name} ! "
                    f"Nous confirmerons votre rendez-vous prochainement."
                )
                return redirect('home:book')

            except Exception as e:
                messages.error(request, f'Impossible de sauvegarder la réservation : {e}')

    return render(request, 'home/book.html', {'doctors': doctors})
