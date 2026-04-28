"""Admin configuration for the custom User model."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.html import format_html
from .models import User


# 🔹 Custom Forms Without Password
class CustomUserChangeForm(UserChangeForm):
    """Form for editing users without password"""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'role',
            'institute_name', 'department', 'designation', 'expertise_area', 'phone_number',
            'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions',
        )


class CustomUserCreationForm(UserCreationForm):
    """Form for creating users without password"""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'role',
            'institute_name', 'department', 'designation', 'expertise_area', 'phone_number',
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password fields
        self.fields.pop('password1', None)
        self.fields.pop('password2', None)

    def save(self, commit=True):
        """Create user without password (unusable password).

        Build a User instance directly from cleaned_data instead of relying on
        UserCreationForm.save() which expects password1/password2 fields.
        """
        data_fields = (
            'username', 'email', 'first_name', 'last_name', 'role',
            'institute_name', 'department', 'designation', 'expertise_area', 'phone_number',
        )
        data = {k: self.cleaned_data.get(k) for k in data_fields}
        # Create instance without saving to DB yet
        user = User(**{k: v for k, v in data.items() if v is not None})
        user.set_unusable_password()
        # set instance so admin can access form.instance
        self.instance = user
        if commit:
            user.save()
        return user

    def save_m2m(self):
        # No many-to-many fields on this creation form; present to satisfy admin.save_related()
        return


# 🔹 Main User Admin - Dynamic Display Based on Role
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """User management with role-specific columns and details"""
    
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Dynamic list_display based on user role
    list_display = ('username', 'email', 'role_badge', 'details_column', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'institute_name', 'expertise_area')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('👤 Account Info', {'fields': ('username', 'email')}),
        ('👤 Personal Info', {'fields': ('first_name', 'last_name')}),
        ('🏢 Reviewer Details', {
            'fields': ('institute_name', 'department', 'designation', 'expertise_area', 'phone_number'),
            'classes': ('collapse',),
            'description': 'Professional details for reviewers'
        }),
        ('📊 Role & Permissions', {'fields': ('role', 'is_staff', 'is_active')}),
        ('📅 Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        ('👤 Create New User', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'role'),
        }),
        ('🏢 Reviewer Details (Optional)', {
            'classes': ('collapse',),
            'fields': ('institute_name', 'department', 'designation', 'expertise_area', 'phone_number'),
            'description': 'Fill these if creating a reviewer account'
        }),
    )

    def get_fieldsets(self, request, obj=None):
        """Use add_fieldsets for creation, fieldsets for editing"""
        if not obj:  # Adding new user
            return self.add_fieldsets
        return self.fieldsets

    def get_form(self, request, obj=None, **kwargs):
        """Use custom forms"""
        if not obj:  # Creating new
            return self.add_form
        return self.form

    def role_badge(self, obj):
        """Show role as colored badge"""
        colors = {
            'author': '#2196F3',
            'reviewer': '#4CAF50',
            'editor': '#FF9800',
            'editor-in-chief': '#F44336',
            'managing-editor': '#9C27B0',
            'associate-editor': '#00BCD4',
            'editorial-assistant': '#8BC34A',
        }
        color = colors.get(obj.role, '#757575')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = "Role"

    def details_column(self, obj):
        """Show role-specific details"""
        if obj.role == 'reviewer':
            details = f"📚 {obj.expertise_area or 'N/A'}"
            if obj.institute_name:
                details += f" | {obj.institute_name[:20]}"
            return details
        elif obj.role.startswith('editor'):
            return "✏️ Editorial"
        elif obj.role == 'author':
            return "✍️ Author"
        return "—"
    details_column.short_description = "Details"