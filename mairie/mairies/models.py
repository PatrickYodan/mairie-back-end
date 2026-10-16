from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class Service(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


class Etablissement(models.Model):
    nom = models.CharField(max_length=150)
    ville = models.TextField()
    email_contact = models.EmailField()
    telephone = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.nom} ({self.ville})'


class Utilisateur(AbstractUser):
    nom = models.CharField(max_length=100, verbose_name='Nom', blank=True)
    prenom = models.CharField(max_length=100, verbose_name='Prénom', blank=True)
    email = models.EmailField(
        unique=True, null=True, blank=True
    )  # null=True évite les conflits d'unicité sur les chaînes vides
    telephone = models.CharField(
        max_length=20, blank=True, null=True
    )

    # Champ ajouté pour la photo de profil de l'utilisateur
    photo = models.ImageField(
        upload_to='photos_profils/', 
        blank=True, 
        null=True, 
        verbose_name='Photo de profil'
    )

    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('RH', 'Agent RH'),
        ('TUTEUR', 'Tuteur'),
    ]

    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
    ]

    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='TUTEUR'
    )
    statut_compte = models.CharField(
        max_length=10, choices=STATUT_CHOICES, default='ACTIF'
    )

    # Compte créé avec un mot de passe provisoire envoyé par e-mail : à la première connexion,
    # l'utilisateur doit renseigner son nom / prénom et choisir son propre mot de passe.
    doit_changer_mdp = models.BooleanField(
        default=False, verbose_name='Première connexion à finaliser'
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tuteurs',
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='mairies_utilisateurs_groups',
        related_query_name='mairies_utilisateur',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='mairies_utilisateurs_permissions',
        related_query_name='mairies_utilisateur',
    )

    def __str__(self):
        return (
            f'{self.prenom} {self.nom} ({self.role})'
            if self.nom
            else self.username
        )


class Stagiaire(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    
    # Champ optionnel si vous voulez aussi une photo pour le stagiaire
    photo = models.ImageField(
        upload_to='photos_stagiaires/', 
        blank=True, 
        null=True, 
        verbose_name='Photo du stagiaire'
    )
    
    adresse = models.TextField(blank=True, null=True)
    niveau_etudes = models.TextField()
    is_deleted = models.BooleanField(default=False)
    etablissement = models.ForeignKey(
        Etablissement,
        on_delete=models.SET_NULL,
        null=True,
        related_name='stagiaires',
    )

    def __str__(self):
        return f'{self.prenom} {self.nom}'


class Stage(models.Model):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente de validation'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('ANNULEE', 'Annulé'),
        ('VALIDE', 'Validé'),
    ]

    intitule = models.CharField(
        max_length=255, verbose_name='Intitulé du stage'
    )
    missions = models.TextField(blank=True, null=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    gratification = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00
    )
    statut = models.CharField(
        max_length=15, choices=STATUT_CHOICES, default='EN_ATTENTE'
    )

    stagiaire = models.ForeignKey(
        Stagiaire, on_delete=models.CASCADE, related_name='stages'
    )
    tuteur = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'TUTEUR'},
        related_name='stages_encadres',
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name='stages'
    )

    def __str__(self):
        return f'{self.intitule} - {self.stagiaire.prenom} {self.stagiaire.nom}'


class Document(models.Model):
    TYPE_DOC_CHOICES = [
        ('CONVENTIONS', 'Convention de stage'),
        ('ATTESTATION', 'Attestation de présence'),
        ('RAPPORT', 'Rapport de stage'),
        ('AUTRE', 'Autre document'),
    ]

    nom_fichier = models.CharField(
        max_length=255, verbose_name='Nom du fichier'
    )
    type_doc = models.CharField(
        max_length=20,
        choices=TYPE_DOC_CHOICES,
        default='AUTRE',
        verbose_name='Type de document',
    )
    chemin_fichier = models.FileField(
        upload_to='document_stages/', verbose_name='Fichier'
    )
    stage = models.ForeignKey(
        Stage, on_delete=models.CASCADE, related_name='documents'
    )
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nom_fichier} ({self.get_type_doc_display()})'

class AccesRole(models.Model):
    """Niveau d'accès d'un rôle à un module de l'application (géré par l'administrateur)."""

    NIVEAU_CHOICES = [
        (0, 'Aucun accès'),
        (1, 'Lecture seule'),
        (2, 'Accès complet'),
    ]

    role = models.CharField(max_length=10, choices=Utilisateur.ROLE_CHOICES)
    module = models.CharField(max_length=30)
    niveau = models.PositiveSmallIntegerField(choices=NIVEAU_CHOICES, default=0)

    class Meta:
        unique_together = ('role', 'module')
        verbose_name = "Droit d'accès"
        verbose_name_plural = "Droits d'accès"

    def __str__(self):
        return f'{self.role} → {self.module} : {self.get_niveau_display()}'
