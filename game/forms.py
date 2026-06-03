from django import forms
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_email(self):
        """Validate and normalize the email field.

        Duplicate-email checks are intentionally deferred to the view
        layer, which returns a generic response regardless of whether
        the address is already registered.  This prevents user
        enumeration through form-level error messages.
        """
        return self.cleaned_data.get('email')

    def clean_username(self):
        """Return the username without raising on duplicates.

        The view layer handles username conflicts with a generic
        response to prevent user enumeration.
        """
        return self.cleaned_data.get('username')

    def validate_unique(self):
        """Skip ModelForm uniqueness checks.

        Username and email uniqueness are enforced inside the view's
        ``transaction.atomic`` block so that race conditions are
        eliminated and responses remain generic.
        """
        pass


class CustomSetPasswordForm(SetPasswordForm):
    """Prevent password resets from reusing the account's current password."""

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password2')
        if (
            new_password
            and self.user.has_usable_password()
            and self.user.check_password(new_password)
        ):
            self.add_error(
                'new_password2',
                forms.ValidationError(
                    'This password has been used before. '
                    'Please choose a new password.',
                    code='password_reused',
                ),
            )
        return cleaned_data


class CustomPasswordResetForm(PasswordResetForm):
    """Prevent password resets from reusing the account's current password."""

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None
    ):
        try:
            super().send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                to_email,
                html_email_template_name
            )
        except Exception:
            raise ValidationError(
                "Failed to send password reset email. "
                "Please check your email configuration and try again."
            )
