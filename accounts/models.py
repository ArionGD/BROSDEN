from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('TENANT', 'Tenant'),
        ('OWNER', 'Owner'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='TENANT')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser

    @property
    def is_tenant(self):
        return self.role == 'TENANT'

    @property
    def is_owner(self):
        return self.role == 'OWNER'

    @property
    def is_kyc_verified(self):
        return hasattr(self, 'kyc') and self.kyc.is_verified

    @property
    def portal_base(self):
        if self.role == 'OWNER':
            return 'owner/portal_base.html'
        elif self.role == 'TENANT':
            return 'tenant/portal_base.html'
        return 'base.html'

    def get_dashboard_url(self):
        if self.role == 'TENANT':
            return 'tenant:dashboard'
        elif self.role == 'OWNER':
            return 'owner:dashboard'
        return 'index'

    @property
    def account_type(self):
        """Returns the membership tier of the user."""
        membership = getattr(self, 'pro_membership', None)
        if membership and membership.is_active:
            return membership.tier
        return 'NORMAL'



class KYC(models.Model):
    ID_TYPES = (
        ('AADHAAR', 'Aadhaar Card'),
        ('PASSPORT', 'Passport'),
        ('VOTER_ID', 'Voter ID'),
        ('DRIVING_LICENSE', "Driver's License"),
    )

    # ── Core Link ──────────────────────────────────────────────────────────
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='kyc')

    # ── Section 1: Common Fields (Both Roles) ──────────────────────────────
    full_name = models.CharField(max_length=255, help_text="As on government ID")
    date_of_birth = models.DateField(null=True, blank=True)
    permanent_address = models.TextField(blank=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    email_address = models.EmailField(blank=True)

    # Identity Proof
    id_type = models.CharField(max_length=20, choices=ID_TYPES, blank=True)
    id_number = models.CharField(max_length=100, blank=True)
    pan_number = models.CharField(max_length=10, blank=True, help_text="10-char PAN (e.g., ABCDE1234F)")
    passport_photo = models.ImageField(upload_to='kyc/photos/', null=True, blank=True)

    # OCR Fields (Auto-filled via Tesseract)
    aadhaar_image = models.ImageField(upload_to='kyc/aadhaar/', null=True, blank=True)
    pan_image = models.ImageField(upload_to='kyc/pan/', null=True, blank=True)
    extracted_id_no = models.CharField(max_length=100, null=True, blank=True)
    verification_score = models.FloatField(default=0.0)

    # ── Section 2: Tenant-Specific Fields ─────────────────────────────────
    TENANT_TYPE_CHOICES = (
        ('PROFESSIONAL', 'Working Professional'),
        ('STUDENT', 'Student'),
    )
    tenant_type = models.CharField(max_length=20, choices=TENANT_TYPE_CHOICES, default='PROFESSIONAL')
    occupation = models.CharField(max_length=200, blank=True)
    employer_name = models.CharField(max_length=200, blank=True)
    employer_address = models.TextField(blank=True)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_relation = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    home_state = models.CharField(max_length=100, blank=True, help_text="For police verification")

    # ── Section 3: Owner-Specific Fields ──────────────────────────────────
    ownership_proof = models.FileField(upload_to='kyc/ownership/', null=True, blank=True,
                                       help_text="Electricity Bill (Latest)")
    property_tax_receipt = models.FileField(upload_to='kyc/tax/', null=True, blank=True,
                                             help_text="Latest receipt")
    property_address = models.TextField(blank=True)
    property_type = models.CharField(max_length=100, blank=True, help_text="e.g., 2BHK Apartment")
    property_size = models.CharField(max_length=50, blank=True, help_text="e.g., 1200 sq.ft")
    amenities_list = models.TextField(blank=True, help_text="Fixtures/furniture list for agreement")
    bank_account_name = models.CharField(max_length=200, blank=True)
    bank_account_number = models.CharField(max_length=30, blank=True)
    bank_ifsc = models.CharField(max_length=15, blank=True)
    co_owner_name = models.CharField(max_length=200, blank=True)
    co_owner_contact = models.CharField(max_length=15, blank=True)

    # ── Status ─────────────────────────────────────────────────────────────
    is_verified = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"KYC for {self.user.username} — {'✅ Verified' if self.is_verified else '⏳ Pending'}"

    @property
    def common_completion(self):
        """Returns percentage of common fields filled."""
        fields = [self.full_name, self.date_of_birth, self.permanent_address,
                  self.mobile_number, self.id_number, self.pan_number]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)

class ProMembership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pro_membership')
    tier = models.CharField(max_length=50, choices=[('PRO', 'BrosDen Pro'), ('GOLD', 'BrosDen Gold')], default='PRO')
    is_active = models.BooleanField(default=False)
    starts_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.tier} ({'Active' if self.is_active else 'Inactive'})"

class ProFeature(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_premium = models.BooleanField(default=True)

    def __str__(self):
        return self.name
