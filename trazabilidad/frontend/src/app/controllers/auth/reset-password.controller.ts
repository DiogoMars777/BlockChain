import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: '../../views/auth/reset-password.view.html',
  styleUrls: ['../../views/auth/reset-password.view.scss']
})
export class ResetPasswordController implements OnInit {
  resetForm: FormGroup;
  token = '';
  showPassword = false;
  showConfirmPassword = false;
  isLoading = false;
  successMessage = '';
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.resetForm = this.fb.group({
      new_password: ['', [Validators.required]],
      confirm_password: ['', [Validators.required]]
    }, { validators: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    this.token = this.route.snapshot.queryParamMap.get('token') || '';
    if (!this.token) {
      this.errorMessage = 'Token de recuperación ausente o inválido.';
    }
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  toggleConfirmPasswordVisibility(): void {
    this.showConfirmPassword = !this.showConfirmPassword;
  }

  get newPasswordValue(): string {
    return this.resetForm.get('new_password')?.value || '';
  }

  get hasMinLength(): boolean {
    return this.newPasswordValue.length >= 8;
  }

  get hasUpper(): boolean {
    return /[A-Z]/.test(this.newPasswordValue);
  }

  get hasLower(): boolean {
    return /[a-z]/.test(this.newPasswordValue);
  }

  get hasNumber(): boolean {
    return /[0-9]/.test(this.newPasswordValue);
  }

  get hasSpecial(): boolean {
    return /[!@#$%^&*()_\-+=.,]/.test(this.newPasswordValue);
  }

  passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const newPassword = control.get('new_password')?.value;
    const confirmPassword = control.get('confirm_password')?.value;
    return newPassword && confirmPassword && newPassword !== confirmPassword
      ? { passwordMismatch: true }
      : null;
  }

  onSubmit(): void {
    if (this.resetForm.invalid || !this.token) {
      this.resetForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.successMessage = '';
    this.errorMessage = '';

    const payload = {
      token: this.token,
      new_password: this.resetForm.value.new_password,
      confirm_password: this.resetForm.value.confirm_password
    };

    this.authService.resetPassword(payload).subscribe({
      next: (res) => {
        this.isLoading = false;
        this.successMessage = res.message;
        setTimeout(() => this.router.navigate(['/login']), 2500);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.detail || 'Ocurrió un error al restablecer la contraseña.';
      }
    });
  }
}
